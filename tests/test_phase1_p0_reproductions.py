"""Phase 1 RED tests for the P0 correctness surfaces named in the Master Prompt.

These tests intentionally describe the target invariants before production
code is changed.  A failing test is defect evidence only; it is not a
replacement for the Phase 3 correctness gate or a formal experiment result.
"""

import json

import numpy as np
import pytest

import tsk_core


def test_fcm_uses_standard_exponent_for_squared_distances():
    """Squared Euclidean distances require exponent -1/(m-1), not -2/(m-1)."""
    X = np.array([[0.0], [0.7], [2.4], [4.1], [5.3]], dtype=float)
    m = 2.0
    centers, _, memberships = tsk_core.fcm(
        X, c=2, m=m, n_init=1, max_iter=500, tol=1e-12, seed=11
    )

    squared_distances = np.stack(
        [np.sum((X - center) ** 2, axis=1) for center in centers]
    )
    inverse_power = squared_distances ** (-1.0 / (m - 1.0))
    expected = inverse_power / inverse_power.sum(axis=0, keepdims=True)

    np.testing.assert_allclose(memberships, expected, rtol=1e-6, atol=1e-6)


def test_sparse_models_pass_fit_intercept_false_to_every_ridge_call(monkeypatch):
    """TSK design matrices already contain rule-level intercept columns."""
    calls = []

    class SpyRidge:
        def __init__(self, *args, **kwargs):
            calls.append(kwargs)

        def fit(self, X, y):
            self.coef_ = np.zeros(X.shape[1])
            return self

    monkeypatch.setattr(tsk_core, "Ridge", SpyRidge)
    X = np.array(
        [[-2.1], [-1.4], [-0.8], [-0.2], [0.3],
         [0.9], [1.6], [2.4], [3.0], [3.8]],
        dtype=float,
    )
    y = 1.0 + 0.2 * X[:, 0]

    models = [
        tsk_core.TSK_SpikeSlab_Fast(k=2),
        tsk_core.TSK_SpikeSlab_Gibbs(k=2, n_burn=0, n_samples=1),
        tsk_core.TSK_SSVS_Gibbs(k=2, n_burn=0, n_samples=1),
    ]
    for model in models:
        model.fit(X, y)

    assert calls
    assert all(call.get("fit_intercept") is False for call in calls)


def test_bic_pips_remain_finite_under_extreme_prior_odds():
    X = np.linspace(-2.0, 2.0, 30).reshape(-1, 1)
    y = 3.0 + 5.0 * X[:, 0]
    model = tsk_core.TSK_SpikeSlab_Fast(
        k=2, pi=1.0 - 1e-12, tau2=2.0
    ).fit(X, y)

    assert np.isfinite(model.pip_).all()


class _DeterministicRng:
    """Force one active block and expose the inverse-gamma scale argument."""

    def __init__(self):
        self.gamma_calls = []

    def rand(self):
        return 0.0

    def standard_normal(self, size):
        return np.zeros(size)

    def gamma(self, shape, scale):
        self.gamma_calls.append((shape, scale))
        return 1.0


def _patch_one_block_gibbs(monkeypatch, rng):
    class ZeroRidge:
        def __init__(self, *args, **kwargs):
            pass

        def fit(self, X, y):
            self.coef_ = np.zeros(X.shape[1])
            return self

    monkeypatch.setattr(tsk_core, "Ridge", ZeroRidge)
    monkeypatch.setattr(tsk_core.np.random, "RandomState", lambda seed: rng)
    monkeypatch.setattr(
        tsk_core,
        "fcm",
        lambda X, k: (
            np.zeros((k, X.shape[1])),
            np.zeros(len(X), dtype=int),
            np.ones((k, len(X))) / k,
        ),
    )
    monkeypatch.setattr(
        tsk_core,
        "gaussian_membership_fit",
        lambda X, centers, labels, k: (
            np.ones((len(X), X.shape[1], k)),
            np.ones((k, X.shape[1])),
        ),
    )


def test_gibbs_block_covariance_matches_scaled_conjugate_prior(monkeypatch):
    """The Gibbs block conditional must use the same scaled prior as Bayes."""
    rng = _DeterministicRng()
    _patch_one_block_gibbs(monkeypatch, rng)
    captured_covariances = []
    original_cholesky = tsk_core.np.linalg.cholesky

    def capture_cholesky(matrix):
        captured_covariances.append(matrix.copy())
        return original_cholesky(matrix)

    monkeypatch.setattr(tsk_core.np.linalg, "cholesky", capture_cholesky)

    X = np.array([[-1.0], [-0.2], [0.4], [1.2]], dtype=float)
    y = np.array([2.0, 2.4, 2.8, 3.6], dtype=float)
    tau2 = 2.0
    tsk_core.TSK_SpikeSlab_Gibbs(
        k=1, tau2=tau2, n_burn=0, n_samples=1
    ).fit(X, y)

    assert len(captured_covariances) == 1
    Phi = np.column_stack([np.ones(len(X)), X])
    sigma2_initial = np.var(y)
    expected = sigma2_initial * np.linalg.solve(
        Phi.T @ Phi + np.eye(Phi.shape[1]) / tau2,
        np.eye(Phi.shape[1]),
    )
    np.testing.assert_allclose(
        captured_covariances[0], expected, rtol=1e-7, atol=1e-9
    )


