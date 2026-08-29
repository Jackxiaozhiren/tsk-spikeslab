# Public Release Boundary — ASOC v2.0.0

## Included

- corrected source code under `src/`;
- correctness/regression tests under `tests/`;
- ASOC manuscript/supplement source and current generated tables/figures;
- frozen rebuilt result JSON/log files listed in `evidence/RESULTS_MANIFEST.sha256`;
- claim/evidence, environment, data-availability, and reproducibility documentation;
- deterministic Git-tracked release manifest generation and CI verification.

## Excluded

- raw UCI downloads and cached `.npz` arrays;
- old `results/` and old `submission_package/` trees from the historical manuscript route;
- internal prompts, reviewer simulations, rejection-risk analyses, editorial-management files, and private workflow notes;
- virtual environments, caches, LaTeX build intermediates, and machine-specific paths.

The historical `v1.0` tag/release remains available and is not rewritten.
