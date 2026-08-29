import numpy as np
import pytest

from rebuild_phase4 import (
    default_output_dir,
    make_calibration_split,
    summarize_rows,
)


def test_calibration_split_is_deterministic_disjoint_and_complete():
    first_fit, first_cal = make_calibration_split(
        n=20, calibration_fraction=0.25, seed=42
    )
    second_fit, second_cal = make_calibration_split(
        n=20, calibration_fraction=0.25, seed=42
    )

    np.testing.assert_array_equal(first_fit, second_fit)
    np.testing.assert_array_equal(first_cal, second_cal)
    assert set(first_fit).isdisjoint(set(first_cal))
    assert sorted(np.concatenate([first_fit, first_cal]).tolist()) == list(range(20))


def test_summary_preserves_missing_scores_as_null():
    rows = [
        {"RMSE": 1.0, "WIS": None, "CRPS": None},
        {"RMSE": 3.0, "WIS": 2.0, "CRPS": 1.0},
    ]

    summary = summarize_rows(rows)

    assert summary["RMSE"]["mean"] == pytest.approx(2.0)
    assert summary["RMSE"]["n"] == 2
    assert summary["WIS"]["mean"] == pytest.approx(2.0)
    assert summary["WIS"]["n"] == 1
    assert summary["CRPS"]["mean"] == pytest.approx(1.0)


def test_default_output_dir_is_not_historical_results_raw():
    output = default_output_dir()

    assert output.name == "rebuild_results_2026-08-29_v1"
    assert output.name != "raw"
