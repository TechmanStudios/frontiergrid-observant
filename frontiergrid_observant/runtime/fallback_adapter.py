"""Deterministic Python substrate used as the stable Phase I demo path."""

from __future__ import annotations

from statistics import mean
from typing import Any

from frontiergrid_observant.context.context_graph import ContextGraph
from frontiergrid_observant.risk.risk_engine import (
    ConfidenceInputs,
    RiskInputs,
    score_confidence,
    score_risk,
    status_for,
)
from frontiergrid_observant.runtime.base import AlertCandidate, ContextState, SubstrateTrace
from frontiergrid_observant.runtime.federated_alignment import FederatedDomainAlignment
from frontiergrid_observant.schemas.alerts import AgentEvidence, AlertCard
from frontiergrid_observant.schemas.events import ObservantEvent
from frontiergrid_observant.schemas.provenance import ReplayStep, ReplayTrace


class FallbackAdapter:
    substrate_name = "fallback"

    def __init__(self) -> None:
        self.scenario_id = "uninitialized"
        self.graph = ContextGraph()
        self.traces: list[SubstrateTrace] = []
        self.alerts: list[AlertCard] = []
        self.federation = FederatedDomainAlignment()

    def initialize(self, scenario_id: str) -> None:
        self.scenario_id = scenario_id
        self.graph = ContextGraph()
        self.traces = []
        self.alerts = []
        self.federation = FederatedDomainAlignment()

    def ingest_event(self, event: ObservantEvent) -> SubstrateTrace:
        self.graph.add_event(event)
        severity = event.ground_truth.severity if event.ground_truth else 0.0
        data_quality = float(event.attributes.get("data_quality", event.source_reliability))
        trace = SubstrateTrace(
            tick=event.tick,
            event_id=event.event_id,
            substrate=self.substrate_name,
            anomaly_score=severity if event.is_anomaly else min(0.25, severity + 0.05),
            data_quality=data_quality,
            notes=[f"risk_type={event.risk_type}", f"modality={event.modality}"],
        )
        trace.manifold_metrics.update(self.federation.record_event(event, trace))
        self.traces.append(trace)
        return trace

    def get_context_state(self) -> ContextState:
        active = sorted(
            {
                event.risk_type
                for event in self.graph.events.values()
                if event.risk_type != "nominal"
            }
        )
        data_quality = (
            mean([trace.data_quality for trace in self.traces[-8:]]) if self.traces else 1.0
        )
        return ContextState(
            scenario_id=self.scenario_id,
            tick=self.graph.latest_tick(),
            event_count=len(self.graph.events),
            active_risk_types=active,
            data_quality=data_quality,
            substrate_metrics={"federated_domain_alignment": self.federation.summary()},
        )

    def get_alert_candidates(self) -> list[AlertCandidate]:
        latest_anomalies = [
            event for event in self.graph.latest_events(limit=8) if event.is_anomaly
        ]
        if len(latest_anomalies) < 3:
            return []
        latest = latest_anomalies[-1]
        risk_type = latest.risk_type
        supporting = self.graph.find_supporting_events(risk_type, latest.tick)
        contradicting = self.graph.find_contradicting_events(risk_type, latest.tick)
        persistence = min(1.0, len(supporting) / 5)
        source_reliability = mean(
            [self.graph.events[event_id].source_reliability for event_id in supporting]
        )
        data_quality = mean(
            [
                float(
                    self.graph.events[event_id].attributes.get("data_quality", source_reliability)
                )
                for event_id in supporting
            ]
        )
        route_relevance = float(latest.attributes.get("logistics_route_relevance", 0.72))
        if "distance_nm" in latest.attributes:
            route_relevance = max(0.2, 1 - float(latest.attributes["distance_nm"]) / 10)
        alignment = float(
            latest.attributes.get("alignment_score", 0.68 if latest.is_anomaly else 0.2)
        )
        federated_alignment = self.federation.alignment_for_candidate(
            risk_type=risk_type,
            tick=latest.tick,
            supporting_events=supporting,
            contradicting_events=contradicting,
            graph=self.graph,
        )
        final_alignment = max(alignment, federated_alignment.context_geodesic_score)
        return [
            AlertCandidate(
                scenario_id=latest.scenario_id,
                tick=latest.tick,
                risk_type=risk_type,
                anomaly_score=latest.ground_truth.severity if latest.ground_truth else 0.0,
                evidence_alignment=final_alignment,
                persistence=persistence,
                proximity_or_route_relevance=route_relevance,
                source_reliability=source_reliability,
                cross_modal_support=max(
                    federated_alignment.cross_domain_support,
                    0.72
                    if len({self.graph.events[event_id].modality for event_id in supporting}) > 1
                    else 0.42,
                ),
                data_quality=data_quality,
                supporting_events=supporting,
                contradicting_events=contradicting,
                context_geodesic_alignment=federated_alignment.context_geodesic_score,
                federated_alignment=federated_alignment.as_trace(),
            )
        ]

    def build_alerts(self) -> list[AlertCard]:
        alerts: list[AlertCard] = []
        for index, candidate in enumerate(self.get_alert_candidates(), start=1):
            severity = score_risk(
                RiskInputs(
                    anomaly_score=candidate.anomaly_score,
                    evidence_alignment=candidate.evidence_alignment,
                    persistence=candidate.persistence,
                    proximity_or_route_relevance=candidate.proximity_or_route_relevance,
                    source_reliability=candidate.source_reliability,
                    cross_modal_support=candidate.cross_modal_support,
                )
            )
            benign_alternative = min(0.65, len(candidate.contradicting_events) * 0.18)
            confidence = score_confidence(
                ConfidenceInputs(
                    data_quality=candidate.data_quality,
                    source_reliability=candidate.source_reliability,
                    agent_agreement=0.70,
                    temporal_consistency=candidate.persistence,
                    replay_completeness=min(1.0, len(candidate.supporting_events) / 4),
                    benign_alternative_score=benign_alternative,
                )
            )
            alert_id = f"alert-{candidate.scenario_id}-{candidate.tick:04d}-{index}"
            agent_evidence = _fallback_agent_evidence(
                candidate=candidate,
                severity=severity,
                confidence=confidence,
                benign_alternative=benign_alternative,
            )
            alert = AlertCard(
                alert_id=alert_id,
                scenario_id=candidate.scenario_id,
                tick=candidate.tick,
                title=_title_for(candidate.risk_type),
                risk_type=candidate.risk_type,
                severity=round(severity, 3),
                confidence=round(confidence, 3),
                data_quality=round(candidate.data_quality, 3),
                status=status_for(
                    severity,
                    confidence,
                    data_quality=candidate.data_quality,
                    source_reliability=candidate.source_reliability,
                    benign_alternative_score=benign_alternative,
                ),
                supporting_events=candidate.supporting_events,
                contradicting_events=candidate.contradicting_events,
                context_geodesic_alignment=round(candidate.context_geodesic_alignment, 3),
                federated_alignment=candidate.federated_alignment,
                agent_votes={role: evidence.score for role, evidence in agent_evidence.items()},
                agent_evidence=agent_evidence,
                explanation=_explain(
                    candidate.risk_type, candidate.supporting_events, candidate.contradicting_events
                ),
            )
            alerts.append(alert)
        self.alerts = alerts
        return alerts

    def replay(self, alert_id: str) -> ReplayTrace:
        alert = next((item for item in self.alerts if item.alert_id == alert_id), None)
        if alert is None:
            return ReplayTrace(alert_id=alert_id)
        timeline = []
        for event_id in alert.supporting_events:
            event = self.graph.events[event_id]
            timeline.append(
                ReplayStep(
                    tick=event.tick,
                    event_id=event_id,
                    state_delta=f"{event.risk_type} evidence increased",
                    dominant_agent="watcher"
                    if event.modality in {"track", "sensor_contact"}
                    else "integrator",
                    confidence_delta=round(
                        (event.ground_truth.severity if event.ground_truth else 0.0) / 10, 3
                    ),
                )
            )
        entities = sorted(
            {
                entity
                for event_id in alert.supporting_events
                for entity in self.graph.events[event_id].entity_refs
            }
        )
        return ReplayTrace(
            alert_id=alert.alert_id,
            timeline=timeline,
            context_summary={
                "who": entities,
                "what": alert.risk_type,
                "where": "synthetic scenario space",
                "when": f"tick {timeline[0].tick if timeline else alert.tick} through {alert.tick}",
                "why_flagged": alert.explanation,
            },
        )


