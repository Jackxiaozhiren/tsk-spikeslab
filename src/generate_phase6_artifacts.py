#!/usr/bin/env python3
"""Generate Phase 6 manuscript tables and figures from Phase 4 JSON outputs.

The manuscript-facing artifacts are deliberately derived from the recorded
JSON files. This keeps rounded values out of the experimental drivers and
prevents stale tables or figures from being silently reused.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import numpy as np


DATASETS = ["Energy-Heating", "Energy-Cooling", "Concrete"]
MAIN_METHODS = [
    "TSK-LS",
    "Bayesian-TSK",
    "TSK-SpikeSlab-BIC",
    "TSK-SpikeSlab-Gibbs",
    "RandomForest",
    "SVR",
    "GaussianProcess",
]
PROBABILISTIC_METHODS = [
    "Bayesian-TSK",
    "TSK-SpikeSlab-BIC",
    "TSK-SpikeSlab-Gibbs",
    "GaussianProcess",
]
DISPLAY_NAMES = {
    "Bayesian-TSK": "Bayesian-TSK",
    "Conformal-TSK-LS": "Conformal-TSK-LS",
    "GaussianProcess": "Gaussian Process",
    "RandomForest": "Random Forest",
    "TSK-LS": "TSK-LS",
    "TSK-SpikeSlab-BIC": "TSK-SpikeSlab-BIC",
    "TSK-SpikeSlab-Gibbs": "TSK-SpikeSlab-Gibbs",
    "SVR": "SVR",
}


def _mean(rows: list[dict[str, Any]], field: str) -> float | None:
    values = [row[field] for row in rows if row.get(field) is not None]
    if not values:
        return None
    value = float(np.mean(values))
    if not np.isfinite(value):
        raise ValueError(f"non-finite mean for {field}")
    return value


def summarize_main(payload: dict[str, Any]) -> dict[str, dict[str, dict[str, float | None]]]:
    """Return means for every dataset/method/metric in main_rebuilt.json."""

    result: dict[str, dict[str, dict[str, float | None]]] = {}
    for dataset, dataset_payload in payload["datasets"].items():
        result[dataset] = {}
        for method, method_payload in dataset_payload["methods"].items():
            rows = method_payload["rows"]
            result[dataset][method] = {
                field: _mean(rows, field)
                for field in (
                    "R2",
                    "RMSE",
                    "MAE",
                    "PICP",
                    "MPIW",
                    "WIS",
                    "CRPS",
                    "ESS_per_s",
                    "active_rule_ratio",
                    "active_rules",
                )
            }
    return result


def _fmt(value: float | None, digits: int = 3) -> str:
    if value is None:
        return "--"
    if not np.isfinite(value):
        raise ValueError("refusing to render a non-finite value")
    return f"{value:.{digits}f}"


def _method_name(method: str) -> str:
    return DISPLAY_NAMES.get(method, method)


def render_main_table(summary: dict[str, dict[str, dict[str, float | None]]]) -> str:
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Main comparison. Values are means over the 30 outer 80/20 splits. RMSE is on the original target scale; PICP is the empirical coverage of the 95\% posterior-predictive interval when available.}",
        r"\label{tab:main}",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{2.5pt}",
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{lccc|ccc|ccc}",
        r"\toprule",
        r"& \multicolumn{3}{c|}{Energy-Heating} & \multicolumn{3}{c|}{Energy-Cooling} & \multicolumn{3}{c}{Concrete} \\",
        r"Method & $R^2$ & RMSE & PICP & $R^2$ & RMSE & PICP & $R^2$ & RMSE & PICP \\",
        r"\midrule",
    ]
    for method in MAIN_METHODS:
        cells = [_method_name(method)]
        for dataset in DATASETS:
            stats = summary[dataset][method]
            cells.extend(
                [_fmt(stats["R2"]), _fmt(stats["RMSE"]), _fmt(stats["PICP"])]
            )
        lines.append(" & ".join(cells) + r" \\")
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}%",
            r"}",
            r"\end{table}",
        ]
    )
    return "\n".join(lines) + "\n"


def render_predictive_table(
    summary: dict[str, dict[str, dict[str, float | None]]]
) -> str:
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Posterior-predictive metrics for methods that produce probabilistic intervals. WIS and CRPS are unavailable for the conformal baseline because it does not define a posterior-predictive distribution.}",
        r"\label{tab:predictive}",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{3pt}",
        r"\begin{tabular}{llrrrr}",
        r"\toprule",
        r"Target & Method & PICP & MPIW & WIS & CRPS \\",
        r"\midrule",
    ]
    for dataset in DATASETS:
        for method in PROBABILISTIC_METHODS:
            stats = summary[dataset][method]
            lines.append(
                " & ".join(
                    [
                        dataset,
                        _method_name(method),
                        _fmt(stats["PICP"]),
                        _fmt(stats["MPIW"]),
                        _fmt(stats["WIS"]),
                        _fmt(stats["CRPS"]),
                    ]
                )
                + r" \\"
            )
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}"])
    return "\n".join(lines) + "\n"


def render_mae_table(
    summary: dict[str, dict[str, dict[str, float | None]]]
) -> str:
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Mean absolute error under the rebuilt 30-split protocol.}",
        r"\label{tab:mae}",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{3pt}",
        r"\begin{tabular}{lrrr}",
        r"\toprule",
        r"Method & Energy-Heating & Energy-Cooling & Concrete \\",
        r"\midrule",
    ]
    for method in MAIN_METHODS + ["Conformal-TSK-LS"]:
        values = [summary[dataset][method]["MAE"] for dataset in DATASETS]
        lines.append(
            f"{_method_name(method)} & "
            + " & ".join(_fmt(value) for value in values)
            + r" \\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}"])
    return "\n".join(lines) + "\n"


def render_conformal_table(
    summary: dict[str, dict[str, dict[str, float | None]]]
) -> str:
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Split-conformal TSK-LS results. Calibration is performed inside each outer training split, so this row is not a posterior-predictive baseline under the same protocol as Table~\ref{tab:predictive}.}",
        r"\label{tab:conformal}",
        r"\scriptsize",
        r"\begin{tabular}{lrrr}",
        r"\toprule",
        r"Target & $R^2$ & PICP & MPIW \\",
        r"\midrule",
    ]
    for dataset in DATASETS:
        stats = summary[dataset]["Conformal-TSK-LS"]
        lines.append(
            f"{dataset} & {_fmt(stats['R2'])} & {_fmt(stats['PICP'])} & {_fmt(stats['MPIW'])} "
            + r"\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}"])
    return "\n".join(lines) + "\n"


def _load_json(results_dir: Path, name: str) -> Any:
    with (results_dir / name).open(encoding="utf-8") as handle:
        return json.load(handle)


def _resolve_results_dir(root: Path) -> Path:
    candidates = [
        root / "rebuild_results_2026-08-29_v1",
        root / "evidence",
    ]
    for candidate in candidates:
        if (candidate / "main_rebuilt.json").exists():
            return candidate
    raise FileNotFoundError("supported Phase 4 results directory not found")


def _summary_rows(payload: dict[str, Any]) -> dict[str, dict[str, float | None]]:
    return {
        method: {
            field: _mean(data.get("rows", []), field)
            for field in ("R2", "RMSE", "MAE", "PICP", "MPIW", "ESS_per_s")
        }
        for method, data in payload["methods"].items()
    }


def render_ablation_table(payload: dict[str, Any]) -> str:
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Ablation of the analytical model-selection pipeline on Energy-Cooling (10 splits, $R=5$).}",
        r"\label{tab:ablation}",
        r"\scriptsize",
        r"\begin{tabular}{lrrr}",
        r"\toprule",
        r"Configuration & $R^2$ & PICP & MPIW \\",
        r"\midrule",
    ]
    for name, values in payload.items():
        label = name.replace("-", " ")
        lines.append(
            f"{label} & {_fmt(values.get('R2'))} & {_fmt(values.get('PICP'))} & {_fmt(values.get('MPIW'))} "
            + r"\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}"])
    return "\n".join(lines) + "\n"


def render_tau2_table(payload: dict[str, list[dict[str, Any]]]) -> str:
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Coefficient-level SSVS sensitivity to the slab variance on Energy-Cooling (10 splits).}",
        r"\label{tab:tau2}",
        r"\scriptsize",
        r"\begin{tabular}{lrrrr}",
        r"\toprule",
        r"$\tau^2$ & $R^2$ & RMSE & PICP & MPIW \\",
        r"\midrule",
    ]
    for tau in sorted(payload, key=float):
        rows = payload[tau]
        stats = {
            field: _mean(rows, field) for field in ("R2", "RMSE", "PICP", "MPIW")
        }
        lines.append(
            f"{tau} & {_fmt(stats['R2'])} & {_fmt(stats['RMSE'])} & {_fmt(stats['PICP'])} & {_fmt(stats['MPIW'])} "
            + r"\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}"])
    return "\n".join(lines) + "\n"


def render_noise_table(payload: dict[str, dict[str, dict[str, Any]]]) -> str:
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Irrelevant-feature ablation on Energy-Cooling. Each row appends standard-normal noise features to the eight original inputs.}",
        r"\label{tab:noise}",
        r"\scriptsize",
        r"\begin{tabular}{lrrr}",
        r"\toprule",
        r"Appended features & TSK-LS & Rule-Gibbs & Coefficient-SSVS \\",
        r"\midrule",
    ]
    for noise in sorted(payload, key=int):
        values = payload[noise]
        lines.append(
            f"{noise} & {_fmt(values['TSK-LS'].get('R2'))} & {_fmt(values['SpikeSlab-Gibbs'].get('R2'))} & {_fmt(values['SSVS-Gibbs'].get('R2'))} "
            + r"\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}"])
    return "\n".join(lines) + "\n"


def render_highdim_table(payload: dict[str, Any]) -> str:
    summary = _summary_rows(payload)
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{High-dimensional probe on Superconductivity (subsample $n=3000$, $d=81$, $R=5$, 30 splits).}",
        r"\label{tab:highdim}",
        r"\scriptsize",
        r"\begin{tabular}{lrrrr}",
        r"\toprule",
        r"Method & RMSE & $R^2$ & PICP & MPIW \\",
        r"\midrule",
    ]
    for method in [
        "TSK-LS",
        "Bayesian-TSK",
        "SpikeSlab-Gibbs",
        "SSVS-Gibbs (tau2=1)",
        "SSVS-Gibbs (tau2=10)",
    ]:
        if method not in summary:
            continue
        stats = summary[method]
        method_display = method.replace("tau2=", r"$\tau^2=$").replace("-", " ")
        lines.append(
            f"{method_display} & {_fmt(stats['RMSE'])} & {_fmt(stats['R2'])} & {_fmt(stats['PICP'])} & {_fmt(stats['MPIW'])} "
            + r"\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}"])
    return "\n".join(lines) + "\n"


def render_highdim_tau_table(payload: dict[str, Any]) -> str:
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Coefficient-level SSVS slab-variance grid on the high-dimensional probe (10 splits).}",
        r"\label{tab:highdimtau}",
        r"\scriptsize",
        r"\begin{tabular}{lrrr}",
        r"\toprule",
        r"$\tau^2$ & $R^2$ & PICP & MPIW \\",
        r"\midrule",
    ]
    for method, data in payload["methods"].items():
        if not method.startswith("SSVS tau2="):
            continue
        stats = data["summary"]
        tau = method.split("=", 1)[1]
        lines.append(
            f"{tau} & {_fmt(stats['R2']['mean'])} & {_fmt(stats['PICP']['mean'])} & {_fmt(stats['MPIW']['mean'])} "
            + r"\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}"])
    return "\n".join(lines) + "\n"


def render_active_rules_table(
    summary: dict[str, dict[str, dict[str, float | None]]]
) -> str:
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Mean active-rule ratio and Gibbs effective sample size in the main experiment.}",
        r"\label{tab:active}",
        r"\scriptsize",
        r"\begin{tabular}{lrrr}",
        r"\toprule",
        r"Target & active-rule ratio & active rules ($R=5$) & ESS/s ($\sigma^2$) \\",
        r"\midrule",
    ]
    for dataset in DATASETS:
        stats = summary[dataset]["TSK-SpikeSlab-Gibbs"]
        active_ratio = stats["active_rule_ratio"]
        active_rules = (
            None if active_ratio is None else active_ratio * 5.0
        )
        lines.append(
            f"{dataset} & {_fmt(active_ratio)} & {_fmt(active_rules, 2)} & {_fmt(stats['ESS_per_s'], 1)} "
            + r"\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}"])
    return "\n".join(lines) + "\n"


def render_diagnostics_table(payload: dict[str, Any]) -> str:
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Three-chain diagnostics for the rule-level Gibbs sampler on representative splits. Raw coefficient and predictive-quantity diagnostics are reported separately.}",
        r"\label{tab:mcmc}",
        r"\scriptsize",
        r"\begin{tabular}{lrrrrr}",
        r"\toprule",
        r"Target & raw $\hat R_\beta$ max & predictive $\hat R$ max & $\hat R_{\sigma^2}$ & ESS($\sigma^2$) & draws \\",
        r"\midrule",
    ]
    for target in ["Energy-Cooling", "Concrete"]:
        values = payload[target]
        lines.append(
            f"{target} & {_fmt(values.get('rhat_beta_max'))} & {_fmt(values.get('rhat_predictive_max'))} & {_fmt(values.get('rhat_sigma2'))} & {_fmt(values.get('ess_sigma2_mean'), 1)} & {values.get('n_samples', '--')} "
            + r"\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}"])
    return "\n".join(lines) + "\n"


def render_synthetic_table(payload: dict[str, Any]) -> str:
    # The verification output is intentionally represented as a compact table
    # of observed discrepancies, rather than retyping per-rule values.
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Synthetic enumeration check for the rule-inclusion update and BMA predictive moments.}",
        r"\label{tab:synthetic}",
        r"\scriptsize",
        r"\begin{tabular}{lr}",
        r"\toprule",
        r"Quantity & Maximum absolute or relative discrepancy \\",
        r"\midrule",
    ]
    fields = [
        ("max_abs_diff_pip", "PIP maximum absolute difference"),
        ("bma_max_abs_mean_diff", "BMA mean maximum absolute difference"),
        ("bma_median_rel_var_diff", "BMA median relative variance difference"),
    ]
    for key, label in fields:
        value = payload.get(key)
        if isinstance(value, (int, float)):
            lines.append(f"{label} & {_fmt(float(value), 4)} " + r"\\")
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}"])
    return "\n".join(lines) + "\n"


def _save_figure(fig: Any, figure_dir: Path, stem: str) -> None:
    figure_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(figure_dir / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(figure_dir / f"{stem}.png", dpi=180, bbox_inches="tight")


def generate_figures(
    summary: dict[str, dict[str, dict[str, float | None]]],
    tau2_payload: dict[str, list[dict[str, Any]]],
    noise_payload: dict[str, dict[str, dict[str, Any]]],
    figure_dir: Path,
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.size": 9, "axes.titlesize": 10, "axes.labelsize": 9})

    fig, ax = plt.subplots(figsize=(8.0, 4.2))
    x = np.arange(len(DATASETS))
    width = 0.11
    for i, method in enumerate(MAIN_METHODS):
        values = [summary[dataset][method]["R2"] for dataset in DATASETS]
        ax.bar(
            x + (i - (len(MAIN_METHODS) - 1) / 2) * width,
            values,
            width,
            label=_method_name(method),
        )
    ax.set_xticks(x, DATASETS)
    ax.set_ylabel(r"$R^2$")
    ax.set_ylim(0, 1.05)
    ax.set_title("Predictive accuracy under the rebuilt protocol")
    ax.legend(ncol=2, fontsize=7, frameon=False)
    ax.grid(axis="y", alpha=0.25)
    _save_figure(fig, figure_dir, "fig_main_comparison")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.0, 4.2))
    cal_methods = [
        "Bayesian-TSK",
        "TSK-SpikeSlab-BIC",
        "TSK-SpikeSlab-Gibbs",
        "GaussianProcess",
        "Conformal-TSK-LS",
    ]
    width = 0.15
    for i, method in enumerate(cal_methods):
        values = [summary[dataset][method]["PICP"] for dataset in DATASETS]
        ax.bar(
            x + (i - (len(cal_methods) - 1) / 2) * width,
            values,
            width,
            label=_method_name(method),
        )
    ax.axhline(0.95, color="black", linestyle="--", linewidth=1, label="nominal 95%")
    ax.set_xticks(x, DATASETS)
    ax.set_ylabel("PICP")
    ax.set_ylim(0.88, 1.0)
    ax.set_title("Empirical coverage of reported 95% intervals")
    ax.legend(ncol=2, fontsize=7, frameon=False)
    ax.grid(axis="y", alpha=0.25)
    _save_figure(fig, figure_dir, "fig_calibration")
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(8.0, 3.5))
    tau_values = sorted((float(key), key) for key in tau2_payload)
    tau_means = [
        float(np.mean([row["R2"] for row in tau2_payload[key]]))
        for _, key in tau_values
    ]
    axes[0].plot([item[0] for item in tau_values], tau_means, marker="o")
    axes[0].axhline(
        summary["Energy-Cooling"]["TSK-LS"]["R2"],
        color="black",
        linestyle="--",
        label="TSK-LS",
    )
    axes[0].set_xscale("log")
    axes[0].set_xlabel(r"SSVS slab variance $\tau^2$")
    axes[0].set_ylabel(r"$R^2$")
    axes[0].set_title("Coefficient-level sensitivity")
    axes[0].grid(alpha=0.25)
    axes[0].legend(frameon=False, fontsize=8)

    noise_values = sorted((int(key), key) for key in noise_payload)
    for method, label in [
        ("TSK-LS", "TSK-LS"),
        ("SpikeSlab-Gibbs", "Rule-Gibbs"),
        ("SSVS-Gibbs", "Coefficient-SSVS"),
    ]:
        axes[1].plot(
            [item[0] for item in noise_values],
            [noise_payload[key][method]["R2"] for _, key in noise_values],
            marker="o",
            label=label,
        )
    axes[1].set_xlabel("Appended noise features")
    axes[1].set_ylabel(r"$R^2$")
    axes[1].set_title("Irrelevant-feature probe")
    axes[1].grid(alpha=0.25)
    axes[1].legend(frameon=False, fontsize=8)
    fig.tight_layout()
    _save_figure(fig, figure_dir, "fig_sparsity_boundary")
    plt.close(fig)


def write_artifacts(root: Path, output_dir: Path) -> list[Path]:
    results_dir = _resolve_results_dir(root)
    output_dir.mkdir(parents=True, exist_ok=True)
    table_dir = output_dir / "tables"
    figure_dir = output_dir / "figures"
    table_dir.mkdir(parents=True, exist_ok=True)

    main_payload = _load_json(results_dir, "main_rebuilt.json")
    summary = summarize_main(main_payload)
    tau2_payload = _load_json(results_dir, "tier2_tau2_v2.json")
    noise_payload = _load_json(results_dir, "tier3_noise_v2.json")
    artifacts = {
        "main_table.tex": render_main_table(summary),
        "mae_table.tex": render_mae_table(summary),
        "active_rules_table.tex": render_active_rules_table(summary),
        "predictive_table.tex": render_predictive_table(summary),
        "conformal_table.tex": render_conformal_table(summary),
        "ablation_table.tex": render_ablation_table(
            _load_json(results_dir, "ablation_isolate_v2.json")
        ),
        "tau2_table.tex": render_tau2_table(tau2_payload),
        "noise_table.tex": render_noise_table(noise_payload),
        "highdim_table.tex": render_highdim_table(
            _load_json(results_dir, "highdim_sparsity.json")
        ),
        "highdim_tau_table.tex": render_highdim_tau_table(
            _load_json(results_dir, "highdim_tau2_grid.json")
        ),
        "diagnostics_table.tex": render_diagnostics_table(
            _load_json(results_dir, "mcmc_diagnostics.json")
        ),
        "synthetic_table.tex": render_synthetic_table(
            _load_json(results_dir, "synthetic_gamma_verify.json")
        ),
    }
    written = []
    for name, content in artifacts.items():
        path = table_dir / name
        path.write_text(content, encoding="utf-8")
        written.append(path)
    generate_figures(summary, tau2_payload, noise_payload, figure_dir)
    written.extend(sorted(table_dir.glob("*.tex")))
    written.extend(sorted(figure_dir.glob("fig_*.pdf")))
    written.extend(sorted(figure_dir.glob("fig_*.png")))
    return sorted(set(written))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output_dir = args.output_dir or Path(
        os.environ.get("TSK_OUTPUT_DIR", root / "rebuild_results_2026-08-29_v1")
    )
    paths = write_artifacts(root, output_dir)
    print(f"generated {len(paths)} Phase 6 artifacts in {output_dir}")


if __name__ == "__main__":
    main()
