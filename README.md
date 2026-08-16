# Exact Bayesian Inference for Spike-and-Slab Priors in TSK Fuzzy Systems

Companion code for *"Exact Bayesian Inference for Spike-and-Slab Priors in Takagi--Sugeno--Kang Fuzzy Systems with Approximately Calibrated Model-Averaged Prediction Intervals"*.

## Reproducing the results

```bash
pip install -r requirements.txt
python src/experiment_v2.py   # runs the main comparison, tau^2 sensitivity, and noise ablation
python src/figures_v2.py      # regenerates Figures 1--4 from results/raw/
```

All experiments use a fixed random seed (`SEED = 42`). Data are the UCI Energy Efficiency (id 242) and Concrete Compressive Strength (id 165) benchmarks, fetched via `ucimlrepo`.

## Method name mapping

The manuscript method names map to the released classes in `src/tsk_core.py` as follows:

| Manuscript name | Code class / result key |
|-----------------|-------------------------|
| TSK-LS          | `TSK_LS`                |
| Bayesian-TSK    | `TSK_Bayesian` (conjugate Gaussian--inverse-gamma) |
| TSK-SpikeSlab-BIC | `TSK_SpikeSlab_Fast` (BIC + Laplace approximation; key `SpikeSlab-Fast`) |
| TSK-SpikeSlab-Gibbs | `TSK_SpikeSlab_Gibbs` (rule-level block-Gibbs + BMA; key `SpikeSlab-Gibbs`) |
| TSK-SSVS        | `TSK_SSVS_Gibbs` (coefficient-level SSVS; key `SSVS-Gibbs`) |

## Structure

- `src/tsk_core.py` — corrected TSK core: true fuzzy c-means, frozen training-time membership spreads, conjugate and Gibbs samplers.
- `src/experiment_v2.py` — experiment drivers (main comparison, τ² sensitivity, noise ablation).
- `src/figures_v2.py` — figure generation.
- `results/raw/` — per-split results (JSON) and data caches (NPZ).
