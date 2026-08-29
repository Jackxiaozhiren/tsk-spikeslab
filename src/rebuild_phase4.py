"""Rebuild the main evaluation protocol into a fresh result directory."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import time

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR

from conformal_baseline import split_conformal_interval
from phase4_metrics import interval_score
from phase4_predictive import (
    evaluate_interval_model,
    evaluate_prediction_arrays,
)
from tsk_core import (
    OUTPUT_DIR,
    SEED,
    TSK_Bayesian,
    TSK_LS,
    TSK_SpikeSlab_Fast,
    TSK_SpikeSlab_Gibbs,
    load_concrete,
    load_energy,
    get_splits,
)


DEFAULT_N_SPLITS = 30
DEFAULT_PREDICTIVE_SAMPLES = 512
CONFORMAL_CALIBRATION_FRACTION = 0.25
METHOD_METRICS = (
    "RMSE", "MAE", "R2", "PICP", "MPIW",
    "IntervalScore95", "Winkler95", "WIS", "CRPS",
    "ESS_sigma2", "ESS_per_s",
)


def default_output_dir():
    return Path(OUTPUT_DIR)


def make_calibration_split(n, calibration_fraction, seed):
    if n < 2:
        raise ValueError("at least two observations are required")
    if not 0.0 < calibration_fraction < 1.0:
        raise ValueError("calibration_fraction must be between 0 and 1")
    n_calibration = int(np.ceil(n * calibration_fraction))
    n_calibration = min(max(n_calibration, 1), n - 1)
    permutation = np.random.RandomState(seed).permutation(n)
    calibration = np.sort(permutation[:n_calibration])
    fit = np.sort(permutation[n_calibration:])
    return fit, calibration


def summarize_rows(rows):
    summary = {}
    for metric in METHOD_METRICS:
        values = [
            float(row[metric]) for row in rows
            if row.get(metric) is not None
        ]
        if values:
            summary[metric] = {
                "mean": float(np.mean(values)),
                "std": float(np.std(values)),
                "n": len(values),
            }
        else:
            summary[metric] = {"mean": None, "std": None, "n": 0}
    return summary


def _point_metrics(y_true, mean):
    y_true = np.asarray(y_true, dtype=float)
    mean = np.asarray(mean, dtype=float)
    squared_error = np.sum((y_true - mean) ** 2)
    total_sum = np.sum((y_true - np.mean(y_true)) ** 2)
    return {
        "RMSE": float(np.sqrt(np.mean((y_true - mean) ** 2))),
        "MAE": float(np.mean(np.abs(y_true - mean))),
        "R2": float(1.0 - squared_error / total_sum),
        "PICP": None,
        "MPIW": None,
        "IntervalScore95": None,
        "Winkler95": None,
        "WIS": None,
        "CRPS": None,
        "n_predictive_samples": None,
    }


def _annotate(result, method, split_idx, n_train, n_test, runtime,
              n_features, active_rules, config):
    result.update({
        "method": method,
        "split_idx": int(split_idx),
        "split_seed": int(SEED + split_idx),
        "n_train": int(n_train),
        "n_test": int(n_test),
        "n_features": int(n_features),
        "runtime_s": float(runtime),
        "active_rules": (
            int(active_rules) if active_rules is not None else None
        ),
        "active_rule_ratio": (
            float(active_rules / config["k"])
            if active_rules is not None and config.get("k")
            else None
        ),
        "model_config": config,
    })
    for metric in METHOD_METRICS:
        value = result.get(metric)
        if value is not None and not np.isfinite(value):
            raise ValueError(f"non-finite {metric} for {method}")
    return result


def _fit_tsk(method, X_train, y_train, X_test, y_test, split_idx,
             predictive_samples, factory, config, is_point=False):
    started = time.perf_counter()
    model = factory()
    model.fit(X_train, y_train)
    if is_point:
        result = _point_metrics(y_test, model.predict(X_test))
    else:
        result = evaluate_interval_model(
            model, X_test, y_test,
            seed=SEED + 10000 + split_idx,
            n_samples=predictive_samples,
        )
    result["ESS_sigma2"] = None
    result["ESS_per_s"] = None
    if hasattr(model, "sigma2_samples_"):
        from diagnostics_gp import _ess
        result["ESS_sigma2"] = float(_ess(model.sigma2_samples_))
        result["ESS_per_s"] = result["ESS_sigma2"] / max(
            time.perf_counter() - started, 1e-12
        )
    return _annotate(
        result, method, split_idx, len(X_train), len(X_test),
        time.perf_counter() - started, X_train.shape[1],
        getattr(model, "active_rules", None), config,
    )


def _fit_gp(X_train, y_train, X_test, y_test, split_idx,
            predictive_samples):
    started = time.perf_counter()
    kernel = (
        1.0 * RBF(length_scale=1.0, length_scale_bounds=(1e-2, 1e2))
        + WhiteKernel(noise_level=1.0, noise_level_bounds=(1e-5, 1e5))
    )
    model = GaussianProcessRegressor(
        kernel=kernel, alpha=1e-6,
        normalize_y=True, random_state=SEED + split_idx,
    )
    model.fit(X_train, y_train)
    mean, std = model.predict(X_test, return_std=True)
    lower = mean - 1.96 * std
    upper = mean + 1.96 * std
    rng = np.random.RandomState(SEED + 20000 + split_idx)
    samples = rng.normal(
        mean[:, None], np.maximum(std[:, None], 1e-12),
        size=(len(X_test), predictive_samples),
    )
    result = evaluate_prediction_arrays(
        y_test, mean, lower, upper, samples=samples
    )
    config = {
        "kernel": "RBF+WhiteKernel",
        "normalize_y": True,
        "n_predictive_samples": predictive_samples,
    }
    return _annotate(
        result, "GaussianProcess", split_idx, len(X_train), len(X_test),
        time.perf_counter() - started, X_train.shape[1], None, config,
    )


def _fit_conformal(X, y, train_indices, test_indices, split_idx, k):
    started = time.perf_counter()
    fit_rel, calibration_rel = make_calibration_split(
        len(train_indices), CONFORMAL_CALIBRATION_FRACTION,
        seed=SEED + 30000 + split_idx,
    )
    fit_indices = train_indices[fit_rel]
    calibration_indices = train_indices[calibration_rel]
    scaler = StandardScaler().fit(X[fit_indices])
    mean, lower, upper, radius = split_conformal_interval(
        scaler.transform(X[fit_indices]), y[fit_indices],
        scaler.transform(X[calibration_indices]), y[calibration_indices],
        scaler.transform(X[test_indices]),
        alpha=0.05, k=k,
    )
    result = _point_metrics(y[test_indices], mean)
    score = interval_score(
        y[test_indices], lower, upper, alpha=0.05
    )
    result.update({
        "PICP": float(np.mean(
            (y[test_indices] >= lower) & (y[test_indices] <= upper)
        )),
        "MPIW": float(np.mean(upper - lower)),
        "IntervalScore95": float(np.mean(score)),
        "Winkler95": float(np.mean(score)),
        "conformal_radius": float(radius),
        "conformal_fit_n": int(len(fit_indices)),
        "conformal_calibration_n": int(len(calibration_indices)),
        "n_predictive_samples": None,
    })
    config = {
        "k": int(k),
        "alpha": 0.05,
        "calibration_fraction_of_outer_train": (
            CONFORMAL_CALIBRATION_FRACTION
        ),
    }
    return _annotate(
        result, "Conformal-TSK-LS", split_idx,
        len(train_indices), len(test_indices),
        time.perf_counter() - started, X.shape[1], k, config,
    )


def _git_head(project_root):
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=project_root, text=True,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def run_main(output_dir=None, n_splits=DEFAULT_N_SPLITS,
             predictive_samples=DEFAULT_PREDICTIVE_SAMPLES):
    output_dir = Path(output_dir) if output_dir else default_output_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    Xe, y_heat, y_cool = load_energy()
    Xc, y_concrete = load_concrete()
    datasets = {
        "Energy-Heating": (Xe, y_heat),
        "Energy-Cooling": (Xe, y_cool),
        "Concrete": (Xc, y_concrete),
    }
    factories = [
        ("TSK-LS", lambda: TSK_LS(k=5),
         {"k": 5}, True),
        ("Bayesian-TSK", lambda: TSK_Bayesian(k=5, tau2=1e3),
         {"k": 5, "tau2": 1e3}, False),
        ("TSK-SpikeSlab-BIC",
         lambda: TSK_SpikeSlab_Fast(k=5, pi=0.5, tau2=1e3),
         {"k": 5, "pi": 0.5, "tau2": 1e3}, False),
        ("TSK-SpikeSlab-Gibbs",
         lambda: TSK_SpikeSlab_Gibbs(
             k=5, pi=0.5, tau2=1e3,
             n_burn=1000, n_samples=2000, seed=SEED,
         ),
         {"k": 5, "pi": 0.5, "tau2": 1e3,
          "n_burn": 1000, "n_samples": 2000}, False),
        ("RandomForest",
         lambda: RandomForestRegressor(
             n_estimators=300, max_depth=10,
             random_state=SEED, n_jobs=-1,
         ),
         {"n_estimators": 300, "max_depth": 10}, True),
        ("SVR",
         lambda: SVR(kernel="rbf", C=1.0, gamma="scale"),
         {"kernel": "rbf", "C": 1.0, "gamma": "scale"}, True),
    ]
    payload = {
        "protocol": {
            "seed": SEED,
            "n_splits": int(n_splits),
            "outer_split": "80/20 without replacement per split",
            "predictive_samples": int(predictive_samples),
            "conformal_calibration_fraction": (
                CONFORMAL_CALIBRATION_FRACTION
            ),
            "source_root": str(Path(__file__).resolve().parents[1]),
            "code_commit": _git_head(Path(__file__).resolve().parents[1]),
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        },
        "datasets": {},
    }
    for dataset_name, (X, y) in datasets.items():
        splits = get_splits(y, n_splits, seed=SEED)
        rows = {}
        for method, factory, config, is_point in factories:
            rows[method] = []
            for split_idx, (train, test) in enumerate(splits):
                scaler = StandardScaler().fit(X[train])
                X_train = scaler.transform(X[train])
                X_test = scaler.transform(X[test])
                rows[method].append(_fit_tsk(
                    method, X_train, y[train], X_test, y[test],
                    split_idx, predictive_samples, factory, config,
                    is_point=is_point,
                ))
        rows["GaussianProcess"] = []
        rows["Conformal-TSK-LS"] = []
        for split_idx, (train, test) in enumerate(splits):
            scaler = StandardScaler().fit(X[train])
            X_train = scaler.transform(X[train])
            X_test = scaler.transform(X[test])
            rows["GaussianProcess"].append(_fit_gp(
                X_train, y[train], X_test, y[test],
                split_idx, predictive_samples,
            ))
            rows["Conformal-TSK-LS"].append(
                _fit_conformal(X, y, train, test, split_idx, k=5)
            )
        payload["datasets"][dataset_name] = {
            "n": int(len(y)),
            "d": int(X.shape[1]),
            "methods": {
                name: {
                    "rows": method_rows,
                    "summary": summarize_rows(method_rows),
                }
                for name, method_rows in rows.items()
            },
        }
    output_path = output_dir / "main_rebuilt.json"
    output_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"saved {output_path}")
    return payload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--n-splits", type=int, default=DEFAULT_N_SPLITS)
    parser.add_argument(
        "--predictive-samples", type=int,
        default=DEFAULT_PREDICTIVE_SAMPLES,
    )
    args = parser.parse_args()
    run_main(
        output_dir=args.output_dir,
        n_splits=args.n_splits,
        predictive_samples=args.predictive_samples,
    )


if __name__ == "__main__":
    main()
