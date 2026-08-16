#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""High-dimensional slab-variance grid for the sparsity boundary (M10).

Runs coefficient-level SSVS on Superconductivity (d=81, n=3000) over the same
full tau^2 grid as the low-dimensional sweep (Supplementary Table 2), so the
"over-shrinks" conclusion on the high-dimensional target is established over
the whole trade-off curve rather than at two isolated points.

Writes results/raw/highdim_tau2_grid.json.  Uses 10 splits (as the
low-dimensional tau^2 sweep does) with 800 burn-in / 800 retained draws.

Usage:  python src/highdim_tau2_grid.py
"""

import json
import os
import sys
import time

import numpy as np
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tsk_core import get_splits, compute_metrics, SEED, TSK_LS, TSK_SSVS_Gibbs
from highdim_probe import load_superconductivity

TAU2_GRID = [0.1, 0.3, 1.0, 3.0, 10.0, 100.0]
N_SPLITS = 10
K = 5


def main():
    X, y = load_superconductivity()
    splits = get_splits(y, N_SPLITS)
    print(f"n={len(y)} d={X.shape[1]} k={K} splits={N_SPLITS}")

    out = {"n": len(y), "d": int(X.shape[1]), "k": K, "n_splits": N_SPLITS,
           "dataset": "Superconductivity (UCI 464, subsample)",
           "methods": {}}
    # Dense reference (10 splits)
    t0 = time.time(); rows = []
    for tr, te in splits:
        sc = StandardScaler(); Xtr = sc.fit_transform(X[tr]); Xte = sc.transform(X[te])
        m = TSK_LS(k=K).fit(Xtr, y[tr])
        yp = m.predict(Xte)
        rows.append(compute_metrics(y[te], yp))
    r2 = np.mean([r["R2"] for r in rows])
    out["methods"]["TSK-LS (dense)"] = {"R2_mean": float(r2)}
    print(f"  TSK-LS            R2={r2:+.3f}  ({time.time()-t0:.0f}s)")

    for tau2 in TAU2_GRID:
        t0 = time.time(); rows = []
        for tr, te in splits:
            sc = StandardScaler(); Xtr = sc.fit_transform(X[tr]); Xte = sc.transform(X[te])
            m = TSK_SSVS_Gibbs(k=K, tau2=tau2, n_burn=800, n_samples=800,
                               seed=SEED).fit(Xtr, y[tr])
            yp, yl, yu = m.predict(Xte)
            rows.append(compute_metrics(y[te], yp, yl, yu))
        r2 = np.mean([r["R2"] for r in rows]); rm = np.mean([r["RMSE"] for r in rows])
        p = np.mean([r["PICP"] for r in rows]); w = np.mean([r["MPIW"] for r in rows])
        out["methods"][f"SSVS tau2={tau2}"] = {
            "R2_mean": float(r2), "RMSE_mean": float(rm),
            "PICP": float(p), "MPIW": float(w),
        }
        print(f"  SSVS tau2={tau2:<6} R2={r2:+.3f} RMSE={rm:.2f} PICP={p:.3f} MPIW={w:.2f}  ({time.time()-t0:.0f}s)")

    out_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "results", "raw", "highdim_tau2_grid.json")
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
