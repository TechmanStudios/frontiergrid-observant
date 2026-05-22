"""Aggregate randomized ablation runs for Phase I stress evidence."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean
from typing import Any

from frontiergrid_observant.config import load_settings
from frontiergrid_observant.eval.ablation_study import (
    ABLATION_MODES,
    MODE_DESCRIPTIONS,
    build_ablation_study,
)
from frontiergrid_observant.ingest.synthetic_generator import SCENARIOS

METRIC_KEYS = (
    "precision",
    "sensitivity",
    "miss_rate",
    "false_discovery_rate",
    "analytic_completeness",
    "validity",
    "consistency",
    "context_geodesic_alignment",
    "active_domain_coverage",
    "domain_contribution_balance",
    "candidate_team_completeness",
    "uncertainty_pressure",
)

DELTA_KEYS = (
    "first_alert_tick_delta",
    "precision_delta",
    "sensitivity_delta",
    "miss_rate_delta",
    "false_discovery_rate_delta",
    "analytic_completeness_delta",
    "context_geodesic_alignment_delta",
)

PROGRESS_FILENAME = "monte_carlo_progress.json"


def build_stress_study(
    *,
    seed: int = 149,
    runs: int = 5,
    ticks: int = 30,
    scenarios: list[str] | None = None,
    modes: tuple[str, ...] = ABLATION_MODES,
    seed_stride: int = 100,
    progress: bool = False,
    progress_artifact_root: Path | None = None,
    refresh_dashboard: bool = False,
) -> dict[str, Any]:
    """Run repeated ablation studies and aggregate proposal-facing metrics."""
    if runs < 1:
        raise ValueError("runs must be at least 1")

    scenario_keys = scenarios or sorted(SCENARIOS)
    records: list[dict[str, Any]] = []
    started_at = _timestamp()
    _write_progress_if_requested(
        progress_artifact_root,
        refresh_dashboard,
        seed=seed,
        seed_stride=seed_stride,
        ticks=ticks,
        runs=runs,
        completed_runs=0,
        current_run=1,
        current_seed=seed,
        scenario_keys=scenario_keys,
        modes=modes,
        records=records,
        status="running",
        started_at=started_at,
        message="Starting Monte Carlo sweep.",
    )
    for run_index in range(runs):
        run_seed = seed + run_index * seed_stride
        if progress:
            print(f"Running stress run {run_index + 1}/{runs} with seed {run_seed}...", flush=True)
        _write_progress_if_requested(
            progress_artifact_root,
            refresh_dashboard,
            seed=seed,
            seed_stride=seed_stride,
            ticks=ticks,
            runs=runs,
            completed_runs=run_index,
            current_run=run_index + 1,
            current_seed=run_seed,
            scenario_keys=scenario_keys,
            modes=modes,
            records=records,
            status="running",
            started_at=started_at,
            message=f"Running stress run {run_index + 1} of {runs}.",
        )
        ablation = build_ablation_study(
            seed=run_seed,
            ticks=ticks,
            scenarios=scenario_keys,
            modes=modes,
        )
        records.extend(_records_from_ablation(ablation, run_index=run_index, run_seed=run_seed))
        next_run = run_index + 2 if run_index + 1 < runs else None
        next_seed = seed + (run_index + 1) * seed_stride if next_run is not None else None
        _write_progress_if_requested(
            progress_artifact_root,
            refresh_dashboard,
            seed=seed,
            seed_stride=seed_stride,
            ticks=ticks,
            runs=runs,
            completed_runs=run_index + 1,
            current_run=next_run,
            current_seed=next_seed,
            last_completed_seed=run_seed,
            scenario_keys=scenario_keys,
            modes=modes,
            records=records,
            status="running" if next_run is not None else "finalizing",
            started_at=started_at,
            message=f"Completed stress run {run_index + 1} of {runs}.",
        )

    study = {
        "study": "observant_randomized_stress_study",
        "seed": seed,
        "seed_stride": seed_stride,
        "runs": runs,
        "ticks": ticks,
        "scenarios": scenario_keys,
        "modes": list(modes),
        "mode_descriptions": {mode: MODE_DESCRIPTIONS[mode] for mode in modes},
        "summary": _summarize_records(records, modes),
        "deltas_vs_rule_only": _summarize_deltas(records, modes),
        "records": records,
        "interpretation_guardrail": (
            "Randomized synthetic stress evidence; use to compare feasibility trends, "
            "not to claim operational performance."
        ),
    }
    _write_progress_if_requested(
        progress_artifact_root,
        refresh_dashboard,
        seed=seed,
        seed_stride=seed_stride,
        ticks=ticks,
        runs=runs,
        completed_runs=runs,
        current_run=None,
        current_seed=None,
        last_completed_seed=seed + (runs - 1) * seed_stride if runs else None,
        scenario_keys=scenario_keys,
        modes=modes,
        records=records,
        status="completed",
        started_at=started_at,
        summary=study["summary"],
        message="Monte Carlo sweep complete.",
    )
    return study


def export_stress_study(
    *,
    seed: int = 149,
    runs: int = 5,
    ticks: int = 30,
    artifact_root: Path | None = None,
    modes: tuple[str, ...] = ABLATION_MODES,
    seed_stride: int = 100,
    progress: bool = False,
    refresh_dashboard: bool = False,
) -> dict[str, Any]:
    root = artifact_root or load_settings().artifact_root
    study = build_stress_study(
        seed=seed,
        runs=runs,
        ticks=ticks,
        modes=modes,
        seed_stride=seed_stride,
        progress=progress,
        progress_artifact_root=root,
        refresh_dashboard=refresh_dashboard,
    )
    write_stress_artifacts(study, root)
    return study


def write_stress_artifacts(study: dict[str, Any], artifact_root: Path) -> tuple[Path, Path]:
    artifact_root.mkdir(parents=True, exist_ok=True)
    metrics_path = artifact_root / "stress_study_metrics.json"
    report_path = artifact_root / "stress_study_report.md"
    metrics_path.write_text(json.dumps(study, indent=2, default=str), encoding="utf-8")
    report_path.write_text(_stress_markdown(study), encoding="utf-8")
    return metrics_path, report_path


def write_progress_artifact(progress_payload: dict[str, Any], artifact_root: Path) -> Path:
    artifact_root.mkdir(parents=True, exist_ok=True)
    progress_path = artifact_root / PROGRESS_FILENAME
    temp_path = artifact_root / f"{PROGRESS_FILENAME}.tmp"
    temp_path.write_text(json.dumps(progress_payload, indent=2, default=str), encoding="utf-8")
    temp_path.replace(progress_path)
    return progress_path


def _records_from_ablation(
    ablation: dict[str, Any], *, run_index: int, run_seed: int
) -> list[dict[str, Any]]:
    records = []
    for scenario in ablation["scenarios"]:
        rule_only = scenario["modes"].get("rule_only")
        for mode in ablation["modes"]:
            result = scenario["modes"][mode]
            first_alert = result.get("first_alert") or {}
            metrics = result["metrics"]
            record = {
                "run_index": run_index,
                "run_seed": run_seed,
                "scenario_key": scenario["scenario_key"],
                "scenario_id": scenario["scenario_id"],
                "mode": mode,
                "alert_count": result["alert_count"],
                "first_alert_tick": result["first_alert_tick"],
                "first_alert_status": first_alert.get("status"),
                "first_alert_severity": first_alert.get("severity"),
                "first_alert_confidence": first_alert.get("confidence"),
                "evidence_complete": bool(
                    first_alert.get("all_agent_evidence_present")
                    or first_alert.get("expected_agent_evidence_complete")
                ),
                "metrics": {key: metrics[key] for key in METRIC_KEYS},
            }
            if rule_only and mode != "rule_only":
                record["delta_vs_rule_only"] = _delta_record(result, rule_only)
            records.append(record)
    return records


def _write_progress_if_requested(
    artifact_root: Path | None,
    refresh_dashboard: bool,
    *,
    seed: int,
    seed_stride: int,
    ticks: int,
    runs: int,
    completed_runs: int,
    current_run: int | None,
    current_seed: int | None,
    scenario_keys: list[str],
    modes: tuple[str, ...],
    records: list[dict[str, Any]],
    status: str,
    started_at: str,
    message: str,
    last_completed_seed: int | None = None,
    summary: dict[str, Any] | None = None,
) -> None:
    if artifact_root is None:
        return
    payload = _progress_payload(
        seed=seed,
        seed_stride=seed_stride,
        ticks=ticks,
        runs=runs,
        completed_runs=completed_runs,
        current_run=current_run,
        current_seed=current_seed,
        last_completed_seed=last_completed_seed,
        scenario_keys=scenario_keys,
        modes=modes,
        records=records,
        status=status,
        started_at=started_at,
        summary=summary,
        message=message,
    )
    write_progress_artifact(payload, artifact_root)
    if refresh_dashboard:
        _refresh_dashboard(artifact_root)


def _progress_payload(
    *,
    seed: int,
    seed_stride: int,
    ticks: int,
    runs: int,
    completed_runs: int,
    current_run: int | None,
    current_seed: int | None,
    last_completed_seed: int | None,
    scenario_keys: list[str],
    modes: tuple[str, ...],
    records: list[dict[str, Any]],
    status: str,
    started_at: str,
    message: str,
    summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    total_samples = runs * len(scenario_keys) * len(modes)
    samples_completed = len(records)
    percent_complete = completed_runs / runs if runs else 0.0
    return {
        "artifact": "monte_carlo_progress",
        "status": status,
        "message": message,
        "seed": seed,
        "seed_stride": seed_stride,
        "ticks": ticks,
        "runs": runs,
        "completed_runs": completed_runs,
        "current_run": current_run,
        "current_seed": current_seed,
        "last_completed_seed": last_completed_seed,
        "scenarios": scenario_keys,
        "modes": list(modes),
        "samples_completed": samples_completed,
        "total_samples": total_samples,
        "percent_complete": round(max(0.0, min(1.0, percent_complete)), 3),
        "started_at": started_at,
        "updated_at": _timestamp(),
        "partial_summary": summary if summary is not None else _summarize_records(records, modes),
    }


def _refresh_dashboard(artifact_root: Path) -> None:
    try:
        from frontiergrid_observant.demo.dashboard import export_demo_dashboard

        export_demo_dashboard(artifact_root)
    except Exception:
        return


def _delta_record(result: dict[str, Any], baseline: dict[str, Any]) -> dict[str, float | None]:
    return {
        "first_alert_tick_delta": _delta(result["first_alert_tick"], baseline["first_alert_tick"]),
        "precision_delta": _delta(result["metrics"]["precision"], baseline["metrics"]["precision"]),
        "sensitivity_delta": _delta(
            result["metrics"]["sensitivity"], baseline["metrics"]["sensitivity"]
        ),
        "miss_rate_delta": _delta(result["metrics"]["miss_rate"], baseline["metrics"]["miss_rate"]),
        "false_discovery_rate_delta": _delta(
            result["metrics"]["false_discovery_rate"],
            baseline["metrics"]["false_discovery_rate"],
        ),
        "analytic_completeness_delta": _delta(
            result["metrics"]["analytic_completeness"],
            baseline["metrics"]["analytic_completeness"],
        ),
        "context_geodesic_alignment_delta": _delta(
            result["metrics"]["context_geodesic_alignment"],
            baseline["metrics"]["context_geodesic_alignment"],
        ),
    }


def _summarize_records(records: list[dict[str, Any]], modes: tuple[str, ...]) -> dict[str, Any]:
    summary = {}
    for mode in modes:
        mode_records = [record for record in records if record["mode"] == mode]
        summary[mode] = {
            "samples": len(mode_records),
            "avg_alert_count": _avg(record["alert_count"] for record in mode_records),
            "avg_first_alert_tick": _avg_optional(
                record["first_alert_tick"] for record in mode_records
            ),
            "avg_first_alert_severity": _avg_optional(
                record["first_alert_severity"] for record in mode_records
            ),
            "avg_first_alert_confidence": _avg_optional(
                record["first_alert_confidence"] for record in mode_records
            ),
            "evidence_complete_rate": _avg(
                1.0 if record["evidence_complete"] else 0.0 for record in mode_records
            ),
            **{
                f"avg_{key}": _avg(record["metrics"][key] for record in mode_records)
                for key in METRIC_KEYS
            },
        }
    return summary


def _summarize_deltas(records: list[dict[str, Any]], modes: tuple[str, ...]) -> dict[str, Any]:
    deltas = {}
    for mode in modes:
        if mode == "rule_only":
            continue
        mode_deltas = [
            record["delta_vs_rule_only"]
            for record in records
            if record["mode"] == mode and "delta_vs_rule_only" in record
        ]
        deltas[mode] = {
            key: _avg_optional(delta[key] for delta in mode_deltas) for key in DELTA_KEYS
        }
    return deltas


def _stress_markdown(study: dict[str, Any]) -> str:
    lines = [
        "# Observant-AI Randomized Stress Study",
        "",
        f"Seed: {study['seed']}",
        f"Runs: {study['runs']}",
        f"Seed stride: {study['seed_stride']}",
        f"Ticks per scenario: {study['ticks']}",
        "",
        f"Guardrail: {study['interpretation_guardrail']}",
        "",
        "## Mode Averages",
        "",
        "| Mode | Samples | Avg alerts | Avg first tick | Alignment | Domains | Team | Precision | Sensitivity | Miss rate | FDR | Analytic completeness | Evidence complete |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for mode in study["modes"]:
        summary = study["summary"][mode]
        lines.append(
            "| "
            f"{mode} | "
            f"{summary['samples']} | "
            f"{_display(summary['avg_alert_count'])} | "
            f"{_display(summary['avg_first_alert_tick'])} | "
            f"{_display(summary['avg_context_geodesic_alignment'])} | "
            f"{_display(summary['avg_active_domain_coverage'])} | "
            f"{_display(summary['avg_candidate_team_completeness'])} | "
            f"{_display(summary['avg_precision'])} | "
            f"{_display(summary['avg_sensitivity'])} | "
            f"{_display(summary['avg_miss_rate'])} | "
            f"{_display(summary['avg_false_discovery_rate'])} | "
            f"{_display(summary['avg_analytic_completeness'])} | "
            f"{_display(summary['evidence_complete_rate'])} |"
        )

    lines.extend(
        [
            "",
            "## Average Deltas Vs Rule-Only",
            "",
            "Negative first-tick delta means the mode alerted earlier than rule-only on average.",
            "",
            "| Mode | First tick delta | Precision delta | Sensitivity delta | Miss-rate delta | FDR delta | Analytic completeness delta | Alignment delta |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for mode, delta in study["deltas_vs_rule_only"].items():
        lines.append(
            "| "
            f"{mode} | "
            f"{_display(delta['first_alert_tick_delta'])} | "
            f"{_display(delta['precision_delta'])} | "
            f"{_display(delta['sensitivity_delta'])} | "
            f"{_display(delta['miss_rate_delta'])} | "
            f"{_display(delta['false_discovery_rate_delta'])} | "
            f"{_display(delta['analytic_completeness_delta'])} |"
            f" {_display(delta['context_geodesic_alignment_delta'])} |"
        )

    return "\n".join(lines).strip() + "\n"


def _timestamp() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def _avg(values: Any) -> float:
    collected = [float(value) for value in values]
    return round(mean(collected), 3) if collected else 0.0


def _avg_optional(values: Any) -> float | None:
    collected = [float(value) for value in values if value is not None]
    return round(mean(collected), 3) if collected else None


def _delta(left: float | int | None, right: float | int | None) -> float | None:
    if left is None or right is None:
        return None
    return round(float(left) - float(right), 3)


def _display(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Export randomized Observant-AI stress study artifacts."
    )
    parser.add_argument("--seed", type=int, default=149)
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--seed-stride", type=int, default=100)
    parser.add_argument("--ticks", type=int, default=30)
    parser.add_argument("--artifact-root", type=Path, default=None)
    parser.add_argument(
        "--refresh-dashboard",
        action="store_true",
        help="Update the static dashboard after each Monte Carlo run boundary.",
    )
    parser.add_argument(
        "--modes",
        nargs="+",
        choices=ABLATION_MODES,
        default=list(ABLATION_MODES),
    )
    args = parser.parse_args(argv)

    study = export_stress_study(
        seed=args.seed,
        runs=args.runs,
        ticks=args.ticks,
        artifact_root=args.artifact_root,
        modes=tuple(args.modes),
        seed_stride=args.seed_stride,
        progress=True,
        refresh_dashboard=args.refresh_dashboard,
    )
    print(
        json.dumps(
            {
                "study": study["study"],
                "runs": study["runs"],
                "samples": len(study["records"]),
                "modes": args.modes,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
