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
from phase4_predictive import evaluate_interval_model
from tsk_core import get_splits, compute_metrics, OUTPUT_DIR, SEED, \
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
        for split_idx, (tr, te) in enumerate(splits):
            started = time.perf_counter()
            sc = StandardScaler()
            Xtr = sc.fit_transform(X[tr]); Xte = sc.transform(X[te])
            ytr, yte = y[tr], y[te]
            m = cls(**kw).fit(Xtr, ytr)
            if cls is TSK_LS:
                yp = m.predict(Xte)
                r = {
                    "RMSE": float(np.sqrt(np.mean((yte - yp) ** 2))),
                    "MAE": float(np.mean(np.abs(yte - yp))),
                    "R2": float(1.0 - np.sum((yte - yp) ** 2)
                                / np.sum((yte - np.mean(yte)) ** 2)),
                    "PICP": None, "MPIW": None,
                    "IntervalScore95": None, "Winkler95": None,
                    "WIS": None, "CRPS": None,
                    "n_predictive_samples": None,
                }
            else:
                r = evaluate_interval_model(
                    m, Xte, yte,
                    seed=SEED + 10000 + split_idx,
                    n_samples=512,
                )
            r.update({
                "split_idx": int(split_idx),
                "runtime_s": float(time.perf_counter() - started),
                "active_rules": (
                    int(m.active_rules)
                    if hasattr(m, "active_rules") else None
                ),
                "active_rule_ratio": (
                    float(m.active_rules / k)
                    if hasattr(m, "active_rules") else None
                ),
                "ESS_sigma2": None,
                "ESS_per_s": None,
                "sparsity_recovery": None,
            })
            if hasattr(m, "sigma2_samples_"):
                from diagnostics_gp import _ess
                ess = float(_ess(m.sigma2_samples_))
                r["ESS_sigma2"] = ess
                r["ESS_per_s"] = ess / max(r["runtime_s"], 1e-12)
            rows.append(r)
        rm = np.mean([r["RMSE"] for r in rows]); r2 = np.mean([r["R2"] for r in rows])
        summary = {}
        for metric in [
            "RMSE", "MAE", "R2", "PICP", "MPIW",
            "IntervalScore95", "Winkler95", "WIS", "CRPS",
            "active_rule_ratio", "ESS_sigma2", "ESS_per_s",
        ]:
            values = [
                r[metric] for r in rows
                if r.get(metric) is not None and np.isfinite(r[metric])
            ]
            summary[metric] = {
                "mean": float(np.mean(values)) if values else None,
                "std": float(np.std(values)) if values else None,
                "n": len(values),
            }
        out["methods"][name] = {
            "rows": rows,
            "summary": summary,
            "sparsity_recovery": None,
        }
        p = summary["PICP"]["mean"]
        w = summary["MPIW"]["mean"]
        p_text = f"{p:.3f}" if p is not None else "NA"
        w_text = f"{w:.2f}" if w is not None else "NA"
        print(f"  {name:<22} RMSE={rm:.3f}  R2={r2:+.3f}  "
              f"PICP={p_text}  MPIW={w_text}  ({time.time()-t0:.0f}s)")
    if out_path:
        import json
        with open(out_path, "w") as f:
            json.dump(out, f, indent=2)
        print("saved ->", out_path)
    return out


if __name__ == "__main__":
    import os
    X, y = load_superconductivity()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, "highdim_sparsity.json")
    run(X, y, n_splits=30, k=5, out_path=out_path)