def _title_for(risk_type: str) -> str:
    return {
        "shadowing_pattern": "Potential shadowing pattern",
        "littoral_hazard_cluster": "Possible littoral hazard cluster",
        "degraded_comms_decoy": "Data-quality and decoy-risk warning",
        "cross_domain_ambiguity": "Cross-domain ambiguity alignment",
        "unknown_unknown_injection": "Unknown-unknown state-space injection",
    }.get(risk_type, "Contextual risk alert")


def _explain(risk_type: str, supporting: list[str], contradicting: list[str]) -> str:
    support_text = ", ".join(supporting) if supporting else "no supporting events"
    contradiction_text = (
        ", ".join(contradicting) if contradicting else "no recent nominal contradiction"
    )
    return (
        f"The {risk_type} alert is based on accumulating synthetic evidence from {support_text}. "
        f"Confidence is bounded by {contradiction_text}. Analyst review is recommended before action."
    )


def _agent_evidence_item(
    agent_name: str,
    score: float,
    confidence: float,
    evidence_event_ids: list[str],
    summary: str,
    notes: list[str] | None = None,
    trace: dict[str, Any] | None = None,
) -> AgentEvidence:
    return AgentEvidence(
        agent_name=agent_name,
        score=round(_bounded(score), 3),
        confidence=round(_bounded(confidence), 3),
        evidence_event_ids=evidence_event_ids,
        summary=summary,
        notes=notes or [],
        trace=trace or {},
    )


