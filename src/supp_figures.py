#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supplementary figures (R3) for the INS resubmission:

  fig5_reliability.pdf  — reliability diagram: empirical PICP vs nominal
                          coverage level, for Bayesian-TSK / Gibbs / GP.
  fig6_pi_band.pdf      — 95% prediction-interval band vs held-out truth
                          on the Energy-Cooling target (representative split).

Reuses the corrected TSK core + GP baseline; no new experiments beyond
collecting per-point predictive mean/std.
"""

import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import norm
from sklearn.preprocessing import StandardScaler
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel

from tsk_core import (
    load_energy, get_splits, TSK_Bayesian, TSK_SpikeSlab_Gibbs, SEED,
)

FIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "results", "figures")
os.makedirs(FIG_DIR, exist_ok=True)

Xe, y_heat, y_cool = load_energy()
X, y = Xe, y_cool  # Energy-Cooling

C = {"bayes": "#1f77b4", "gibbs": "#ff7f0e", "gp": "#2ca02c"}


def _gp():
    kernel = 1.0 * RBF(length_scale=1.0, length_scale_bounds=(1e-2, 1e2)) + \
             WhiteKernel(noise_level=1.0, noise_level_bounds=(1e-5, 1e5))
    return GaussianProcessRegressor(kernel=kernel, alpha=1e-6,
                                    normalize_y=True, random_state=SEED)


def collect(splits):
    """Return per-method lists of (y_true, mean, std) across all test points."""
    methods = {
        "bayes": TSK_Bayesian(k=5),
        "gibbs": TSK_SpikeSlab_Gibbs(k=5, pi=0.5, tau2=1e3,
                                     n_burn=1000, n_samples=2000),
    }
    acc = {"bayes": [], "gibbs": [], "gp": []}
    for tr, te in splits:
        sc = StandardScaler()
        Xtr = sc.fit_transform(X[tr]); Xte = sc.transform(X[te])
        ytr, yte = y[tr], y[te]
        for name, m in methods.items():
            m.fit(Xtr, ytr)
            yp, yl, yu = m.predict(Xte)
            mean = yp
            std = (yu - yl) / (2 * 1.96)
            acc[name].append((yte, mean, std))
        gp = _gp().fit(Xtr, ytr)
        yp, ystd = gp.predict(Xte, return_std=True)
        acc["gp"].append((yte, yp, ystd))
    out = {}
    for name in acc:
        yt = np.concatenate([a[0] for a in acc[name]])
        mn = np.concatenate([a[1] for a in acc[name]])
        sd = np.concatenate([a[2] for a in acc[name]])
        out[name] = (yt, mn, sd)
    return out


def reliability(acc):
    levels = np.array([0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99])
    fig, ax = plt.subplots(figsize=(5.2, 4.2))
    ax.plot([0.5, 1.0], [0.5, 1.0], "k--", lw=1, label="Ideal")
    for name, lbl in [("bayes", "Bayesian-TSK"), ("gibbs", "Gibbs/BMA"),
                      ("gp", "Gaussian process")]:
        yt, mn, sd = acc[name]
        emp = []
        for q in levels:
            z = norm.ppf((1 + q) / 2)
            emp.append(np.mean(np.abs(yt - mn) <= z * sd))
        ax.plot(levels, emp, marker="o", ms=4, lw=1.5,
                color=C[name], label=lbl)
    ax.set_xlabel("Nominal coverage")
    ax.set_ylabel("Empirical coverage")
    ax.set_title("Reliability (Energy-Cooling, 30 splits)")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(alpha=0.25, lw=0.5)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "fig5_reliability.pdf"))
    fig.savefig(os.path.join(FIG_DIR, "fig5_reliability.png"), dpi=200)
    plt.close(fig)
    print("fig5_reliability written")


def pi_band(acc):
    # representative split 0 (of the 30-split protocol)
    tr, te = get_splits(y, 30)[0]
    sc = StandardScaler()
    Xtr = sc.fit_transform(X[tr]); Xte = sc.transform(X[te])
    ytr, yte = y[tr], y[te]

    def band(model):
        m = model.fit(Xtr, ytr)
        yp, yl, yu = m.predict(Xte)
        return yp, (yu - yl) / (2 * 1.96)

    fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.8), sharey=True)
    for ax, name, model in [
        (axes[0], "bayes", TSK_Bayesian(k=5)),
        (axes[1], "gibbs", TSK_SpikeSlab_Gibbs(k=5, pi=0.5, tau2=1e3,
                                               n_burn=1000, n_samples=2000)),
    ]:
        yp, std = band(model)
        order = np.argsort(yte)
        xs = np.arange(len(yte))
        ax.fill_between(xs, yp[order] - 1.96 * std[order],
                        yp[order] + 1.96 * std[order],
                        color=C[name], alpha=0.25, lw=0)
        ax.plot(xs, yp[order], color=C[name], lw=1.2,
                label="Mean prediction")
        ax.scatter(xs, yte[order], s=10, color="black", alpha=0.6,
                   label="Held-out truth", zorder=3)
        ax.set_xlabel("Test point (sorted by truth)")
        if name == "bayes":
            ax.set_ylabel("Cooling load")
            ax.set_title("Bayesian-TSK (conjugate)")
        else:
            ax.set_title("Gibbs + BMA")
        ax.legend(frameon=False, fontsize=7, loc="upper left")
        ax.grid(alpha=0.25, lw=0.5)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "fig6_pi_band.pdf"))
    fig.savefig(os.path.join(FIG_DIR, "fig6_pi_band.png"), dpi=200)
    plt.close(fig)
    print("fig6_pi_band written")


if __name__ == "__main__":
    acc = collect(get_splits(y, 30))
    reliability(acc)
    pi_band(acc)
    print("Done.")
