#!/usr/bin/env python3
"""Stage 4: Supplementary ablation experiments — tau^2, alpha, bootstrap PICP."""
import numpy as np
import json, os, time
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.cluster import KMeans
from sklearn.metrics import r2_score
from scipy.linalg import solve
import warnings
warnings.filterwarnings('ignore')

SEED = 42
np.random.seed(SEED)
DATA_DIR = "/Users/jackson/ASC论文/results/raw"
os.makedirs(DATA_DIR, exist_ok=True)

# ---- TSK Core (same as experiment.py) ----
def fcm_centers(X, k):
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

# ---- TSK-SpikeSlab with configurable tau^2 and ridge alpha ----
class TSK_SpikeSlab_Fast:
    def __init__(self, k=5, pi=0.5, tau2=1e3, ridge_alpha=0.01):
        self.k = k; self.pi = pi; self.tau2 = tau2; self.ridge_alpha = ridge_alpha

    def fit(self, X, y):
        n, d = X.shape
        R = self.k; pp = d + 1
        self.ctr_, self.lbl_ = fcm_centers(X, R)
        self.mu_, _ = gaussian_membership(X, self.ctr_, self.lbl_, R)
        self.W_ = tsk_weights(self.mu_)
        self.Phi_, self.p_ = tsk_phi(self.W_, X)
        Phi = self.Phi_
        self.X_train_ = X

        ridge = Ridge(alpha=self.ridge_alpha)
        ridge.fit(Phi, y)
        beta_hat_full = ridge.coef_
        y_hat = Phi @ beta_hat_full
        self.sigma2_ = max(np.var(y - y_hat), 1e-4)

        self.pip_ = np.zeros(R)
        for j in range(R):
            idx_j = slice(j*pp, (j+1)*pp)
            Phi_j = Phi[:, idx_j]
            idx_others = [i for i in range(R*pp) if i < j*pp or i >= (j+1)*pp]
            Phi_others = Phi[:, idx_others]
            beta_others = beta_hat_full[idx_others]
            resid_no_j = y - Phi_others @ beta_others
            beta_j_on_resid = solve(Phi_j.T @ Phi_j + np.eye(pp)*1e-4,
                                     Phi_j.T @ resid_no_j, assume_a='pos')
            resid_with_j = resid_no_j - Phi_j @ beta_j_on_resid
            rss_no_j = np.sum(resid_no_j**2) + 1e-12
            rss_with_j = np.sum(resid_with_j**2) + 1e-12
            bic_no_j = n * np.log(rss_no_j / n)
            bic_with_j = n * np.log(rss_with_j / n) + pp * np.log(n)
            log_bf = -0.5 * (bic_with_j - bic_no_j)
            prior_odds = self.pi / (1 - self.pi + 1e-12)
            posterior_odds = prior_odds * np.exp(log_bf)
            pip = posterior_odds / (1 + posterior_odds)
            self.pip_[j] = np.clip(pip, 0.001, 0.999)

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
        ridge_active = Ridge(alpha=self.ridge_alpha)
        ridge_active.fit(Phi_active, y)
        beta_active = ridge_active.coef_
        self.beta_ = np.zeros(R * pp)
        for k_idx, full_idx in enumerate(active_indices):
            self.beta_[full_idx] = beta_active[k_idx]

        prior_prec = np.zeros(R * pp)
        for j in range(R):
            if self.active_mask_[j]:
                prior_prec[j*pp:(j+1)*pp] = 1.0 / self.tau2
            else:
                prior_prec[j*pp:(j+1)*pp] = 1e10
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

# ---- TSK-LS for bootstrap ----
class TSK_LS:
    def __init__(self, k=5): self.k = k
    def fit(self, X, y):
        self.ctr_, self.lbl_ = fcm_centers(X, self.k)
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

def compute_metrics(y_true, y_pred, y_lower=None, y_upper=None):
    rmse = float(np.sqrt(np.mean((y_true - y_pred)**2)))
    mae = float(np.mean(np.abs(y_true - y_pred)))
    r2 = float(r2_score(y_true, y_pred))
    result = {"RMSE": rmse, "MAE": mae, "R2": r2}
    if y_lower is not None and y_upper is not None:
        result["PICP"] = float(np.mean((y_true >= y_lower) & (y_true <= y_upper)))
        result["MPIW"] = float(np.mean(y_upper - y_lower))
    return result

