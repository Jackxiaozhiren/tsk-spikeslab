# v2.0.0 — ASOC corrected reproducibility release

This major release freezes the Applied Soft Computing manuscript-active state and supersedes the historical `v1.0` result narrative without rewriting that tag.

## Scientific changes

- corrected fuzzy-c-means membership update and numerically stable firing strengths;
- corrected no-intercept TSK consequent initialization;
- corrected conjugate Bayesian predictive intervals;
- corrected rule-level and coefficient-level spike-and-slab Gibbs conditionals;
- direct posterior-predictive quantiles for Bayesian model averaging;
- rebuilt 30-split benchmark evidence, GP/conformal references, MCMC diagnostics, synthetic verification, and high-dimensional sensitivity probes;
- conservative interpretation: no demonstrated predictive or calibration advantage for spike-and-slab TSK on the tested benchmarks.

## Reproducibility changes

- 30 correctness/regression tests;
- 11 structured frozen-result JSON artifacts protected by SHA-256 checksums;
- execution `.log` traces kept as local audit history rather than public release evidence;
- public raw `.npz` caches and historical submission/result trees removed from the active branch;
- deterministic Git release manifest and CI verification;
- exact observed rebuild environment documented separately from compatibility requirements.
