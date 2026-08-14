#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Smoke test for the corrected TSK core (Phase 1 deliverable).

Validates: (1) FCM + fixed-membership gives sane dense baselines, (2) all five
model classes fit/predict without error, (3) the headline noise-feature result
(sparse variants do not beat the dense baseline; sparsity offers no free lunch)
reproduces.
"""

import numpy as np
from sklearn.preprocessing import StandardScaler

from tsk_core import (
    load_energy, load_concrete, append_noise_features,
    get_splits, compute_metrics,
    TSK_LS, TSK_Bayesian, TSK_SpikeSlab_Fast, TSK_SpikeSlab_Gibbs, TSK_SSVS_Gibbs,
)

N_SPLITS = 3


def run_one(cls, Xtr, ytr, Xte, yte, **kw):
    m = cls(**kw).fit(Xtr, ytr)
    if cls is TSK_LS:
        yp = m.predict(Xte)
        return compute_metrics(yte, yp), m.active_rules, None
    yp, yl, yu = m.predict(Xte)
    r = compute_metrics(yte, yp, yl, yu)
    feat = m.feature_pips() if hasattr(m, "feature_pips") else None
    return r, m.active_rules, feat


# ---- 1. Data sanity ----
Xe, y_heat, y_cool = load_energy()
Xc, y_conc = load_concrete()
print("Data shapes:")
print(f"  Energy: {Xe.shape} (expect n=768, d=8)")
print(f"  Concrete: {Xc.shape} (expect n=1030, d=8)")

# ---- 2. All models on Energy-Cooling (clean low-d) ----
print("\n" + "=" * 70)
print("Energy-Cooling (clean, n=768, d=8): all models")
print("=" * 70)
X, y = Xe, y_cool
splits = get_splits(y, N_SPLITS)
methods = [
    ("TSK-LS", TSK_LS, {}),
    ("Bayesian-TSK", TSK_Bayesian, {}),
    ("SpikeSlab-Fast", TSK_SpikeSlab_Fast, {}),
    ("SpikeSlab-Gibbs", TSK_SpikeSlab_Gibbs, {"n_burn": 500, "n_samples": 800}),
    ("SSVS-Gibbs", TSK_SSVS_Gibbs, {"n_burn": 500, "n_samples": 800}),
]
print(f"\n{'Method':<18}{'RMSE':<11}{'R²':<10}{'PICP':<9}{'Rules':<7}")
print("-" * 55)
for name, cls, kw in methods:
    rm, r2, p, rules = [], [], [], []
    for tr, te in splits:
        sc = StandardScaler()
        Xtr = sc.fit_transform(X[tr]); Xte = sc.transform(X[te])
        ytr, yte = y[tr], y[te]
        r, ar, _ = run_one(cls, Xtr, ytr, Xte, yte, **kw)
        rm.append(r["RMSE"]); r2.append(r["R2"])
        p.append(r.get("PICP", np.nan)); rules.append(ar)
    ps = f"{np.nanmean(p):.3f}" if not np.all(np.isnan(p)) else "---"
    print(f"{name:<18}{np.mean(rm):.3f}     {np.mean(r2):+.3f}   {ps:<9}{np.mean(rules):.1f}")

# ---- 3. Headline: noise-feature regime ----
print("\n" + "=" * 70)
print("Energy-Cooling + 12 noise features (d=20): sparse vs dense")
print("=" * 70)
Xn = append_noise_features(Xe, 12)
splits = get_splits(y_cool, N_SPLITS)
print(f"\n{'Method':<22}{'RMSE':<11}{'R²':<11}{'PICP':<9}")
print("-" * 55)
for name, cls, kw in [
    ("Dense (TSK-LS)", TSK_LS, {}),
    ("Dense (Bayesian-TSK)", TSK_Bayesian, {}),
    ("Sparse (SSVS-Gibbs)", TSK_SSVS_Gibbs, {"n_burn": 500, "n_samples": 800}),
]:
    rm, r2, p = [], [], []
    feat_pips = []
    for tr, te in splits:
        sc = StandardScaler()
        Xtr = sc.fit_transform(Xn[tr]); Xte = sc.transform(Xn[te])
        ytr, yte = y_cool[tr], y_cool[te]
        r, _, feat = run_one(cls, Xtr, ytr, Xte, yte, **kw)
        rm.append(r["RMSE"]); r2.append(r["R2"]); p.append(r.get("PICP", np.nan))
        if feat is not None:
            feat_pips.append(feat)
    ps = f"{np.nanmean(p):.3f}" if not np.all(np.isnan(p)) else "---"
    print(f"{name:<22}{np.mean(rm):.3f}     {np.mean(r2):+.3f}   {ps}")
    if feat_pips:
        fp = np.mean(feat_pips, axis=0)
        print(f"    per-feature PIP (8 real | 12 noise):")
        print(f"      real:  {np.round(fp[:8], 2)}")
        print(f"      noise: {np.round(fp[8:], 2)}")

print("\nSmoke test complete.")
