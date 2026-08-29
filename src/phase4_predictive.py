"""Predictive sampling and proper-score evaluation for Phase 4."""

import numpy as np
from scipy.stats import t as student_t

from phase4_metrics import (
    crps_from_samples,
    interval_score,
    weighted_interval_score,
)
from tsk_core import (
    TSK_Bayesian,
    TSK_SpikeSlab_Fast,
    gaussian_membership_predict,
    tsk_phi,
    tsk_weights,
)


def _design_matrix(model, X):
    memberships = gaussian_membership_predict(
        X, model.ctr_, model.spreads_, model.k
    )
    return tsk_phi(tsk_weights(memberships), X)[0]


def predictive_samples(model, X, n_samples=512, seed=42):
    """Draw posterior-predictive samples shaped (n_observations, n_samples)."""
    if n_samples <= 0:
        raise ValueError("n_samples must be positive")
    rng = np.random.RandomState(seed)
    X = np.asarray(X, dtype=float)
    Phi = _design_matrix(model, X)

    if isinstance(model, TSK_Bayesian):
        mean = Phi @ model.beta_
        factor = 1.0 + np.einsum(
            "ij,jk,ik->i", Phi, model.cov_post_, Phi
        )
        scale = np.sqrt(
            np.maximum(model.b_n_ / model.a_n_ * factor, 1e-12)
        )
        return student_t.rvs(
            df=2.0 * model.a_n_,
            loc=mean[:, None],
            scale=scale[:, None],
            size=(len(X), n_samples),
            random_state=rng,
        )

    if isinstance(model, TSK_SpikeSlab_Fast):
        coefficient_draws = rng.multivariate_normal(
            model.beta_, model.cov_beta_, size=n_samples
        )
        means = Phi @ coefficient_draws.T
        noise = rng.normal(
            0.0, np.sqrt(max(model.sigma2_, 1e-12)),
            size=(len(X), n_samples),
        )
        return means + noise

    if hasattr(model, "beta_samples_") and hasattr(model, "sigma2_samples_"):
        posterior_indices = rng.randint(
            0, len(model.beta_samples_), size=n_samples
        )
        means = Phi @ model.beta_samples_[posterior_indices].T
        noise = rng.normal(
            0.0,
            np.sqrt(np.maximum(
                model.sigma2_samples_[posterior_indices], 1e-12
            )),
            size=(len(X), n_samples),
        )
        return means + noise

    raise TypeError(f"predictive sampling is not defined for {type(model)!r}")


def evaluate_prediction_arrays(
    y_test, mean, lower, upper, samples=None, n_samples=None
):
    """Evaluate predictions and optional posterior-predictive samples."""
    quantile_probs = (0.025, 0.1, 0.2, 0.25, 0.5,
                      0.75, 0.8, 0.9, 0.975)
    result = {
        "RMSE": float(np.sqrt(np.mean((y_test - mean) ** 2))),
        "MAE": float(np.mean(np.abs(y_test - mean))),
        "R2": float(1.0 - np.sum((y_test - mean) ** 2)
                    / np.sum((y_test - np.mean(y_test)) ** 2)),
        "PICP": float(np.mean((y_test >= lower) & (y_test <= upper))),
        "MPIW": float(np.mean(upper - lower)),
        "IntervalScore95": float(np.mean(
            interval_score(y_test, lower, upper, alpha=0.05)
        )),
        "Winkler95": float(np.mean(
            interval_score(y_test, lower, upper, alpha=0.05)
        )),
        "WIS": None,
        "CRPS": None,
        "n_predictive_samples": (
            int(samples.shape[1]) if samples is not None else n_samples
        ),
    }
    if samples is not None:
        quantiles = {
            probability: np.quantile(samples, probability, axis=1)
            for probability in quantile_probs
        }
        result["WIS"] = float(np.mean(
            weighted_interval_score(y_test, quantiles)
        ))
        result["CRPS"] = float(np.mean(crps_from_samples(y_test, samples)))
    return result


def evaluate_interval_model(model, X_test, y_test, seed=42, n_samples=512):
    """Evaluate a fitted probabilistic model with proper interval scores."""
    mean, lower, upper = model.predict(X_test)
    samples = predictive_samples(model, X_test, n_samples, seed)
    return evaluate_prediction_arrays(
        y_test, mean, lower, upper, samples=samples
    )
