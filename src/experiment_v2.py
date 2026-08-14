#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrected experiment pipeline for the reframed paper:

  "Correct Bayesian Inference for TSK Fuzzy Systems: a Reproducibility Fix
   and Calibrated Model-Averaged Prediction Intervals"

Tiers:
  1. Main comparison — 4 TSK methods + RF/SVR, 4 datasets, 30 splits.
  2. tau2 sensitivity — the sparsity-accuracy trade-off (SSVS coefficient-level).
  3. Irrelevant-feature regime — FCM robustness (dense does NOT collapse).
"""

import json
import os
import time

import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR

from tsk_core import (
    load_energy, load_concrete, append_noise_features,
    get_splits, compute_metrics,
    TSK_LS, TSK_Bayesian, TSK_SpikeSlab_Fast, TSK_SpikeSlab_Gibbs, TSK_SSVS_Gibbs,
    DATA_DIR, SEED,
)

N_SPLITS = 30

DATASETS = {}
Xe, y_heat, y_cool = load_energy()
Xc, y_conc = load_concrete()
DATASETS["Energy-Heating"] = (Xe, y_heat)
DATASETS["Energy-Cooling"] = (Xe, y_cool)
DATASETS["Concrete"] = (Xc, y_conc)

METHODS = [
    ("TSK-LS", TSK_LS, {"k": 5}),
    ("Bayesian-TSK", TSK_Bayesian, {"k": 5}),
    ("SpikeSlab-Fast", TSK_SpikeSlab_Fast, {"k": 5, "pi": 0.5}),
    ("SpikeSlab-Gibbs", TSK_SpikeSlab_Gibbs, {"k": 5, "pi": 0.5, "n_burn": 1000, "n_samples": 2000}),
]

ML_METHODS = [
    ("RandomForest", "rf", {"max_depth": 10}),
    ("SVR", "svr", {"C": 1.0, "gamma": "scale"}),
]


def fit_predict(cls, kw, Xtr, ytr, Xte, yte, split_idx):
    m = cls(**kw).fit(Xtr, ytr)
    if cls is TSK_LS:
        yp = m.predict(Xte)
        return compute_metrics(yte, yp), m.active_rules
    yp, yl, yu = m.predict(Xte)
    r = compute_metrics(yte, yp, yl, yu)
    return r, m.active_rules


def run_main_comparison():
    print("=" * 70)
    print("TIER 1: MAIN COMPARISON (30 splits)")
    print("=" * 70)
    results = {}
    for ds_name, (X, y) in DATASETS.items():
        print(f"\n--- {ds_name} (n={len(y)}, d={X.shape[1]}) ---")
        splits = get_splits(y, N_SPLITS)
        ds_res = {}
        for name, cls, kw in METHODS:
            t0 = time.time()
            rows = []
            for si, (tr, te) in enumerate(splits):
                sc = StandardScaler()
                Xtr = sc.fit_transform(X[tr]); Xte = sc.transform(X[te])
                ytr, yte = y[tr], y[te]
                r, ar = fit_predict(cls, kw, Xtr, ytr, Xte, yte, si)
                r["ActiveRules"] = ar
                rows.append(r)
            ds_res[name] = rows
            rm = np.mean([r["RMSE"] for r in rows]); r2 = np.mean([r["R2"] for r in rows])
            p = np.nanmean([r.get("PICP", np.nan) for r in rows])
            w = np.nanmean([r.get("MPIW", np.nan) for r in rows])
            ar = np.mean([r["ActiveRules"] for r in rows])
            print(f"  {name:<16} RMSE={rm:.3f}  R2={r2:+.3f}  Rules={ar:.1f}  "
                  f"PICP={p:.3f}  MPIW={w:.2f}  ({time.time()-t0:.0f}s)")
        for name, kind, kw in ML_METHODS:
            t0 = time.time()
            rows = []
            for si, (tr, te) in enumerate(splits):
                sc = StandardScaler()
                Xtr = sc.fit_transform(X[tr]); Xte = sc.transform(X[te])
                ytr, yte = y[tr], y[te]
                if kind == "rf":
                    m = RandomForestRegressor(n_estimators=300, max_depth=kw["max_depth"],
                                              random_state=SEED + si, n_jobs=-1)
                else:
                    m = SVR(kernel="rbf", C=kw["C"], gamma=kw["gamma"])
                m.fit(Xtr, ytr)
                yp = m.predict(Xte)
                r = compute_metrics(yte, yp)
                r["ActiveRules"] = None
                rows.append(r)
            ds_res[name] = rows
            rm = np.mean([r["RMSE"] for r in rows]); r2 = np.mean([r["R2"] for r in rows])
            print(f"  {name:<16} RMSE={rm:.3f}  R2={r2:+.3f}  ({time.time()-t0:.0f}s)")
        results[ds_name] = ds_res
    with open(os.path.join(DATA_DIR, "tier1_v2.json"), "w") as f:
        json.dump({k: {kk: vv for kk, vv in v.items()} for k, v in results.items()},
                  f, indent=2, default=float)
    return results


def run_tau2_sensitivity():
    print("\n" + "=" * 70)
    print("TIER 2: tau2 SENSITIVITY (SSVS, Energy-Cooling, 10 splits)")
    print("=" * 70)
    X, y = DATASETS["Energy-Cooling"]
    splits = get_splits(y, 10)
    out = {}
    for tau2 in [0.1, 0.3, 1.0, 3.0, 10.0, 100.0]:
        rows = []
        for tr, te in splits:
            sc = StandardScaler()
            Xtr = sc.fit_transform(X[tr]); Xte = sc.transform(X[te])
            ytr, yte = y[tr], y[te]
            m = TSK_SSVS_Gibbs(k=5, tau2=tau2, n_burn=800, n_samples=800).fit(Xtr, ytr)
            yp, yl, yu = m.predict(Xte)
            r = compute_metrics(yte, yp, yl, yu)
            rows.append(r)
        rm = np.mean([r["RMSE"] for r in rows]); r2 = np.mean([r["R2"] for r in rows])
        p = np.mean([r["PICP"] for r in rows])
        out[str(tau2)] = rows
        print(f"  tau2={tau2:<6} RMSE={rm:.3f}  R2={r2:+.3f}  PICP={p:.3f}")
    with open(os.path.join(DATA_DIR, "tier2_tau2_v2.json"), "w") as f:
        json.dump({k: v for k, v in out.items()}, f, indent=2, default=float)
    return out


def run_noise_regime():
    print("\n" + "=" * 70)
    print("TIER 3: IRRELEVANT-FEATURE REGIME (FCM, Energy-Cooling + noise)")
    print("=" * 70)
    from sklearn.metrics import r2_score
    X, y = DATASETS["Energy-Cooling"]
    out = {}
    for n_noise in [0, 4, 12, 30]:
        Xn = append_noise_features(X, n_noise) if n_noise else X
        splits = get_splits(y, 10)
        row = {}
        for name, cls, kw in [
            ("TSK-LS", TSK_LS, {"k": 5}),
            ("SpikeSlab-Gibbs", TSK_SpikeSlab_Gibbs, {"k": 5, "n_burn": 800, "n_samples": 800}),
            ("SSVS-Gibbs", TSK_SSVS_Gibbs, {"k": 5, "n_burn": 800, "n_samples": 800}),
        ]:
            rms, r2s = [], []
            for tr, te in splits:
                sc = StandardScaler()
                Xtr = sc.fit_transform(Xn[tr]); Xte = sc.transform(Xn[te])
                ytr, yte = y[tr], y[te]
                m = cls(**kw).fit(Xtr, ytr)
                yp = m.predict(Xte) if cls is TSK_LS else m.predict(Xte)[0]
                rms.append(np.sqrt(np.mean((yte - yp) ** 2)))
                r2s.append(r2_score(yte, yp))
            row[name] = {"RMSE": float(np.mean(rms)), "R2": float(np.mean(r2s))}
        out[str(n_noise)] = row
        line = f"  noise={n_noise:<3} d={X.shape[1]+n_noise:<3} | "
        for name in ["TSK-LS", "SpikeSlab-Gibbs", "SSVS-Gibbs"]:
            line += f"{name}: RMSE={row[name]['RMSE']:.3f} R2={row[name]['R2']:+.3f}  "
        print(line)
    with open(os.path.join(DATA_DIR, "tier3_noise_v2.json"), "w") as f:
        json.dump(out, f, indent=2, default=float)
    return out


if __name__ == "__main__":
    run_main_comparison()
    run_tau2_sensitivity()
    run_noise_regime()
    print("\n\nAll tiers complete. Results in", DATA_DIR)
