#!/usr/bin/env python3
"""Generate all publication figures — carefully reviewed for visual clarity."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import os

FIG_DIR = "/Users/jackson/ASC论文/results/figures"
os.makedirs(FIG_DIR, exist_ok=True)

plt.rcParams.update({
    'font.size': 11, 'font.family': 'serif',
    'axes.labelsize': 12, 'axes.titlesize': 13,
    'legend.fontsize': 9, 'figure.dpi': 300,
})

COLORS = {
    "TSK-LS": "#4472C4", "TSK-LASSO": "#ED7D31",
    "TSK-SpikeSlab": "#D7191C", "Bayesian-TSK": "#70AD47",
    "RandomForest": "#9B59B6", "SVR": "#95A5A6",
}

METHOD_ORDER = ["TSK-LS", "TSK-LASSO", "TSK-SpikeSlab", "Bayesian-TSK", "RandomForest", "SVR"]

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
        "n_per_bin": [51, 51, 51],
    },
    "Concrete": {
        "Low":  {"SS": 43.6182, "LASSO": 43.2208, "LS": 12.5},
        "Med":  {"SS": 41.0373, "LASSO": 41.7264, "LS": 11.1},
        "High": {"SS": 41.1021, "LASSO": 41.2910, "LS": 11.7},
        "n_per_bin": [52, 52, 52],
    },
}

agg_ranks = {
    "RF": 1.00, "SVR": 2.21, "Bayesian-TSK": 2.75,
    "TSK-LS": 3.80, "TSK-SpikeSlab": 5.12, "TSK-LASSO": 6.00,
}

ds_names = ["Energy-Heating", "Energy-Cooling", "Concrete"]

# ============================================================
# FIGURE 1: Main comparison — dual panel with y-lim safety
# ============================================================
print("Figure 1...")
fig, axes = plt.subplots(2, 1, figsize=(9, 8), gridspec_kw={'height_ratios': [1, 1.3]})

x = np.arange(len(ds_names))
width = 0.15

# Panel (a): low RMSE
ax = axes[0]
low_methods = ["TSK-LS", "Bayesian-TSK", "RandomForest", "SVR"]
for j, mn in enumerate(low_methods):
    means = [results[ds][mn]["RMSE"][0] for ds in ds_names]
    stds = [results[ds][mn]["RMSE"][1] for ds in ds_names]
    offset = (j - len(low_methods)/2 + 0.5) * width
    ax.bar(x + offset, means, width, yerr=stds, color=COLORS[mn],
           capsize=2, edgecolor='white', linewidth=0.3, label=mn)
ax.set_xticks(x)
ax.set_xticklabels([])
ax.set_ylabel('RMSE')
ax.set_ylim(0, 17)
ax.set_title('(a) Methods with competitive accuracy')
ax.legend(fontsize=9, ncol=4, loc='upper left')
ax.grid(axis='y', alpha=0.3)

# Panel (b): high RMSE
ax = axes[1]
high_methods = ["TSK-LASSO", "TSK-SpikeSlab"]
for j, mn in enumerate(high_methods):
    means = [results[ds][mn]["RMSE"][0] for ds in ds_names]
    stds = [results[ds][mn]["RMSE"][1] for ds in ds_names]
    offset = (j - 0.5) * width * 2
    ax.bar(x + offset, means, width*1.8, yerr=stds, color=COLORS[mn],
           capsize=2, edgecolor='black', linewidth=0.5, label=mn, hatch='//')
ax.set_ylim(0, 55)
ax.set_xticks(x)
ax.set_xticklabels(ds_names, fontsize=10)
ax.set_ylabel('RMSE')
ax.set_title('(b) Methods with degraded accuracy')
ax.legend(fontsize=9)
ax.grid(axis='y', alpha=0.3)

# Broken axis break marks
d = .015
kwargs = dict(transform=axes[0].transAxes, color='k', clip_on=False, linewidth=1)
axes[0].plot((-d, +d), (-d, +d), **kwargs)
axes[1].plot((-d, +d), (1-d, 1+d), **kwargs)
kwargs.update(transform=axes[1].transAxes)
axes[1].plot((-d, +d), (-d, +d), **kwargs)

plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "fig1_main_comparison.pdf"), dpi=300)
plt.savefig(os.path.join(FIG_DIR, "fig1_main_comparison.png"), dpi=300)
plt.close()

# ============================================================
# FIGURE 2: Uncertainty scatter — clean, no overlap
# ============================================================
print("Figure 2...")
fig, ax = plt.subplots(figsize=(8, 5.5))

markers_ds = {"Energy-Heating": 'o', "Energy-Cooling": 's', "Concrete": 'D'}

for ds_name in ["Energy-Heating", "Energy-Cooling", "Concrete"]:
    for mn in ["TSK-SpikeSlab", "Bayesian-TSK"]:
        if "PICP" not in results[ds_name][mn]:
            continue
        picp = results[ds_name][mn]["PICP"]
        mpiw = results[ds_name][mn]["MPIW"]
        ax.scatter(picp, mpiw, c=COLORS[mn], marker=markers_ds[ds_name],
                  s=300, edgecolors='black', linewidth=0.8, zorder=5)

custom_legend = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor='#D7191C', markersize=10, label='TSK-SpikeSlab'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='#70AD47', markersize=10, label='Bayesian-TSK'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='w', markeredgecolor='k', markersize=9, label='Energy-Heating'),
    Line2D([0], [0], marker='s', color='w', markerfacecolor='w', markeredgecolor='k', markersize=9, label='Energy-Cooling'),
    Line2D([0], [0], marker='D', color='w', markerfacecolor='w', markeredgecolor='k', markersize=9, label='Concrete'),
    Line2D([0], [1], color='gray', linestyle='--', linewidth=1.5, label='Nominal 95%'),
]
ax.legend(handles=custom_legend, fontsize=9, loc='upper left', framealpha=0.9)

ax.axvline(x=0.95, color='gray', linestyle='--', linewidth=1.5, alpha=0.7)
ax.set_xlabel('PICP')
ax.set_ylabel('MPIW')
ax.set_xlim(-0.02, 1.05)
ax.set_title('Fig. 2. Calibration: PICP vs MPIW')
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "fig2_uncertainty.pdf"), dpi=300)
plt.savefig(os.path.join(FIG_DIR, "fig2_uncertainty.png"), dpi=300)
plt.close()

# ============================================================
# FIGURE 3: Mechanism — independent y-axes per panel
# ============================================================
print("Figure 3...")
fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), gridspec_kw={'wspace': 0.45})

for ax_i, (ds_name, mech) in enumerate(mechanism.items()):
    ax = axes[ax_i]
    bins = ["Low", "Med", "High"]
    x = np.arange(len(bins))
    ss_vals = [mech[b]["SS"] for b in bins]
    lasso_vals = [mech[b]["LASSO"] for b in bins]
    ls_vals = [mech[b]["LS"] for b in bins]
    n_bin = mech["n_per_bin"]

    # Fill between
    ax.fill_between(x, ss_vals, lasso_vals, alpha=0.10, color='#888888')

    # Distinct markers — small enough not to overlap
    ax.plot(x, lasso_vals, linestyle='dotted', color=COLORS["TSK-LASSO"],
            marker='s', markersize=7, linewidth=2, label='TSK-LASSO',
            markerfacecolor='white', markeredgewidth=1.2)
    ax.plot(x, ss_vals, linestyle='dashdot', color=COLORS["TSK-SpikeSlab"],
            marker='*', markersize=9, linewidth=2, label='TSK-SpikeSlab')
    ax.plot(x, ls_vals, linestyle='-', color=COLORS["TSK-LS"],
            marker='o', markersize=6, linewidth=1.5, alpha=0.55,
            label='TSK-LS (ref.)')

    # Per-panel y-range: Energy-Cooling ~0-38, Concrete ~8-48
    if ds_name == "Concrete":
        ax.set_ylim(5, 50)
    else:
        ax.set_ylim(0, 38)

    # Sample size label below each x tick
    for i, n in enumerate(n_bin):
        ax.annotate(f'n≈{n}', (x[i], -0.10), xycoords=('data', 'axes fraction'),
                   ha='center', fontsize=7, color='#666666', annotation_clip=False)

    ax.set_xticks(x)
    ax.set_xticklabels(bins, fontsize=10)
    ax.set_xlabel('Uncertainty bin', fontsize=11)
    ax.set_ylabel('RMSE', fontsize=11)
    ax.set_title(ds_name, fontweight='bold')
    ax.legend(fontsize=8, loc='upper left', framealpha=0.85)
    ax.grid(axis='y', alpha=0.3)

fig.suptitle('Fig. 3. Mechanism: RMSE by uncertainty bin', fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "fig3_mechanism.pdf"), dpi=300)
plt.savefig(os.path.join(FIG_DIR, "fig3_mechanism.png"), dpi=300)
plt.close()

# ============================================================
# FIGURE 4: FCM sensitivity
# ============================================================
print("Figure 4...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 4.5))

ax1.plot(fcm_k, fcm_rmse, 'o-', color='#4472C4', linewidth=2, markersize=9)
for k, r in zip(fcm_k, fcm_rmse):
    ax1.annotate(f'{r:.1f}', (k, r), textcoords="offset points",
                xytext=(0, 10), ha='center', fontsize=7)
ax1.set_xlabel('FCM Clusters (k)')
ax1.set_ylabel('RMSE')
ax1.set_title('(a) Accuracy', fontweight='bold')
ax1.grid(alpha=0.3)

ax2.plot(fcm_k, fcm_rules, 's--', color='#D7191C', linewidth=2, markersize=9)
for k, r in zip(fcm_k, fcm_rules):
    ax2.annotate(f'{r:.1f}', (k, r), textcoords="offset points",
                xytext=(0, 10), ha='center', fontsize=7)
ax2.set_xlabel('FCM Clusters (k)')
ax2.set_ylabel('Active Rules')
ax2.set_title('(b) Sparsity', fontweight='bold')
ax2.grid(alpha=0.3)

fig.suptitle('Fig. 4. FCM cluster count sensitivity', fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "fig4_fcm_sensitivity.pdf"), dpi=300)
plt.savefig(os.path.join(FIG_DIR, "fig4_fcm_sensitivity.png"), dpi=300)
plt.close()

# ============================================================
# FIGURE 5: CD Diagram
# ============================================================
print("Figure 5...")
k_methods = 6
N_datasets = 3
q_alpha = 2.850
CD = q_alpha * np.sqrt(k_methods * (k_methods + 1) / (6 * N_datasets))

fig, ax = plt.subplots(figsize=(9, 2.5))
rank_items = sorted(agg_ranks.items(), key=lambda x: x[1])

for i, (lbl, r) in enumerate(rank_items):
    color = COLORS.get(lbl, '#95A5A6')
    marker = '*' if lbl == "TSK-SpikeSlab" else 'o'
    size = 200 if lbl == "TSK-SpikeSlab" else 100
    ax.scatter(r, 0, c=color, s=size, marker=marker,
              edgecolors='black' if lbl == "TSK-SpikeSlab" else 'none',
              linewidth=1.5 if lbl == "TSK-SpikeSlab" else 0, zorder=5)
    offset_y = 0.04 if i % 2 == 0 else -0.025
    ax.annotate(lbl, (r, offset_y), ha='center', fontsize=9,
               fontweight='bold' if lbl == "TSK-SpikeSlab" else 'normal')

best_r = min([v for _, v in rank_items])
ax.annotate('', xy=(best_r, -0.06), xytext=(best_r + CD, -0.06),
           arrowprops=dict(arrowstyle='<->', color='k', lw=2))
ax.annotate(f'CD={CD:.2f}', (best_r + CD/2, -0.08), ha='center', fontsize=9, fontweight='bold')

ax.set_xlim(0.5, 6.5)
ax.set_ylim(-0.14, 0.10)
ax.set_xlabel('Average Rank (1 = best)', fontsize=10)
ax.set_yticks([])
for s in ['left', 'right', 'top']:
    ax.spines[s].set_visible(False)
ax.set_title('Fig. 5. CD Diagram (Friedman-Nemenyi)', fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "fig5_cd_diagram.pdf"), dpi=300)
plt.savefig(os.path.join(FIG_DIR, "fig5_cd_diagram.png"), dpi=300)
plt.close()

# ============================================================
# FIGURE 6: Rule PIPs
# ============================================================
print("Figure 6...")
fig, ax = plt.subplots(figsize=(7, 4))

pips = [0.3004, 0.6996, 0.8992, 0.5998, 0.6996]
rule_labels = [f'R{i+1}' for i in range(5)]
colors_rules = ['#D7191C' if p > 0.5 else '#757575' for p in pips]

bars = ax.barh(rule_labels, pips, color=colors_rules, edgecolor='black',
               height=0.5, linewidth=0.8)
ax.axvline(x=0.5, color='black', linestyle='--', linewidth=1.5, label='Threshold')

# Add value labels at bar ends (carefully offset)
for i, (bar, p) in enumerate(zip(bars, pips)):
    status = 'ACTIVE' if p > 0.5 else 'inactive'
    ax.annotate(f'{p:.3f}', (bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2),
               va='center', fontsize=9, color='#D7191C' if p > 0.5 else '#757575',
               fontweight='bold' if p > 0.5 else 'normal')

ax.set_xlabel('Posterior Inclusion Probability', fontsize=11)
ax.set_xlim(0, 1.25)
ax.legend(fontsize=9, loc='lower right')
ax.set_title('Fig. 6. Rule inclusion probabilities (Energy-Cooling)', fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "fig6_rules.pdf"), dpi=300)
plt.savefig(os.path.join(FIG_DIR, "fig6_rules.png"), dpi=300)
plt.close()

# ============================================================
# FIGURE 7: R2 bar chart
# ============================================================
print("Figure 7...")
fig, ax = plt.subplots(figsize=(9, 5))

x = np.arange(len(ds_names))
width = 0.12

for j, mn in enumerate(METHOD_ORDER):
    r2_vals = [results[ds][mn]["R2"] for ds in ds_names]
    offset = (j - len(METHOD_ORDER)/2 + 0.5) * width
    ax.bar(x + offset, r2_vals, width, color=COLORS[mn],
           edgecolor='white', linewidth=0.3, label=mn)

ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
ax.set_xticks(x)
ax.set_xticklabels(ds_names, fontsize=9)
ax.set_ylabel('R²', fontsize=11)
ax.set_ylim(-12, 1.2)
ax.set_title('Fig. 7. Predictive performance (R²) across datasets', fontweight='bold')
ax.legend(fontsize=8, ncol=3, loc='lower left')
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "fig7_pareto.pdf"), dpi=300)
plt.savefig(os.path.join(FIG_DIR, "fig7_pareto.png"), dpi=300)
plt.close()

print(f"\nAll 7 figures saved to {FIG_DIR}/")
