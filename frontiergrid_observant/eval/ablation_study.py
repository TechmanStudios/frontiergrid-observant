"""Run proposal-facing ablation studies across simple and shared-context modes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean
from typing import Any

from frontiergrid_observant.config import load_settings
from frontiergrid_observant.eval.run_eval import evaluate_payload
from frontiergrid_observant.ingest.synthetic_generator import SCENARIOS, generate_scenario
from frontiergrid_observant.risk.risk_engine import ConfidenceInputs, score_confidence, status_for
from frontiergrid_observant.runtime.fallback_adapter import FallbackAdapter
from frontiergrid_observant.runtime.frontier_os_adapter import FrontierOSAdapter
from frontiergrid_observant.schemas.alerts import AgentEvidence, AlertCard
from frontiergrid_observant.schemas.events import ObservantEvent

EXPECTED_AGENT_ROLES = ("watcher", "integrator", "risk_officer", "skeptic", "explainer")
ABLATION_MODES = (
    "rule_only",
    "centralized_sequential",
    "fallback_shared_context",
    "native_manifold_shared_context",
)

MODE_DESCRIPTIONS = {
    "rule_only": "Event-local rules with no shared context or agent evidence.",
    "centralized_sequential": "Ordered scoring pipeline with limited role separation.",
    "fallback_shared_context": "Deterministic shared-context adapter with five-role evidence.",
    "native_manifold_shared_context": "Frontier_OS / Exciton-MoA shared-context adapter with manifold traces.",
}


def build_ablation_study(
    *,
    seed: int = 149,
    ticks: int = 30,
    scenarios: list[str] | None = None,
    modes: tuple[str, ...] = ABLATION_MODES,
) -> dict[str, Any]:
    """Build an in-memory ablation study for synthetic Observant-AI scenarios."""
    scenario_keys = scenarios or sorted(SCENARIOS)
    scenario_results = []
    for index, scenario in enumerate(scenario_keys):
        scenario_seed = seed + index
        events = generate_scenario(scenario, seed=scenario_seed, ticks=ticks)
        mode_results = {}
        for mode in modes:
            payload = _payload_for_mode(mode, scenario, scenario_seed, ticks, events)
            mode_results[mode] = _mode_result(events, payload, mode)

        scenario_results.append(
            {
                "scenario_key": scenario,
                "scenario_id": events[0].scenario_id,
                "seed": scenario_seed,
                "ticks": ticks,
                "modes": mode_results,
                "deltas_vs_rule_only": _deltas_vs_rule_only(mode_results),
            }
        )

    return {
        "study": "observant_ablation_study",
        "seed": seed,
        "ticks": ticks,
        "modes": list(modes),
        "mode_descriptions": {mode: MODE_DESCRIPTIONS[mode] for mode in modes},
        "expected_agent_roles": list(EXPECTED_AGENT_ROLES),
        "scenarios": scenario_results,
        "interpretation_guardrail": (
            "Synthetic scenario-local evidence; use to guide Phase I feasibility work, "
            "not to claim operational performance."
        ),
    }


def export_ablation_study(
    *,
    seed: int = 149,
    ticks: int = 30,
    artifact_root: Path | None = None,
    modes: tuple[str, ...] = ABLATION_MODES,
) -> dict[str, Any]:
    study = build_ablation_study(seed=seed, ticks=ticks, modes=modes)
    root = artifact_root or load_settings().artifact_root
    write_ablation_artifacts(study, root)
    return study


def write_ablation_artifacts(study: dict[str, Any], artifact_root: Path) -> tuple[Path, Path]:
    artifact_root.mkdir(parents=True, exist_ok=True)
    metrics_path = artifact_root / "ablation_study_metrics.json"
    report_path = artifact_root / "ablation_study_report.md"
    metrics_path.write_text(json.dumps(study, indent=2, default=str), encoding="utf-8")
    report_path.write_text(_ablation_markdown(study), encoding="utf-8")
    return metrics_path, report_path


def _payload_for_mode(
    mode: str,
    scenario: str,
    seed: int,
    ticks: int,
    events: list[ObservantEvent],
) -> dict[str, Any]:
    if mode == "rule_only":
        return _rule_only_payload(events)
    if mode == "centralized_sequential":
        return _centralized_sequential_payload(events)
    if mode == "fallback_shared_context":
        return _stream_adapter_payload(events, substrate="fallback")
    if mode == "native_manifold_shared_context":
        return _stream_adapter_payload(events, substrate="frontier_os")
    raise ValueError(f"Unknown ablation mode: {mode} for {scenario} seed={seed} ticks={ticks}")


def _stream_adapter_payload(events: list[ObservantEvent], *, substrate: str) -> dict[str, Any]:
    settings = load_settings()
    adapter = (
        FrontierOSAdapter(
            settings.frontier_os_root,
            node_count=settings.frontier_os_node_count,
            tau_threshold=settings.frontier_os_tau_threshold,
        )
        if substrate == "frontier_os"
        else FallbackAdapter()
    )
    adapter.initialize(events[0].scenario_id)
    alerts_by_id: dict[str, dict[str, Any]] = {}
    for event in events:
        adapter.ingest_event(event)
        for alert in adapter.build_alerts():
            alerts_by_id.setdefault(alert.alert_id, alert.model_dump())

    return {
        "scenario_id": events[0].scenario_id,
        "substrate": adapter.substrate_name,
        "event_count": len(events),
        "context": adapter.get_context_state().model_dump(),
        "alerts": list(alerts_by_id.values()),
    }


def _rule_only_payload(events: list[ObservantEvent]) -> dict[str, Any]:
    alerts = []
    for event in events:
        score = _event_rule_score(event)
        if score < 0.74:
            continue
        data_quality = _data_quality(event)
        confidence = max(0.1, min(1.0, 0.6 * event.source_reliability + 0.4 * data_quality))
        alert = _make_baseline_alert(
            mode="rule_only",
            event=event,
            severity=score,
            confidence=confidence,
            data_quality=data_quality,
            supporting_events=[event.event_id],
            contradicting_events=[],
            evidence={
                "rule_engine": _evidence(
                    "rule_engine",
                    score,
                    confidence,
                    [event.event_id],
                    "Event-local threshold crossed without shared contextual review.",
                    trace={"rule_score": round(score, 3)},
                )
            },
        )
        alerts.append(alert)

    return _baseline_payload(events, "rule_only", alerts)


def _centralized_sequential_payload(events: list[ObservantEvent]) -> dict[str, Any]:
    alerts = []
    for index, event in enumerate(events):
        recent = events[max(0, index - 5) : index + 1]
        scored_recent = [(item, _event_rule_score(item)) for item in recent]
        supporting = [item for item, score in scored_recent if score >= 0.55]
        if len(supporting) < 3:
            continue

        support_scores = [_event_rule_score(item) for item in supporting]
        support_ids = [item.event_id for item in supporting]
        severity = max(support_scores) * 0.65 + min(1.0, len(supporting) / 5) * 0.35
        data_quality = mean(_data_quality(item) for item in supporting)
        source_reliability = mean(item.source_reliability for item in supporting)
        benign_alternative = mean(
            float(item.attributes.get("false_positive_pressure", 0.0)) for item in supporting
        )
        confidence = score_confidence(
            ConfidenceInputs(
                data_quality=data_quality,
                source_reliability=source_reliability,
                agent_agreement=0.62,
                temporal_consistency=min(1.0, len(supporting) / 5),
                replay_completeness=min(1.0, len(supporting) / 4),
                benign_alternative_score=min(0.65, benign_alternative),
            )
        )
        evidence = {
            "watcher": _evidence(
                "watcher",
                max(support_scores),
                _data_quality(event),
                [event.event_id],
                "Observed event-local anomaly pressure in the ordered pipeline.",
            ),
            "integrator": _evidence(
                "integrator",
                min(1.0, len(supporting) / 5),
                source_reliability,
                support_ids,
                "Aggregated recent supporting events in sequence.",
            ),
            "risk_officer": _evidence(
                "risk_officer",
                severity,
                confidence,
                support_ids,
                "Converted sequential evidence into a risk score.",
            ),
            "explainer": _evidence(
                "explainer",
                min(1.0, len(supporting) / 4),
                confidence,
                support_ids,
                "Prepared a compact explanation from recent evidence only.",
            ),
        }
        alerts.append(
            _make_baseline_alert(
                mode="centralized_sequential",
                event=event,
                severity=severity,
                confidence=confidence,
                data_quality=data_quality,
                supporting_events=support_ids,
                contradicting_events=[],
                evidence=evidence,
            )
        )

    return _baseline_payload(events, "centralized_sequential", alerts)


def _baseline_payload(
    events: list[ObservantEvent], mode: str, alerts: list[dict[str, Any]]
) -> dict[str, Any]:
    return {
        "scenario_id": events[0].scenario_id,
        "substrate": mode,
        "event_count": len(events),
        "context": {
            "baseline_mode": mode,
            "description": MODE_DESCRIPTIONS[mode],
            "shared_context": False,
        },
        "alerts": alerts,
    }


def _make_baseline_alert(
    *,
    mode: str,
    event: ObservantEvent,
    severity: float,
    confidence: float,
    data_quality: float,
    supporting_events: list[str],
    contradicting_events: list[str],
    evidence: dict[str, AgentEvidence],
) -> dict[str, Any]:
    benign_alternative = float(event.attributes.get("false_positive_pressure", 0.0))
    alert = AlertCard(
        alert_id=f"alert-{event.scenario_id}-{mode}-{event.tick:04d}",
        scenario_id=event.scenario_id,
        tick=event.tick,
        title=_title_for(event.risk_type),
        risk_type=event.risk_type,
        severity=round(_bounded(severity), 3),
        confidence=round(_bounded(confidence), 3),
        data_quality=round(_bounded(data_quality), 3),
        status=status_for(
            severity,
            confidence,
            data_quality=data_quality,
            source_reliability=event.source_reliability,
            benign_alternative_score=benign_alternative,
        ),
        supporting_events=supporting_events,
        contradicting_events=contradicting_events,
        agent_votes={role: item.score for role, item in evidence.items()},
        agent_evidence=evidence,
        explanation=(
            f"The {mode} baseline flagged {event.risk_type} at tick {event.tick} from "
            f"{len(supporting_events)} supporting synthetic event(s)."
        ),
    )
    return alert.model_dump()


def _mode_result(
    events: list[ObservantEvent], payload: dict[str, Any], mode: str
) -> dict[str, Any]:
    metrics = evaluate_payload(events, payload, mode)
    explanation_scores = _explanation_scores(payload)
    metrics.analytic_completeness = explanation_scores["analytic_completeness"]
    metrics.uniqueness = explanation_scores["uniqueness"]
    metrics.validity = explanation_scores["validity"]
    metrics.consistency = explanation_scores["consistency"]
    alerts = payload["alerts"]
    first_alert = _first_alert_summary(alerts[0]) if alerts else None
    return {
        "mode": mode,
        "description": MODE_DESCRIPTIONS[mode],
        "reported_substrate": payload["substrate"],
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
        "expected_agent_evidence_complete": set(agent_roles) == set(EXPECTED_AGENT_ROLES),
    }


def _deltas_vs_rule_only(mode_results: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    baseline = mode_results.get("rule_only")
    if baseline is None:
        return {}
    deltas = {}
    for mode, result in mode_results.items():
        if mode == "rule_only":
            continue
        deltas[mode] = {
            "first_alert_tick_delta": _delta(
                result["first_alert_tick"], baseline["first_alert_tick"]
            ),
            "precision_delta": _delta(
                result["metrics"]["precision"], baseline["metrics"]["precision"]
            ),
            "sensitivity_delta": _delta(
                result["metrics"]["sensitivity"], baseline["metrics"]["sensitivity"]
            ),
            "miss_rate_delta": _delta(
                result["metrics"]["miss_rate"], baseline["metrics"]["miss_rate"]
            ),
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
    return deltas


def _event_rule_score(event: ObservantEvent) -> float:
    attrs = event.attributes
    scores = [0.0]
    if "alignment_score" in attrs:
        scores.append(float(attrs["alignment_score"]))
    if "distance_nm" in attrs:
        scores.append(max(0.0, 1.0 - float(attrs["distance_nm"]) / 10.0))
    if "cluster_density" in attrs:
        scores.append(min(1.0, float(attrs["cluster_density"])))
    if "logistics_route_relevance" in attrs:
        scores.append(float(attrs["logistics_route_relevance"]))
    if "message_latency_ms" in attrs:
        scores.append(min(1.0, max(0.0, (float(attrs["message_latency_ms"]) - 250.0) / 1200.0)))
    if attrs.get("missing_message_window"):
        scores.append(0.68)
    if _data_quality(event) < 0.55:
        scores.append(0.55)
    return _bounded(max(scores))


def _data_quality(event: ObservantEvent) -> float:
    return _bounded(float(event.attributes.get("data_quality", event.source_reliability)))


def _evidence(
    agent_name: str,
    score: float,
    confidence: float,
    evidence_event_ids: list[str],
    summary: str,
    *,
    trace: dict[str, Any] | None = None,
) -> AgentEvidence:
    return AgentEvidence(
        agent_name=agent_name,
        score=round(_bounded(score), 3),
        confidence=round(_bounded(confidence), 3),
        evidence_event_ids=evidence_event_ids,
        summary=summary,
        trace=trace or {},
    )


def _explanation_scores(payload: dict[str, Any]) -> dict[str, float]:
    alerts = payload.get("alerts", [])
    if not alerts:
        return {
            "analytic_completeness": 0.0,
            "uniqueness": 0.0,
            "validity": 0.0,
            "consistency": 0.0,
        }

    role_coverages = []
    support_densities = []
    validity_scores = []
    explanation_scores = []
    for alert in alerts:
        roles = set(alert.get("agent_evidence", {}))
        role_coverages.append(len(roles & set(EXPECTED_AGENT_ROLES)) / len(EXPECTED_AGENT_ROLES))
        support_densities.append(min(1.0, len(alert.get("supporting_events", [])) / 4))
        evidence = alert.get("agent_evidence", {})
        grounded_roles = [
            role
            for role, item in evidence.items()
            if item.get("evidence_event_ids") or role not in EXPECTED_AGENT_ROLES
        ]
        validity_scores.append(len(grounded_roles) / max(len(evidence), 1))
        explanation_scores.append(1.0 if alert.get("explanation") else 0.0)

    role_coverage = mean(role_coverages)
    support_density = mean(support_densities)
    explanation_presence = mean(explanation_scores)
    return {
        "analytic_completeness": round(
            _bounded(0.40 * role_coverage + 0.35 * support_density + 0.25 * explanation_presence),
            3,
        ),
        "uniqueness": round(_bounded(0.55 * support_density + 0.45 * explanation_presence), 3),
        "validity": round(_bounded(mean(validity_scores)), 3),
        "consistency": round(_bounded(0.50 * role_coverage + 0.50 * support_density), 3),
    }


def _ablation_markdown(study: dict[str, Any]) -> str:
    lines = [
        "# Observant-AI Ablation Study",
        "",
        f"Seed: {study['seed']}",
        f"Ticks per scenario: {study['ticks']}",
        "",
        f"Guardrail: {study['interpretation_guardrail']}",
        "",
        "## Modes",
        "",
        "| Mode | Description |",
        "| --- | --- |",
    ]
    for mode in study["modes"]:
        lines.append(f"| {mode} | {study['mode_descriptions'][mode]} |")

    lines.extend(
        [
            "",
            "## Scenario Summary",
            "",
            "| Scenario | Mode | Alerts | First tick | Severity | Confidence | Alignment | Domains | Precision | Sensitivity | Miss rate | FDR | Analytic completeness | Evidence |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for scenario in study["scenarios"]:
        for mode in study["modes"]:
            result = scenario["modes"][mode]
            first_alert = result["first_alert"] or {}
            metrics = result["metrics"]
            lines.append(
                "| "
                f"{scenario['scenario_id']} | "
                f"{mode} | "
                f"{result['alert_count']} | "
                f"{_display(first_alert.get('tick'))} | "
                f"{_display(first_alert.get('severity'))} | "
                f"{_display(first_alert.get('confidence'))} | "
                f"{_display(first_alert.get('context_geodesic_alignment'))} | "
                f"{metrics['active_domain_coverage']:.3f} | "
                f"{metrics['precision']:.3f} | "
                f"{metrics['sensitivity']:.3f} | "
                f"{metrics['miss_rate']:.3f} | "
                f"{metrics['false_discovery_rate']:.3f} | "
                f"{metrics['analytic_completeness']:.3f} | "
                f"{_evidence_display(first_alert)} |"
            )

    lines.extend(
        [
            "",
            "## Deltas vs Rule-Only",
            "",
            "Negative first-tick delta means the mode alerted earlier than the rule-only baseline.",
            "",
            "| Scenario | Mode | First tick delta | Precision delta | Sensitivity delta | Miss-rate delta | FDR delta | Analytic completeness delta | Alignment delta |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for scenario in study["scenarios"]:
        for mode, delta in scenario["deltas_vs_rule_only"].items():
            lines.append(
                "| "
                f"{scenario['scenario_id']} | "
                f"{mode} | "
                f"{_display(delta.get('first_alert_tick_delta'))} | "
                f"{_display(delta.get('precision_delta'))} | "
                f"{_display(delta.get('sensitivity_delta'))} | "
                f"{_display(delta.get('miss_rate_delta'))} | "
                f"{_display(delta.get('false_discovery_rate_delta'))} | "
                f"{_display(delta.get('analytic_completeness_delta'))} |"
                f" {_display(delta.get('context_geodesic_alignment_delta'))} |"
            )

    return "\n".join(lines).strip() + "\n"


def _title_for(risk_type: str) -> str:
    return {
        "shadowing_pattern": "Potential shadowing pattern",
        "littoral_hazard_cluster": "Possible littoral hazard cluster",
        "degraded_comms_decoy": "Data-quality and decoy-risk warning",
        "cross_domain_ambiguity": "Cross-domain ambiguity alignment",
        "unknown_unknown_injection": "Unknown-unknown state-space injection",
        "nominal": "Rule-only contextual risk alert",
    }.get(risk_type, "Contextual risk alert")


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


def _evidence_display(first_alert: dict[str, Any]) -> str:
    if not first_alert:
        return "n/a"
    if first_alert.get("expected_agent_evidence_complete"):
        return "complete"
    return ", ".join(first_alert.get("agent_roles_present", [])) or "missing"


def _bounded(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Export Observant-AI ablation study artifacts.")
    parser.add_argument("--seed", type=int, default=149)
    parser.add_argument("--ticks", type=int, default=30)
    parser.add_argument("--artifact-root", type=Path, default=None)
    parser.add_argument(
        "--modes",
        nargs="+",
        choices=ABLATION_MODES,
        default=list(ABLATION_MODES),
    )
    args = parser.parse_args(argv)

    study = export_ablation_study(
        seed=args.seed,
        ticks=args.ticks,
        artifact_root=args.artifact_root,
        modes=tuple(args.modes),
    )
    print(
        json.dumps(
            {"study": study["study"], "scenarios": len(study["scenarios"]), "modes": args.modes},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
