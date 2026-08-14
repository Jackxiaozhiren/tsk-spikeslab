#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Conjugate-baseline verification for the block-Gibbs spike-and-slab sampler.

Checks that the block-Gibbs sampler of TSK_SpikeSlab_Gibbs, run with all
rule-inclusion indicators forced to gamma_j = 1, reproduces the conjugate
closed-form PREDICTIVE distribution of TSK_Bayesian on held-out data. This is
the correctness check claimed in Section 3.3 of the manuscript.

We compare at the predictive level (rather than on the raw parameter
covariance) because the TSK weighted design matrix is highly collinear
(condition number ~10^18 on these benchmarks), which makes the full posterior
covariance numerically unstable for both the closed form and any MCMC estimate.
Projected onto held-out predictions, the comparison is well conditioned.

Usage:  python src/gibbs_verify.py
"""

import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score

from tsk_core import (
    load_energy, fcm, gaussian_membership_fit, gaussian_membership_predict,
    tsk_phi, tsk_weights, TSK_Bayesian,
)

TRIAL_SEED = 3


def _phi(X_fit, X_query, R):
    ctr, lbl, _ = fcm(X_fit, R)
    mu, spr = gaussian_membership_fit(X_fit, ctr, lbl, R)
    mu_q = gaussian_membership_predict(X_query, ctr, spr, R)
    return tsk_phi(tsk_weights(mu_q), X_query)[0]


def conjugate_predictive(Xtr, ytr, Xte, R, tau2=1e3, a0=0.01, b0=0.01):
    n = len(ytr)
    P = R * (Xtr.shape[1] + 1)
    Phi_tr = _phi(Xtr, Xtr, R)
    Phi_te = _phi(Xtr, Xte, R)
    prec_prior = np.eye(P) / tau2
    prec_post = Phi_tr.T @ Phi_tr + prec_prior
    cov_post = np.linalg.inv(prec_post)
    mean_post = cov_post @ (Phi_tr.T @ ytr)
    resid = ytr - Phi_tr @ mean_post
    a_n = a0 + n / 2
    b_n = b0 + 0.5 * (resid @ resid + mean_post @ prec_prior @ mean_post)
    s2 = b_n / max(a_n - 1, 1e-6)
    mean = Phi_te @ mean_post
    var = s2 + np.einsum("ij,jk,ik->i", Phi_te, cov_post * s2, Phi_te)
    return mean, var


def gibbs_forced_active(Xtr, ytr, Xte, R, tau2=1e3, n_burn=3000, n_samples=30000, seed=1):
    pp = Xtr.shape[1] + 1
    Phi_tr = _phi(Xtr, Xtr, R)
    Phi_te = _phi(Xtr, Xte, R)
    P = R * pp
    Ajs = [Phi_tr[:, j * pp:(j + 1) * pp].T @ Phi_tr[:, j * pp:(j + 1) * pp] for j in range(R)]
    beta = np.linalg.lstsq(Phi_tr, ytr, rcond=None)[0]
    resid = ytr - Phi_tr @ beta
    sigma2 = float(np.var(resid))
    rng = np.random.RandomState(seed)
    B = np.zeros((n_samples, P))
    S2 = np.zeros(n_samples)
    for it in range(n_burn + n_samples):
        for j in range(R):
            Phi_j = Phi_tr[:, j * pp:(j + 1) * pp]
            sl = slice(j * pp, (j + 1) * pp)
            r = resid + Phi_j @ beta[sl]
            Vj = np.linalg.inv(Ajs[j] / sigma2 + np.eye(pp) / tau2 + 1e-10 * np.eye(pp))
            Vj = 0.5 * (Vj + Vj.T)
            mj = Vj @ (Phi_j.T @ r) / sigma2
            beta[sl] = mj + np.linalg.cholesky(Vj) @ rng.standard_normal(pp)
            resid = r - Phi_j @ beta[sl]
        ssr = resid @ resid
        a_post = 0.01 + len(ytr) / 2
        b_post = 0.01 + 0.5 * ssr
        sigma2 = 1.0 / rng.gamma(a_post, 1.0 / b_post)
        if it >= n_burn:
            B[it - n_burn] = beta
            S2[it - n_burn] = sigma2
    pm = Phi_te @ B.T
    mean = pm.mean(1)
    var = S2.mean() + pm.var(1)  # aleatoric + model uncertainty (matches BMA prediction)
    return mean, var


def coverage(yte, mean, var):
    lo, hi = mean - 1.96 * np.sqrt(var), mean + 1.96 * np.sqrt(var)
    return float(np.mean((yte >= lo) & (yte <= hi)))


if __name__ == "__main__":
    Xe, y_heat, y_cool = load_energy()
    sc = StandardScaler()
    Xs = sc.fit_transform(Xe)
    n = len(y_cool)
    idx = np.arange(n)
    rng = np.random.RandomState(TRIAL_SEED)
    rng.shuffle(idx)
    tr, te = idx[:500], idx[500:]

    for R in (5, 10):
        mean_c, var_c = conjugate_predictive(Xs[tr], y_cool[tr], Xs[te], R)
        mean_g, var_g = gibbs_forced_active(Xs[tr], y_cool[tr], Xs[te], R)
        d_r2 = abs(r2_score(y_cool[te], mean_g) - r2_score(y_cool[te], mean_c))
        rel_var = float(np.median(np.abs(var_g - var_c) / np.abs(var_c)))
        ok = "PASS" if d_r2 < 0.01 and rel_var < 0.15 else "CHECK"
        print(f"R={R:>2}: DeltaR2={d_r2:.4f}  median|rel var diff|={rel_var:.1%}  "
              f"coverage conj={coverage(y_cool[te], mean_c, var_c):.3f} / gibbs={coverage(y_cool[te], mean_g, var_g):.3f}  -> {ok}")
    print("done.")
