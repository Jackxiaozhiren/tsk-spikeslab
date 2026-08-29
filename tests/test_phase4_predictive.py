import numpy as np
import pytest

import tsk_core
from phase4_predictive import evaluate_interval_model, predictive_samples


def _patch_empty_antecedent(monkeypatch):
    monkeypatch.setattr(
        tsk_core,
        "gaussian_membership_predict",
        lambda X, centers, spreads, k: np.ones((len(X), 0, k)),
    )
    monkeypatch.setattr(
        tsk_core,
        "tsk_weights",
        lambda memberships: np.ones((len(memberships), 1)),
    )
    monkeypatch.setattr(
        tsk_core,
        "tsk_phi",
        lambda weights, X: (np.ones((len(X), 1)), 1),
    )


def test_bayesian_predictive_samples_are_reproducible(monkeypatch):
    _patch_empty_antecedent(monkeypatch)
    model = tsk_core.TSK_Bayesian(k=1)
    model.ctr_ = np.empty((1, 0))
    model.spreads_ = np.empty((1, 0))
    model.beta_ = np.array([2.0])
    model.cov_post_ = np.array([[0.25]])
    model.a_n_ = 10.0
    model.b_n_ = 2.0
    model.cov_beta_ = np.array([[0.2]])
    model.sigma2_ = 0.25

    first = predictive_samples(model, np.zeros((3, 0)), n_samples=64, seed=9)
    second = predictive_samples(model, np.zeros((3, 0)), n_samples=64, seed=9)

    assert first.shape == (3, 64)
    assert np.isfinite(first).all()
    np.testing.assert_array_equal(first, second)


def test_evaluate_interval_model_reports_proper_scores(monkeypatch):
    class FakeModel:
        def predict(self, X):
            mean = np.zeros(len(X))
            return mean, -np.ones(len(X)), np.ones(len(X))

    monkeypatch.setattr(
        "phase4_predictive.predictive_samples",
        lambda model, X, n_samples, seed: np.zeros((len(X), n_samples)),
    )
    y_true = np.array([0.0, 2.0])
    result = evaluate_interval_model(
        FakeModel(), np.zeros((2, 1)), y_true, seed=1, n_samples=32
    )

    assert result["PICP"] == pytest.approx(0.5)
    assert result["MPIW"] == pytest.approx(2.0)
    assert result["IntervalScore95"] > 2.0
    assert result["WIS"] >= 0.0
    assert result["CRPS"] >= 0.0
