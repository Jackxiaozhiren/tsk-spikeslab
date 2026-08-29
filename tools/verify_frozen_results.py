"""Verify frozen ASOC result checksums and selected manuscript-active values."""
from __future__ import annotations
import hashlib, json, math
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / "evidence"

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def close(actual, expected, tol=1e-12):
    if not math.isclose(float(actual), float(expected), rel_tol=0.0, abs_tol=tol):
        raise AssertionError(f"value mismatch: {actual!r} != {expected!r}")

def main():
    manifest = EVIDENCE / "RESULTS_MANIFEST.sha256"
    checked = 0
    for raw in manifest.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        expected, rel = raw.split(None, 1)
        path = EVIDENCE / rel.strip()
        if not path.is_file():
            raise FileNotFoundError(path)
        actual = sha256(path)
        if actual != expected:
            raise AssertionError(f"checksum mismatch for {rel}: {actual} != {expected}")
        checked += 1

    main_payload = json.loads((EVIDENCE / "main_rebuilt.json").read_text())
    def mean(ds, method, metric):
        return main_payload["datasets"][ds]["methods"][method]["summary"][metric]["mean"]
    close(mean("Energy-Heating", "TSK-LS", "R2"), 0.9570422336863281)
    close(mean("Energy-Cooling", "TSK-LS", "R2"), 0.9228993765919412)
    close(mean("Concrete", "TSK-LS", "R2"), 0.7858915135552952)
    close(mean("Energy-Heating", "TSK-SpikeSlab-Gibbs", "R2"), 0.9567254873068926)
    close(mean("Energy-Cooling", "TSK-SpikeSlab-Gibbs", "PICP"), 0.9337690631808279)
    close(mean("Concrete", "GaussianProcess", "R2"), 0.8890639757362924)

    diag = json.loads((EVIDENCE / "mcmc_diagnostics.json").read_text())
    close(diag["Energy-Cooling"]["rhat_beta_max"], 1.060882950587297)
    close(diag["Concrete"]["rhat_beta_max"], 1.0301546979822636)

    syn = json.loads((EVIDENCE / "synthetic_gamma_verify.json").read_text())
    close(syn["max_abs_diff_pip"], 0.02609532436761608)
    close(syn["bma_max_abs_mean_diff"], 0.022373800905861163)
    close(syn["bma_median_rel_var_diff"], 0.0026823024632596087)

    ab = json.loads((EVIDENCE / "ablation_isolate_v2.json").read_text())
    if any(float(v["R2"]) <= 0 for v in ab.values()):
        raise AssertionError("repaired BIC ablation unexpectedly contains non-positive R2")

    forbidden = list(ROOT.rglob("*.npz"))
    if forbidden:
        raise AssertionError(f"public release contains excluded NPZ cache(s): {forbidden}")

    print(f"Frozen result verification passed: {checked} checksummed files + headline gates")

if __name__ == "__main__":
    main()