def _agent_result_evidence(result: Any, summary: str) -> AgentEvidence:
    return _agent_evidence_item(
        agent_name=str(result.agent_name),
        score=float(result.score),
        confidence=float(result.confidence),
        evidence_event_ids=list(result.evidence_event_ids),
        summary=summary,
        notes=list(result.notes),
        trace=dict(result.trace),
    )


def _fallback_agent_evidence(
    candidate: AlertCandidate,
    severity: float,
    confidence: float,
    benign_alternative: float,
) -> dict[str, AgentEvidence]:
    replay_completeness = min(1.0, len(candidate.supporting_events) / 4)
    latest_event = candidate.supporting_events[-1:] or candidate.supporting_events
    return {
        "watcher": _agent_evidence_item(
            "watcher",
            candidate.anomaly_score,
            candidate.data_quality,
            latest_event,
            "Observed anomaly pressure in the latest supporting event.",
            trace={
                "risk_type": candidate.risk_type,
                "anomaly_score": round(candidate.anomaly_score, 3),
                "supporting_event_count": len(candidate.supporting_events),
            },
        ),
        "integrator": _agent_evidence_item(
            "integrator",
            candidate.evidence_alignment,
            candidate.source_reliability,
            candidate.supporting_events,
            "Linked supporting events into a common contextual cluster.",
            trace={
                "evidence_alignment": round(candidate.evidence_alignment, 3),
                "cross_modal_support": round(candidate.cross_modal_support, 3),
                "persistence": round(candidate.persistence, 3),
                "context_geodesic_score": round(candidate.context_geodesic_alignment, 3),
                "active_domains": candidate.federated_alignment.get("active_domains", []),
                "domain_contributions": candidate.federated_alignment.get(
                    "domain_contributions", {}
                ),
                "candidate_team": candidate.federated_alignment.get("candidate_team", []),
            },
        ),
        "risk_officer": _agent_evidence_item(
            "risk_officer",
            severity,
            candidate.source_reliability,
            candidate.supporting_events,
            "Converted anomaly, persistence, route relevance, and source support into severity.",
            trace={
                "severity": round(severity, 3),
                "route_relevance": round(candidate.proximity_or_route_relevance, 3),
                "source_reliability": round(candidate.source_reliability, 3),
            },
        ),
        "skeptic": _agent_evidence_item(
            "skeptic",
            benign_alternative,
            1.0 - benign_alternative,
            candidate.contradicting_events,
            "Estimated benign-alternative pressure from contradicting evidence.",
            trace={
                "benign_alternative_score": round(benign_alternative, 3),
                "contradicting_event_count": len(candidate.contradicting_events),
            },
        ),
        "explainer": _agent_evidence_item(
            "explainer",
            replay_completeness,
            confidence,
            candidate.supporting_events + candidate.contradicting_events,
            "Prepared the analyst-facing explanation and replay evidence set.",
            trace={
                "replay_completeness": round(replay_completeness, 3),
                "supporting_event_count": len(candidate.supporting_events),
                "contradicting_event_count": len(candidate.contradicting_events),
            },
        ),
    }


def _bounded(value: float) -> float:
    return max(0.0, min(1.0, float(value)))
