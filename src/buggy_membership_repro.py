#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reproduction of the membership-spread bug (before-values for Fig. 1).

The buggy implementation fixes the fuzzy partition at training time but, at
prediction time, RE-ESTIMATES the Gaussian membership spreads from the query
data while passing a placeholder (all-zero) label vector.  The partition used
to build the prediction-time design matrix therefore no longer matches the one
used to fit the consequents, which silently depresses accuracy.

This script reproduces exactly that behavior on the same 30 fixed splits
(SEED=42) used by the main pipeline and writes results/raw/buggy_baselines.json
so the "reported (buggy)" R^2 values shown in Fig. 1 are regenerable from data
rather than hard-coded constants.

Usage:  python src/buggy_membership_repro.py
"""

import json
import os

import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score

from tsk_core import (
    load_energy, load_concrete, get_splits, compute_metrics,
    gaussian_membership_fit, gaussian_membership_predict,
    tsk_phi, tsk_weights, TSK_LS, TSK_Bayesian,
    DATA_DIR, SEED,
)

N_SPLITS = 30
R = 5
S = 1.5


def buggy_phi(X, centers, k=R, s=S):
    """Prediction-time design matrix under the buggy membership routine.

    Spreads are re-estimated from the query data with a placeholder all-zero
    label vector, so every query point is assigned to rule 0: rule 0 receives
    the global query spread and the remaining rules receive the empty-cluster
    default.  This is the 'labels=zeros' re-estimation described in the paper.
    """
    labels = np.zeros(len(X), dtype=int)
    mu, _spreads = gaussian_membership_fit(X, centers, labels, k, s=s)
    return tsk_phi(tsk_weights(mu), X)[0]


def run_buggy(ds_name, X, y):
    splits = get_splits(y, N_SPLITS)
    rows = {"TSK-LS": [], "Bayesian-TSK": []}
    for tr, te in splits:
        sc = StandardScaler()
        Xtr = sc.fit_transform(X[tr]); Xte = sc.transform(X[te])
        ytr, yte = y[tr], y[te]

        # Correct training-time partition: centers + spreads fixed on training.
        m = TSK_LS(k=R).fit(Xtr, ytr)
        ctr = m.ctr_
        # Buggy prediction-time design matrix (spreads re-estimated from query).
        Phi_te_bug = buggy_phi(Xte, ctr)
        yp = Phi_te_bug @ m.beta_
        rows["TSK-LS"].append(compute_metrics(yte, yp))

        mb = TSK_Bayesian(k=R).fit(Xtr, ytr)
        ctrb = mb.ctr_
        Phi_te_bug_b = buggy_phi(Xte, ctrb)
        mean = Phi_te_bug_b @ mb.beta_
        var = np.array([mb.sigma2_ + Phi_te_bug_b[i] @ mb.cov_beta_ @ Phi_te_bug_b[i]
                        for i in range(len(Xte))])
        yl, yu = mean - 1.96 * np.sqrt(var), mean + 1.96 * np.sqrt(var)
        rows["Bayesian-TSK"].append(compute_metrics(yte, mean, yl, yu))
    return rows


def main():
    Xe, y_heat, y_cool = load_energy()
    Xc, y_conc = load_concrete()
    out = {}
    for name, X, y in [("Energy-Heating", Xe, y_heat),
                       ("Energy-Cooling", Xe, y_cool),
                       ("Concrete", Xc, y_conc)]:
        rows = run_buggy(name, X, y)
        out[name] = rows
        for meth in ["TSK-LS", "Bayesian-TSK"]:
            r2 = np.mean([r["R2"] for r in rows[meth]])
            print(f"  {name:14s} {meth:12s} buggy R^2 = {r2:.4f}")
    with open(os.path.join(DATA_DIR, "buggy_baselines.json"), "w") as f:
        json.dump(out, f, indent=2, default=float)
    print("wrote results/raw/buggy_baselines.json")


if __name__ == "__main__":
    main()
