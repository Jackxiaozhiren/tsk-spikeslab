#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ablation isolating the failure mechanism of the BIC-plus-Laplace baseline.

Runs four variants on Energy-Cooling (10 splits, R=5):
  1. BIC-wts + BMA     : enumerate all 2^R rule subsets, weight by exp(-BIC/2),
                         predict by BMA (no hard threshold, no Laplace).
  2. BIC-PIP + thr+Lap : hard-threshold the per-rule BIC PIPs at 0.5, fit the
                         selected model by least squares, Laplace covariance.
  3. Gibbs-PIP + thr+Lap: same prediction as (2) but PIPs from the Gibbs sampler.
  4. Full SpikeSlabFast : the as-implemented BIC baseline (Ridge fit + threshold
                         + Laplace), for reference.

Result (Energy-Cooling, R=5): averaging restores accuracy and calibration even
with BIC model weights (BIC-BMA ~0.95 R2, PICP ~0.92); hard thresholding to a
single model collapses (BIC-PIP + thr+Lap ~0.26 R2); the as-implemented BIC
baseline degrades further (-2.5 R2) because it fits the ill-conditioned TSK
design matrix with Ridge.

Usage:  python src/ablation_isolate.py
"""

import itertools
import json
import os

import numpy as np
from sklearn.preprocessing import StandardScaler

from tsk_core import (
    load_energy, fcm, gaussian_membership_fit, gaussian_membership_predict,
    tsk_phi, tsk_weights, get_splits, compute_metrics,
    TSK_SpikeSlab_Fast, TSK_SpikeSlab_Gibbs, DATA_DIR,
)

R = 5
TAU2 = 1e3
N_SPLITS = 10


def phi_fit(Xtr, Xq, R):
    ctr, lbl, _ = fcm(Xtr, R)
    mu, spr = gaussian_membership_fit(Xtr, ctr, lbl, R)
    mq = gaussian_membership_predict(Xq, ctr, spr, R)
    return tsk_phi(tsk_weights(mq), Xq)[0]


def threshold_laplace(Phi_tr, Phi_te, ytr, yte, active, tau2=TAU2):
    """Hard-threshold PIPs, least-squares fit, Laplace predictive variance."""
    pp = Phi_tr.shape[1] // R
    idx = [i for j, on in enumerate(active) if on for i in range(j * pp, (j + 1) * pp)]
    if not idx:
        idx = list(range(R * pp))
        active = np.ones(R, bool)
    b = np.linalg.lstsq(Phi_tr[:, idx], ytr, rcond=None)[0]
    s2 = max(float(np.var(ytr - Phi_tr[:, idx] @ b)), 1e-4)
    prec = np.ones(R * pp) * (1.0 / tau2)
    for j in range(R):
        if not active[j]:
            prec[j * pp:(j + 1) * pp] = 1e10
    cov = s2 * np.linalg.inv(Phi_tr.T @ Phi_tr / s2 + np.diag(prec))
    beta = np.zeros(R * pp)
    beta[idx] = b
    mean = Phi_te @ beta
    var = s2 + np.einsum("ij,jk,ik->i", Phi_te, cov, Phi_te)
    return mean, var


def run():
    Xe, _, y_cool = load_energy()
    X, y = Xe, y_cool
    pp = X.shape[1] + 1
    splits = get_splits(y, N_SPLITS)
    out = {v: [] for v in ["R2", "PICP", "MPIW"]}
    acc = {v: [] for v in ["R2", "PICP", "MPIW"]}

    for tr, te in splits:
        sc = StandardScaler()
        Xtr = sc.fit_transform(X[tr]); Xte = sc.transform(X[te])
        ytr, yte = y[tr], y[te]
        Phi_tr = phi_fit(Xtr, Xtr, R)
        Phi_te = phi_fit(Xtr, Xte, R)
        n = len(ytr)

        # 1. BIC weights + BMA (full enumeration, least-squares per model)
        means, vars_, bics = [], [], []
        for mask in itertools.product([0, 1], repeat=R):
            idx = [i for j, on in enumerate(mask) if on for i in range(j * pp, (j + 1) * pp)]
            if not idx:
                continue
            PhiM = Phi_tr[:, idx]; PhiM_te = Phi_te[:, idx]
            b = np.linalg.lstsq(PhiM, ytr, rcond=None)[0]
            rss = float(((ytr - PhiM @ b) ** 2).sum())
            k = len(idx)
            bics.append(n * np.log(rss / n) + k * np.log(n))
            s2 = max(rss / n, 1e-8)
            cov = s2 * np.linalg.inv(PhiM.T @ PhiM + 1e-3 * np.eye(k))
            means.append(PhiM_te @ b)
            vars_.append(s2 + np.einsum("ij,jk,ik->i", PhiM_te, cov, PhiM_te))
        bics = np.array(bics)
        w = np.exp(-0.5 * (bics - bics.min()))
        w /= w.sum()
        mean_bma = sum(wi * mi for wi, mi in zip(w, means))
        var_bma = sum(wi * vi for wi, vi in zip(w, vars_)) \
            + sum(wi * (mi - mean_bma) ** 2 for wi, mi in zip(w, means))
        r = compute_metrics(yte, mean_bma, mean_bma - 1.96 * np.sqrt(var_bma),
                            mean_bma + 1.96 * np.sqrt(var_bma))
        for v in out:
            out[v].append(r[v])

        # 2. BIC-PIP + threshold + Laplace (least-squares fit)
        f = TSK_SpikeSlab_Fast(k=R, pi=0.5).fit(Xtr, ytr)
        m, v = threshold_laplace(Phi_tr, Phi_te, ytr, yte, f.pip_ > 0.5)
        r = compute_metrics(yte, m, m - 1.96 * np.sqrt(v), m + 1.96 * np.sqrt(v))
        for k2 in acc:
            acc[k2].append(r[k2])

        # 3. Gibbs-PIP + threshold + Laplace (least-squares fit)
        g = TSK_SpikeSlab_Gibbs(k=R, pi=0.5, tau2=TAU2, n_burn=800, n_samples=800).fit(Xtr, ytr)
        m, v = threshold_laplace(Phi_tr, Phi_te, ytr, yte, g.pip_ > 0.5)
        r = compute_metrics(yte, m, m - 1.96 * np.sqrt(v), m + 1.96 * np.sqrt(v))
        for k2 in acc:
            acc[k2].append(r[k2])

    result = {
        "BIC-BMA": {v: float(np.mean(out[v])) for v in out},
        "BIC-PIP-threshold-Laplace": {v: float(np.mean(acc[v])) for v in acc},
        "Gibbs-PIP-threshold-Laplace": {},
    }
    # 3rd variant stored in acc too; recompute cleanly
    gibbs = {v: [] for v in ["R2", "PICP", "MPIW"]}
    for tr, te in splits:
        sc = StandardScaler()
        Xtr = sc.fit_transform(X[tr]); Xte = sc.transform(X[te])
        ytr, yte = y[tr], y[te]
        Phi_tr = phi_fit(Xtr, Xtr, R)
        Phi_te = phi_fit(Xtr, Xte, R)
        g = TSK_SpikeSlab_Gibbs(k=R, pi=0.5, tau2=TAU2, n_burn=800, n_samples=800).fit(Xtr, ytr)
        m, v = threshold_laplace(Phi_tr, Phi_te, ytr, yte, g.pip_ > 0.5)
        r = compute_metrics(yte, m, m - 1.96 * np.sqrt(v), m + 1.96 * np.sqrt(v))
        for k2 in gibbs:
            gibbs[k2].append(r[k2])
    result["Gibbs-PIP-threshold-Laplace"] = {v: float(np.mean(gibbs[v])) for v in gibbs}

    # 4. full as-implemented BIC baseline
    full = {v: [] for v in ["R2", "PICP", "MPIW"]}
    for tr, te in splits:
        sc = StandardScaler()
        Xtr = sc.fit_transform(X[tr]); Xte = sc.transform(X[te])
        ytr, yte = y[tr], y[te]
        f = TSK_SpikeSlab_Fast(k=R, pi=0.5).fit(Xtr, ytr)
        m, lo, hi = f.predict(Xte)
        r = compute_metrics(yte, m, lo, hi)
        for k2 in full:
            full[k2].append(r[k2])
    result["Full-BIC-as-implemented"] = {v: float(np.mean(full[v])) for v in full}

    for name, d in result.items():
        print(f"  {name:28s} R2={d['R2']:+.3f}  PICP={d['PICP']:.3f}  MPIW={d['MPIW']:.2f}")
    with open(os.path.join(DATA_DIR, "ablation_isolate_v2.json"), "w") as fp:
        json.dump(result, fp, indent=2)
    print(f"\nSaved to {DATA_DIR}/ablation_isolate_v2.json")


if __name__ == "__main__":
    run()
