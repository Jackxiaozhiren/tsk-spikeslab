# Bayesian TSK Fuzzy Regression — ASOC Reproducibility Materials

Reproducibility repository for the Applied Soft Computing manuscript:

**Correctness and Predictive Uncertainty in Bayesian TSK Fuzzy Regression: A Reproducible Evaluation of Spike-and-Slab Model Averaging**

## Current manuscript-active state

This `v2.0.0` line supersedes the earlier Information Sciences-era `v1.0` snapshot for the current ASOC manuscript. The historical release remains available for provenance, but it is **not** the evidence source for the ASOC results.

The rebuilt protocol corrects implementation details in fuzzy c-means, training-time membership handling, linear-consequent fitting, Bayesian posterior calculations, and posterior-predictive interval construction. The scientific conclusion is intentionally narrow: rule-level spike-and-slab model averaging is reproducible and diagnostically useful, but this study does not establish an accuracy or calibration advantage over dense TSK references.

### Frozen headline results

Across 30 fixed 80/20 splits:

| Target | TSK-LS R² | Gibbs/BMA R² | Gibbs PICP | GP R² |
| --- | ---: | ---: | ---: | ---: |
| Energy-Heating | 0.9570 | 0.9567 | 0.9399 | 0.9978 |
| Energy-Cooling | 0.9229 | 0.9224 | 0.9338 | 0.9794 |
| Concrete | 0.7859 | 0.7840 | 0.9379 | 0.8891 |

Additional frozen diagnostics include:

- repaired BIC-ablation R² values of 0.9372 / 0.9338 / 0.9325 / 0.9307;
- raw coefficient \(\hat R_{max}\) of 1.061 and 1.030 for the two representative Gibbs diagnostics, so the release does **not** claim universal chain convergence;
- finite synthetic-enumeration discrepancies of 0.0261 (max PIP), 0.0224 (max BMA mean), and 0.0027 (median relative predictive-variance difference);
- a high-dimensional probe where no stable sparsity advantage is established under the tested protocol.

## Repository map

- `src/` — corrected TSK/Bayesian/Gibbs implementation and rebuild scripts.
- `tests/` — 30 correctness/regression tests.
- `evidence/` — frozen JSON/log evidence plus the original results SHA-256 manifest.
- `tables/` and `figures/` — manuscript-active artifacts generated from the frozen evidence.
- `manuscript.tex`, `supplementary.tex`, `references.bib` — ASOC-aligned source snapshot.
- `docs/CLAIM_EVIDENCE_MAP.md` — claim-to-evidence boundary.
- `docs/REPRODUCIBILITY.md` — reproducibility and environment guidance.
- `PUBLIC_RELEASE_MANIFEST.md` — public/private artifact boundary.

## Quick verification

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-ci.txt
python -m compileall -q src tests tools
pytest -q
python tools/verify_frozen_results.py
```

The clean release candidate passes **30/30 tests**. CI also verifies the frozen-result checksums and the deterministic Git-tracked release manifest.

## Regenerating tables and figures from frozen evidence

```bash
python src/generate_phase6_artifacts.py --output-dir /tmp/asoc_artifacts
```

The generator reads `evidence/main_rebuilt.json` and the associated frozen JSON files when a fresh rebuild directory is not present.

## Full rebuild boundary

The manuscript-active results were rebuilt from corrected code using UCI Energy Efficiency (dataset 242), Concrete Compressive Strength (dataset 165), and the explicitly labeled Superconductivity (dataset 464) high-dimensional probe. Public raw/cache `.npz` files are deliberately excluded from this repository. Obtain source data from UCI and run the relevant scripts under `src/`.

The observed manuscript-workstation environment is recorded in `docs/ENVIRONMENT_OBSERVED_2026-08-29.txt`. `requirements.txt` remains a compatibility specification rather than a claim of bit-identical results across hardware and library versions.

## Version history

- `v1.0` — historical Information Sciences-era snapshot and earlier Zenodo archive.
- `v2.0.0` — ASOC-aligned corrected implementation, rebuilt evidence, tests, and manuscript-active artifacts.

## Citation

Use GitHub's **Cite this repository** metadata from `CITATION.cff`. The historical Zenodo DOI `10.5281/zenodo.21929319` corresponds to the earlier snapshot; a new version-specific Zenodo DOI should be used for the ASOC-aligned `v2.0.0` snapshot once deposited.

## License

BSD 3-Clause for project-authored code and documentation. Third-party datasets remain subject to their original terms.
