import numpy as np
import pytest

from phase4_metrics import (
    crps_from_samples,
    interval_score,
    weighted_interval_score,
)


def test_interval_score_penalizes_misses_at_the_declared_level():
    y = np.array([0.0, 2.0])
    lower = np.array([-1.0, -1.0])
    upper = np.array([1.0, 1.0])

    score = interval_score(y, lower, upper, alpha=0.1)

    np.testing.assert_allclose(score, np.array([2.0, 22.0]))


def test_wis_uses_central_intervals_and_median():
    y = np.array([0.0])
    quantiles = {
        0.25: np.array([-1.0]),
        0.75: np.array([1.0]),
        0.5: np.array([0.0]),
    }

    score = weighted_interval_score(y, quantiles)

    assert score.shape == (1,)
    assert score[0] == pytest.approx(1.0 / 3.0)


def test_crps_from_degenerate_samples_is_absolute_error():
    y = np.array([1.0])
    samples = np.array([[0.0, 0.0, 0.0]])

    score = crps_from_samples(y, samples)

    assert score[0] == pytest.approx(1.0)