# ---- LOAD DATA ----
from ucimlrepo import fetch_ucirepo
energy = fetch_ucirepo(id=242)
X_e = energy.data.features.values.astype(float)
y_cool = energy.data.targets.iloc[:, 1].values.astype(float)
X, y = X_e, y_cool
print(f"Energy-Cooling: n={len(y)}, d={X.shape[1]}")

N_SPLITS = 10  # use 10 splits for ablation speed

# ============================================================
# ABLATION 1: tau^2 (slab variance) sensitivity
# ============================================================
print("\n" + "=" * 60)
print("ABLATION: τ² (slab variance) — 10 splits, Energy-Cooling")
print("=" * 60)

splits = get_splits(y, N_SPLITS)
tau2_values = [1e0, 1e1, 1e2, 1e3, 1e4, 1e5, 1e6]
tau2_results = {}

for tau2 in tau2_values:
    res_list = []
    for si, (tr, te) in enumerate(splits):
        scaler = StandardScaler()
        Xtr = scaler.fit_transform(X[tr]); Xte = scaler.transform(X[te])
        ytr, yte = y[tr], y[te]
        model = TSK_SpikeSlab_Fast(k=5, pi=0.5, tau2=tau2, ridge_alpha=0.01).fit(Xtr, ytr)
        yp, yl, yu, _ = model.predict(Xte)
        met = compute_metrics(yte, yp, yl, yu)
        met["ActiveRules"] = model.active_rules
        met["PIPs"] = model.pip_.tolist()
        res_list.append(met)
    tau2_results[str(tau2)] = res_list
    rmse_arr = [r["RMSE"] for r in res_list]
    ar = [r["ActiveRules"] for r in res_list]
    picp_arr = [r.get("PICP", 0) for r in res_list]
    mpiw_arr = [r.get("MPIW", 0) for r in res_list]
    print(f"  τ²={tau2:.0e}: RMSE={np.mean(rmse_arr):.4f}±{np.std(rmse_arr):.4f}  "
          f"Rules={np.mean(ar):.1f}  PICP={np.mean(picp_arr):.3f}  MPIW={np.mean(mpiw_arr):.2f}")

with open(os.path.join(DATA_DIR, "tier4_tau2_ablation.json"), "w") as f:
    json.dump({str(k): [{kk: vv for kk, vv in r.items()} for r in v]
               for k, v in tau2_results.items()}, f, indent=2, default=float)

# ============================================================
# ABLATION 2: Ridge alpha sensitivity
# ============================================================
print("\n" + "=" * 60)
print("ABLATION: Ridge α — 10 splits, Energy-Cooling")
print("=" * 60)

alpha_values = [1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1e0, 1e1]
alpha_results = {}

for alpha in alpha_values:
    res_list = []
    for si, (tr, te) in enumerate(splits):
        scaler = StandardScaler()
        Xtr = scaler.fit_transform(X[tr]); Xte = scaler.transform(X[te])
        ytr, yte = y[tr], y[te]
        model = TSK_SpikeSlab_Fast(k=5, pi=0.5, tau2=1e3, ridge_alpha=alpha).fit(Xtr, ytr)
        yp, yl, yu, _ = model.predict(Xte)
        met = compute_metrics(yte, yp, yl, yu)
        met["ActiveRules"] = model.active_rules
        met["PIPs"] = model.pip_.tolist()
        res_list.append(met)
    alpha_results[str(alpha)] = res_list
    rmse_arr = [r["RMSE"] for r in res_list]
    ar = [r["ActiveRules"] for r in res_list]
    picp_arr = [r.get("PICP", 0) for r in res_list]
    mpiw_arr = [r.get("MPIW", 0) for r in res_list]
    print(f"  α={alpha:.0e}: RMSE={np.mean(rmse_arr):.4f}±{np.std(rmse_arr):.4f}  "
          f"Rules={np.mean(ar):.1f}  PICP={np.mean(picp_arr):.3f}  MPIW={np.mean(mpiw_arr):.2f}")

