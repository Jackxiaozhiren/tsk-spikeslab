# Reproducibility

## Core reproduction path

The released workflow uses:

```bash
pip install -r requirements.txt
python src/experiment_v2.py
python src/figures_v2.py
```

The experiments use `SEED = 42` and obtain the UCI Energy Efficiency (id 242) and Concrete Compressive Strength (id 165) datasets through `ucimlrepo`.

## Environment policy

The current `requirements.txt` declares compatible lower bounds and is suitable for ordinary installation, but it is not proof of the exact package versions used for the manuscript results.

For the archival manuscript release, export the exact environment from the machine or container used for the final run (for example, a `pip freeze`/lock file or an exact Conda environment). Do not infer or fabricate historical package versions after the fact.

## Archival release checklist

Before assigning a DOI to the manuscript reproducibility release:

1. record the exact Git commit SHA;
2. record Python, OS, and exact dependency versions;
3. record the dataset IDs and retrieval date/version information available from the provider;
4. verify that `SEED = 42` and all experiment hyperparameters match the manuscript;
5. regenerate the manuscript figures/tables from a clean environment;
6. record SHA-256 checksums for the released result files and publication figures;
7. document any platform-dependent numerical tolerance;
8. tag the verified state as a semantic version (recommended `v1.0.0`) and archive that tag in a DOI-issuing repository.

## CI versus manuscript reproduction

Continuous integration is intentionally a fast structural/smoke check. It verifies that the source compiles and imports; it is not a substitute for the full manuscript experiment, which downloads benchmark data and performs computationally heavier Bayesian experiments.
