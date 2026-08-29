import numpy as np
import pytest

from conformal_baseline import split_conformal_interval


def test_split_conformal_uses_calibration_residual_quantile(monkeypatch):
    class FakeTSK:
        def __init__(self, k):
            self.k = k

        def fit(self, X, y):
            return self

        def predict(self, X):
            return np.asarray(X[:, 0], dtype=float)

    monkeypatch.setattr("conformal_baseline.TSK_LS", FakeTSK)
    X_fit = np.array([[0.0], [1.0], [2.0]])
    y_fit = np.array([0.0, 1.0, 2.0])
    X_cal = np.array([[0.0], [1.0], [2.0], [3.0]])
    y_cal = np.array([1.0, 0.0, 4.0, 1.0])
    X_test = np.array([[2.0], [4.0]])

    mean, lower, upper, q = split_conformal_interval(
        X_fit, y_fit, X_cal, y_cal, X_test, alpha=0.25, k=2
    )

    # Absolute calibration residuals are [1, 1, 2, 2]; the finite-sample
    # higher quantile at ceil((n+1)(1-alpha))/n is 2.
    np.testing.assert_allclose(mean, np.array([2.0, 4.0]))
    np.testing.assert_allclose(lower, np.array([0.0, 2.0]))
    np.testing.assert_allclose(upper, np.array([4.0, 6.0]))
    assert q == pytest.approx(2.0)
