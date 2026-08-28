# Exact Bayesian Inference for Spike-and-Slab Priors in TSK Fuzzy Systems

Companion code for *"Exact Bayesian Inference for Spike-and-Slab Priors in Takagi--Sugeno--Kang Fuzzy Systems with Approximately Calibrated Model-Averaged Prediction Intervals"*.

## Reproducing the results

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/experiment_v2.py
python src/figures_v2.py
```

All experiments use a fixed random seed (`SEED = 42`). Data are the UCI Energy Efficiency (id 242) and Concrete Compressive Strength (id 165) benchmarks, fetched via `ucimlrepo`.

## Method name mapping

| Manuscript name | Code class / result key |
|-----------------|-------------------------|
| TSK-LS | `TSK_LS` |
| Bayesian-TSK | `TSK_Bayesian` (conjugate Gaussian--inverse-gamma) |
| TSK-SpikeSlab-BIC | `TSK_SpikeSlab_Fast` (BIC + Laplace approximation; key `SpikeSlab-Fast`) |
| TSK-SpikeSlab-Gibbs | `TSK_SpikeSlab_Gibbs` (rule-level block-Gibbs + BMA; key `SpikeSlab-Gibbs`) |
| TSK-SSVS | `TSK_SSVS_Gibbs` (coefficient-level SSVS; key `SSVS-Gibbs`) |

## Repository structure

- `src/tsk_core.py` — TSK core implementation, fuzzy c-means, frozen training-time membership spreads, conjugate and Gibbs samplers;
- `src/experiment_v2.py` — main comparison, tau-squared sensitivity, and noise ablation;
- `src/figures_v2.py` — figure generation;
- `results/raw/` — per-split result files and data caches used by the released workflow;
- `results/figures/` — generated figures;
- `manuscript.tex`, `references.bib` — manuscript source retained for traceability;
- `docs/REPRODUCIBILITY.md` — environment and archival-release guidance.

## Reproducibility boundary

`requirements.txt` is a compatibility specification with lower-bound versions; it is not an exact historical environment lock. For the manuscript archival release, export the exact package environment from the machine/container used for the final manuscript run rather than reconstructing or guessing versions later. The archival release should also record the exact commit SHA, dataset identifiers, seed, output checksums, and the mapping between manuscript tables/figures and generated files.

## Citation

Use GitHub's **Cite this repository** function, generated from `CITATION.cff`, to cite the software repository. Once the associated article is formally published, the citation metadata can be updated with the article as the preferred citation.

## License

The source code is released under the BSD 3-Clause License. Third-party datasets and dependencies remain subject to their original terms.
