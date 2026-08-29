import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _main_results_path() -> Path:
    candidates = [
        ROOT / "rebuild_results_2026-08-29_v1" / "main_rebuilt.json",
        ROOT / "evidence" / "main_rebuilt.json",
    ]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError("main_rebuilt.json not found in supported layouts")


def test_phase6_artifact_summary_uses_all_main_methods():
    from src.generate_phase6_artifacts import summarize_main

    payload = json.loads(
        _main_results_path().read_text()
    )
    summary = summarize_main(payload)

    assert set(summary) == {"Energy-Heating", "Energy-Cooling", "Concrete"}
    assert set(summary["Energy-Cooling"]) >= {
        "TSK-LS",
        "Bayesian-TSK",
        "TSK-SpikeSlab-BIC",
        "TSK-SpikeSlab-Gibbs",
        "GaussianProcess",
        "Conformal-TSK-LS",
    }
    assert summary["Energy-Cooling"]["TSK-LS"]["R2"] == 0.9228993765919412


def test_phase6_generated_tex_contains_no_nonfinite_tokens():
    from src.generate_phase6_artifacts import render_main_table, summarize_main

    payload = json.loads(
        _main_results_path().read_text()
    )
    tex = render_main_table(summarize_main(payload))
    assert "nan" not in tex.lower()
    assert "inf" not in tex.lower()
    assert "0.923" in tex
