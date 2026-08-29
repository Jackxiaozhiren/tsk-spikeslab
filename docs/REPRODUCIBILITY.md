# Reproducibility

## Scientific authority

For the ASOC manuscript, the controlling evidence is the `v2.0.0` line: corrected source under `src/`, 30 regression/correctness tests under `tests/`, and frozen result artifacts under `evidence/`. The older `v1.0` release is historical and must not be mixed with the ASOC result set.

## Integrity checks

```bash
pip install -r requirements-ci.txt
python -m compileall -q src tests tools
pytest -q
python tools/verify_frozen_results.py
```

`tools/verify_frozen_results.py` verifies the original result-file SHA-256 manifest, checks selected manuscript headline values directly from the frozen JSON, and confirms that public raw `.npz` caches are absent.

## Frozen protocol

- Seed: `42`.
- Main evaluation: 30 deterministic 80/20 splits.
- Bayesian predictive evaluation: 512 predictive samples in the rebuilt main protocol.
- Split conformal: outer-train data are further split with calibration fraction 0.25; its protocol is therefore not identical to the ordinary TSK fit.
- Energy Efficiency: UCI 242; Heating and Cooling are treated as separate targets.
- Concrete Compressive Strength: UCI 165.
- High-dimensional probe: Superconductivity UCI 464, labeled as a probe rather than a main benchmark.

The exact protocol metadata is embedded in `evidence/main_rebuilt.json`.

## Correctness changes relative to historical v1.0

The ASOC line includes corrections to the fuzzy-c-means membership update, log-domain firing strengths, no-intercept linear consequent initialization, scaled Gaussian/inverse-gamma calculations, spike-and-slab Gibbs conditionals, and direct posterior-predictive quantiles. These changes materially alter the old result narrative; therefore the historical result files are not manuscript-active.

## Regenerating manuscript artifacts

```bash
python src/generate_phase6_artifacts.py --output-dir /tmp/asoc_artifacts
```

This reads the frozen `evidence/*.json` files and regenerates the manuscript tables and figures without rerunning the expensive benchmark experiments.

## Full experimental rebuild

A full rebuild requires obtaining the UCI datasets and running the relevant drivers under `src/`. Set `TSK_OUTPUT_DIR` to a new directory so historical/public evidence is never overwritten. Example:

```bash
export TSK_OUTPUT_DIR="$PWD/rebuild_results_local"
python src/rebuild_phase4.py
```

Additional diagnostic scripts (`diagnostics_gp.py`, `highdim_probe.py`, `highdim_tau2_grid.py`, `synthetic_gamma_verify.py`, and related utilities) correspond to the evidence files documented in `docs/CLAIM_EVIDENCE_MAP.md`.

## Environment boundary

`requirements.txt` is a compatibility specification. The observed manuscript rebuild environment is recorded separately in `docs/ENVIRONMENT_OBSERVED_2026-08-29.txt`.

## Inference boundary

The release does not claim universal MCMC convergence, universal calibration, a general sparsity advantage, or predictive superiority of spike-and-slab TSK. Raw coefficient diagnostics include \(\hat R_{max}>1.01\) in representative runs; those diagnostics are reported rather than hidden.
