import numpy as np
import pytest

from phase4_phase_diagram import (
    design_descriptors,
    pairwise_rule_overlap,
    signal_to_noise_ratio,
)


def test_pairwise_rule_overlap_has_expected_bounds_and_extremes():
    identical = np.array([[1.0, 1.0], [2.0, 2.0]])
    orthogonal = np.eye(2)

    assert pairwise_rule_overlap(identical) == pytest.approx(1.0)
    assert pairwise_rule_overlap(orthogonal) == pytest.approx(0.0)


def test_design_descriptors_report_n_over_p_and_finite_geometry():
    X = np.column_stack([
        np.linspace(-1.0, 1.0, 30),
        np.sin(np.linspace(-1.0, 1.0, 30)),
    ])

    result = design_descriptors(X, k=3)

    assert result["n"] == 30
    assert result["d"] == 2
    assert result["p"] == 9
    assert result["n_over_p"] == pytest.approx(30.0 / 9.0)
    assert 0.0 <= result["rule_overlap"] <= 1.0
    assert np.isfinite(result["condition_number"])


def test_signal_to_noise_ratio_is_scale_invariant():
    signal = np.array([-2.0, 0.0, 2.0])
    assert signal_to_noise_ratio(signal, 2.0) == pytest.approx(
        np.std(signal) / 2.0
    )
