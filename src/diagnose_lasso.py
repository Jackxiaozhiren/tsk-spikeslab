#!/usr/bin/env python3
"""Diagnose TSK-LASSO catastrophic failure root cause."""
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LassoCV, RidgeCV
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings('ignore')

SEED = 42

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

from ucimlrepo import fetch_ucirepo

energy = fetch_ucirepo(id=242)
X_e = energy.data.features.values.astype(float)
y_cool = energy.data.targets.iloc[:, 1].values.astype(float)

def run_diagnosis(X, y, split_idx=0):
    n = len(y)
    rng = np.random.RandomState(SEED + split_idx)
    n_test = max(int(n * 0.2), 5)
    test_idx = rng.choice(n, size=n_test, replace=False)
    train_idx = np.setdiff1d(np.arange(n), test_idx)

    scaler = StandardScaler()
    Xtr = scaler.fit_transform(X[train_idx])
    Xte = scaler.transform(X[test_idx])
    ytr, yte = y[train_idx], y[test_idx]

    ctr, lbl = fcm_centers(Xtr, 5)
    mu, _ = gaussian_membership(Xtr, ctr, lbl, 5)
    W = tsk_weights(mu)
    Phi, pp = tsk_phi(W, Xtr)

    print(f"n_train={len(ytr)}, Phi shape={Phi.shape}")
    print(f"Condition number of Phi: {np.linalg.cond(Phi):.2e}")

    # Check the original alpha grid
    alpha_max = np.max(np.abs(Phi.T @ ytr)) / max(len(ytr), 1)
    print(f"\n--- Original alpha grid ---")
    print(f"alpha_max = {alpha_max:.6f}")
    alphas_orig = np.logspace(max(-6, np.log10(alpha_max * 1e-3)), np.log10(alpha_max), 50)
    print(f"alpha range: [{alphas_orig[0]:.6f}, {alphas_orig[-1]:.6f}]")
    print(f"50 alphas: {alphas_orig[:5]} ... {alphas_orig[-5:]}")

    n_alphas = 50
    cv_folds = min(5, len(ytr) // 20)
    lcv = LassoCV(alphas=alphas_orig, cv=max(cv_folds, 2), max_iter=20000, random_state=SEED, tol=1e-4)
    lcv.fit(Phi, ytr)
    print(f"\n--- LassoCV results (original grid) ---")
    print(f"Selected alpha: {lcv.alpha_:.6f}")
    print(f"Non-zero coefficients: {np.sum(np.abs(lcv.coef_) > 1e-6)} / {len(lcv.coef_)}")
    yp = Phi @ lcv.coef_
    rmse_train = np.sqrt(np.mean((ytr - yp)**2))
    r2_train = 1 - np.sum((ytr - yp)**2) / np.sum((ytr - np.mean(ytr))**2)
    print(f"Train RMSE: {rmse_train:.4f}, Train R²: {r2_train:.4f}")

    # Now try a MUCH wider alpha grid
    alphas_wide = np.logspace(-8, np.log10(alpha_max) if alpha_max > 0 else 2, 100)
    print(f"\n--- Wider alpha grid ---")
    print(f"alpha range: [{alphas_wide[0]:.8f}, {alphas_wide[-1]:.6f}]")

    lcv2 = LassoCV(alphas=alphas_wide, cv=max(cv_folds, 2), max_iter=20000, random_state=SEED, tol=1e-4)
    lcv2.fit(Phi, ytr)
    print(f"Selected alpha: {lcv2.alpha_:.8f}")
    print(f"Non-zero coefficients: {np.sum(np.abs(lcv2.coef_) > 1e-6)} / {len(lcv2.coef_)}")
    yp2 = Phi @ lcv2.coef_
    rmse_train2 = np.sqrt(np.mean((ytr - yp2)**2))
    r2_train2 = 1 - np.sum((ytr - yp2)**2) / np.sum((ytr - np.mean(ytr))**2)
    print(f"Train RMSE: {rmse_train2:.4f}, Train R²: {r2_train2:.4f}")

    # Try ElasticNet
    from sklearn.linear_model import ElasticNetCV
    alphas_en = np.logspace(-6, 3, 100)
    l1_ratios = [0.1, 0.3, 0.5, 0.7, 0.9, 0.95, 0.99]
    encv = ElasticNetCV(alphas=alphas_en, l1_ratio=l1_ratios, cv=max(cv_folds, 2),
                         max_iter=20000, random_state=SEED, tol=1e-4)
    encv.fit(Phi, ytr)
    yp_en = Phi @ encv.coef_
    rmse_en = np.sqrt(np.mean((ytr - yp_en)**2))
    r2_en = 1 - np.sum((ytr - yp_en)**2) / np.sum((ytr - np.mean(ytr))**2)
    print(f"\n--- ElasticNetCV ---")
    print(f"Selected alpha: {encv.alpha_:.6f}, l1_ratio: {encv.l1_ratio_:.3f}")
    print(f"Non-zero coefs: {np.sum(np.abs(encv.coef_) > 1e-6)} / {len(encv.coef_)}")
    print(f"Train RMSE: {rmse_en:.4f}, Train R²: {r2_en:.4f}")

    # What does RidgeCV give?
    rcv = RidgeCV(alphas=np.logspace(-4, 3, 50))
    rcv.fit(Phi, ytr)
    yp_ridge = Phi @ rcv.coef_
    rmse_ridge = np.sqrt(np.mean((ytr - yp_ridge)**2))
    r2_ridge = 1 - np.sum((ytr - yp_ridge)**2) / np.sum((ytr - np.mean(ytr))**2)
    print(f"\n--- RidgeCV ---")
    print(f"Selected alpha: {rcv.alpha_:.4f}")
    print(f"Train RMSE: {rmse_ridge:.4f}, Train R²: {r2_ridge:.4f}")

    # Test set performance
    from sklearn.linear_model import Ridge
    mu_te, _ = gaussian_membership(Xte, ctr, np.zeros(len(Xte), dtype=int), 5)
    W_te = tsk_weights(mu_te)
    Phi_te, _ = tsk_phi(W_te, Xte)

    for name, coef in [("LassoCV orig", lcv.coef_), ("LassoCV wide", lcv2.coef_),
                        ("ElasticNetCV", encv.coef_), ("RidgeCV", rcv.coef_)]:
        yp_te = Phi_te @ coef
        rmse_te = np.sqrt(np.mean((yte - yp_te)**2))
        r2_te = 1 - np.sum((yte - yp_te)**2) / np.sum((yte - np.mean(yte))**2)
        print(f"  {name:<20}: Test RMSE={rmse_te:.4f}, Test R²={r2_te:.4f}")

    # Check: is the problem that LASSO coefficients collapse to ~0?
    beta_norms = np.linalg.norm(lcv.coef_.reshape(5, 9), axis=1)
    print(f"\nPer-rule L2 norms of LassoCV (original grid): {beta_norms}")
    print(f"All coefs < 1e-6: {np.sum(np.abs(lcv.coef_) < 1e-6)} / {len(lcv.coef_)}")

    # Direct OLS
    from scipy.linalg import solve
    reg = 1e-4 * np.eye(Phi.shape[1])
    beta_ols = solve(Phi.T @ Phi + reg, Phi.T @ ytr, assume_a='pos')
    yp_ols = Phi_te @ beta_ols
    rmse_ols = np.sqrt(np.mean((yte - yp_ols)**2))
    r2_ols = 1 - np.sum((yte - yp_ols)**2) / np.sum((yte - np.mean(yte))**2)
    print(f"\n  TSK-LS (OLS+reg):   Test RMSE={rmse_ols:.4f}, Test R²={r2_ols:.4f}")

print("=" * 70)
print("TSK-LASSO DIAGNOSIS — Energy-Cooling, Split 0")
print("=" * 70)
run_diagnosis(X_e, y_cool, 0)

print("\n" + "=" * 70)
print("Testing across 5 splits with wider alpha grid...")
print("=" * 70)

rmse_results = {"orig": [], "wide": [], "en": [], "ols": []}
for s in range(5):
    n = len(y_cool)
    rng = np.random.RandomState(SEED + s)
    n_test = max(int(n * 0.2), 5)
    test_idx = rng.choice(n, size=n_test, replace=False)
    train_idx = np.setdiff1d(np.arange(n), test_idx)

    scaler = StandardScaler()
    Xtr = scaler.fit_transform(X_e[train_idx]); Xte = scaler.transform(X_e[test_idx])
    ytr, yte = y_cool[train_idx], y_cool[test_idx]

    ctr, lbl = fcm_centers(Xtr, 5)
    mu, _ = gaussian_membership(Xtr, ctr, lbl, 5)
    W = tsk_weights(mu)
    Phi, pp = tsk_phi(W, Xtr)

    mu_te, _ = gaussian_membership(Xte, ctr, np.zeros(len(Xte), dtype=int), 5)
    W_te = tsk_weights(mu_te)
    Phi_te, _ = tsk_phi(W_te, Xte)

    # Original grid
    alpha_max = np.max(np.abs(Phi.T @ ytr)) / max(len(ytr), 1)
    alphas_orig = np.logspace(max(-6, np.log10(alpha_max * 1e-3)), np.log10(alpha_max), 50)
    cv_folds = min(5, len(ytr) // 20)
    lcv = LassoCV(alphas=alphas_orig, cv=max(cv_folds, 2), max_iter=20000, random_state=SEED, tol=1e-4)
    lcv.fit(Phi, ytr)
    rmse_results["orig"].append(np.sqrt(np.mean((yte - Phi_te @ lcv.coef_)**2)))

    # Wide grid
    alphas_wide = np.logspace(-8, max(0, np.log10(alpha_max)), 100)
    lcv2 = LassoCV(alphas=alphas_wide, cv=max(cv_folds, 2), max_iter=20000, random_state=SEED, tol=1e-4)
    lcv2.fit(Phi, ytr)
    rmse_results["wide"].append(np.sqrt(np.mean((yte - Phi_te @ lcv2.coef_)**2)))

    # ElasticNet
    from sklearn.linear_model import ElasticNetCV
    encv = ElasticNetCV(alphas=np.logspace(-6, 3, 100), l1_ratio=[0.1,0.3,0.5,0.7,0.9,0.95,0.99],
                         cv=max(cv_folds, 2), max_iter=20000, random_state=SEED)
    encv.fit(Phi, ytr)
    rmse_results["en"].append(np.sqrt(np.mean((yte - Phi_te @ encv.coef_)**2)))

    # OLS
    from scipy.linalg import solve
    reg = 1e-4 * np.eye(Phi.shape[1])
    beta_ols = solve(Phi.T @ Phi + reg, Phi.T @ ytr, assume_a='pos')
    rmse_results["ols"].append(np.sqrt(np.mean((yte - Phi_te @ beta_ols)**2)))

for k, v in rmse_results.items():
    print(f"  {k}: mean={np.mean(v):.4f} ± {np.std(v):.4f}")
