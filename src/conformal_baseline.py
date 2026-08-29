"""Split-conformal prediction baseline for the rebuilt experiment."""

import numpy as np

from tsk_core import TSK_LS


def split_conformal_interval(
    X_fit, y_fit, X_calibration, y_calibration, X_test,
    alpha=0.05, k=5,
):
    """Fit TSK-LS, calibrate absolute residuals, and return test intervals."""
    if len(y_calibration) == 0:
        raise ValueError("the calibration set must not be empty")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be between 0 and 1")

    model = TSK_LS(k=k).fit(X_fit, y_fit)
    calibration_prediction = model.predict(X_calibration)
    scores = np.abs(np.asarray(y_calibration) - calibration_prediction)
    quantile_level = min(
        1.0,
        np.ceil((len(scores) + 1) * (1.0 - alpha)) / len(scores),
    )
    quantile = float(np.quantile(scores, quantile_level, method="higher"))
    mean = model.predict(X_test)
    return mean, mean - quantile, mean + quantile, quantile
