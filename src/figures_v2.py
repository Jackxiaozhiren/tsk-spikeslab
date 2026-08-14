#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate figures for the reframed paper:
"Correct Bayesian Inference for TSK Fuzzy Systems: a Reproducibility Fix and
Calibrated Model-Averaged Prediction Intervals."

Reads the corrected results (tier1/tier2/tier3_v2.json) and produces:
  fig1_repro_fix.pdf       — the membership-bug reproducibility fix (before/after R^2)
  fig2_main_comparison.pdf — R^2 across 3 datasets / 6 methods
  fig3_calibration.pdf     — PICP (with nominal-95% reference)
  fig4_sparsity_boundary.pdf — tau2 sensitivity + noise regime (no free lunch)
"""

import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

FIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "results", "figures")
RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "results", "raw")
os.makedirs(FIG_DIR, exist_ok=True)

plt.rcParams.update({
    "font.size": 13, "font.family": "serif",
    "axes.labelsize": 14, "axes.titlesize": 15,
    "legend.fontsize": 10.5, "figure.dpi": 300,
    "pdf.fonttype": 42, "ps.fonttype": 42,
})

COLORS = {
    "TSK-LS": "#4472C4",
    "Bayesian-TSK": "#0072B2",
    "SpikeSlab-Fast": "#D55E00",
    "SpikeSlab-Gibbs": "#2CA02C",
    "RandomForest": "#9B59B6",
    "SVR": "#95A5A6",
}

DATASETS = ["Energy-Heating", "Energy-Cooling", "Concrete"]
METHOD_ORDER = ["TSK-LS", "Bayesian-TSK", "SpikeSlab-Fast", "SpikeSlab-Gibbs",
                "RandomForest", "SVR"]


def _mean(rows, key):
    vals = [r[key] for r in rows if r.get(key) is not None]
    return float(np.mean(vals)) if vals else np.nan


def _mean_std(rows, key):
    vals = [r[key] for r in rows if r.get(key) is not None]
    return (float(np.mean(vals)), float(np.std(vals))) if vals else (np.nan, np.nan)


# ---- Load corrected results ----
tier1 = json.load(open(os.path.join(RAW_DIR, "tier1_v2.json")))
tier2 = json.load(open(os.path.join(RAW_DIR, "tier2_tau2_v2.json")))
tier3 = json.load(open(os.path.join(RAW_DIR, "tier3_noise_v2.json")))

# ---- R^2 values reported in the REJECTED manuscript (buggy baselines) ----
REPORTED_R2 = {
    "Energy-Heating": {"TSK-LS": 0.5671, "Bayesian-TSK": 0.8681},
    "Energy-Cooling": {"TSK-LS": 0.4084, "Bayesian-TSK": 0.8049},
    "Concrete": {"TSK-LS": 0.4376, "Bayesian-TSK": 0.5030},
}


# ============================================================
# FIGURE 1: Reproducibility fix (reported vs corrected R^2)
# ============================================================
print("Figure 1: reproducibility fix ...")
fig, axes = plt.subplots(1, 2, figsize=(10, 4.6), sharey=True)
for ax, method in zip(axes, ["TSK-LS", "Bayesian-TSK"]):
    x = np.arange(len(DATASETS))
    w = 0.36
    reported = [REPORTED_R2[ds][method] for ds in DATASETS]
    corrected = [_mean(tier1[ds][method], "R2") for ds in DATASETS]
    b1 = ax.bar(x - w / 2, reported, w, color="#D55E00", edgecolor="black",
                linewidth=0.6, label="Reported (buggy)")
    b2 = ax.bar(x + w / 2, corrected, w, color="#4472C4", edgecolor="black",
                linewidth=0.6, label="Corrected")
    for b, v in zip(b1, reported):
        ax.annotate(f"{v:.2f}", (b.get_x() + b.get_width() / 2, v),
                    ha="center", va="bottom", fontsize=9, color="#D55E00")
    for b, v in zip(b2, corrected):
        ax.annotate(f"{v:.2f}", (b.get_x() + b.get_width() / 2, v),
                    ha="center", va="bottom", fontsize=9, color="#4472C4",
                    fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(DATASETS, rotation=15, fontsize=10.5)
    ax.set_title(f"{method}", fontweight="bold")
    ax.grid(axis="y", alpha=0.3)
    ax.set_ylim(0, 1.18)
axes[0].set_ylabel("$R^2$")
axes[0].legend(fontsize=10, framealpha=0.9, loc="upper left")
fig.suptitle("Reproducibility fix: membership-spread bug corrected",
             fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "fig1_repro_fix.pdf"), bbox_inches="tight")
plt.savefig(os.path.join(FIG_DIR, "fig1_repro_fix.png"), bbox_inches="tight")
plt.close()

# ============================================================
# FIGURE 2: Main comparison (R^2 across 3 datasets / 6 methods)
# ============================================================
print("Figure 2: main comparison ...")
fig, ax = plt.subplots(figsize=(9.5, 5))
x = np.arange(len(DATASETS))
w = 0.13
for j, mname in enumerate(METHOD_ORDER):
    vals = [_mean(tier1[ds][mname], "R2") for ds in DATASETS]
    off = (j - len(METHOD_ORDER) / 2 + 0.5) * w
    ax.bar(x + off, vals, w, color=COLORS[mname], edgecolor="white",
           linewidth=0.4, label=mname)
ax.axhline(0, color="black", linewidth=0.8)
ax.set_xticks(x)
ax.set_xticklabels(DATASETS, fontsize=11)
ax.set_ylabel("$R^2$")
ax.set_title("Predictive accuracy across datasets", fontweight="bold")
ax.set_ylim(-7.0, 1.15)
ax.legend(fontsize=9.5, ncol=3, loc="lower left", framealpha=0.9)
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "fig2_main_comparison.pdf"), bbox_inches="tight")
plt.savefig(os.path.join(FIG_DIR, "fig2_main_comparison.png"), bbox_inches="tight")
plt.close()

# ============================================================
# FIGURE 3: Calibration (PICP vs nominal 95%)
# ============================================================
print("Figure 3: calibration ...")
fig, ax = plt.subplots(figsize=(8, 4.8))
methods_cal = ["Bayesian-TSK", "SpikeSlab-Gibbs", "SpikeSlab-Fast"]
x = np.arange(len(DATASETS))
w = 0.24
for j, mname in enumerate(methods_cal):
    vals = [_mean(tier1[ds][mname], "PICP") for ds in DATASETS]
    off = (j - len(methods_cal) / 2 + 0.5) * w
    bars = ax.bar(x + off, vals, w, color=COLORS[mname], edgecolor="white",
                  linewidth=0.4, label=mname)
    for b, v in zip(bars, vals):
        ax.annotate(f"{v:.2f}", (b.get_x() + b.get_width() / 2, v),
                    ha="center", va="bottom", fontsize=8.5)
ax.axhline(0.95, color="gray", linestyle="--", linewidth=1.5, label="Nominal 95%")
ax.set_xticks(x)
ax.set_xticklabels(DATASETS, fontsize=11)
ax.set_ylabel("PICP (coverage)")
ax.set_title("Prediction-interval calibration", fontweight="bold")
ax.set_ylim(0, 1.12)
ax.legend(fontsize=10, framealpha=0.9, loc="lower left")
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "fig3_calibration.pdf"), bbox_inches="tight")
plt.savefig(os.path.join(FIG_DIR, "fig3_calibration.png"), bbox_inches="tight")
plt.close()

# ============================================================
# FIGURE 4: Sparsity boundary (tau2 sensitivity + noise regime)
# ============================================================
print("Figure 4: sparsity boundary ...")
fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.6))

# (a) tau2 sensitivity
ax = axes[0]
tau2s = sorted([float(k) for k in tier2.keys()])
r2_tau = [_mean(tier2[str(t)], "R2") for t in tau2s]
dense_r2 = _mean(tier1["Energy-Cooling"]["TSK-LS"], "R2")
ax.semilogx(tau2s, r2_tau, "o-", color="#2CA02C", linewidth=2.5, markersize=8,
            label="SSVS-Gibbs (coefficient)")
ax.axhline(dense_r2, color="#4472C4", linestyle="--", linewidth=1.8,
           label=f"Dense TSK-LS ($R^2$={dense_r2:.2f})")
ax.set_xlabel(r"Slab variance $\tau^2$")
ax.set_ylabel("$R^2$")
ax.set_title("(a) Coefficient-level sparsity trade-off", fontweight="bold")
ax.set_ylim(-7, 1.05)
ax.legend(fontsize=9.5, framealpha=0.9, loc="lower right")
ax.grid(alpha=0.3, which="both")

# (b) noise regime
ax = axes[1]
noise_levels = sorted([int(k) for k in tier3.keys()])
ds = [tier3[str(n)]["TSK-LS"]["R2"] for n in noise_levels]
sg = [tier3[str(n)]["SpikeSlab-Gibbs"]["R2"] for n in noise_levels]
ss = [tier3[str(n)]["SSVS-Gibbs"]["R2"] for n in noise_levels]
ax.plot(noise_levels, ds, "o-", color="#4472C4", linewidth=2, markersize=7,
        label="Dense TSK-LS")
ax.plot(noise_levels, sg, "s--", color="#2CA02C", linewidth=2, markersize=7,
        label="SpikeSlab-Gibbs (rule)")
ax.plot(noise_levels, ss, "^-", color="#D55E00", linewidth=2, markersize=7,
        label="SSVS-Gibbs (coefficient)")
ax.set_xlabel("Number of appended noise features")
ax.set_ylabel("$R^2$")
ax.set_title("(b) Irrelevant-feature regime", fontweight="bold")
ax.set_ylim(0.75, 1.0)
ax.legend(fontsize=9.5, framealpha=0.9, loc="lower left")
ax.grid(alpha=0.3)

fig.suptitle("Sparsity gives no free lunch under correct FCM", fontweight="bold",
             y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "fig4_sparsity_boundary.pdf"), bbox_inches="tight")
plt.savefig(os.path.join(FIG_DIR, "fig4_sparsity_boundary.png"), bbox_inches="tight")
plt.close()

print(f"\nAll figures saved to {FIG_DIR}/")
