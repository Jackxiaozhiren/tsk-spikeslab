#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Synthetic validation of the rule-level inclusion full conditional (Eq. 10).

Generates a TSK regression with KNOWN sparse ground truth (only two of R=5
rules active), runs the block-Gibbs sampler, and compares the sampler's
posterior inclusion probabilities against EXACT values obtained by exhaustive
enumeration of all 2^R rule configurations (marginal likelihood computed in
closed form, sigma^2 integrated out over its inverse-gamma prior).  This is the
direct validation of the gamma full conditional that the real benchmarks cannot
provide (there the inclusion indicators saturate near 1).

Writes results/raw/synthetic_gamma_verify.json.

Usage:  python src/synthetic_gamma_verify.py
"""

import json
import os

import numpy as np
from scipy.integrate import quad
from scipy.special import logsumexp

from tsk_core import (
    fcm, gaussian_membership_fit, gaussian_membership_predict,
    tsk_phi, tsk_weights, TSK_SpikeSlab_Gibbs, DATA_DIR,
)

R = 5
D = 2
N = 600
TRUE_ACTIVE = {0, 2}          # rules 0 and 2 are active in the ground truth
SIGMA2_TRUE = 1.0
PRIOR_PI = 0.5
TAU2 = 10.0
BURN, SAMPLES = 2000, 10000
SEED = 42


def build_synthetic():
    rng = np.random.RandomState(SEED)
    X = rng.uniform(0.05, 0.95, size=(N, D))
    X = (X - X.mean(axis=0)) / X.std(axis=0)
    ctr, lbl, _ = fcm(X, R)
    mu, spr = gaussian_membership_fit(X, ctr, lbl, R)
    Phi, pp = tsk_phi(tsk_weights(mu), X)

    beta_true = np.zeros(R * pp)
    beta_true[0 * pp:1 * pp] = np.array([0.8, 0.5, -0.3])
    beta_true[2 * pp:3 * pp] = np.array([-0.6, 0.4, 0.2])
    y = Phi @ beta_true + np.sqrt(SIGMA2_TRUE) * rng.standard_normal(N)
    return X, y, Phi, pp, ctr, spr


def exact_marginal_logp(y, Phi_g, sigma2, tau2=TAU2):
    """log p(y | gamma, sigma2) = log N(y; 0, sigma2 I + tau2 Phi_g Phi_g^T).

    Woodbury identities with A = Phi_g^T Phi_g / sigma2 + I / tau2:
      det(sigma2 I + tau2 Phi Phi^T) = sigma2^n * tau2^p * det(A)
      y^T (sigma2 I + tau2 Phi Phi^T)^{-1} y
          = (y.y)/sigma2 - (Phi^T y)^T A^{-1} (Phi^T y) / sigma2^2
    """
    n = len(y)
    G = Phi_g.T @ Phi_g
    A = G / sigma2 + np.eye(G.shape[0]) / tau2
    _, logdetA = np.linalg.slogdet(A)
    logdetS = n * np.log(sigma2) + G.shape[0] * np.log(tau2) + logdetA
    yG = Phi_g.T @ y
    quad_form = (y @ y) / sigma2 - (yG @ np.linalg.solve(A, yG)) / sigma2 ** 2
    return -0.5 * (n * np.log(2 * np.pi) + logdetS + quad_form)


def exact_inclusion_probs(Phi, pp, y):
    """Exact posterior inclusion probabilities via 2^R enumeration.

    Integrates sigma2 out over InvGamma(0.01, 0.01) by Gauss-Legendre in log
    space, then weights configurations by pi^{|g|} (1-pi)^{R-|g|} p(y|g).
    """
    R_ = R
    logw = np.zeros(1 << R_)
    active_sets = []
    nodes, weights = np.polynomial.legendre.leggauss(200)
    t = 5.0 * nodes                      # t in [-5, 5]  ->  sigma2 in [e^-5, e^5]
    sg = np.exp(t)
    wg = weights * 5.0 * sg              # dx/dt weight
    a0 = b0 = 0.01
    for code in range(1 << R_):
        act = [j for j in range(R_) if (code >> j) & 1]
        active_sets.append(act)
        Phi_g = Phi[:, [j * pp + c for j in act for c in range(pp)]] if act else Phi[:, :0]
        if act:
            vals = np.array([exact_marginal_logp(y, Phi_g, s) for s in sg])
            vals += -b0 / sg - (a0 + 1.0) * np.log(sg)   # InvGamma prior
            logw[code] = logsumexp(vals + np.log(wg))    # integrate sigma2
        else:                                            # gamma = 0 config: y ~ N(0, s^2 I)
            vals = np.array([-0.5 * (len(y) * np.log(2 * np.pi * s) + (y @ y) / s) for s in sg])
            vals += -b0 / sg - (a0 + 1.0) * np.log(sg)
            logw[code] = logsumexp(vals + np.log(wg))
        k = len(act)
        logw[code] += k * np.log(PRIOR_PI) + (R_ - k) * np.log(1 - PRIOR_PI)
    logw -= logsumexp(logw)              # normalize
    w = np.exp(logw)
    pip = np.zeros(R_)
    for j in range(R_):
        pip[j] = sum(w[code] for code in range(1 << R_) if (code >> j) & 1)
    return pip, w, active_sets


def main():
    X, y, Phi, pp, ctr, spr = build_synthetic()
    print(f"synthetic: n={N} d={D} R={R} true active rules={sorted(TRUE_ACTIVE)}")

    # Exact enumeration
    pip_exact, w, active_sets = exact_inclusion_probs(Phi, pp, y)
    print("exact inclusion probs:", np.round(pip_exact, 4))

    # Gibbs sampler (as in the paper: pi=0.5, tau2, sigma2 InvGamma(0.01,0.01))
    m = TSK_SpikeSlab_Gibbs(k=R, pi=PRIOR_PI, tau2=TAU2,
                            n_burn=BURN, n_samples=SAMPLES, seed=SEED).fit(X, y)
    pip_gibbs = m.pip_
    print("gibbs inclusion probs:", np.round(pip_gibbs, 4))

    # Agreement
    diff = np.abs(pip_gibbs - pip_exact)
    top = int(np.argmax(pip_exact))
    print(f"max |gibbs - exact| = {diff.max():.4f} (rule {diff.argmax()})")
    print(f"top active rule {top}: gibbs {pip_gibbs[top]:.4f} vs exact {pip_exact[top]:.4f}")

    # BMA predictive from the sampler's own samples (law of total variance)
    Phi_te = Phi
    B, G, S2 = m.beta_samples_, m.gamma_samples_, m.sigma2_samples_
    means = Phi_te @ B.T                       # (n, n_samples)
    mean_g = means.mean(axis=1)
    var_g = S2.mean() + means.var(axis=1)      # aleatoric + model uncertainty
    # exact BMA predictive: E[y*|y] = sum_g w(g) mean_post(g); Var via total variance
    mean_exact = np.zeros(N)
    var_exact = np.zeros(N)
    yg = y
    for code, act in enumerate(active_sets):
        Phi_g = Phi[:, [j * pp + c for j in act for c in range(pp)]] if act else Phi[:, :0]
        if act:
            G = Phi_g.T @ Phi_g
            A = G / SIGMA2_TRUE + np.eye(G.shape[0]) / TAU2
            mpost = np.linalg.solve(A, Phi_g.T @ yg) / SIGMA2_TRUE
            mean_c = Phi_te[:, [j * pp + c for j in act for c in range(pp)]] @ mpost
            # predictive var under config (sigma2 fixed): s2 + Phi C Phi^T
            C = np.linalg.inv(A) / SIGMA2_TRUE * SIGMA2_TRUE  # (G/s2 + I/tau2)^{-1}
            var_c = SIGMA2_TRUE + np.einsum("ij,jk,ik->i",
                                            Phi_te[:, [j * pp + c for j in act for c in range(pp)]],
                                            C, Phi_te[:, [j * pp + c for j in act for c in range(pp)]])
        else:
            mean_c = np.zeros(N)
            var_c = SIGMA2_TRUE * np.ones(N)
        mean_exact += w[code] * mean_c
        var_exact += w[code] * (var_c + mean_c ** 2)
    var_exact -= mean_exact ** 2
    # Compare to Gibbs BMA predictive (var uses sampled sigma2 + model uncertainty)
    rel_var = float(np.median(np.abs(var_g - var_exact) / np.abs(var_exact)))
    d_mean = float(np.max(np.abs(mean_g - mean_exact)))
    print(f"BMA predictive: max|mean diff|={d_mean:.4f}  median|rel var diff|={rel_var:.1%}")

    out = {
        "n": N, "d": D, "R": R, "true_active": sorted(TRUE_ACTIVE),
        "pi": PRIOR_PI, "tau2": TAU2, "seed": SEED,
        "pip_exact": list(np.round(pip_exact, 5)),
        "pip_gibbs": list(np.round(pip_gibbs, 5)),
        "max_abs_diff_pip": float(diff.max()),
        "bma_max_abs_mean_diff": float(d_mean),
        "bma_median_rel_var_diff": float(rel_var),
    }
    with open(os.path.join(DATA_DIR, "synthetic_gamma_verify.json"), "w") as f:
        json.dump(out, f, indent=2)
    print("wrote results/raw/synthetic_gamma_verify.json")


if __name__ == "__main__":
    main()
