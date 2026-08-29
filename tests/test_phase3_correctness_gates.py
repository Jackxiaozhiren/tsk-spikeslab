"""Small, independent correctness gates before any formal experiment rerun."""

import numpy as np
import pytest

import tsk_core


def _reference_fcm(X, c, m, max_iter, tol, seed):
    rng = np.random.RandomState(seed)
    memberships = rng.rand(c, len(X))
    memberships /= memberships.sum(axis=0, keepdims=True)
    for _ in range(max_iter):
        weighted = memberships ** m
        centers = (weighted @ X) / weighted.sum(axis=1, keepdims=True)
        squared = np.stack(
            [np.sum((X - center) ** 2, axis=1) for center in centers]
        )
        inverse_power = np.maximum(squared, 1e-16) ** (-1.0 / (m - 1.0))
        updated = inverse_power / inverse_power.sum(axis=0, keepdims=True)
        if np.abs(updated - memberships).max() < tol:
            memberships = updated
            break
        memberships = updated
    return centers, memberships


def test_fcm_matches_independent_reference_implementation():
    X = np.array(
        [[-1.2, 0.2], [-0.4, 1.1], [0.3, -0.7],
         [1.2, 0.6], [1.8, -1.0], [2.4, 0.1]],
        dtype=float,
    )
    kwargs = dict(c=3, m=2.0, max_iter=400, tol=1e-10, seed=19)
    expected_centers, expected_memberships = _reference_fcm(
        X, **kwargs
    )
    centers, _, memberships = tsk_core.fcm(
        X, n_init=1, **kwargs
    )

    np.testing.assert_allclose(centers, expected_centers, rtol=1e-7, atol=1e-9)
    np.testing.assert_allclose(
        memberships, expected_memberships, rtol=1e-7, atol=1e-9
    )


def test_forced_active_gibbs_matches_analytic_predictive_moments(monkeypatch):
    import gibbs_verify

    Xtr = np.arange(6, dtype=float).reshape(-1, 1)
    Xte = np.array([[0.2], [1.5], [2.9]], dtype=float)
    y = np.array([1.0, 1.7, 2.5, 3.4, 4.0, 5.2], dtype=float)
    Phi_tr = np.column_stack([np.ones(len(Xtr)), Xtr[:, 0]])
    Phi_te = np.column_stack([np.ones(len(Xte)), Xte[:, 0]])

    monkeypatch.setattr(
        gibbs_verify,
        "_phi",
        lambda X_fit, X_query, R: (
            Phi_tr if len(X_query) == len(Xtr) else Phi_te
        ),
    )

    tau2 = 1.5
    mean, variance = gibbs_verify.gibbs_forced_active(
        Xtr, y, Xte, R=1, tau2=tau2,
        n_burn=300, n_samples=4000, seed=17,
    )

    precision = Phi_tr.T @ Phi_tr + np.eye(2) / tau2
    covariance = np.linalg.solve(precision, np.eye(2))
    posterior_mean = covariance @ Phi_tr.T @ y
    residual = y - Phi_tr @ posterior_mean
    a_n = tsk_core.SIGMA2_A0 + len(y) / 2
    b_n = tsk_core.SIGMA2_B0 + 0.5 * (
        residual @ residual + posterior_mean @ posterior_mean / tau2
    )
    expected_mean = Phi_te @ posterior_mean
    expected_variance = (b_n / (a_n - 1.0)) * (
        1.0 + np.einsum("ij,jk,ik->i", Phi_te, covariance, Phi_te)
    )

    np.testing.assert_allclose(mean, expected_mean, rtol=0.05, atol=0.05)
    np.testing.assert_allclose(
        variance, expected_variance, rtol=0.10, atol=0.05
    )