with open(os.path.join(DATA_DIR, "tier4_alpha_ablation.json"), "w") as f:
    json.dump({str(k): [{kk: vv for kk, vv in r.items()} for r in v]
               for k, v in alpha_results.items()}, f, indent=2, default=float)

# ============================================================
# ABLATION 3: Bootstrap TSK-LS prediction intervals
# ============================================================
print("\n" + "=" * 60)
print("Bootstrap TSK-LS PICP — 30 splits, Energy-Cooling")
print("=" * 60)

N_SPLITS_BOOT = 30
splits_30 = get_splits(y, N_SPLITS_BOOT)
bootstrap_results = []

for si, (tr, te) in enumerate(splits_30):
    scaler = StandardScaler()
    Xtr = scaler.fit_transform(X[tr]); Xte = scaler.transform(X[te])
    ytr, yte = y[tr], y[te]

    # Bootstrap: resample training data with replacement, fit TSK-LS, predict on test
    n_train = len(ytr)
    B = 200  # bootstrap replications
    preds = np.zeros((B, len(yte)))

    for b in range(B):
        rng = np.random.RandomState(SEED * 1000 + si * B + b)
        boot_idx = rng.choice(n_train, size=n_train, replace=True)
        X_boot = Xtr[boot_idx]
        y_boot = ytr[boot_idx]

        try:
            model_b = TSK_LS(k=5).fit(X_boot, y_boot)
            preds[b] = model_b.predict(Xte)
        except Exception:
            preds[b] = np.nan

    # Remove failed bootstrap replicates
    valid_preds = preds[~np.isnan(preds).any(axis=1)]
    mean_pred = np.mean(valid_preds, axis=0)
    lower = np.percentile(valid_preds, 2.5, axis=0)
    upper = np.percentile(valid_preds, 97.5, axis=0)

    met = compute_metrics(yte, mean_pred, lower, upper)
    met["ActiveRules"] = 5  # dense
    bootstrap_results.append(met)

rmse_arr = [r["RMSE"] for r in bootstrap_results]
picp_arr = [r.get("PICP", 0) for r in bootstrap_results]
mpiw_arr = [r.get("MPIW", 0) for r in bootstrap_results]
print(f"  Bootstrap TSK-LS: RMSE={np.mean(rmse_arr):.4f}±{np.std(rmse_arr):.4f}  "
      f"PICP={np.mean(picp_arr):.3f}  MPIW={np.mean(mpiw_arr):.2f}")

with open(os.path.join(DATA_DIR, "tier4_bootstrap_tskls.json"), "w") as f:
    json.dump([{kk: vv for kk, vv in r.items()} for r in bootstrap_results], f, indent=2, default=float)

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print("\nτ² ablation (RMSE range across values):")
tau2_rmses = {k: np.mean([r["RMSE"] for r in v]) for k, v in tau2_results.items()}
print(f"  Min τ²={min(tau2_rmses, key=lambda k: tau2_rmses[k])}: RMSE={tau2_rmses[min(tau2_rmses, key=lambda k: tau2_rmses[k])]:.4f}")
print(f"  Max τ²={max(tau2_rmses, key=lambda k: tau2_rmses[k])}: RMSE={tau2_rmses[max(tau2_rmses, key=lambda k: tau2_rmses[k])]:.4f}")
print(f"  Range: {max(tau2_rmses.values()) - min(tau2_rmses.values()):.4f}")

print("\nα ablation (RMSE range across values):")
alpha_rmses = {k: np.mean([r["RMSE"] for r in v]) for k, v in alpha_results.items()}
print(f"  Min α={min(alpha_rmses, key=lambda k: alpha_rmses[k])}: RMSE={alpha_rmses[min(alpha_rmses, key=lambda k: alpha_rmses[k])]:.4f}")
print(f"  Max α={max(alpha_rmses, key=lambda k: alpha_rmses[k])}: RMSE={alpha_rmses[max(alpha_rmses, key=lambda k: alpha_rmses[k])]:.4f}")
print(f"  Range: {max(alpha_rmses.values()) - min(alpha_rmses.values()):.4f}")

print(f"\nBootstrap TSK-LS: PICP={np.mean(picp_arr):.3f}, MPIW={np.mean(mpiw_arr):.2f}")
print("Done!")
