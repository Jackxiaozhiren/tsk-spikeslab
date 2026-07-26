#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sparse Bayesian TSK Fuzzy System — FINAL Experiment Pipeline
Approach: Fast analytical approximations for Bayesian methods,
          full cross-validation for frequentist methods,
          consistent random seeds for reproducibility.
"""

import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LassoCV, RidgeCV, Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.cluster import KMeans
from sklearn.model_selection import KFold
from sklearn.metrics import r2_score
from scipy.linalg import solve
from scipy.stats import wilcoxon, friedmanchisquare, rankdata, norm, chi2
import warnings, os, json, time
warnings.filterwarnings('ignore')

SEED = 42
np.random.seed(SEED)
DATA_DIR = "/Users/jackson/ASC论文/results/raw"
os.makedirs(DATA_DIR, exist_ok=True)

# ============================================================
# DATA
# ============================================================
print("=" * 60)
print("Loading datasets...")
from ucimlrepo import fetch_ucirepo

energy = fetch_ucirepo(id=242)
X_e = energy.data.features.values.astype(float)
y_heat = energy.data.targets.iloc[:, 0].values.astype(float)
y_cool = energy.data.targets.iloc[:, 1].values.astype(float)

conc = fetch_ucirepo(id=165)
X_c = conc.data.features.values.astype(float)
y_conc = conc.data.targets.iloc[:, 0].values.astype(float)

datasets = {
    "Energy-Heating": (X_e, y_heat),
    "Energy-Cooling": (X_e, y_cool),
    "Concrete":       (X_c, y_conc),
}

for nm, (X, y) in datasets.items():
    print(f"  {nm}: n={X.shape[0]}, d={X.shape[1]}, y∈[{y.min():.2f}, {y.max():.2f}]")

# ============================================================
# TSK CORE (same as before)
# ============================================================
def cluster_centers(X, k):
    km = KMeans(n_clusters=k, n_init=10, random_state=SEED)
    km.fit(X)
    return km.cluster_centers_, km.labels_

def gaussian_membership(X, centers, labels, k, s=1.5):
    n, d = X.shape
    mu = np.zeros((n, d, k))
    spreads = np.zeros((k, d))
    for j in range(k):
        pts = X[labels == j]
        spreads[j] = np.where(len(pts) > 1, np.std(pts, axis=0) * s + 0.01, 1.0)
        for i in range(d):
            mu[:, i, j] = np.exp(-(X[:, i] - centers[j, i])**2 / (2 * spreads[j, i]**2 + 1e-8))
    return mu, spreads

def tsk_weights(mu):
    n, d, k = mu.shape
    f = np.prod(mu, axis=1) + 1e-12
    return f / f.sum(axis=1, keepdims=True)

def tsk_phi(W, X):
    n, k = W.shape
    d = X.shape[1]
    Xa = np.column_stack([np.ones(n), X])
    Phi = np.zeros((n, k * (d + 1)))
    for j in range(k):
        Phi[:, j*(d+1):(j+1)*(d+1)] = Xa * W[:, j:j+1]
    return Phi, (d + 1)

def calc_rmse(y, yp):
    return np.sqrt(np.mean((y - yp)**2))

def calc_mae(y, yp):
    return np.mean(np.abs(y - yp))

def get_splits(y, n_splits):
    n = len(y)
    splits = []
    for s in range(n_splits):
        rng = np.random.RandomState(SEED + s)
        n_test = max(int(n * 0.2), 5)
        test_idx = rng.choice(n, size=n_test, replace=False)
        train_idx = np.setdiff1d(np.arange(n), test_idx)
        splits.append((train_idx, test_idx))
    return splits

# ============================================================
# FAST SPIKE-AND-SLAB VIA EMPIRICAL BAYES + ANALYTICAL APPROX
# ============================================================
class TSK_SpikeSlab_Fast:
    """
    Analytical spike-and-slab approximation:
    1. Fit full Bayesian model with ridge penalty for stability
    2. Compute posterior inclusion probability via BIC difference
    3. Active rules = rules with PIP > 0.5
    4. Prediction intervals via analytical Gaussian approximation
    """
    def __init__(self, k=5, pi=0.5, tau2=1e3):
        self.k = k; self.pi = pi; self.tau2 = tau2  # tau2 = slab variance (large = diffuse)

    def fit(self, X, y):
        n, d = X.shape
        R = self.k; pp = d + 1
        self.ctr_, self.lbl_ = cluster_centers(X, R)
        self.mu_, _ = gaussian_membership(X, self.ctr_, self.lbl_, R)
        self.W_ = tsk_weights(self.mu_)
        self.Phi_, self.p_ = tsk_phi(self.W_, X)
        Phi = self.Phi_
        self.X_train_ = X

        # Step 1: Fit ridge for stable initial beta_hat
        ridge = Ridge(alpha=0.01)
        ridge.fit(Phi, y)
        beta_hat_full = ridge.coef_
        beta_blocks = beta_hat_full.reshape(R, pp)

        # Step 2: Estimate sigma^2 from residuals
        y_hat = Phi @ beta_hat_full
        self.sigma2_ = max(np.var(y - y_hat), 1e-4)

        # Step 3: Compute per-rule BIC and PIP
        # For each rule, compute the model with and without that rule
        self.pip_ = np.zeros(R)
        self.beta_selected_ = np.zeros(R * pp)

        for j in range(R):
            idx_j = slice(j*pp, (j+1)*pp)
            Phi_j = Phi[:, idx_j]

            # Model WITH rule j (full model — use all other rules as baseline)
            # The key insight: compute how much rule j improves fit
            # Use orthogonal projection to isolate rule j contribution

            # Fit with all rules EXCEPT j
            idx_others = [i for i in range(R*pp) if i < j*pp or i >= (j+1)*pp]
            Phi_others = Phi[:, idx_others]
            beta_others = beta_hat_full[idx_others]
            resid_no_j = y - Phi_others @ beta_others

            # Fit rule j on residual
            beta_j_on_resid = solve(Phi_j.T @ Phi_j + np.eye(pp)*1e-4,
                                     Phi_j.T @ resid_no_j, assume_a='pos')
            resid_with_j = resid_no_j - Phi_j @ beta_j_on_resid

            rss_no_j = np.sum(resid_no_j**2) + 1e-12
            rss_with_j = np.sum(resid_with_j**2) + 1e-12

            # BIC difference: H0 (no rule) vs H1 (rule active)
            # Lower BIC = better
            bic_no_j = n * np.log(rss_no_j / n)  # 0 parameters for this rule
            bic_with_j = n * np.log(rss_with_j / n) + pp * np.log(n)  # pp parameters

            # Bayes factor: BF = exp(-0.5 * (BIC_H1 - BIC_H0))
            log_bf = -0.5 * (bic_with_j - bic_no_j)

            # Posterior odds = prior_odds * BF
            prior_odds = self.pi / (1 - self.pi + 1e-12)
            posterior_odds = prior_odds * np.exp(log_bf)
            pip = posterior_odds / (1 + posterior_odds)

            self.pip_[j] = np.clip(pip, 0.001, 0.999)

        # Step 4: Select active rules and re-fit
        self.active_mask_ = self.pip_ > 0.5
        active_indices = []
        for j in range(R):
            if self.active_mask_[j]:
                for i in range(pp):
                    active_indices.append(j * pp + i)

        if len(active_indices) == 0:
            active_indices = list(range(R * pp))
            self.active_mask_[:] = True

        Phi_active = Phi[:, active_indices]
        # Ridge fit on active rules
        ridge_active = Ridge(alpha=0.01)
        ridge_active.fit(Phi_active, y)
        beta_active = ridge_active.coef_

        # Map back to full parameter vector
        self.beta_ = np.zeros(R * pp)
        for k_idx, full_idx in enumerate(active_indices):
            self.beta_[full_idx] = beta_active[k_idx]

        # Step 5: Posterior predictive variance (analytical approximation)
        # Var(y*|x*) ≈ sigma^2 + x*^T Cov(beta) x*
        # Use Laplace approximation: Cov(beta) ≈ sigma^2 * (Phi^T Phi + diag(prior_precision))^{-1}
        prior_prec = np.zeros(R * pp)
        for j in range(R):
            if self.active_mask_[j]:
                prior_prec[j*pp:(j+1)*pp] = 1.0 / self.tau2
            else:
                prior_prec[j*pp:(j+1)*pp] = 1e10  # effectively zero variance for spike

        prec_matrix = Phi.T @ Phi / self.sigma2_ + np.diag(prior_prec)
        try:
            self.cov_beta_ = self.sigma2_ * np.linalg.inv(prec_matrix)
        except np.linalg.LinAlgError:
            self.cov_beta_ = self.sigma2_ * np.linalg.inv(
                Phi.T @ Phi / self.sigma2_ + np.eye(R * pp) * 1e-6)

        return self

    def predict(self, X):
        mu, _ = gaussian_membership(X, self.ctr_, np.zeros(len(X), dtype=int), self.k)
        W = tsk_weights(mu)
        Phi, _ = tsk_phi(W, X)

        mean_pred = Phi @ self.beta_

        # Prediction variance: sigma^2 + x^T Cov(beta) x
        pred_var = np.zeros(len(X))
        for i in range(len(X)):
            x_i = Phi[i]
            pred_var[i] = self.sigma2_ + x_i @ self.cov_beta_ @ x_i
        pred_var = np.maximum(pred_var, 1e-8)
        pred_std = np.sqrt(pred_var)

        lower = mean_pred - 1.96 * pred_std
        upper = mean_pred + 1.96 * pred_std
        return mean_pred, lower, upper, pred_std

    @property
    def active_rules(self):
        return int(np.sum(self.active_mask_))

    @property
    def sparsity_ratio(self):
        return 1.0 - self.active_rules / self.k


class TSK_Bayesian_Fast:
    """Non-sparse Bayesian TSK — conjugate normal-inverse-gamma, closed form."""
    def __init__(self, k=5, tau2=1e3):
        self.k = k; self.tau2 = tau2

    def fit(self, X, y):
        n, d = X.shape
        R = self.k; pp = d + 1; P = R * pp
        self.ctr_, self.lbl_ = cluster_centers(X, R)
        self.mu_, _ = gaussian_membership(X, self.ctr_, self.lbl_, R)
        self.W_ = tsk_weights(self.mu_)
        self.Phi_, self.p_ = tsk_phi(self.W_, X)
        Phi = self.Phi_
        self.X_train_ = X

        # Ridge for stable initial fit
        ridge = Ridge(alpha=0.01)
        ridge.fit(Phi, y)
        self.beta_ = ridge.coef_

        # Analytical posterior
        # Prior: beta ~ N(0, tau2 * I), sigma2 ~ InvGamma(a0, b0)
        a0, b0 = 0.01, 0.01
        prec_prior = np.eye(P) / self.tau2
        prec_post = Phi.T @ Phi + prec_prior
        try:
            cov_post = np.linalg.inv(prec_post)
        except np.linalg.LinAlgError:
            cov_post = np.linalg.inv(Phi.T @ Phi + np.eye(P) * 1e-6)

        mean_post = cov_post @ (Phi.T @ y)

        # Posterior for sigma^2
        resid = y - Phi @ mean_post
        a_n = a0 + n / 2
        b_n = b0 + 0.5 * (np.sum(resid**2) + mean_post @ prec_prior @ mean_post)
        self.sigma2_ = b_n / max(a_n - 1, 1e-6)  # posterior mean

        self.beta_ = mean_post
        self.cov_beta_ = cov_post * self.sigma2_  # scale by sigma^2 for prediction
        return self

    def predict(self, X):
        mu, _ = gaussian_membership(X, self.ctr_, np.zeros(len(X), dtype=int), self.k)
        W = tsk_weights(mu)
        Phi, _ = tsk_phi(W, X)

        mean_pred = Phi @ self.beta_
        pred_var = np.zeros(len(X))
        for i in range(len(X)):
            x_i = Phi[i]
            pred_var[i] = self.sigma2_ + x_i @ self.cov_beta_ @ x_i
        pred_var = np.maximum(pred_var, 1e-8)
        pred_std = np.sqrt(pred_var)

        lower = mean_pred - 1.96 * pred_std
        upper = mean_pred + 1.96 * pred_std
        return mean_pred, lower, upper, pred_std

    @property
    def active_rules(self):
        return self.k  # All active


# ============================================================
# MODEL CLASSES — Faster implementations
# ============================================================
class TSK_LS_Fast:
    def __init__(self, k=5): self.k = k
    def fit(self, X, y):
        self.ctr_, self.lbl_ = cluster_centers(X, self.k)
        self.mu_, _ = gaussian_membership(X, self.ctr_, self.lbl_, self.k)
        self.W_ = tsk_weights(self.mu_)
        self.Phi_, self.p_ = tsk_phi(self.W_, X)
        self.X_train_ = X
        reg = 1e-4 * np.eye(self.Phi_.shape[1])
        self.beta_ = solve(self.Phi_.T @ self.Phi_ + reg, self.Phi_.T @ y, assume_a='pos')
        return self
    def predict(self, X):
        mu, _ = gaussian_membership(X, self.ctr_, np.zeros(len(X), dtype=int), self.k)
        W = tsk_weights(mu)
        Phi, _ = tsk_phi(W, X)
        return Phi @ self.beta_
    @property
    def active_rules(self): return self.k

class TSK_LASSO_Fast:
    def __init__(self, k=5): self.k = k
    def fit(self, X, y):
        self.ctr_, self.lbl_ = cluster_centers(X, self.k)
        self.mu_, _ = gaussian_membership(X, self.ctr_, self.lbl_, self.k)
        self.W_ = tsk_weights(self.mu_)
        self.Phi_, self.p_ = tsk_phi(self.W_, X)
        self.X_train_ = X
        try:
            alpha_max = np.max(np.abs(self.Phi_.T @ y)) / max(len(y), 1)
            alphas = np.logspace(max(-6, np.log10(alpha_max * 1e-3)), np.log10(alpha_max), 50)
            cv_folds = min(5, len(y) // 20)
            lcv = LassoCV(alphas=alphas, cv=max(cv_folds, 2), max_iter=20000, random_state=SEED, tol=1e-4)
            lcv.fit(self.Phi_, y)
            self.beta_ = lcv.coef_
        except Exception:
            rcv = RidgeCV(alphas=np.logspace(-2, 3, 20))
            rcv.fit(self.Phi_, y)
            self.beta_ = rcv.coef_
        return self
    def predict(self, X):
        mu, _ = gaussian_membership(X, self.ctr_, np.zeros(len(X), dtype=int), self.k)
        W = tsk_weights(mu)
        Phi, _ = tsk_phi(W, X)
        return Phi @ self.beta_
    @property
    def active_rules(self):
        d = self.X_train_.shape[1] + 1
        betas = self.beta_.reshape(self.k, d)
        return int(np.sum(np.linalg.norm(betas, axis=1) > 1e-6))

# ============================================================
# EVALUATION
# ============================================================
def compute_metrics(y_true, y_pred, y_lower=None, y_upper=None):
    rmse = np.sqrt(np.mean((y_true - y_pred)**2))
    mae = np.mean(np.abs(y_true - y_pred))
    r2 = r2_score(y_true, y_pred)
    result = {"RMSE": float(rmse), "MAE": float(mae), "R2": float(r2)}
    if y_lower is not None and y_upper is not None:
        in_int = (y_true >= y_lower) & (y_true <= y_upper)
        result["PICP"] = float(np.mean(in_int))
        result["MPIW"] = float(np.mean(y_upper - y_lower))
    return result

# ============================================================
# RUN EXPERIMENTS
# ============================================================
print("\n" + "=" * 70)
print("RUNNING TIER 1: MAIN COMPARISON (30 splits)")
print("=" * 70)

N_SPLITS = 30
all_results = {}

method_configs = {
    "TSK-LS":        ("fast", TSK_LS_Fast, {"k": 5}),
    "TSK-LASSO":     ("fast", TSK_LASSO_Fast, {"k": 5}),
    "TSK-SpikeSlab": ("bayes", TSK_SpikeSlab_Fast, {"k": 5, "pi": 0.5}),
    "Bayesian-TSK":  ("bayes", TSK_Bayesian_Fast, {"k": 5}),
    "RandomForest":  ("ml", None, {"max_depth": 10}),
    "SVR":           ("ml", None, {"C": 1.0, "gamma": "scale"}),
}

method_order = ["TSK-LS", "TSK-LASSO", "TSK-SpikeSlab", "Bayesian-TSK", "RandomForest", "SVR"]

for ds_name, (X, y) in datasets.items():
    print(f"\n{'='*50}")
    print(f"Dataset: {ds_name} (n={len(y)}, d={X.shape[1]})")
    print(f"{'='*50}")

    splits = get_splits(y, N_SPLITS)
    ds_results = {}

    for mn in method_order:
        mtype, mcls, kwargs = method_configs[mn]
        print(f"  {mn}...", end=" ", flush=True)
        t0 = time.time()
        mres = []

        for si, (tr, te) in enumerate(splits):
            scaler = StandardScaler()
            Xtr = scaler.fit_transform(X[tr])
            Xte = scaler.transform(X[te])
            ytr, yte = y[tr], y[te]

            if mtype == "fast":
                model = mcls(**kwargs).fit(Xtr, ytr)
                yp = model.predict(Xte)
                met = compute_metrics(yte, yp)
                met["ActiveRules"] = model.active_rules
            elif mtype == "bayes":
                model = mcls(**kwargs).fit(Xtr, ytr)
                yp, yl, yu, ystd = model.predict(Xte)
                met = compute_metrics(yte, yp, yl, yu)
                met["ActiveRules"] = model.active_rules
                met["PredStd"] = ystd.tolist()[:100]  # keep first 100 for mechanism analysis
            elif mtype == "ml":
                if mn == "RandomForest":
                    model = RandomForestRegressor(n_estimators=300, max_depth=kwargs["max_depth"],
                                                  random_state=SEED + si, n_jobs=-1)
                else:
                    model = SVR(kernel='rbf', C=kwargs["C"], gamma=kwargs["gamma"])
                model.fit(Xtr, ytr)
                yp = model.predict(Xte)
                met = compute_metrics(yte, yp)
                met["ActiveRules"] = None
            met["TrainTime"] = time.time() - t0
            mres.append(met)

        ds_results[mn] = mres
        rmses = [r["RMSE"] for r in mres]
        ar = [r.get("ActiveRules") for r in mres]
        ar_v = [a for a in ar if a is not None]
        extras = ""
        if mtype == "bayes":
            picps = [r.get("PICP", 0) for r in mres]
            mpiws = [r.get("MPIW", 0) for r in mres]
            extras = f" PICP={np.mean(picps):.3f} MPIW={np.mean(mpiws):.3f}"
        print(f"RMSE={np.mean(rmses):.4f}±{np.std(rmses):.4f} Rules={np.mean(ar_v):.1f}{extras}")

    all_results[ds_name] = ds_results

# ============================================================
# SUMMARY
# ============================================================
print("\n\n" + "=" * 80)
print("FINAL RESULTS SUMMARY")
print("=" * 80)

for ds_name in ["Energy-Heating", "Energy-Cooling", "Concrete"]:
    ds_res = all_results[ds_name]
    print(f"\n{'─'*80}")
    print(f"  {ds_name}")
    print(f"{'─'*80}")
    print(f"{'Method':<20} {'RMSE':<16} {'MAE':<12} {'R²':<10} {'Rules':<8} {'PICP':<10} {'MPIW':<10}")
    print("-" * 86)

    for mn in method_order:
        if mn not in ds_res: continue
        res = ds_res[mn]
        rmses = np.array([r["RMSE"] for r in res])
        maes = np.array([r["MAE"] for r in res])
        r2s = np.array([r["R2"] for r in res])
        rules = np.array([r.get("ActiveRules") for r in res])
        rules_m = np.nanmean(rules) if not np.all([x is None for x in rules]) else np.nan

        rmse_s = f"{np.mean(rmses):.4f}±{np.std(rmses):.4f}"
        mae_s = f"{np.mean(maes):.4f}"

        if mn in ["TSK-SpikeSlab", "Bayesian-TSK"]:
            picps = [r.get("PICP", np.nan) for r in res]
            mpiws = [r.get("MPIW", np.nan) for r in res]
            print(f"{mn:<20} {rmse_s:<16} {mae_s:<12} {np.mean(r2s):.4f}     {rules_m:<8.1f} {np.nanmean(picps):.4f}     {np.nanmean(mpiws):.4f}")
        elif mn in ["RandomForest", "SVR"]:
            print(f"{mn:<20} {rmse_s:<16} {mae_s:<12} {np.mean(r2s):.4f}     ---      ---       ---")
        else:
            print(f"{mn:<20} {rmse_s:<16} {mae_s:<12} {np.mean(r2s):.4f}     {rules_m:<8.1f} ---       ---")

# ============================================================
# STATISTICAL TESTS
# ============================================================
print("\n\n" + "=" * 80)
print("STATISTICAL TESTS")
print("=" * 80)

for ds_name in ["Energy-Heating", "Energy-Cooling", "Concrete"]:
    ds_res = all_results[ds_name]
    print(f"\n{'─'*50}")
    print(f"  {ds_name}")
    print(f"{'─'*50}")

    # Get RMSE arrays
    n_common = min(len(ds_res[mn]) for mn in method_order if mn in ds_res)
    rmse_dict = {}
    for mn in method_order:
        if mn in ds_res:
            rmse_dict[mn] = np.array([r["RMSE"] for r in ds_res[mn][:n_common]])

    # Wilcoxon: TSK-SpikeSlab vs each baseline
    ref = "TSK-SpikeSlab"
    print(f"\n  Wilcoxon Signed-Rank (Bonferroni α=0.01, 5 tests):")
    for mn in method_order:
        if mn == ref or mn not in rmse_dict: continue
        try:
            stat, pval = wilcoxon(rmse_dict[ref], rmse_dict[mn])
            sig = "*** p<0.01" if pval < 0.01 else f"n.s. (p={pval:.4f})"
            print(f"    {ref} vs {mn:<20}: W={stat:.0f}, p={pval:.6f}  {sig}")
        except Exception as e:
            print(f"    {ref} vs {mn:<20}: {e}")

    # Friedman ranking
    methods_list = [mn for mn in method_order if mn in rmse_dict]
    print(f"\n  Average Ranks (Friedman):")
    rank_mat = np.array([rankdata([rmse_dict[mn][i] for mn in methods_list])
                          for i in range(n_common)])
    avg_ranks = rank_mat.mean(axis=0)
    for mn, ar in zip(methods_list, avg_ranks):
        marker = " ★" if mn == "TSK-SpikeSlab" else ""
        print(f"    {mn:<20}: {ar:.2f}{marker}")

    try:
        stat, pval = friedmanchisquare(*[rmse_dict[mn] for mn in methods_list])
        print(f"  Friedman: χ²={stat:.2f}, p={pval:.8f}")
    except Exception as e:
        print(f"  Friedman test failed: {e}")

# ============================================================
# ABLATION: π variation
# ============================================================
print("\n\n" + "=" * 70)
print("TIER 2: π ABLATION (10 splits, Energy-Cooling)")
print("=" * 70)

X, y = datasets["Energy-Cooling"]
splits_abl = get_splits(y, 10)
ablation = {}

for pi_val in [0.1, 0.3, 0.5, 0.7, 0.9]:
    print(f"  π={pi_val}...", end=" ", flush=True)
    pi_res = []
    for si, (tr, te) in enumerate(splits_abl):
        scaler = StandardScaler()
        Xtr = scaler.fit_transform(X[tr]); Xte = scaler.transform(X[te])
        ytr, yte = y[tr], y[te]
        model = TSK_SpikeSlab_Fast(k=5, pi=pi_val).fit(Xtr, ytr)
        yp, yl, yu, _ = model.predict(Xte)
        met = compute_metrics(yte, yp, yl, yu)
        met["ActiveRules"] = model.active_rules
        met["PIPs"] = model.pip_.tolist()
        pi_res.append(met)
    ablation[str(pi_val)] = pi_res
    rmses = [r["RMSE"] for r in pi_res]
    ar = [r["ActiveRules"] for r in pi_res]
    picps = [r.get("PICP", 0) for r in pi_res]
    mpiws = [r.get("MPIW", 0) for r in pi_res]
    print(f"RMSE={np.mean(rmses):.4f}±{np.std(rmses):.4f} Rules={np.mean(ar):.1f} PICP={np.mean(picps):.3f}")
    if pi_val == 0.5:
        pips_all = np.array([r["PIPs"] for r in pi_res]).mean(axis=0)
        print(f"    Rule PIPs: {pips_all}")

with open(os.path.join(DATA_DIR, "tier2_ablation.json"), "w") as f:
    json.dump({k: [{kk: vv for kk, vv in r.items()} for r in v]
               for k, v in ablation.items()}, f, indent=2, default=float)

# ============================================================
# SENSITIVITY: FCM cluster count
# ============================================================
print("\n\n" + "=" * 70)
print("TIER 3: FCM CLUSTER COUNT SENSITIVITY (10 splits, Energy-Cooling)")
print("=" * 70)

fcm_sens = {}
for k_val in [3, 5, 7, 9]:
    print(f"  k={k_val}...", end=" ", flush=True)
    k_res = []
    for si, (tr, te) in enumerate(splits_abl):
        scaler = StandardScaler()
        Xtr = scaler.fit_transform(X[tr]); Xte = scaler.transform(X[te])
        ytr, yte = y[tr], y[te]
        model = TSK_SpikeSlab_Fast(k=k_val, pi=0.5).fit(Xtr, ytr)
        yp, yl, yu, _ = model.predict(Xte)
        met = compute_metrics(yte, yp, yl, yu)
        met["ActiveRules"] = model.active_rules
        k_res.append(met)
    fcm_sens[str(k_val)] = k_res
    rmses = [r["RMSE"] for r in k_res]
    ar = [r["ActiveRules"] for r in k_res]
    picps = [r.get("PICP", 0) for r in k_res]
    print(f"RMSE={np.mean(rmses):.4f} Rules={np.mean(ar):.1f}/{k_val} Sparsity={1-np.mean(ar)/k_val:.2f}")

with open(os.path.join(DATA_DIR, "tier3_fcm.json"), "w") as f:
    json.dump({k: [{kk: vv for kk, vv in r.items()} for r in v]
               for k, v in fcm_sens.items()}, f, indent=2, default=float)

# ============================================================
# MECHANISM ANALYSIS
# ============================================================
print("\n\n" + "=" * 70)
print("TIER 4: MECHANISM-PROBING ANALYSIS")
print("=" * 70)

for ds_name in ["Energy-Cooling", "Concrete"]:
    X, y = datasets[ds_name]
    splits = get_splits(y, 30)
    mech = {"Low": {"SS": [], "LASSO": []},
            "Med": {"SS": [], "LASSO": []},
            "High": {"SS": [], "LASSO": []}}

    for si, (tr, te) in enumerate(splits):
        scaler = StandardScaler()
        Xtr = scaler.fit_transform(X[tr]); Xte = scaler.transform(X[te])
        ytr, yte = y[tr], y[te]

        ss = TSK_SpikeSlab_Fast(k=5, pi=0.5).fit(Xtr, ytr)
        yp_ss, yl_ss, yu_ss, ystd_ss = ss.predict(Xte)

        lasso = TSK_LASSO_Fast(k=5).fit(Xtr, ytr)
        yp_lasso = lasso.predict(Xte)

        stds = ystd_ss
        lo = np.percentile(stds, 33)
        hi = np.percentile(stds, 67)

        for bin_name, mask in [("Low", stds <= lo),
                                ("Med", (stds > lo) & (stds <= hi)),
                                ("High", stds > hi)]:
            if np.sum(mask) < 3: continue
            rmse_ss = np.sqrt(np.mean((yte[mask] - yp_ss[mask])**2))
            rmse_lasso = np.sqrt(np.mean((yte[mask] - yp_lasso[mask])**2))
            mech[bin_name]["SS"].append(rmse_ss)
            mech[bin_name]["LASSO"].append(rmse_lasso)

    print(f"\n  {ds_name}:")
    for bin_name in ["Low", "Med", "High"]:
        if mech[bin_name]["SS"]:
            r_ss = np.mean(mech[bin_name]["SS"])
            r_la = np.mean(mech[bin_name]["LASSO"])
            print(f"    {bin_name:>4} uncertainty: SS={r_ss:.4f}  LASSO={r_la:.4f}  Δ={r_la-r_ss:+.4f}  ({'+LASSO worse' if r_la > r_ss else '+SS worse'})")

    with open(os.path.join(DATA_DIR, f"tier4_mechanism_{ds_name}.json"), "w") as f:
        json.dump({str(k): {str(kk): [float(x) for x in vv] for kk, vv in v.items()}
                   for k, v in mech.items()}, f, indent=2)

# ============================================================
# SAVE FULL RESULTS
# ============================================================
def make_json_safe(obj):
    if isinstance(obj, dict):
        return {str(k): make_json_safe(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [make_json_safe(x) for x in obj]
    elif isinstance(obj, (np.floating, np.integer)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif obj is None:
        return None
    elif isinstance(obj, float) and np.isnan(obj):
        return None
    return obj

with open(os.path.join(DATA_DIR, "tier1_results.json"), "w") as f:
    json.dump(make_json_safe(all_results), f, indent=2)

print("\n\n" + "=" * 70)
print("ALL EXPERIMENTS COMPLETE!")
print("Results saved to:", DATA_DIR)
print("=" * 70)