def test_gibbs_sigma2_conditional_includes_beta_prior_quadratic(monkeypatch):
    """The conjugate sigma² update must include the active β prior term."""
    rng = _DeterministicRng()
    _patch_one_block_gibbs(monkeypatch, rng)

    X = np.array([[-1.0], [-0.2], [0.4], [1.2]], dtype=float)
    y = np.array([2.0, 2.4, 2.8, 3.6], dtype=float)
    tau2 = 2.0
    model = tsk_core.TSK_SpikeSlab_Gibbs(
        k=1, tau2=tau2, n_burn=0, n_samples=1
    ).fit(X, y)

    assert len(rng.gamma_calls) == 1
    beta = model.beta_samples_[0]
    Phi = np.column_stack([np.ones(len(X)), X])
    residual = y - Phi @ beta
    expected_b_post = 0.01 + 0.5 * (
        residual @ residual + beta @ beta / tau2
    )
    observed_shape = rng.gamma_calls[0][0]
    assert observed_shape == pytest.approx(0.01 + (len(y) + len(beta)) / 2)
    observed_scale = rng.gamma_calls[0][1]
    assert observed_scale == pytest.approx(1.0 / expected_b_post)


def test_synthetic_marginal_likelihood_matches_scaled_prior():
    """Enumeration must use the same scaled prior as the Gibbs sampler."""
    import synthetic_gamma_verify

    y = np.array([0.4, -0.2, 1.1, 0.7], dtype=float)
    Phi = np.array(
        [[1.0, -1.0], [1.0, -0.2], [1.0, 0.4], [1.0, 1.2]],
        dtype=float,
    )
    sigma2 = 0.7
    tau2 = 2.0
    actual = synthetic_gamma_verify.exact_marginal_logp(
        y, Phi, sigma2, tau2=tau2
    )

    covariance = sigma2 * (
        np.eye(len(y)) + tau2 * Phi @ Phi.T
    )
    sign, logdet = np.linalg.slogdet(covariance)
    expected = -0.5 * (
        len(y) * np.log(2.0 * np.pi)
        + logdet
        + y @ np.linalg.solve(covariance, y)
    )

    assert sign > 0
    assert actual == pytest.approx(expected, rel=1e-10, abs=1e-10)


def test_conjugate_predictive_bounds_are_student_t_quantiles(monkeypatch):
    """The dense conjugate model must return posterior-predictive quantiles."""
    monkeypatch.setattr(
        tsk_core,
        "fcm",
        lambda X, k: (
            np.zeros((k, X.shape[1])),
            np.zeros(len(X), dtype=int),
            np.ones((k, len(X))) / k,
        ),
    )
    monkeypatch.setattr(
        tsk_core,
        "gaussian_membership_fit",
        lambda X, centers, labels, k: (
            np.ones((len(X), X.shape[1], k)),
            np.ones((k, X.shape[1])),
        ),
    )

    X = np.array([[-1.0], [-0.2], [0.4], [1.2]], dtype=float)
    y = np.array([2.0, 2.4, 2.8, 3.6], dtype=float)
    model = tsk_core.TSK_Bayesian(k=1, tau2=2.0).fit(X, y)
    mean, lower, upper = model.predict(np.array([[0.3]], dtype=float))

    from scipy.stats import t as student_t

    phi = np.array([[1.0, 0.3]])
    factor = 1.0 + phi @ model.cov_post_ @ phi.T
    scale = np.sqrt(model.b_n_ / model.a_n_ * factor[0, 0])
    expected_lower = student_t.ppf(
        0.025, df=2.0 * model.a_n_, loc=mean[0], scale=scale
    )
    expected_upper = student_t.ppf(
        0.975, df=2.0 * model.a_n_, loc=mean[0], scale=scale
    )

    assert lower[0] == pytest.approx(expected_lower, rel=1e-10, abs=1e-10)
    assert upper[0] == pytest.approx(expected_upper, rel=1e-10, abs=1e-10)


