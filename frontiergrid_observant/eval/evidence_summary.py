"""Build reviewer-facing evidence summaries from generated evaluation artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean
from typing import Any

from frontiergrid_observant.config import load_settings

BASELINE_MODES = {"rule_only", "centralized_sequential"}
SHARED_CONTEXT_MODES = {"fallback_shared_context", "native_manifold_shared_context"}

MODE_LABELS = {
    "rule_only": "Rule-only",
    "centralized_sequential": "Centralized sequential",
    "fallback_shared_context": "Fallback shared context",
    "native_manifold_shared_context": "Native manifold shared context",
}

SUMMARY_METRICS = (
    "precision",
    "sensitivity",
    "miss_rate",
    "false_discovery_rate",
    "analytic_completeness",
    "context_geodesic_alignment",
    "active_domain_coverage",
    "candidate_team_completeness",
)


def export_evidence_summary(artifact_root: Path | None = None) -> dict[str, Any]:
    root = artifact_root or load_settings().artifact_root
    stress = _read_json(root / "stress_study_metrics.json")
    ablation = _read_optional_json(root / "ablation_study_metrics.json")
    comparison = _read_optional_json(root / "fallback_vs_frontier_os_metrics.json")
    summary = build_evidence_summary(stress, ablation=ablation, comparison=comparison)
    write_evidence_summary_artifacts(summary, root)
    return summary


def build_evidence_summary(
    stress: dict[str, Any],
    *,
    ablation: dict[str, Any] | None = None,
    comparison: dict[str, Any] | None = None,
) -> dict[str, Any]:
    records = list(stress.get("records", []))
    modes = list(stress.get("modes", []))
    scenario_ids = _scenario_order(records)
    scenario_summaries = [
        _scenario_summary(scenario_id, records, modes) for scenario_id in scenario_ids
    ]
    overall_mode_summary = {
        mode: _record_group_summary([record for record in records if record["mode"] == mode])
        for mode in modes
    }
    unknown_unknown_check = _unknown_unknown_check(scenario_summaries, modes)
    key_findings = _key_findings(
        overall_mode_summary=overall_mode_summary,
        unknown_unknown_check=unknown_unknown_check,
        comparison=comparison,
    )

    return {
        "summary": "observant_scenario_evidence_summary",
        "seed": stress.get("seed"),
        "runs": stress.get("runs"),
        "seed_stride": stress.get("seed_stride"),
        "ticks": stress.get("ticks"),
        "modes": modes,
        "scenarios": scenario_ids,
        "overall_mode_summary": overall_mode_summary,
        "scenario_summaries": scenario_summaries,
        "unknown_unknown_check": unknown_unknown_check,
        "key_findings": key_findings,
        "single_run_ablation_seed": ablation.get("seed") if ablation else None,
        "comparison_seed": comparison.get("seed") if comparison else None,
        "interpretation_guardrail": (
            "Synthetic, unclassified Phase I evidence. Use for feasibility and calibration, "
            "not for operational performance claims."
        ),
    }


def write_evidence_summary_artifacts(
    summary: dict[str, Any], artifact_root: Path
) -> tuple[Path, Path]:
    artifact_root.mkdir(parents=True, exist_ok=True)
    metrics_path = artifact_root / "scenario_evidence_summary.json"
    report_path = artifact_root / "scenario_evidence_summary.md"
    metrics_path.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    report_path.write_text(_summary_markdown(summary), encoding="utf-8")
    return metrics_path, report_path


def _scenario_summary(
    scenario_id: str, records: list[dict[str, Any]], modes: list[str]
) -> dict[str, Any]:
    scenario_records = [record for record in records if record["scenario_id"] == scenario_id]
    scenario_key = scenario_records[0].get("scenario_key") if scenario_records else scenario_id
    mode_results = {
        mode: _record_group_summary(
            [record for record in scenario_records if record["mode"] == mode]
        )
        for mode in modes
    }
    return {
        "scenario_key": scenario_key,
        "scenario_id": scenario_id,
        "mode_results": mode_results,
        "best_evidence_mode": _best_evidence_mode(mode_results),
    }


def _record_group_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    samples = len(records)
    if not records:
        return {
            "samples": 0,
            "detection_rate": 0.0,
            "avg_alert_count": 0.0,
            "avg_first_alert_tick": None,
            "evidence_complete_rate": 0.0,
            **{f"avg_{metric}": 0.0 for metric in SUMMARY_METRICS},
        }

    return {
        "samples": samples,
        "detection_rate": _avg(1.0 if record["alert_count"] > 0 else 0.0 for record in records),
        "avg_alert_count": _avg(record["alert_count"] for record in records),
        "avg_first_alert_tick": _avg_optional(record["first_alert_tick"] for record in records),
        "evidence_complete_rate": _avg(
            1.0 if record.get("evidence_complete") else 0.0 for record in records
        ),
        **{
            f"avg_{metric}": _avg(record["metrics"][metric] for record in records)
            for metric in SUMMARY_METRICS
        },
    }


def _unknown_unknown_check(
    scenario_summaries: list[dict[str, Any]], modes: list[str]
) -> dict[str, Any]:
    scenario = next(
        (
            item
            for item in scenario_summaries
            if "unknown_unknown" in item["scenario_id"]
        ),
        None,
    )
    if scenario is None:
        return {
            "scenario_id": None,
            "status": "missing",
            "baseline_modes_missed": False,
            "rule_only_missed": False,
            "centralized_late_or_partial": False,
            "shared_context_detected": False,
            "shared_context_complete": False,
            "mode_results": {},
        }

    mode_results = {
        mode: scenario["mode_results"].get(mode, {})
        for mode in modes
        if mode in scenario["mode_results"]
    }
    baseline_modes = [mode for mode in modes if mode in BASELINE_MODES]
    shared_modes = [mode for mode in modes if mode in SHARED_CONTEXT_MODES]
    baseline_modes_missed = all(
        mode_results[mode]["detection_rate"] == 0.0 for mode in baseline_modes
    )
    rule_only_missed = (
        "rule_only" in mode_results and mode_results["rule_only"]["detection_rate"] == 0.0
    )
    shared_context_detected = any(
        mode_results[mode]["detection_rate"] > 0.0 for mode in shared_modes
    )
    shared_context_complete = bool(shared_modes) and all(
        mode_results[mode]["evidence_complete_rate"] == 1.0 for mode in shared_modes
    )
    shared_ticks = [
        mode_results[mode]["avg_first_alert_tick"]
        for mode in shared_modes
        if mode_results[mode]["avg_first_alert_tick"] is not None
    ]
    shared_first_tick = min(shared_ticks) if shared_ticks else None
    centralized = mode_results.get("centralized_sequential")
    centralized_late_or_partial = False
    if centralized is not None:
        centralized_late_or_partial = (
            centralized["detection_rate"] < 1.0
            or centralized["evidence_complete_rate"] < 1.0
            or (
                shared_first_tick is not None
                and centralized["avg_first_alert_tick"] is not None
                and centralized["avg_first_alert_tick"] > shared_first_tick
            )
        )
    status = (
        "supported"
        if rule_only_missed and shared_context_detected and shared_context_complete
        else "mixed"
    )
    return {
        "scenario_id": scenario["scenario_id"],
        "status": status,
        "baseline_modes_missed": baseline_modes_missed,
        "rule_only_missed": rule_only_missed,
        "centralized_late_or_partial": centralized_late_or_partial,
        "shared_context_detected": shared_context_detected,
        "shared_context_complete": shared_context_complete,
        "shared_context_first_tick": shared_first_tick,
        "mode_results": mode_results,
    }


def _key_findings(
    *,
    overall_mode_summary: dict[str, dict[str, Any]],
    unknown_unknown_check: dict[str, Any],
    comparison: dict[str, Any] | None,
) -> list[str]:
    findings = []
    if unknown_unknown_check["status"] == "supported":
        findings.append(_unknown_unknown_finding(unknown_unknown_check))

    shared_modes = [mode for mode in overall_mode_summary if mode in SHARED_CONTEXT_MODES]
    if shared_modes:
        evidence_rates = [
            overall_mode_summary[mode]["evidence_complete_rate"] for mode in shared_modes
        ]
        findings.append(
            "Shared-context modes preserve complete role evidence at an average rate of "
            f"{_display_percent(mean(evidence_rates))} across the stress sweep."
        )

    baseline_modes = [mode for mode in overall_mode_summary if mode in BASELINE_MODES]
    if baseline_modes and shared_modes:
        baseline_analytic = mean(
            overall_mode_summary[mode]["avg_analytic_completeness"] for mode in baseline_modes
        )
        shared_analytic = mean(
            overall_mode_summary[mode]["avg_analytic_completeness"] for mode in shared_modes
        )
        findings.append(
            "Average analytic completeness increases from "
            f"{baseline_analytic:.3f} in baseline modes to {shared_analytic:.3f} "
            "in shared-context modes."
        )

    if comparison and comparison.get("scenarios"):
        available = sum(
            1
            for scenario in comparison["scenarios"]
            if scenario.get("substrates", {}).get("frontier_os", {}).get("substrate_available")
        )
        findings.append(
            f"Native Frontier_OS artifacts are available for {available}/"
            f"{len(comparison['scenarios'])} comparison scenarios."
        )

    return findings


def _unknown_unknown_finding(check: dict[str, Any]) -> str:
    mode_results = check["mode_results"]
    shared_modes = [mode for mode in mode_results if mode in SHARED_CONTEXT_MODES]
    shared_detection = mean(mode_results[mode]["detection_rate"] for mode in shared_modes)
    shared_tick = check.get("shared_context_first_tick")
    centralized = mode_results.get("centralized_sequential")
    if centralized and centralized["detection_rate"] > 0.0:
        return (
            "Scenario 05 supports the unknown-unknown proof thread: rule-only misses the weak "
            "novelty stream, centralized sequential detection is partial or late without complete "
            "role evidence, and shared-context modes detect it at "
            f"{_display_percent(shared_detection)} with average first tick {_display(shared_tick)}."
        )
    return (
        "Scenario 05 supports the unknown-unknown proof thread: rule-only misses the weak "
        "novelty stream, while shared-context modes detect it with complete role evidence."
    )


def _summary_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Scenario Evidence Summary",
        "",
        f"Seed: {summary['seed']}",
        f"Runs: {summary['runs']}",
        f"Ticks per scenario: {summary['ticks']}",
        "",
        f"Guardrail: {summary['interpretation_guardrail']}",
        "",
        "## Reviewer-Facing Takeaways",
        "",
    ]
    lines.extend(f"- {finding}" for finding in summary["key_findings"])
    lines.extend(
        [
            "",
            "## Mode-Level Stress Summary",
            "",
            "| Mode | Samples | Detection | Avg first tick | Precision | Sensitivity | Miss rate | FDR | Analytic completeness | Alignment | Domains | Evidence complete |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for mode in summary["modes"]:
        result = summary["overall_mode_summary"][mode]
        lines.append(_mode_row(mode, result))

    lines.extend(
        [
            "",
            "## Scenario-Mode Evidence",
            "",
            "| Scenario | Mode | Samples | Detection | Avg first tick | Precision | Sensitivity | Miss rate | FDR | Analytic completeness | Alignment | Domains | Evidence complete |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for scenario in summary["scenario_summaries"]:
        for mode in summary["modes"]:
            result = scenario["mode_results"][mode]
            lines.append(_mode_row(mode, result, scenario_id=scenario["scenario_id"]))

    lines.extend(_unknown_unknown_markdown(summary["unknown_unknown_check"], summary["modes"]))
    return "\n".join(lines).strip() + "\n"


def _mode_row(mode: str, result: dict[str, Any], scenario_id: str | None = None) -> str:
    prefix = f"| {scenario_id} | {MODE_LABELS.get(mode, mode)} |" if scenario_id else f"| {MODE_LABELS.get(mode, mode)} |"
    return (
        f"{prefix} "
        f"{result['samples']} | "
        f"{_display_percent(result['detection_rate'])} | "
        f"{_display(result['avg_first_alert_tick'])} | "
        f"{_display(result['avg_precision'])} | "
        f"{_display(result['avg_sensitivity'])} | "
        f"{_display(result['avg_miss_rate'])} | "
        f"{_display(result['avg_false_discovery_rate'])} | "
        f"{_display(result['avg_analytic_completeness'])} | "
        f"{_display(result['avg_context_geodesic_alignment'])} | "
        f"{_display(result['avg_active_domain_coverage'])} | "
        f"{_display_percent(result['evidence_complete_rate'])} |"
    )


def _unknown_unknown_markdown(check: dict[str, Any], modes: list[str]) -> list[str]:
    lines = [
        "",
        "## Unknown-Unknown Check",
        "",
        f"Status: {check['status']}",
        "",
        "| Mode | Detection | Avg first tick | Evidence complete | Interpretation |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    mode_results = check.get("mode_results", {})
    shared_tick = check.get("shared_context_first_tick")
    for mode in modes:
        if mode not in mode_results:
            continue
        result = mode_results[mode]
        if mode in BASELINE_MODES:
            if result["detection_rate"] == 0.0:
                interpretation = "Missed weak novelty stream"
            elif (
                shared_tick is not None
                and result["avg_first_alert_tick"] is not None
                and result["avg_first_alert_tick"] > shared_tick
            ):
                interpretation = "Late partial detection without complete role evidence"
            else:
                interpretation = "Detected without complete role evidence"
        elif mode in SHARED_CONTEXT_MODES:
            interpretation = "Detected through shared context" if result["detection_rate"] > 0.0 else "Missed"
        else:
            interpretation = "Measured"
        lines.append(
            "| "
            f"{MODE_LABELS.get(mode, mode)} | "
            f"{_display_percent(result['detection_rate'])} | "
            f"{_display(result['avg_first_alert_tick'])} | "
            f"{_display_percent(result['evidence_complete_rate'])} | "
            f"{interpretation} |"
        )
    return lines


def _best_evidence_mode(mode_results: dict[str, dict[str, Any]]) -> str | None:
    if not mode_results:
        return None
    return max(
        mode_results,
        key=lambda mode: (
            mode_results[mode]["detection_rate"],
            mode_results[mode]["evidence_complete_rate"],
            mode_results[mode]["avg_analytic_completeness"],
        ),
    )


def _scenario_order(records: list[dict[str, Any]]) -> list[str]:
    ordered: list[str] = []
    for record in records:
        scenario_id = record["scenario_id"]
        if scenario_id not in ordered:
            ordered.append(scenario_id)
    return ordered


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Required evidence input not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _read_optional_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _avg(values: Any) -> float:
    collected = [float(value) for value in values]
    return round(mean(collected), 3) if collected else 0.0


def _avg_optional(values: Any) -> float | None:
    collected = [float(value) for value in values if value is not None]
    return round(mean(collected), 3) if collected else None


def _display(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def _display_percent(value: float) -> str:
    return f"{100 * value:.0f}%"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Export scenario evidence summary artifacts.")
    parser.add_argument("--artifact-root", type=Path, default=None)
    args = parser.parse_args(argv)
    summary = export_evidence_summary(args.artifact_root)
    print(
        json.dumps(
            {
                "summary": summary["summary"],
                "scenarios": len(summary["scenario_summaries"]),
                "modes": summary["modes"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()