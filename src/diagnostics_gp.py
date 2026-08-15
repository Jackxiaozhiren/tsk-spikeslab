#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E2 + E3 supplements for the INS resubmission:

  E2  MCMC convergence diagnostics (multi-chain R-hat + ESS) for
      TSK_SpikeSlab_Gibbs on a representative split.
  E3  Gaussian-process regression baseline (sklearn, probabilistic with
      closed-form predictive intervals) on the full 30-split protocol.

Outputs:
  results/raw/mcmc_diagnostics.json
  results/raw/gp_baseline.json
"""

import json
import os
import time

import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel

from tsk_core import (
    load_energy, load_concrete, get_splits, compute_metrics,
    TSK_SpikeSlab_Gibbs, DATA_DIR, SEED,
)

N_SPLITS = 30


# ---------------------------------------------------------------
# E2: MCMC convergence diagnostics
# ---------------------------------------------------------------
def _rhat(chains):
    """Gelman-Rubin R-hat. chains: list of (n_samples, [dim]) arrays."""
    chains = [np.asarray(c, dtype=float) for c in chains]
    n = chains[0].shape[0]
    m = len(chains)
    if chains[0].ndim == 1:
        chains = [c[:, None] for c in chains]
    C = np.stack(chains)                      # (m, n, dim)
    W = C.var(axis=1, ddof=1).mean(axis=0)    # within-chain (dim,)
    B = C.mean(axis=1).var(axis=0, ddof=1) * n  # between (dim,)
    var_hat = (n - 1) / n * W + B / n
    W = np.maximum(W, 1e-16)
    return np.sqrt(var_hat / W)


def _ess(x):
    """Effective sample size via monotone autocorrelation."""
    x = np.asarray(x, dtype=float)
    x = x - x.mean()
    n = len(x)
    ac = np.correlate(x, x, mode="full")[n - 1:]
    ac = ac / (ac[0] + 1e-16)
    tau = 1.0
    for k in range(1, n):
        rho = ac[k]
        if rho < 0:
            break
        tau += 2.0 * rho
    return n / max(tau, 1e-6)


def run_mcmc_diagnostics():
    print("=" * 70)
    print("E2: MCMC CONVERGENCE DIAGNOSTICS (TSK_SpikeSlab_Gibbs, 3 chains)")
    print("=" * 70)
    out = {}
    datasets = {}
    Xe, y_heat, y_cool = load_energy()
    Xc, y_conc = load_concrete()
    datasets["Energy-Cooling"] = (Xe, y_cool)
    datasets["Concrete"] = (Xc, y_conc)

    for ds_name, (X, y) in datasets.items():
        splits = get_splits(y, N_SPLITS)
        tr, te = splits[0]
        sc = StandardScaler()
        Xtr = sc.fit_transform(X[tr])
        ytr = y[tr]
        chains_gamma, chains_beta, chains_s2 = [], [], []
        for chain_seed in [42, 123, 456]:
            t0 = time.time()
            m = TSK_SpikeSlab_Gibbs(k=5, pi=0.5, tau2=1e3,
                                    n_burn=1000, n_samples=2000, seed=chain_seed).fit(Xtr, ytr)
            chains_gamma.append(m.gamma_samples_)     # (2000, R)
            chains_beta.append(m.beta_samples_)       # (2000, P)
            chains_s2.append(m.sigma2_samples_)       # (2000,)
            print(f"  {ds_name} chain seed={chain_seed}: "
                  f"mean PIP={m.pip_.mean():.3f} ({time.time()-t0:.0f}s)")

        rhat_gamma = _rhat(chains_gamma)              # (R,)
        rhat_beta = _rhat(chains_beta)                # (P,)
        rhat_s2 = _rhat([c for c in chains_s2])       # (1,)

        # ESS on gamma (averaged over rules and chains)
        ess_gamma = np.mean([[_ess(ch[:, j]) for j in range(ch.shape[1])]
                             for ch in chains_gamma])
        ess_s2 = np.mean([_ess(c) for c in chains_s2])

        rec = {
            "rhat_gamma": [float(v) for v in rhat_gamma],
            "rhat_gamma_max": float(rhat_gamma.max()),
            "rhat_beta_median": float(np.median(rhat_beta)),
            "rhat_beta_max": float(rhat_beta.max()),
            "rhat_sigma2": float(rhat_s2[0]),
            "ess_gamma_mean": float(ess_gamma),
            "ess_sigma2_mean": float(ess_s2),
            "n_chains": 3, "n_burn": 1000, "n_samples": 2000,
        }
        out[ds_name] = rec
        print(f"  -> Rhat gamma max={rec['rhat_gamma_max']:.3f} | "
              f"Rhat beta median={rec['rhat_beta_median']:.3f} max={rec['rhat_beta_max']:.3f} | "
              f"Rhat sigma2={rec['rhat_sigma2']:.3f} | "
              f"ESS gamma={rec['ess_gamma_mean']:.0f} sigma2={rec['ess_sigma2_mean']:.0f}")

    with open(os.path.join(DATA_DIR, "mcmc_diagnostics.json"), "w") as f:
        json.dump(out, f, indent=2)
    return out


# ---------------------------------------------------------------
# E3: Gaussian-process regression baseline (probabilistic, with PIs)
# ---------------------------------------------------------------
def run_gp_baseline():
    print("\n" + "=" * 70)
    print("E3: GAUSSIAN-PROCESS REGRESSION BASELINE (30 splits)")
    print("=" * 70)
    Xe, y_heat, y_cool = load_energy()
    Xc, y_conc = load_concrete()
    datasets = {
        "Energy-Heating": (Xe, y_heat),
        "Energy-Cooling": (Xe, y_cool),
        "Concrete": (Xc, y_conc),
    }
    out = {}
    kernel = 1.0 * RBF(length_scale=1.0, length_scale_bounds=(1e-2, 1e2)) + \
             WhiteKernel(noise_level=1.0, noise_level_bounds=(1e-5, 1e5))
    for ds_name, (X, y) in datasets.items():
        splits = get_splits(y, N_SPLITS)
        rows = []
        t0 = time.time()
        for si, (tr, te) in enumerate(splits):
            sc = StandardScaler()
            Xtr = sc.fit_transform(X[tr]); Xte = sc.transform(X[te])
            ytr, yte = y[tr], y[te]
            gp = GaussianProcessRegressor(kernel=kernel, alpha=1e-6,
                                          normalize_y=True, random_state=SEED)
            gp.fit(Xtr, ytr)
            yp, ystd = gp.predict(Xte, return_std=True)
            r = compute_metrics(yte, yp, yp - 1.96 * ystd, yp + 1.96 * ystd)
            rows.append(r)
        out[ds_name] = rows
        rm = np.mean([r["RMSE"] for r in rows]); r2 = np.mean([r["R2"] for r in rows])
        p = np.mean([r["PICP"] for r in rows]); w = np.mean([r["MPIW"] for r in rows])
        print(f"  {ds_name:<16} RMSE={rm:.3f}  R2={r2:+.3f}  "
              f"PICP={p:.3f}  MPIW={w:.2f}  ({time.time()-t0:.0f}s)")
    with open(os.path.join(DATA_DIR, "gp_baseline.json"), "w") as f:
        json.dump({k: v for k, v in out.items()}, f, indent=2, default=float)
    return out


if __name__ == "__main__":
    run_mcmc_diagnostics()
    run_gp_baseline()
    print("\n\nE2/E3 complete. Results in", DATA_DIR)
