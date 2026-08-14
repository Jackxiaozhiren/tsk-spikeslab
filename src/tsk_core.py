#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrected, reusable TSK fuzzy-system core for the spike-and-slab refactor.

Fixes relative to the rejected manuscript's `experiment.py`:

1. **Membership-spread bug** — fuzzy-set spreads are now fixed at training time
   (from each cluster's training points) and *reused* at prediction. The old
   `predict()` recomputed spreads from test data with `labels=zeros`, silently
   corrupting every TSK baseline.

2. **True fuzzy c-means** — antecedent centers now come from Bezdek's FCM
   (matching the manuscript's claim), not sklearn KMeans.

3. **Two sparse Bayesian estimators** replacing the failed BIC + hard
   threshold + Laplace approximation, both with Gibbs sampling + BMA:
   - `TSK_SpikeSlab_Gibbs` — *rule-level* spike-and-slab (block Gibbs + BMA).
   - `TSK_SSVS_Gibbs`   — *coefficient-level* spike-and-slab (SSVS Gibbs + BMA).

   Note on the building-energy domain (d=8): sparsity gives *no free lunch* —
   rule-level sparsity does not activate (all PIP~1) and coefficient-level SSVS
   matches (not beats) the dense baseline under FCM. These are reported as a
   boundary characterization, not a selling point.

All samplers predict via Bayesian Model Averaging (BMA): the predictive
distribution is a Gaussian mixture over posterior draws, so total variance =
mean(sigma^2) + Var_t(phi* beta^(t)) (law of total variance). This avoids both
hard-discarding rules (accuracy collapse) and Laplace-covariance collapse
(interval undercoverage).
"""

import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score

SEED = 42


# ============================================================
# DATA
# ============================================================
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results", "raw")


def _load_cached(name):
    path = os.path.join(DATA_DIR, name + ".npz")
    if os.path.exists(path):
        d = np.load(path)
        return d
    return None


def load_energy():
    d = _load_cached("energy")
    if d is not None:
        return d["X"], d["y_heat"], d["y_cool"]
    from ucimlrepo import fetch_ucirepo
    e = fetch_ucirepo(id=242)
    X = e.data.features.values.astype(float)
    y_heat = e.data.targets.iloc[:, 0].values.astype(float)
    y_cool = e.data.targets.iloc[:, 1].values.astype(float)
    return X, y_heat, y_cool


def load_concrete():
    d = _load_cached("concrete")
    if d is not None:
        return d["X"], d["y"]
    from ucimlrepo import fetch_ucirepo
    c = fetch_ucirepo(id=165)
    X = c.data.features.values.astype(float)
    y = c.data.targets.iloc[:, 0].values.astype(float)
    return X, y


def load_facebook():
    """UCI Facebook metrics (id=368). Honest description: 500 rows; the
    categorical 'Type' column is one-hot encoded, giving 21 continuous features.
    Target = Total Interactions."""
    d = _load_cached("facebook")
    if d is not None:
        return d["X"], d["y"]
    import pandas as pd
    from ucimlrepo import fetch_ucirepo
    fb = fetch_ucirepo(id=368)
    X = fb.data.features.copy()
    y = fb.data.targets.iloc[:, 0].values.astype(float)
    cat_cols = X.select_dtypes(include=["object"]).columns.tolist()
    X = pd.get_dummies(X, columns=cat_cols, drop_first=False)
    X = X.values.astype(float)
    return X, y


def append_noise_features(X, n_noise, seed=7):
    """Append standard-normal noise columns (for the irrelevant-feature regime)."""
    rng = np.random.RandomState(seed)
    return np.column_stack([X, rng.randn(X.shape[0], n_noise)])


# ============================================================
# TSK CORE
# ============================================================
def fcm(X, c, m=2.0, n_init=10, max_iter=100, tol=1e-5, seed=SEED):
    """Bezdek fuzzy c-means. Returns (centers, hard_labels, membership_U)."""
    n, d = X.shape
    rng = np.random.RandomState(seed)
    best_cost, best = np.inf, None
    for _ in range(n_init):
        U = rng.rand(c, n)
        U /= U.sum(axis=0, keepdims=True)
        for _ in range(max_iter):
            Um = U ** m
            centers = (Um @ X) / Um.sum(axis=1, keepdims=True)
            dist = np.zeros((c, n))
            for j in range(c):
                diff = X - centers[j]
                dist[j] = np.einsum("ij,ij->i", diff, diff)
            dist = np.maximum(dist, 1e-16)
            inv = dist ** (-2.0 / (m - 1.0))
            U_new = inv / inv.sum(axis=0, keepdims=True)
            if np.abs(U_new - U).max() < tol:
                U = U_new
                break
            U = U_new
        cost = float(np.sum((U ** m) * dist))
        if np.isfinite(cost) and cost < best_cost:
            best_cost = cost
            best = (centers.copy(), U.copy())
    if best is None:
        raise ValueError("FCM failed to converge (degenerate or NaN-containing input)")
    centers, U = best
    labels = U.argmax(axis=0)
    return centers, labels, U


def gaussian_membership_fit(X, centers, labels, k, s=1.5):
    """Gaussian membership + per-cluster spreads FIXED on training data."""
    n, d = X.shape
    mu = np.zeros((n, d, k))
    spreads = np.zeros((k, d))
    for j in range(k):
        pts = X[labels == j]
        sd = np.std(pts, axis=0) if len(pts) > 1 else np.ones(d)
        spreads[j] = sd * s + 0.01
        for i in range(d):
            mu[:, i, j] = np.exp(-(X[:, i] - centers[j, i]) ** 2
                                  / (2 * spreads[j, i] ** 2 + 1e-8))
    return mu, spreads


def gaussian_membership_predict(X, centers, spreads, k):
    """Membership for new points using the FIXED training spreads."""
    n, d = X.shape
    mu = np.zeros((n, d, k))
    for j in range(k):
        for i in range(d):
            mu[:, i, j] = np.exp(-(X[:, i] - centers[j, i]) ** 2
                                  / (2 * spreads[j, i] ** 2 + 1e-8))
    return mu


def tsk_weights(mu):
    f = np.prod(mu, axis=1) + 1e-12
    return f / f.sum(axis=1, keepdims=True)


def tsk_phi(W, X):
    n, k = W.shape
    d = X.shape[1]
    Xa = np.column_stack([np.ones(n), X])
    Phi = np.zeros((n, k * (d + 1)))
    for j in range(k):
        Phi[:, j * (d + 1):(j + 1) * (d + 1)] = Xa * W[:, j:j + 1]
    return Phi, (d + 1)


def get_splits(y, n_splits, seed=SEED):
    n = len(y)
    splits = []
    for s in range(n_splits):
        rng = np.random.RandomState(seed + s)
        n_test = max(int(n * 0.2), 5)
        test_idx = rng.choice(n, size=n_test, replace=False)
        train_idx = np.setdiff1d(np.arange(n), test_idx)
        splits.append((train_idx, test_idx))
    return splits


def compute_metrics(y_true, y_pred, y_lower=None, y_upper=None):
    rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
    mae = float(np.mean(np.abs(y_true - y_pred)))
    r2 = float(r2_score(y_true, y_pred))
    out = {"RMSE": rmse, "MAE": mae, "R2": r2}
    if y_lower is not None and y_upper is not None:
        in_int = (y_true >= y_lower) & (y_true <= y_upper)
        out["PICP"] = float(np.mean(in_int))
        out["MPIW"] = float(np.mean(y_upper - y_lower))
    return out


# ============================================================
# BASELINE MODELS (correct membership)
# ============================================================
class TSK_LS:
    """Dense least-squares TSK."""
    def __init__(self, k=5):
        self.k = k

    def fit(self, X, y):
        self.ctr_, self.lbl_, _ = fcm(X, self.k)
        self.mu_, self.spreads_ = gaussian_membership_fit(X, self.ctr_, self.lbl_, self.k)
        Phi, _ = tsk_phi(tsk_weights(self.mu_), X)
        reg = 1e-4 * np.eye(Phi.shape[1])
        self.beta_ = np.linalg.solve(Phi.T @ Phi + reg, Phi.T @ y)
        return self

    def predict(self, X):
        mu = gaussian_membership_predict(X, self.ctr_, self.spreads_, self.k)
        Phi, _ = tsk_phi(tsk_weights(mu), X)
        return Phi @ self.beta_

    @property
    def active_rules(self):
        return self.k


class TSK_Bayesian:
    """Non-sparse conjugate normal-inverse-gamma TSK (closed form)."""
    def __init__(self, k=5, tau2=1e3):
        self.k, self.tau2 = k, tau2

    def fit(self, X, y):
        n = len(y)
        R, pp, P = self.k, X.shape[1] + 1, self.k * (X.shape[1] + 1)
        self.ctr_, self.lbl_, _ = fcm(X, R)
        self.mu_, self.spreads_ = gaussian_membership_fit(X, self.ctr_, self.lbl_, R)
        Phi, _ = tsk_phi(tsk_weights(self.mu_), X)
        prec_prior = np.eye(P) / self.tau2
        prec_post = Phi.T @ Phi + prec_prior
        cov_post = np.linalg.inv(prec_post)
        mean_post = cov_post @ (Phi.T @ y)
        resid = y - Phi @ mean_post
        a0, b0 = 0.01, 0.01
        a_n = a0 + n / 2
        b_n = b0 + 0.5 * (resid @ resid + mean_post @ prec_prior @ mean_post)
        self.sigma2_ = b_n / max(a_n - 1, 1e-6)
        self.beta_ = mean_post
        self.cov_beta_ = cov_post * self.sigma2_
        return self

    def predict(self, X):
        mu = gaussian_membership_predict(X, self.ctr_, self.spreads_, self.k)
        Phi, _ = tsk_phi(tsk_weights(mu), X)
        mean_pred = Phi @ self.beta_
        var = np.array([self.sigma2_ + Phi[i] @ self.cov_beta_ @ Phi[i]
                        for i in range(len(X))])
        std = np.sqrt(np.maximum(var, 1e-8))
        return mean_pred, mean_pred - 1.96 * std, mean_pred + 1.96 * std

    @property
    def active_rules(self):
        return self.k


class TSK_SpikeSlab_Fast:
    """The rejected paper's method (BIC + hard threshold + Laplace), kept for
    continuity/contrast. Membership bug already fixed so the comparison is fair."""
    def __init__(self, k=5, pi=0.5, tau2=1e3):
        self.k, self.pi, self.tau2 = k, pi, tau2

    def fit(self, X, y):
        n = len(y)
        R, pp = self.k, X.shape[1] + 1
        self.ctr_, self.lbl_, _ = fcm(X, R)
        self.mu_, self.spreads_ = gaussian_membership_fit(X, self.ctr_, self.lbl_, R)
        Phi, _ = tsk_phi(tsk_weights(self.mu_), X)
        beta_hat = Ridge(alpha=0.01).fit(Phi, y).coef_
        self.sigma2_ = max(np.var(y - Phi @ beta_hat), 1e-4)
        self.pip_ = np.zeros(R)
        for j in range(R):
            idx_j = slice(j * pp, (j + 1) * pp)
            Phi_j = Phi[:, idx_j]
            others = [i for i in range(R * pp) if i < j * pp or i >= (j + 1) * pp]
            Phi_o = Phi[:, others]
            resid = y - Phi_o @ beta_hat[others]
            bj = np.linalg.solve(Phi_j.T @ Phi_j + 1e-4 * np.eye(pp), Phi_j.T @ resid)
            rss0 = resid @ resid + 1e-12
            rss1 = (resid - Phi_j @ bj) @ (resid - Phi_j @ bj) + 1e-12
            log_bf = -0.5 * ((n * np.log(rss1 / n) + pp * np.log(n)) - n * np.log(rss0 / n))
            po = (self.pi / (1 - self.pi)) * np.exp(log_bf)
            self.pip_[j] = np.clip(po / (1 + po), 0.001, 0.999)
        self.active_ = self.pip_ > 0.5
        idx = [i for j in range(R) if self.active_[j] for i in range(j * pp, (j + 1) * pp)]
        if not idx:
            idx, self.active_ = list(range(R * pp)), np.ones(R, bool)
        self.beta_ = np.zeros(R * pp)
        self.beta_[idx] = Ridge(alpha=0.01).fit(Phi[:, idx], y).coef_
        prec = np.zeros(R * pp)
        for j in range(R):
            prec[j * pp:(j + 1) * pp] = 1.0 / self.tau2 if self.active_[j] else 1e10
        try:
            self.cov_beta_ = self.sigma2_ * np.linalg.inv(Phi.T @ Phi / self.sigma2_ + np.diag(prec))
        except np.linalg.LinAlgError:
            self.cov_beta_ = self.sigma2_ * np.linalg.inv(Phi.T @ Phi / self.sigma2_ + 1e-6 * np.eye(R * pp))
        return self

    def predict(self, X):
        mu = gaussian_membership_predict(X, self.ctr_, self.spreads_, self.k)
        Phi, _ = tsk_phi(tsk_weights(mu), X)
        mean_pred = Phi @ self.beta_
        std = np.sqrt(np.maximum([self.sigma2_ + Phi[i] @ self.cov_beta_ @ Phi[i]
                                  for i in range(len(X))], 1e-8))
        return mean_pred, mean_pred - 1.96 * std, mean_pred + 1.96 * std

    @property
    def active_rules(self):
        return int(self.active_.sum())


# ============================================================
# PROPOSED SPARSE BAYESIAN MODELS (Gibbs + BMA)
# ============================================================
class _BMA_Mixin:
    """Shared BMA prediction: Gaussian mixture over posterior draws."""

    def _predict_bma(self, X):
        mu = gaussian_membership_predict(X, self.ctr_, self.spreads_, self.k)
        Phi, _ = tsk_phi(tsk_weights(mu), X)
        means = Phi @ self.beta_samples_.T          # n_test x T
        mean_pred = means.mean(axis=1)
        var_model = means.var(axis=1)                # epistemic (across-model)
        total_var = self.sigma2_samples_.mean() + var_model
        std = np.sqrt(np.maximum(total_var, 1e-12))
        return mean_pred, mean_pred - 1.96 * std, mean_pred + 1.96 * std


class TSK_SpikeSlab_Gibbs(_BMA_Mixin):
    """Rule-level (block) spike-and-slab via block Gibbs + BMA."""
    def __init__(self, k=5, pi=0.5, tau2=1e3, n_burn=1000, n_samples=2000, seed=SEED):
        self.k, self.pi, self.tau2 = k, pi, tau2
        self.n_burn, self.n_samples, self.seed = n_burn, n_samples, seed

    def fit(self, X, y):
        n = len(y)
        R, pp, P = self.k, X.shape[1] + 1, self.k * (X.shape[1] + 1)
        self.ctr_, self.lbl_, _ = fcm(X, R)
        self.mu_, self.spreads_ = gaussian_membership_fit(X, self.ctr_, self.lbl_, R)
        Phi, _ = tsk_phi(tsk_weights(self.mu_), X)
        blocks = [Phi[:, j * pp:(j + 1) * pp] for j in range(R)]
        Ajs = [blocks[j].T @ blocks[j] for j in range(R)]

        beta = Ridge(alpha=0.01).fit(Phi, y).coef_.copy()
        gamma = np.ones(R)
        resid = y - Phi @ beta
        sigma2 = max(float(np.var(resid)), 1e-4)
        rng = np.random.RandomState(self.seed)

        B = np.zeros((self.n_samples, P))
        G = np.zeros((self.n_samples, R))
        S2 = np.zeros(self.n_samples)

        for it in range(self.n_burn + self.n_samples):
            for j in range(R):
                Phi_j = blocks[j]
                sl = slice(j * pp, (j + 1) * pp)
                r = resid + Phi_j @ beta[sl]          # residual excluding block j
                a = self.tau2 / sigma2
                S = np.eye(pp) + a * Ajs[j]
                _, logdetS = np.linalg.slogdet(S)
                z = Phi_j.T @ r
                log_bf = -0.5 * logdetS + 0.5 * (a / sigma2) * (z @ np.linalg.solve(S, z))
                lo = np.log(self.pi / (1 - self.pi)) + log_bf
                gamma[j] = 1.0 if rng.rand() < 1.0 / (1.0 + np.exp(-lo)) else 0.0
                if gamma[j] == 1.0:
                    Vj = np.linalg.inv(Ajs[j] / sigma2 + np.eye(pp) / self.tau2 + 1e-10 * np.eye(pp))
                    Vj = 0.5 * (Vj + Vj.T)
                    mj = Vj @ (Phi_j.T @ r) / sigma2
                    beta[sl] = mj + np.linalg.cholesky(Vj) @ rng.standard_normal(pp)
                else:
                    beta[sl] = 0.0
                resid = r - Phi_j @ beta[sl]
            ssr = resid @ resid
            a_post = 0.01 + n / 2
            b_post = 0.01 + 0.5 * ssr
            sigma2 = 1.0 / rng.gamma(a_post, 1.0 / b_post)
            if it >= self.n_burn:
                i = it - self.n_burn
                B[i], G[i], S2[i] = beta, gamma, sigma2

        self.beta_samples_ = B
        self.gamma_samples_ = G
        self.sigma2_samples_ = S2
        self.pip_ = G.mean(axis=0)
        self.active_ = self.pip_ > 0.5
        return self

    def predict(self, X):
        return self._predict_bma(X)

    @property
    def active_rules(self):
        return int(self.active_.sum())


class TSK_SSVS_Gibbs(_BMA_Mixin):
    """Coefficient-level stochastic-search variable selection (SSVS) + BMA.
    Each TSK consequent coefficient gets its own spike-and-slab prior, so
    irrelevant features are shrunk/pruned and BMA stays calibrated."""
    def __init__(self, k=5, pi=0.5, tau2=1.0, n_burn=1000, n_samples=1000, seed=SEED):
        self.k, self.pi, self.tau2 = k, pi, tau2
        self.n_burn, self.n_samples, self.seed = n_burn, n_samples, seed

    def fit(self, X, y):
        n = len(y)
        R, pp, P = self.k, X.shape[1] + 1, self.k * (X.shape[1] + 1)
        self.d_ = X.shape[1]
        self.ctr_, self.lbl_, _ = fcm(X, R)
        self.mu_, self.spreads_ = gaussian_membership_fit(X, self.ctr_, self.lbl_, R)
        Phi, _ = tsk_phi(tsk_weights(self.mu_), X)
        self.Phi_ = Phi
        cols2 = (Phi ** 2).sum(axis=0)              # ||phi_i||^2 per coefficient

        beta = Ridge(alpha=0.01).fit(Phi, y).coef_.copy()
        gamma = np.ones(P)
        resid = y - Phi @ beta
        sigma2 = max(float(np.var(resid)), 1e-4)
        rng = np.random.RandomState(self.seed)

        B = np.zeros((self.n_samples, P))
        G = np.zeros((self.n_samples, P))
        S2 = np.zeros(self.n_samples)

        for it in range(self.n_burn + self.n_samples):
            for i in range(P):
                phi_i = Phi[:, i]
                r = resid + phi_i * beta[i]          # residual excluding coeff i
                a = self.tau2 / sigma2
                denom = 1.0 + a * cols2[i]
                logdet = np.log(denom)
                z = float(phi_i @ r)
                log_bf = -0.5 * logdet + 0.5 * (a / sigma2) * z * z / denom
                lo = np.log(self.pi / (1 - self.pi)) + log_bf
                gamma[i] = 1.0 if rng.rand() < 1.0 / (1.0 + np.exp(-lo)) else 0.0
                if gamma[i] == 1.0:
                    v = 1.0 / (cols2[i] / sigma2 + 1.0 / self.tau2)
                    m = v * z / sigma2
                    beta[i] = m + np.sqrt(v) * rng.standard_normal()
                else:
                    beta[i] = 0.0
                resid = r - phi_i * beta[i]
            ssr = resid @ resid
            a_post = 0.01 + n / 2
            b_post = 0.01 + 0.5 * ssr
            sigma2 = 1.0 / rng.gamma(a_post, 1.0 / b_post)
            if it >= self.n_burn:
                i = it - self.n_burn
                B[i], G[i], S2[i] = beta, gamma, sigma2

        self.beta_samples_ = B
        self.gamma_samples_ = G
        self.sigma2_samples_ = S2
        self.pip_ = G.mean(axis=0)                   # per-coefficient PIP
        return self

    def predict(self, X):
        return self._predict_bma(X)

    def feature_pips(self):
        """Per-feature relevance = max coefficient PIP across rules (feature f
        is 'active' if any rule uses it). Excludes intercept column."""
        R, pp = self.k, self.d_ + 1
        pips = self.pip_.reshape(R, pp)
        return pips[:, 1:].max(axis=0)

    @property
    def active_rules(self):
        R, pp = self.k, self.d_ + 1
        pips = self.pip_.reshape(R, pp)
        # a rule is "active" if its intercept (or any coeff) has PIP > 0.5
        return int(np.sum(pips.max(axis=1) > 0.5))
