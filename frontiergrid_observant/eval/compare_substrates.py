"""Export fallback versus native Frontier_OS comparison artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from frontiergrid_observant.config import load_settings
from frontiergrid_observant.demo.run_demo import run_demo
from frontiergrid_observant.eval.run_eval import evaluate_payload
from frontiergrid_observant.ingest.synthetic_generator import SCENARIOS, generate_scenario

SUBSTRATES = ("fallback", "frontier_os")
EXPECTED_AGENT_ROLES = ("watcher", "integrator", "risk_officer", "skeptic", "explainer")


def build_substrate_comparison(
    *,
    seed: int = 149,
    ticks: int = 30,
    scenarios: list[str] | None = None,
    substrates: tuple[str, ...] = SUBSTRATES,
) -> dict[str, Any]:
    scenario_keys = scenarios or sorted(SCENARIOS)
    scenario_results = []
    for index, scenario in enumerate(scenario_keys):
        scenario_seed = seed + index
        events = generate_scenario(scenario, seed=scenario_seed, ticks=ticks)
        substrate_results = {}
        for substrate in substrates:
            payload = run_demo(
                scenario=scenario,
                substrate=substrate,
                seed=scenario_seed,
                ticks=ticks,
            )
            substrate_results[substrate] = _substrate_result(events, payload, substrate)

        scenario_results.append(
            {
                "scenario_key": scenario,
                "scenario_id": events[0].scenario_id,
                "seed": scenario_seed,
                "ticks": ticks,
                "substrates": substrate_results,
                "delta": _frontier_delta(substrate_results),
            }
        )

    return {
        "comparison": "fallback_vs_frontier_os",
        "seed": seed,
        "ticks": ticks,
        "substrates": list(substrates),
        "expected_agent_roles": list(EXPECTED_AGENT_ROLES),
        "scenarios": scenario_results,
    }


def export_substrate_comparison(
    *,
    seed: int = 149,
    ticks: int = 30,
    artifact_root: Path | None = None,
) -> dict[str, Any]:
    comparison = build_substrate_comparison(seed=seed, ticks=ticks)
    root = artifact_root or load_settings().artifact_root
    write_comparison_artifacts(comparison, root)
    return comparison


def write_comparison_artifacts(
    comparison: dict[str, Any], artifact_root: Path
) -> tuple[Path, Path]:
    artifact_root.mkdir(parents=True, exist_ok=True)
    metrics_path = artifact_root / "fallback_vs_frontier_os_metrics.json"
    report_path = artifact_root / "fallback_vs_frontier_os_report.md"
    metrics_path.write_text(json.dumps(comparison, indent=2, default=str), encoding="utf-8")
    report_path.write_text(_comparison_markdown(comparison), encoding="utf-8")
    return metrics_path, report_path


def _substrate_result(events: list[Any], payload: dict[str, Any], substrate: str) -> dict[str, Any]:
    metrics = evaluate_payload(events, payload, substrate)
    alerts = payload["alerts"]
    first_alert = _first_alert_summary(alerts[0]) if alerts else None
    context = payload.get("context", {})
    substrate_metrics = context.get("substrate_metrics", {}) if isinstance(context, dict) else {}
    return {
        "substrate": substrate,
        "reported_substrate": payload["substrate"],
        "substrate_available": True
        if substrate == "fallback"
        else substrate_metrics.get("available", False),
        "event_count": payload["event_count"],
        "alert_count": len(alerts),
        "first_alert_tick": first_alert["tick"] if first_alert else None,
        "first_alert": first_alert,
        "metrics": metrics.summary(),
    }


def _first_alert_summary(alert: dict[str, Any]) -> dict[str, Any]:
    agent_roles = sorted(alert.get("agent_evidence", {}))
    return {
        "alert_id": alert["alert_id"],
        "tick": alert["tick"],
        "title": alert["title"],
        "risk_type": alert["risk_type"],
        "severity": alert["severity"],
        "confidence": alert["confidence"],
        "data_quality": alert["data_quality"],
        "context_geodesic_alignment": alert.get("context_geodesic_alignment", 0.0),
        "federated_alignment": alert.get("federated_alignment", {}),
        "status": alert["status"],
        "agent_roles_present": agent_roles,
        "all_agent_evidence_present": set(agent_roles) == set(EXPECTED_AGENT_ROLES),
    }


def _frontier_delta(substrate_results: dict[str, dict[str, Any]]) -> dict[str, Any]:
    fallback = substrate_results.get("fallback")
    frontier = substrate_results.get("frontier_os")
    if fallback is None or frontier is None:
        return {}

    fallback_alert = fallback["first_alert"] or {}
    frontier_alert = frontier["first_alert"] or {}
    return {
        "alert_count_delta": frontier["alert_count"] - fallback["alert_count"],
        "first_alert_tick_delta": _delta(
            frontier["first_alert_tick"], fallback["first_alert_tick"]
        ),
        "severity_delta": _delta(frontier_alert.get("severity"), fallback_alert.get("severity")),
        "confidence_delta": _delta(
            frontier_alert.get("confidence"), fallback_alert.get("confidence")
        ),
        "alignment_delta": _delta(
            frontier_alert.get("context_geodesic_alignment"),
            fallback_alert.get("context_geodesic_alignment"),
        ),
        "native_agent_evidence_complete": bool(
            frontier_alert.get("all_agent_evidence_present", False)
        ),
    }


def _delta(left: float | int | None, right: float | int | None) -> float | None:
    if left is None or right is None:
        return None
    return round(float(left) - float(right), 3)


def _comparison_markdown(comparison: dict[str, Any]) -> str:
    lines = [
        "# Fallback vs Frontier_OS Comparison",
        "",
        f"Seed: {comparison['seed']}",
        f"Ticks per scenario: {comparison['ticks']}",
        "",
        "## Scenario Summary",
        "",
        "| Scenario | Substrate | Available | Alerts | First tick | Severity | Confidence | Alignment | Status | Precision | Sensitivity | Agent evidence |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | --- |",
    ]
    for scenario in comparison["scenarios"]:
        for substrate in comparison["substrates"]:
            result = scenario["substrates"][substrate]
            first_alert = result["first_alert"] or {}
            metrics = result["metrics"]
            lines.append(
                "| "
                f"{scenario['scenario_id']} | "
                f"{substrate} | "
                f"{_display(result['substrate_available'])} | "
                f"{result['alert_count']} | "
                f"{_display(first_alert.get('tick'))} | "
                f"{_display(first_alert.get('severity'))} | "
                f"{_display(first_alert.get('confidence'))} | "
                f"{_display(first_alert.get('context_geodesic_alignment'))} | "
                f"{_display(first_alert.get('status'))} | "
                f"{metrics['precision']:.3f} | "
                f"{metrics['sensitivity']:.3f} | "
                f"{_evidence_display(first_alert)} |"
            )

    lines.extend(
        [
            "",
            "## Native Delta",
            "",
            "Negative first-tick delta means the native Frontier_OS path alerted earlier than fallback.",
            "",
            "| Scenario | Alert count delta | First tick delta | Severity delta | Confidence delta | Alignment delta | Native evidence complete |",
            "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for scenario in comparison["scenarios"]:
        delta = scenario["delta"]
        lines.append(
            "| "
            f"{scenario['scenario_id']} | "
            f"{_display(delta.get('alert_count_delta'))} | "
            f"{_display(delta.get('first_alert_tick_delta'))} | "
            f"{_display(delta.get('severity_delta'))} | "
            f"{_display(delta.get('confidence_delta'))} | "
            f"{_display(delta.get('alignment_delta'))} | "
            f"{_display(delta.get('native_agent_evidence_complete'))} |"
        )

    return "\n".join(lines).strip() + "\n"


def _display(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def _evidence_display(first_alert: dict[str, Any]) -> str:
    if not first_alert:
        return "n/a"
    if first_alert.get("all_agent_evidence_present"):
        return "complete"
    return ", ".join(first_alert.get("agent_roles_present", [])) or "missing"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Export fallback versus native Frontier_OS comparison artifacts."
    )
    parser.add_argument("--seed", type=int, default=149)
    parser.add_argument("--ticks", type=int, default=30)
    parser.add_argument("--artifact-root", type=Path, default=None)
    args = parser.parse_args(argv)

    comparison = export_substrate_comparison(
        seed=args.seed,
        ticks=args.ticks,
        artifact_root=args.artifact_root,
    )
    print(
        json.dumps(
            {"comparison": comparison["comparison"], "scenarios": len(comparison["scenarios"])},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
