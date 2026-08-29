"""Geometry and sparsity phase-diagram descriptors for Phase 4."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import time

import numpy as np
from sklearn.preprocessing import StandardScaler

from tsk_core import (
    OUTPUT_DIR,
    SEED,
    TSK_SpikeSlab_Gibbs,
    append_noise_features,
    fcm,
    gaussian_membership_fit,
    load_concrete,
    load_energy,
    tsk_phi,
    tsk_weights,
)


def pairwise_rule_overlap(weights):
    """Mean pairwise cosine overlap of normalized rule firing strengths."""
    weights = np.asarray(weights, dtype=float)
    if weights.ndim != 2 or weights.shape[1] < 2:
        return 0.0
    norms = np.linalg.norm(weights, axis=0)
    normalized = weights / np.maximum(norms, 1e-15)
    values = [
        float(normalized[:, i] @ normalized[:, j])
        for i in range(weights.shape[1])
        for j in range(i + 1, weights.shape[1])
    ]
    return float(np.mean(values))


def signal_to_noise_ratio(signal, noise_std):
    if noise_std <= 0:
        raise ValueError("noise_std must be positive")
    return float(np.std(np.asarray(signal, dtype=float)) / noise_std)


def design_descriptors(X, k=5):
    """Describe the fitted TSK geometry without using any result values."""
    X = np.asarray(X, dtype=float)
    if X.ndim != 2:
        raise ValueError("X must be a two-dimensional array")
    centers, labels, _ = fcm(X, k)
    memberships, _ = gaussian_membership_fit(
        X, centers, labels, k
    )
    weights = tsk_weights(memberships)
    Phi, pp = tsk_phi(weights, X)
    condition_number = float(np.linalg.cond(Phi))
    if not np.isfinite(condition_number):
        condition_number = None
    return {
        "n": int(X.shape[0]),
        "d": int(X.shape[1]),
        "k": int(k),
        "p": int(pp * k),
        "n_over_p": float(X.shape[0] / (pp * k)),
        "rule_overlap": pairwise_rule_overlap(weights),
        "condition_number": condition_number,
        "log10_condition_number": (
            float(np.log10(condition_number))
            if condition_number is not None else None
        ),
    }


def make_synthetic_case(n, d, k, noise_std, seed):
    rng = np.random.RandomState(seed)
    X = rng.normal(size=(n, d))
    X = StandardScaler().fit_transform(X)
    centers, labels, _ = fcm(X, k, seed=seed)
    memberships, spreads = gaussian_membership_fit(
        X, centers, labels, k
    )
    Phi, pp = tsk_phi(tsk_weights(memberships), X)
    beta = np.zeros(k * pp)
    beta[:pp] = np.array([0.8, 0.5, -0.3])[:pp]
    if k >= 3 and pp >= 3:
        beta[2 * pp:3 * pp] = np.array([-0.6, 0.4, 0.2])
    signal = Phi @ beta
    y = signal + noise_std * rng.standard_normal(n)
    return X, y, signal, Phi, centers, spreads


def _active_ratio_from_main(output_dir, dataset):
    path = Path(output_dir) / "main_rebuilt.json"
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload["datasets"][dataset]["methods"][
        "TSK-SpikeSlab-Gibbs"
    ]["rows"]
    values = [
        row["active_rule_ratio"] for row in rows
        if row.get("active_rule_ratio") is not None
    ]
    return float(np.mean(values)) if values else None


def run_phase_diagram(output_dir=None):
    output_dir = Path(output_dir) if output_dir else Path(OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    Xe, y_heat, y_cool = load_energy()
    Xc, y_concrete = load_concrete()
    datasets = {
        "Energy-Heating": (Xe, y_heat),
        "Energy-Cooling": (Xe, y_cool),
        "Concrete": (Xc, y_concrete),
    }
    benchmark_geometry = []
    for dataset, (X, _) in datasets.items():
        X_scaled = StandardScaler().fit_transform(X)
        for k in (3, 5, 7, 10):
            row = design_descriptors(X_scaled, k=k)
            row.update({
                "dataset": dataset,
                "source": "full cached benchmark geometry",
                "active_rule_ratio": (
                    _active_ratio_from_main(output_dir, dataset)
                    if k == 5 else None
                ),
                "snr": None,
                "irrelevant_feature_ratio": 0.0,
            })
            benchmark_geometry.append(row)

    noise_geometry = []
    for n_noise in (0, 4, 12, 30):
        X_noise = append_noise_features(Xe, n_noise) if n_noise else Xe
        X_scaled = StandardScaler().fit_transform(X_noise)
        row = design_descriptors(X_scaled, k=5)
        row.update({
            "dataset": "Energy-Cooling",
            "n_noise": int(n_noise),
            "source": "full cached benchmark plus generated noise columns",
            "snr": None,
            "active_rule_ratio": None,
            "irrelevant_feature_ratio": float(
                n_noise / X_noise.shape[1]
            ),
        })
        noise_geometry.append(row)

    synthetic_snr = []
    for n in (60, 120, 240):
        for noise_std in (0.25, 1.0, 2.0):
            seed = SEED + n + int(noise_std * 100)
            X, y, signal, Phi, _, _ = make_synthetic_case(
                n=n, d=2, k=3, noise_std=noise_std, seed=seed
            )
            started = time.perf_counter()
            model = TSK_SpikeSlab_Gibbs(
                k=3, pi=0.5, tau2=2.0,
                n_burn=200, n_samples=400, seed=seed,
            ).fit(X, y)
            row = design_descriptors(X, k=3)
            row.update({
                "source": "generated synthetic TSK case",
                "noise_std": float(noise_std),
                "snr": signal_to_noise_ratio(signal, noise_std),
                "active_rule_ratio": float(model.active_rules / 3),
                "irrelevant_feature_ratio": 0.0,
                "runtime_s": float(time.perf_counter() - started),
                "predictive_samples": 400,
            })
            synthetic_snr.append(row)

    payload = {
        "protocol": {
            "seed": SEED,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "note": "descriptors and small synthetic gate; not manuscript numbers",
        },
        "benchmark_geometry": benchmark_geometry,
        "noise_geometry": noise_geometry,
        "synthetic_snr": synthetic_snr,
    }
    path = output_dir / "phase_diagram.json"
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"saved {path}")
    return payload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()
    run_phase_diagram(args.output_dir)


if __name__ == "__main__":
    main()