def _exact_synthetic_components(Phi, pp, y, weights, active_sets, tau2):
    from scipy.stats import t as student_t

    a_n = tsk_core.SIGMA2_A0 + len(y) / 2
    component_means = []
    component_scales = []
    component_variances = []
    for active in active_sets:
        if active:
            indices = [
                j * pp + c for j in active for c in range(pp)
            ]
            Phi_g = Phi[:, indices]
            precision = Phi_g.T @ Phi_g + np.eye(len(indices)) / tau2
            covariance = np.linalg.solve(
                precision, np.eye(len(indices))
            )
            posterior_mean = covariance @ Phi_g.T @ y
            residual = y - Phi_g @ posterior_mean
            b_n = tsk_core.SIGMA2_B0 + 0.5 * (
                residual @ residual + posterior_mean @ posterior_mean / tau2
            )
            mean = Phi_g @ posterior_mean
            scale = np.sqrt(
                (b_n / a_n)
                * (1.0 + np.einsum(
                    "ij,jk,ik->i", Phi_g, covariance, Phi_g
                ))
            )
        else:
            b_n = tsk_core.SIGMA2_B0 + 0.5 * (y @ y)
            mean = np.zeros(len(y))
            scale = np.sqrt(np.ones(len(y)) * b_n / a_n)
        df = 2.0 * a_n
        component_means.append(mean)
        component_scales.append(scale)
        component_variances.append(scale ** 2 * df / (df - 2.0))

    means = np.asarray(component_means)
    scales = np.asarray(component_scales)
    variances = np.asarray(component_variances)
    mixture_mean = np.sum(weights[:, None] * means, axis=0)
    mixture_variance = np.sum(
        weights[:, None] * (variances + means ** 2), axis=0
    ) - mixture_mean ** 2

    def mixture_quantile(level):
        left = np.min(means - 12.0 * scales, axis=0)
        right = np.max(means + 12.0 * scales, axis=0)
        for _ in range(70):
            mid = 0.5 * (left + right)
            cdf = np.sum(
                weights[:, None]
                * student_t.cdf(
                    (mid[None, :] - means) / scales, df=df
                ),
                axis=0,
            )
            move_right = cdf < level
            left = np.where(move_right, mid, left)
            right = np.where(move_right, right, mid)
        return 0.5 * (left + right)

    return (
        mixture_mean,
        mixture_variance,
        mixture_quantile(0.025),
        mixture_quantile(0.975),
    )


def test_small_r_synthetic_gate_matches_configuration_and_predictive_reference(
    monkeypatch,
):
    import synthetic_gamma_verify as synthetic

    monkeypatch.setattr(synthetic, "R", 3)
    monkeypatch.setattr(synthetic, "D", 2)
    monkeypatch.setattr(synthetic, "N", 120)
    monkeypatch.setattr(synthetic, "TRUE_ACTIVE", {0, 2})
    monkeypatch.setattr(synthetic, "SIGMA2_TRUE", 0.5)
    monkeypatch.setattr(synthetic, "PRIOR_PI", 0.5)
    monkeypatch.setattr(synthetic, "TAU2", 2.0)
    monkeypatch.setattr(synthetic, "SEED", 13)

    X, y, Phi, pp, _, _ = synthetic.build_synthetic()
    pip_exact, weights, active_sets = synthetic.exact_inclusion_probs(
        Phi, pp, y, tau2=synthetic.TAU2, pi=synthetic.PRIOR_PI
    )
    model = tsk_core.TSK_SpikeSlab_Gibbs(
        k=synthetic.R, pi=synthetic.PRIOR_PI, tau2=synthetic.TAU2,
        n_burn=500, n_samples=5000, seed=synthetic.SEED,
    ).fit(X, y)
    mean, lower, upper = model.predict(X[:5])

    exact_mean, exact_variance, exact_lower, exact_upper = (
        _exact_synthetic_components(
            Phi, pp, y, weights, active_sets, synthetic.TAU2
        )
    )
    sampled_prediction_means = Phi @ model.beta_samples_.T
    sampled_variance = (
        model.sigma2_samples_.mean()
        + sampled_prediction_means.var(axis=1)
    )

    np.testing.assert_allclose(model.pip_, pip_exact, atol=0.08)
    np.testing.assert_allclose(mean, exact_mean[:5], atol=0.15)
    np.testing.assert_allclose(
        sampled_variance, exact_variance, rtol=0.12, atol=0.05
    )
    np.testing.assert_allclose(lower, exact_lower[:5], atol=0.20)
    np.testing.assert_allclose(upper, exact_upper[:5], atol=0.20)


def test_intermediate_pip_scenario_explores_both_indicator_states():
    X = np.linspace(-1.0, 1.0, 20).reshape(-1, 1)
    y = 0.2 * X[:, 0] + np.random.RandomState(1).normal(
        0.0, 1.0, len(X)
    )
    model = tsk_core.TSK_SpikeSlab_Gibbs(
        k=2, pi=0.5, tau2=0.3,
        n_burn=400, n_samples=2000, seed=17,
    ).fit(X, y)

    assert np.any((model.pip_ > 0.15) & (model.pip_ < 0.85))
    assert all(
        len(np.unique(model.gamma_samples_[:, j])) == 2
        for j in range(model.gamma_samples_.shape[1])
    )