def test_ablation_variants_use_independent_metric_containers(monkeypatch, tmp_path):
    """BIC-threshold and Gibbs-threshold rows must not share one accumulator."""
    import ablation_isolate

    X = np.arange(6, dtype=float).reshape(-1, 1)
    y = np.arange(6, dtype=float)
    monkeypatch.setattr(
        ablation_isolate, "load_energy", lambda: (X, y, y)
    )
    monkeypatch.setattr(
        ablation_isolate,
        "get_splits",
        lambda values, n_splits: [
            (np.array([0, 1, 2, 3]), np.array([4, 5]))
        ],
    )
    monkeypatch.setattr(ablation_isolate, "R", 1)
    monkeypatch.setattr(ablation_isolate, "OUTPUT_DIR", str(tmp_path))

    def fixed_phi(Xtr, Xq, R):
        return np.column_stack(
            [np.ones(len(Xq)), np.arange(len(Xq), dtype=float)]
        )

    monkeypatch.setattr(ablation_isolate, "phi_fit", fixed_phi)

    def fake_metrics(y_true, y_pred, y_lower=None, y_upper=None):
        marker = float(np.mean(y_pred))
        return {"R2": marker, "PICP": marker, "MPIW": marker}

    monkeypatch.setattr(ablation_isolate, "compute_metrics", fake_metrics)

    def fake_threshold(Phi_tr, Phi_te, ytr, yte, active, tau2=None):
        marker = 2.0 if not bool(active[0]) else 3.0
        return np.full(len(yte), marker), np.ones(len(yte))

    monkeypatch.setattr(ablation_isolate, "threshold_laplace", fake_threshold)

    class FakeFast:
        def __init__(self, *args, **kwargs):
            pass

        def fit(self, Xtr, ytr):
            self.pip_ = np.array([0.0])
            return self

        def predict(self, Xq):
            n = len(Xq)
            return np.full(n, 4.0), np.zeros(n), np.ones(n)

    class FakeGibbs:
        def __init__(self, *args, **kwargs):
            pass

        def fit(self, Xtr, ytr):
            self.pip_ = np.array([1.0])
            return self

    monkeypatch.setattr(ablation_isolate, "TSK_SpikeSlab_Fast", FakeFast)
    monkeypatch.setattr(ablation_isolate, "TSK_SpikeSlab_Gibbs", FakeGibbs)

    ablation_isolate.run()
    result = json.loads(
        (tmp_path / "ablation_isolate_v2.json").read_text(encoding="utf-8")
    )

    assert result["BIC-PIP-threshold-Laplace"]["R2"] == pytest.approx(2.0)
    assert result["Gibbs-PIP-threshold-Laplace"]["R2"] == pytest.approx(3.0)


def test_spike_slab_covariance_matches_stable_scaled_posterior(monkeypatch):
    """The Laplace/reference covariance must use the intended posterior form."""
    captured = {}
    original_phi = tsk_core.tsk_phi

    def capture_phi(weights, X):
        result = original_phi(weights, X)
        captured["Phi"] = result[0].copy()
        return result

    monkeypatch.setattr(tsk_core, "tsk_phi", capture_phi)
    X = np.linspace(-2.0, 2.0, 30).reshape(-1, 1)
    y = 3.0 + 5.0 * X[:, 0]
    tau2 = 2.0
    model = tsk_core.TSK_SpikeSlab_Fast(
        k=2, pi=1.0 - 1e-12, tau2=tau2
    ).fit(X, y)

    assert np.all(model.active_)
    Phi = captured["Phi"]
    expected = model.sigma2_ * np.linalg.solve(
        Phi.T @ Phi + np.eye(Phi.shape[1]) / tau2,
        np.eye(Phi.shape[1]),
    )
    np.testing.assert_allclose(
        model.cov_beta_, expected, rtol=1e-7, atol=1e-10
    )


def test_tsk_weights_remain_distinct_when_linear_products_underflow():
    """Firing-strength normalization must operate in log space."""
    mu = np.empty((1, 200, 2), dtype=float)
    mu[:, :, 0] = 1e-3
    mu[:, :, 1] = 2e-3

    weights = tsk_core.tsk_weights(mu)

    assert weights[0, 1] > 1.0 - 1e-12
    assert weights[0, 0] < 1e-12


def test_bma_interval_uses_direct_posterior_predictive_quantiles(monkeypatch):
    """Separated mixture components must not be collapsed to a Gaussian CI."""
    model = tsk_core.TSK_SpikeSlab_Gibbs(k=1)
    model.ctr_ = np.empty((1, 0))
    model.spreads_ = np.empty((1, 0))
    model.beta_samples_ = np.array([[0.0], [10.0]])
    model.sigma2_samples_ = np.array([0.01, 0.01])

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

    mean, lower, upper = model.predict(np.zeros((1, 0)))

    assert mean[0] == pytest.approx(5.0)
    assert -0.5 < lower[0] < 0.5
    assert 9.5 < upper[0] < 10.5
