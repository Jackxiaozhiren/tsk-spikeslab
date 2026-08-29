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
from phase4_predictive import evaluate_interval_model
from tsk_core import (
    get_splits, OUTPUT_DIR, SEED, TSK_LS, TSK_SSVS_Gibbs
)
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
    for split_idx, (tr, te) in enumerate(splits):
        sc = StandardScaler(); Xtr = sc.fit_transform(X[tr]); Xte = sc.transform(X[te])
        started = time.perf_counter()
        m = TSK_LS(k=K).fit(Xtr, y[tr])
        yp = m.predict(Xte)
        rows.append({
            "RMSE": float(np.sqrt(np.mean((y[te] - yp) ** 2))),
            "MAE": float(np.mean(np.abs(y[te] - yp))),
            "R2": float(1.0 - np.sum((y[te] - yp) ** 2)
                        / np.sum((y[te] - np.mean(y[te])) ** 2)),
            "PICP": None, "MPIW": None,
            "IntervalScore95": None, "Winkler95": None,
            "WIS": None, "CRPS": None,
            "split_idx": int(split_idx),
            "runtime_s": float(time.perf_counter() - started),
            "active_rule_ratio": 1.0,
            "ESS_sigma2": None, "ESS_per_s": None,
        })
    r2 = np.mean([r["R2"] for r in rows])
    out["methods"]["TSK-LS (dense)"] = {
        "rows": rows,
        "summary": {
            "R2": {
                "mean": float(r2), "std": float(np.std([r["R2"] for r in rows])),
                "n": len(rows),
            },
            "MAE": {
                "mean": float(np.mean([r["MAE"] for r in rows])),
                "std": float(np.std([r["MAE"] for r in rows])),
                "n": len(rows),
            },
            "PICP": {"mean": None, "std": None, "n": 0},
            "MPIW": {"mean": None, "std": None, "n": 0},
        },
        "sparsity_recovery": None,
    }
    print(f"  TSK-LS            R2={r2:+.3f}  ({time.time()-t0:.0f}s)")

    for tau2 in TAU2_GRID:
        t0 = time.time(); rows = []
        for split_idx, (tr, te) in enumerate(splits):
            sc = StandardScaler(); Xtr = sc.fit_transform(X[tr]); Xte = sc.transform(X[te])
            started = time.perf_counter()
            m = TSK_SSVS_Gibbs(k=K, tau2=tau2, n_burn=800, n_samples=800,
                               seed=SEED).fit(Xtr, y[tr])
            row = evaluate_interval_model(
                m, Xte, y[te],
                seed=SEED + 10000 + split_idx, n_samples=512,
            )
            row.update({
                "split_idx": int(split_idx),
                "runtime_s": float(time.perf_counter() - started),
                "active_rule_ratio": float(m.active_rules / K),
                "ESS_sigma2": None, "ESS_per_s": None,
            })
            from diagnostics_gp import _ess
            row["ESS_sigma2"] = float(_ess(m.sigma2_samples_))
            row["ESS_per_s"] = row["ESS_sigma2"] / max(row["runtime_s"], 1e-12)
            rows.append(row)
        summary = {}
        for metric in [
            "RMSE", "MAE", "R2", "PICP", "MPIW",
            "IntervalScore95", "Winkler95", "WIS", "CRPS",
            "active_rule_ratio", "ESS_sigma2", "ESS_per_s",
        ]:
            values = [r[metric] for r in rows if r.get(metric) is not None]
            summary[metric] = {
                "mean": float(np.mean(values)) if values else None,
                "std": float(np.std(values)) if values else None,
                "n": len(values),
            }
        out["methods"][f"SSVS tau2={tau2}"] = {
            "rows": rows, "summary": summary,
            "sparsity_recovery": None,
        }
        r2 = summary["R2"]["mean"]; rm = summary["RMSE"]["mean"]
        p = summary["PICP"]["mean"]; w = summary["MPIW"]["mean"]
        print(f"  SSVS tau2={tau2:<6} R2={r2:+.3f} RMSE={rm:.2f} "
              f"PICP={p:.3f} MPIW={w:.2f}  ({time.time()-t0:.0f}s)")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, "highdim_tau2_grid.json")
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
