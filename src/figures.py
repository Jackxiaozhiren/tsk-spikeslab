#!/usr/bin/env python3
"""Generate all publication figures for the ASC paper — revised edition."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import os

FIG_DIR = "/Users/jackson/ASC论文/results/figures"
os.makedirs(FIG_DIR, exist_ok=True)

plt.rcParams.update({
    'font.size': 9, 'font.family': 'serif',
    'axes.labelsize': 10, 'axes.titlesize': 11,
    'legend.fontsize': 8, 'figure.dpi': 300,
    'savefig.bbox': 'tight', 'savefig.pad_inches': 0.05,
})

COLORS = {
    "TSK-LS": "#4472C4", "TSK-LASSO": "#ED7D31",
    "TSK-SpikeSlab": "#D7191C", "Bayesian-TSK": "#70AD47",
    "RandomForest": "#9B59B6", "SVR": "#95A5A6",
}
LINESTYLES = {
    "TSK-SpikeSlab": 'dashdot',
    "TSK-LASSO": 'dotted',
    "TSK-LS": 'solid',
}
MARKERS = {
    "TSK-LS": "o", "TSK-LASSO": "s",
    "TSK-SpikeSlab": "*", "Bayesian-TSK": "^",
    "RandomForest": "D", "SVR": "v",
}

METHOD_ORDER = ["TSK-LS", "TSK-LASSO", "TSK-SpikeSlab", "Bayesian-TSK", "RandomForest", "SVR"]
HATCHES = {m: ('//' if m == "TSK-SpikeSlab" else '') for m in METHOD_ORDER}

results = {
    "Energy-Heating": {
        "TSK-LS":        {"RMSE": (4.7966, 4.5374), "R2": 0.5671, "Rules": 5.0},
        "TSK-LASSO":     {"RMSE": (29.2815, 1.8215), "R2": -7.5994, "Rules": 5.0},
        "TSK-SpikeSlab": {"RMSE": (19.1231, 2.0825), "R2": -2.7023, "Rules": 3.1, "PICP": 0.0569, "MPIW": 12.3369},
        "Bayesian-TSK":  {"RMSE": (3.5725, 0.7066), "R2": 0.8681, "Rules": 5.0, "PICP": 0.9399, "MPIW": 21.7698},
        "RandomForest":  {"RMSE": (0.4919, 0.0575), "R2": 0.9975},
        "SVR":           {"RMSE": (2.7294, 0.2063), "R2": 0.9252},
    },
    "Energy-Cooling": {
        "TSK-LS":        {"RMSE": (5.5955, 4.7961), "R2": 0.4084, "Rules": 5.0},
        "TSK-LASSO":     {"RMSE": (31.8187, 1.0594), "R2": -10.3746, "Rules": 5.0},
        "TSK-SpikeSlab": {"RMSE": (21.2877, 1.7718), "R2": -4.1312, "Rules": 3.1, "PICP": 0.0769, "MPIW": 17.1036},
        "Bayesian-TSK":  {"RMSE": (4.1099, 0.7982), "R2": 0.8049, "Rules": 5.0, "PICP": 0.9610, "MPIW": 30.1905},
        "RandomForest":  {"RMSE": (1.6657, 0.1267), "R2": 0.9687},
        "SVR":           {"RMSE": (3.0931, 0.2208), "R2": 0.8925},
    },
    "Concrete": {
        "TSK-LS":        {"RMSE": (11.7563, 4.2471), "R2": 0.4376, "Rules": 5.0},
        "TSK-LASSO":     {"RMSE": (42.0959, 1.3702), "R2": -5.3836, "Rules": 5.0},
        "TSK-SpikeSlab": {"RMSE": (41.9710, 4.3577), "R2": -5.3998, "Rules": 5.0, "PICP": 0.3150, "MPIW": 87.9444},
        "Bayesian-TSK":  {"RMSE": (11.1744, 3.5095), "R2": 0.5030, "Rules": 5.0, "PICP": 0.9002, "MPIW": 46.2563},
        "RandomForest":  {"RMSE": (5.1728, 0.4031), "R2": 0.9032},
        "SVR":           {"RMSE": (9.9666, 0.4313), "R2": 0.6429},
    },
}

fcm_k = [3, 5, 7, 9]
fcm_rmse = [28.3947, 20.5494, 24.2288, 20.5100]
fcm_rules = [2.2, 3.2, 5.2, 5.4]

mechanism = {
    "Energy-Cooling": {
        "Low":  {"SS": 22.1988, "LASSO": 32.0565, "LS": 10.4},
        "Med":  {"SS": 20.3595, "LASSO": 31.7596, "LS": 3.7},
        "High": {"SS": 20.9205, "LASSO": 31.6191, "LS": 2.8},
        "n_per_bin": [102, 102, 102],
    },
    "Concrete": {
        "Low":  {"SS": 43.6182, "LASSO": 43.2208, "LS": 12.5},
        "Med":  {"SS": 41.0373, "LASSO": 41.7264, "LS": 11.1},
        "High": {"SS": 41.1021, "LASSO": 41.2910, "LS": 11.7},
        "n_per_bin": [103, 103, 103],
    },
}

# Aggregate ranks (averaged across 3 datasets per method, from diagnosis data)
agg_ranks = {
    "RF": 1.00, "SVR": 2.40, "Bayesian-TSK": 2.84,
    "TSK-LS": 3.80, "TSK-SpikeSlab": 5.21, "TSK-LASSO": 5.75,
}

# ============================================================
# FIGURE 1: Main Comparison — Dual-panel (low/high RMSE)
# ============================================================
print("Figure 1: Main comparison (dual-panel)...")
fig, axes = plt.subplots(2, 1, figsize=(10, 7), gridspec_kw={'height_ratios': [1, 1.5]})

ds_names = ["Energy-Heating", "Energy-Cooling", "Concrete"]
# Top panel: low RMSE methods only (TSK-LS, Bayesian-TSK, RF, SVR)
low_methods = ["TSK-LS", "Bayesian-TSK", "RandomForest", "SVR"]
# Bottom panel: all methods with broken scale annotation

x = np.arange(len(ds_names))
width = 0.18

# Panel (a): low RMSE
ax = axes[0]
for j, mn in enumerate(low_methods):
    means = [results[ds][mn]["RMSE"][0] for ds in ds_names]
    stds = [results[ds][mn]["RMSE"][1] for ds in ds_names]
    offset = (j - len(low_methods)/2 + 0.5) * width
    bars = ax.bar(x + offset, means, width, yerr=stds, color=COLORS[mn],
                  capsize=3, edgecolor='white', linewidth=0.5, label=mn,
                  hatch=HATCHES[mn])
ax.set_xticks(x)
ax.set_xticklabels(ds_names, fontsize=9)
ax.set_ylabel('RMSE')
ax.set_title('(a) Methods with competitive accuracy', fontweight='bold')
ax.legend(fontsize=7, ncol=4, loc='upper left')
ax.grid(axis='y', alpha=0.3)

# Panel (b): high RMSE (TSK-LASSO, TSK-SpikeSlab) with broken-axis context
ax = axes[1]
high_methods = ["TSK-LASSO", "TSK-SpikeSlab"]
for j, mn in enumerate(high_methods):
    means = [results[ds][mn]["RMSE"][0] for ds in ds_names]
    stds = [results[ds][mn]["RMSE"][1] for ds in ds_names]
    offset = (j - 1) * width * 1.5
    bars = ax.bar(x + offset, means, width*1.5, yerr=stds, color=COLORS[mn],
                  capsize=3, edgecolor='black', linewidth=0.8, label=mn,
                  hatch='//')
    # Annotate with sparsity
    if mn == "TSK-SpikeSlab":
        for xi, ds in enumerate(ds_names):
            rules = results[ds][mn].get("Rules", 0)
            ax.annotate(f'{rules:.0f}/5', (x[xi] + offset, means[xi] + 1.5),
                       ha='center', fontsize=8, color=COLORS[mn], fontweight='bold')

ax.set_xticks(x)
ax.set_xticklabels(ds_names, fontsize=9)
ax.set_ylabel('RMSE')
ax.set_title('(b) Methods with degraded accuracy (note broken y-axis)', fontweight='bold')
ax.legend(fontsize=8, ncol=2)
ax.grid(axis='y', alpha=0.3)

# Add broken-axis visual
d = .015
kwargs = dict(transform=axes[0].transAxes, color='k', clip_on=False, linewidth=1)
axes[0].plot((-d, +d), (-d, +d), **kwargs)
axes[1].plot((-d, +d), (1-d, 1+d), **kwargs)
kwargs.update(transform=axes[1].transAxes)
axes[1].plot((-d, +d), (-d, +d), **kwargs)

fig.suptitle('Fig. 1. Prediction accuracy (RMSE) across methods and datasets', y=1.01, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "fig1_main_comparison.pdf"), dpi=300)
plt.savefig(os.path.join(FIG_DIR, "fig1_main_comparison.png"), dpi=300)
plt.close()

# ============================================================
# FIGURE 2: Uncertainty — PICP vs MPIW scatter
# ============================================================
print("Figure 2: Uncertainty calibration (scatter)...")
fig, ax = plt.subplots(figsize=(6, 5))

all_datasets = ["Energy-Heating", "Energy-Cooling", "Concrete"]
markers_ds = {"Energy-Heating": 'o', "Energy-Cooling": 's', "Concrete": 'D'}

for ds_name in all_datasets:
    for mn in ["TSK-SpikeSlab", "Bayesian-TSK"]:
        if "PICP" not in results[ds_name][mn]:
            continue
        picp = results[ds_name][mn]["PICP"]
        mpiw = results[ds_name][mn]["MPIW"]
        color = COLORS[mn]
        marker = markers_ds[ds_name]
        label = f"{mn} ({ds_name})"
        ax.scatter(picp, mpiw, c=color, marker=marker, s=150, edgecolors='black',
                  linewidth=0.8, label=label, zorder=5)
        # Annotate
        offset_y = 2 if mn == "Bayesian-TSK" else -3
        ax.annotate(ds_name[:3], (picp, mpiw), textcoords="offset points",
                   xytext=(5, offset_y), fontsize=7, color=color)

ax.axvline(x=0.95, color='gray', linestyle='--', linewidth=1, alpha=0.7, label='Nominal 95%')
# Ideal region annotation
ax.annotate('Ideal', xy=(0.95, 2), fontsize=8, color='gray', ha='center',
            style='italic')

ax.set_xlabel('PICP (Prediction Interval Coverage Probability)')
ax.set_ylabel('MPIW (Mean Prediction Interval Width)')
ax.set_title('Fig. 2. Calibration: PICP vs MPIW for Bayesian methods', fontweight='bold')

# Simplify legend
handles, labels = ax.get_legend_handles_labels()
# Group by method
ss_handles = [h for h, l in zip(handles, labels) if 'SpikeSlab' in l]
bt_handles = [h for h, l in zip(handles, labels) if 'Bayesian-TSK' in l]
nom_handle = [h for h, l in zip(handles, labels) if 'Nominal' in l]
custom_legend = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor='#D7191C', markersize=8, label='TSK-SpikeSlab'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='#70AD47', markersize=8, label='Bayesian-TSK'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='w', markeredgecolor='k', markersize=8, label='Energy-Heating'),
    Line2D([0], [0], marker='s', color='w', markerfacecolor='w', markeredgecolor='k', markersize=8, label='Energy-Cooling'),
    Line2D([0], [0], marker='D', color='w', markerfacecolor='w', markeredgecolor='k', markersize=8, label='Concrete'),
    Line2D([0], [1], color='gray', linestyle='--', linewidth=1, label='Nominal 95%'),
]
ax.legend(handles=custom_legend, fontsize=7, loc='upper left')
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "fig2_uncertainty.pdf"), dpi=300)
plt.savefig(os.path.join(FIG_DIR, "fig2_uncertainty.png"), dpi=300)
plt.close()

# ============================================================
# FIGURE 3: Mechanism Analysis — with TSK-LS reference, b&w-friendly
# ============================================================
print("Figure 3: Mechanism analysis (revised)...")
fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))

for ax_i, (ds_name, mech) in enumerate(mechanism.items()):
    ax = axes[ax_i]
    bins = ["Low", "Med", "High"]
    x = np.arange(len(bins))
    ss_vals = [mech[b]["SS"] for b in bins]
    lasso_vals = [mech[b]["LASSO"] for b in bins]
    ls_vals = [mech[b]["LS"] for b in bins]
    n_bin = mech["n_per_bin"]

    # TSK-SpikeSlab: red dash-dot with star marker
    ax.plot(x, ss_vals, linestyle='dashdot', color=COLORS["TSK-SpikeSlab"],
            marker='*', markersize=12, linewidth=2.5, label='TSK-SpikeSlab')
    # TSK-LASSO: orange dotted with square marker
    ax.plot(x, lasso_vals, linestyle='dotted', color=COLORS["TSK-LASSO"],
            marker='s', markersize=8, linewidth=2, label='TSK-LASSO')
    # TSK-LS: blue solid with circle marker (reference)
    ax.plot(x, ls_vals, linestyle='-', color=COLORS["TSK-LS"],
            marker='o', markersize=7, linewidth=1.5, alpha=0.7, label='TSK-LS (ref.)')

    # Fill between SS and LASSO
    ax.fill_between(x, ss_vals, lasso_vals, alpha=0.12, color='gray')

    # Annotate delta (SS vs LASSO)
    for i, b in enumerate(bins):
        delta = mech[b]["LASSO"] - mech[b]["SS"]
        mid = (ss_vals[i] + lasso_vals[i]) / 2
        color_delta = 'black'
        ax.annotate(f'Δ={delta:+.1f}\n(n≈{n_bin[i]})', (x[i], mid),
                   ha='center', fontsize=8, color=color_delta, fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels([f'{b}\n(lowest uncert.)' if b == 'Low' else
                        f'{b}\n(highest uncert.)' if b == 'High' else b
                        for b in bins], fontsize=8)
    ax.set_xlabel('Posterior Predictive Uncertainty')
    ax.set_ylabel('RMSE')
    ax.set_title(ds_name, fontweight='bold')
    ax.legend(fontsize=7, loc='upper left')
    ax.grid(alpha=0.3)
    # Honest annotation for Concrete
    if ds_name == "Concrete":
        ax.annotate('Differences < 5% of RMSE scale', xy=(0.5, 0.08),
                   xycoords='axes fraction', ha='center', fontsize=8,
                   color='gray', style='italic')

fig.suptitle('Fig. 3. Mechanism-probing: RMSE by uncertainty bin', fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "fig3_mechanism.pdf"), dpi=300)
plt.savefig(os.path.join(FIG_DIR, "fig3_mechanism.png"), dpi=300)
plt.close()

# ============================================================
# FIGURE 4: FCM Sensitivity — side-by-side instead of dual axis
# ============================================================
print("Figure 4: FCM sensitivity (side-by-side)...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 4))

# RMSE subplot
ax1.plot(fcm_k, fcm_rmse, 'o-', color='#4472C4', linewidth=2, markersize=10)
ax1.set_xlabel('FCM Clusters (k)')
ax1.set_ylabel('RMSE')
ax1.set_title('(a) Accuracy', fontweight='bold')
ax1.grid(alpha=0.3)
for k, r in zip(fcm_k, fcm_rmse):
    ax1.annotate(f'{r:.1f}', (k, r), textcoords="offset points", xytext=(0, 8),
                ha='center', fontsize=8)

# Active Rules subplot
ax2.plot(fcm_k, fcm_rules, 's--', color='#D7191C', linewidth=2, markersize=10)
for k, r in zip(fcm_k, fcm_rules):
    ax2.annotate(f'{r:.1f}/{k}', (k, r), textcoords="offset points", xytext=(0, 8),
                ha='center', fontsize=8)
ax2.set_xlabel('FCM Clusters (k)')
ax2.set_ylabel('Active Rules')
ax2.set_title('(b) Sparsity', fontweight='bold')
ax2.grid(alpha=0.3)

fig.suptitle('Fig. 4. Effect of FCM cluster count on accuracy and sparsity', fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "fig4_fcm_sensitivity.pdf"), dpi=300)
plt.savefig(os.path.join(FIG_DIR, "fig4_fcm_sensitivity.png"), dpi=300)
plt.close()

# ============================================================
# FIGURE 5: Aggregate CD Diagram (3 datasets, with CD line)
# ============================================================
print("Figure 5: Aggregate CD diagram...")

# Calculate critical difference
# CD = q_alpha * sqrt(k*(k+1)/(6*N)) where k=6 methods, N=3 datasets
# q_0.05 for k=6 is ~2.85 (from Demšar 2006 table)
k_methods = 6
N_datasets = 3
q_alpha = 2.850  # Nemenyi critical value for alpha=0.05, k=6
CD = q_alpha * np.sqrt(k_methods * (k_methods + 1) / (6 * N_datasets))

fig, ax = plt.subplots(figsize=(8, 2.5))

# Sort by average rank
rank_items = sorted(agg_ranks.items(), key=lambda x: x[1])
labels_cd = [k for k, _ in rank_items]
x_vals_cd = [v for _, v in rank_items]

for i, (lbl, r) in enumerate(rank_items):
    color = COLORS.get(lbl, '#95A5A6')
    marker = '*' if lbl == "TSK-SpikeSlab" else 'o'
    size = 250 if lbl == "TSK-SpikeSlab" else 120
    ax.scatter(r, 0, c=color, s=size, marker=marker,
              edgecolors='black' if lbl == "TSK-SpikeSlab" else 'none',
              linewidth=1.5 if lbl == "TSK-SpikeSlab" else 0, zorder=5)
    offset_y = 0.035 if i % 2 == 0 else -0.025
    ax.annotate(lbl, (r, offset_y), ha='center', fontsize=8,
               fontweight='bold' if lbl == "TSK-SpikeSlab" else 'normal')

# CD bar annotation
best_rank = min(x_vals_cd)
cd_end = best_rank + CD
ax.annotate('', xy=(best_rank, -0.06), xytext=(cd_end, -0.06),
           arrowprops=dict(arrowstyle='<->', color='black', lw=2))
ax.annotate(f'CD={CD:.2f}', ((best_rank + cd_end)/2, -0.08), ha='center', fontsize=9, fontweight='bold')

# Nemenyi grouping: underline groups not significantly different
# Methods within CD of each other
rank_dict = dict(rank_items)
# Find groups within CD
for lbl, r in rank_items:
    same_group = [l2 for l2, r2 in rank_items if abs(r - r2) < CD and l2 != lbl]
    if same_group and r < rank_dict.get(same_group[0] if same_group else '', 999):
        # draw underline
        group_ranks = [r] + [rank_dict[l2] for l2 in same_group]
        ax.axhline(y=-0.12, xmin=(min(group_ranks)-0.5)/6.5, xmax=(max(group_ranks)-0.5)/6.5,
                  color='gray', linewidth=3, alpha=0.4)

ax.set_xlim(0.5, 6.5)
ax.set_ylim(-0.14, 0.08)
ax.set_xlabel('Average Rank (1 = best) across 3 datasets', fontsize=10)
ax.set_yticks([])
ax.spines['left'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)

ax.set_title('Fig. 5. Critical Difference Diagram (Friedman–Nemenyi, 3 datasets)', fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "fig5_cd_diagram.pdf"), dpi=300)
plt.savefig(os.path.join(FIG_DIR, "fig5_cd_diagram.png"), dpi=300)
plt.close()

# ============================================================
# FIGURE 6: Rule Selection — add hatching for colorblind
# ============================================================
print("Figure 6: Rule selection...")
fig, ax = plt.subplots(figsize=(6.5, 3.2))

pips = [0.3004, 0.6996, 0.8992, 0.5998, 0.6996]
rule_labels = [f'R{i+1}' for i in range(5)]
colors_rules = ['#D7191C' if p > 0.5 else '#757575' for p in pips]
hatch_rules = ['//' if p > 0.5 else '\\\\' for p in pips]

bars = ax.barh(rule_labels, pips, color=colors_rules, edgecolor='black',
               height=0.6, linewidth=0.8)
for bar, hatch in zip(bars, hatch_rules):
    bar.set_hatch(hatch)

ax.axvline(x=0.5, color='black', linestyle='--', linewidth=1.5, label='Selection threshold')
ax.set_xlabel('Posterior Inclusion Probability')
ax.set_xlim(0, 1)
ax.legend(fontsize=8, loc='lower right')
ax.set_title('Fig. 6. Rule PIPs (Energy-Cooling, π=0.5, averaged over 10 splits)', fontweight='bold')

for i, p in enumerate(pips):
    status = 'ACTIVE' if p > 0.5 else 'INACTIVE'
    ax.annotate(f'{status} ({p:.2f})', (p + 0.03, i), va='center', fontsize=8,
               color='#D7191C' if p > 0.5 else '#757575', fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "fig6_rules.pdf"), dpi=300)
plt.savefig(os.path.join(FIG_DIR, "fig6_rules.png"), dpi=300)
plt.close()

# ============================================================
# FIGURE 7: sMethod overview (replacing the confusing pareto plot)
# ============================================================
print("Figure 7: Method overview (R2 by dataset)...")
fig, ax = plt.subplots(figsize=(9, 4.5))

x = np.arange(len(ds_names))
width = 0.12

for j, mn in enumerate(METHOD_ORDER):
    r2_vals = [results[ds][mn]["R2"] for ds in ds_names]
    offset = (j - len(METHOD_ORDER)/2 + 0.5) * width
    bars = ax.bar(x + offset, r2_vals, width, color=COLORS[mn],
                  edgecolor='white', linewidth=0.3, label=mn, hatch=HATCHES[mn])
    # Annotate negative R2
    for xi, r2 in enumerate(r2_vals):
        if r2 < 0:
            ax.annotate(f'{r2:.1f}', (x[xi] + offset, max(r2, -12) - 0.5),
                       ha='center', fontsize=6, color=COLORS[mn], rotation=90)

ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
ax.set_xticks(x)
ax.set_xticklabels(ds_names, fontsize=9)
ax.set_ylabel('R²')
ax.set_title('Fig. 7. Predictive performance (R²) across methods and datasets', fontweight='bold')
ax.legend(fontsize=7, ncol=3, loc='lower left')
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "fig7_pareto.pdf"), dpi=300)
plt.savefig(os.path.join(FIG_DIR, "fig7_pareto.png"), dpi=300)
plt.close()

print(f"\nAll 7 revised figures saved to {FIG_DIR}/")
print("Done!")
