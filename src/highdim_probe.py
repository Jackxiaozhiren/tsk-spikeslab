#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
R1 probe: does sparsity pay off on a REAL high-dimensional regression
benchmark (Superconductivity, UCI id 464, d=81)?

Compares dense TSK-LS / conjugate Bayesian-TSK against rule-level Gibbs
sparsity and coefficient-level SSVS. If sparsity beats the dense baseline
here, the "sparsity boundary" becomes a constructive regime characterization
(high-d with irrelevant features); if not, the boundary extends to real
high-d data.
"""

import os
import sys
import time

import numpy as np
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tsk_core import get_splits, compute_metrics, SEED, \
    TSK_LS, TSK_Bayesian, TSK_SpikeSlab_Gibbs, TSK_SSVS_Gibbs


def load_superconductivity(n_subsample=3000, seed=SEED):
    from ucimlrepo import fetch_ucirepo
    d = fetch_ucirepo(id=464)
    X = d.data.features.values.astype(float)
    y = d.data.targets.values.astype(float).ravel()
    rng = np.random.RandomState(seed)
    idx = rng.choice(len(y), size=min(n_subsample, len(y)), replace=False)
    return X[idx], y[idx]


def run(X, y, n_splits=30, k=5, out_path=None):
    splits = get_splits(y, n_splits)
    methods = [
        ("TSK-LS", TSK_LS, {"k": k}),
        ("Bayesian-TSK", TSK_Bayesian, {"k": k}),
        ("SpikeSlab-Gibbs", TSK_SpikeSlab_Gibbs,
         {"k": k, "pi": 0.5, "n_burn": 1000, "n_samples": 2000}),
        ("SSVS-Gibbs (tau2=1)", TSK_SSVS_Gibbs,
         {"k": k, "pi": 0.5, "tau2": 1.0, "n_burn": 800, "n_samples": 800}),
        ("SSVS-Gibbs (tau2=10)", TSK_SSVS_Gibbs,
         {"k": k, "pi": 0.5, "tau2": 10.0, "n_burn": 800, "n_samples": 800}),
    ]
    print(f"n={len(y)}  d={X.shape[1]}  k={k}  splits={n_splits}")
    out = {"n": len(y), "d": int(X.shape[1]), "k": k, "n_splits": n_splits,
           "dataset": "Superconductivity (UCI 464, subsample)", "methods": {}}
    for name, cls, kw in methods:
        t0 = time.time()
        rows = []
        for tr, te in splits:
            sc = StandardScaler()
            Xtr = sc.fit_transform(X[tr]); Xte = sc.transform(X[te])
            ytr, yte = y[tr], y[te]
            m = cls(**kw).fit(Xtr, ytr)
            if cls is TSK_LS:
                yp = m.predict(Xte)
                r = compute_metrics(yte, yp)
            else:
                yp, yl, yu = m.predict(Xte)
                r = compute_metrics(yte, yp, yl, yu)
            rows.append(r)
        rm = np.mean([r["RMSE"] for r in rows]); r2 = np.mean([r["R2"] for r in rows])
        pics = [r.get("PICP") for r in rows if r.get("PICP") is not None]
        mpis = [r.get("MPIW") for r in rows if r.get("MPIW") is not None]
        p = np.mean(pics) if pics else np.nan
        w = np.mean(mpis) if mpis else np.nan
        out["methods"][name] = {
            "RMSE_mean": float(rm), "RMSE_std": float(np.std([r["RMSE"] for r in rows])),
            "R2_mean": float(r2), "R2_std": float(np.std([r["R2"] for r in rows])),
            "PICP": float(p), "MPIW": float(w),
        }
        print(f"  {name:<22} RMSE={rm:.3f}  R2={r2:+.3f}  "
              f"PICP={p:.3f}  MPIW={w:.2f}  ({time.time()-t0:.0f}s)")
    if out_path:
        import json
        with open(out_path, "w") as f:
            json.dump(out, f, indent=2)
        print("saved ->", out_path)
    return out


if __name__ == "__main__":
    import os
    X, y = load_superconductivity()
    out_path = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "results", "raw", "highdim_sparsity.json")
    run(X, y, n_splits=30, k=5, out_path=out_path)
