"""Proper scoring rules used by the rebuilt experiment ledger."""

import numpy as np


def interval_score(y_true, lower, upper, alpha=0.05):
    """Return the interval score for a central interval with miscoverage alpha."""
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be between 0 and 1")
    y_true = np.asarray(y_true, dtype=float)
    lower = np.asarray(lower, dtype=float)
    upper = np.asarray(upper, dtype=float)
    score = upper - lower
    score = score + (2.0 / alpha) * np.maximum(lower - y_true, 0.0)
    score = score + (2.0 / alpha) * np.maximum(y_true - upper, 0.0)
    return score


def weighted_interval_score(y_true, quantiles):
    """Return the normalized WIS from central quantile pairs.

    quantiles maps probabilities such as 0.025 and 0.975 to arrays and must
    contain a 0.5 median.  Each lower probability p is paired with 1-p.
    """
    y_true = np.asarray(y_true, dtype=float)
    if 0.5 not in quantiles:
        raise ValueError("quantiles must contain the 0.5 median")
    median = np.asarray(quantiles[0.5], dtype=float)
    total = 0.5 * np.abs(y_true - median)
    interval_count = 0
    for lower_prob in sorted(p for p in quantiles if 0.0 < p < 0.5):
        upper_prob = 1.0 - lower_prob
        if upper_prob not in quantiles:
            raise ValueError(
                f"missing central counterpart for quantile {lower_prob}"
            )
        alpha = 2.0 * lower_prob
        total = total + (alpha / 2.0) * interval_score(
            y_true, quantiles[lower_prob], quantiles[upper_prob], alpha
        )
        interval_count += 1
    if interval_count == 0:
        raise ValueError("quantiles must contain at least one central interval")
    return total / (interval_count + 0.5)


def crps_from_samples(y_true, samples):
    """Return the empirical CRPS for samples shaped (n_observations, n_samples)."""
    y_true = np.asarray(y_true, dtype=float)
    samples = np.asarray(samples, dtype=float)
    if samples.ndim != 2 or samples.shape[0] != len(y_true):
        raise ValueError("samples must have shape (len(y_true), n_samples)")
    sorted_samples = np.sort(samples, axis=1)
    n_samples = samples.shape[1]
    weights = 2.0 * np.arange(n_samples) - n_samples + 1.0
    expected_pairwise_abs = (
        2.0 * (sorted_samples @ weights) / n_samples ** 2
    )
    score = np.mean(np.abs(samples - y_true[:, None]), axis=1)
    score = score - 0.5 * expected_pairwise_abs
    return np.maximum(score, 0.0)
