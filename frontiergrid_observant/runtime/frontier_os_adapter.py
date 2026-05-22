"""Frontier_OS / Exciton-MoA substrate adapter."""

from __future__ import annotations

from pathlib import Path
from statistics import mean

from frontiergrid_observant.risk.risk_engine import (
    ConfidenceInputs,
    RiskInputs,
    score_confidence,
    score_risk,
    status_for,
)
from frontiergrid_observant.runtime.base import AlertCandidate, ContextState, SubstrateTrace
from frontiergrid_observant.runtime.fallback_adapter import (
    FallbackAdapter,
    _agent_evidence_item,
    _agent_result_evidence,
    _title_for,
)
from frontiergrid_observant.runtime.manifold_bridge import (
    FrontierManifoldBridge,
    clamp,
    resolve_frontier_os_root,
)
from frontiergrid_observant.schemas.alerts import AlertCard
from frontiergrid_observant.schemas.events import ObservantEvent
from frontiergrid_observant.schemas.provenance import ReplayStep, ReplayTrace


class FrontierOSAdapter(FallbackAdapter):
    substrate_name = "frontier_os"

    def __init__(
        self,
        frontier_os_root: Path | None = None,
        node_count: int = 1024,
        tau_threshold: float = 1.0,
    ) -> None:
        super().__init__()
        self.frontier_os_root = frontier_os_root
        self.node_count = node_count
        self.tau_threshold = tau_threshold
        self.available = False
        self.bridge: FrontierManifoldBridge | None = None
        self.import_note = (
            "Frontier_OS adapter unavailable; using deterministic safe-mode fallback."
        )
        self.watcher = None
        self.integrator = None
        self.risk_officer = None
        self.skeptic = None
        self.explainer = None
        self.event_epicenters: dict[str, str] = {}

    def initialize(self, scenario_id: str) -> None:
        super().initialize(scenario_id)
        resolved_root = resolve_frontier_os_root(self.frontier_os_root)
        if resolved_root is None:
            self.available = False
            self.bridge = None
            self.import_note = "Frontier_OS root not found; using deterministic safe-mode fallback."
            return

        try:
            self.bridge = FrontierManifoldBridge(
                root=resolved_root,
                node_count=self.node_count,
                tau_threshold=self.tau_threshold,
            )
            self.bridge.initialize(scenario_id)
        except Exception as exc:  # pragma: no cover - exercised by operator environment failures
            self.available = False
            self.bridge = None
            self.import_note = f"Frontier_OS adapter failed to initialize: {exc}"
            return

        # Initialize native agents
        from frontiergrid_observant.agents.explainer import ExplainerAgent
        from frontiergrid_observant.agents.integrator import IntegratorAgent
        from frontiergrid_observant.agents.risk_officer import RiskOfficerAgent
        from frontiergrid_observant.agents.skeptic import SkepticAgent
        from frontiergrid_observant.agents.watcher import WatcherAgent

        self.watcher = WatcherAgent()
        self.integrator = IntegratorAgent()
        self.risk_officer = RiskOfficerAgent()
        self.skeptic = SkepticAgent()
        self.explainer = ExplainerAgent()
        self.event_epicenters = {}

        self.frontier_os_root = resolved_root
        self.available = True
        self.import_note = f"Frontier_OS manifold active at {resolved_root}"

    def ingest_event(self, event: ObservantEvent) -> SubstrateTrace:
        self.graph.add_event(event)
        if not self.available or self.bridge is None or self.watcher is None:
            trace = super().ingest_event(event)
            trace.substrate = "frontier_os_safe_mode"
            trace.notes.append(self.import_note)
            return trace

        try:
            manifold_step = self.bridge.ingest_event(event)
            if manifold_step.epicenter_node:
                self.event_epicenters[event.event_id] = manifold_step.epicenter_node
        except Exception as exc:  # pragma: no cover - exercised by operator environment failures
            trace = super().ingest_event(event)
            trace.substrate = "frontier_os_safe_mode"
            trace.notes.append(f"Frontier_OS manifold ingest failed: {exc}")
            return trace

        watcher_result = self.watcher.evaluate_event(self.bridge, event)

        trace = SubstrateTrace(
            tick=event.tick,
            event_id=event.event_id,
            substrate=self.substrate_name,
            anomaly_score=watcher_result.score,
            data_quality=watcher_result.confidence,
            notes=[
                "frontier_os_manifold=active",
                f"epicenter_node={manifold_step.epicenter_node}",
                f"peak_resonance={manifold_step.peak_resonance:.3f}",
                f"burst_count={manifold_step.burst_count}",
            ],
            manifold_metrics=manifold_step.as_trace_metrics(),
        )
        trace.manifold_metrics.update(self.federation.record_event(event, trace))
        self.traces.append(trace)
        return trace

    def get_context_state(self) -> ContextState:
        state = super().get_context_state()
        federated_summary = state.substrate_metrics.get("federated_domain_alignment")
        if self.available and self.bridge is not None:
            state.substrate_metrics = self.bridge.summary()
            state.substrate_metrics["federated_domain_alignment"] = federated_summary
        else:
            state.substrate_metrics = {
                "available": False,
                "note": self.import_note,
                "federated_domain_alignment": federated_summary,
            }
        return state

    def get_alert_candidates(self) -> list[AlertCandidate]:
        if (
            not self.available
            or self.bridge is None
            or not self.bridge.steps
            or self.watcher is None
        ):
            return super().get_alert_candidates()

        latest_anomalies = [
            event for event in self.graph.latest_events(limit=8) if event.is_anomaly
        ]
        if len(latest_anomalies) < 3:
            return []

        latest = latest_anomalies[-1]
        risk_type = latest.risk_type

        # Find topological epicenter of latest step
        latest_step = self.bridge.steps[-1]
        epicenter_node = latest_step.epicenter_node
        if epicenter_node is None:
            return []

        supporting = []
        contradicting = []

        # Find events connected topologically
        for event_id, event in self.graph.events.items():
            if event.risk_type == risk_type:
                ev_epicenter = self.event_epicenters.get(event_id)
                if ev_epicenter is not None:
                    try:
                        import networkx as nx

                        if ev_epicenter == epicenter_node or nx.has_path(
                            self.bridge.core.graph, ev_epicenter, epicenter_node
                        ):
                            dist = nx.shortest_path_length(
                                self.bridge.core.graph, ev_epicenter, epicenter_node
                            )
                            if dist <= 2:
                                supporting.append(event_id)
                    except Exception:
                        if ev_epicenter == epicenter_node:
                            supporting.append(event_id)
            elif event.risk_type == "nominal" or event.risk_type != risk_type:
                ev_epicenter = self.event_epicenters.get(event_id)
                if ev_epicenter == epicenter_node:
                    contradicting.append(event_id)

        if not supporting:
            supporting = self.graph.find_supporting_events(risk_type, latest.tick)
            contradicting = self.graph.find_contradicting_events(risk_type, latest.tick)

        # Run topological multi-agent evaluations
        watcher_result = self.watcher.evaluate_event(self.bridge, latest)
        integrator_result = self.integrator.evaluate_alignment(
            self.bridge, epicenter_node, supporting, latest.tick
        )
        skeptic_result = self.skeptic.evaluate_confidence(
            self.bridge, epicenter_node, contradicting, latest.tick
        )
        federated_alignment = self.federation.alignment_for_candidate(
            risk_type=risk_type,
            tick=latest.tick,
            supporting_events=supporting,
            contradicting_events=contradicting,
            graph=self.graph,
        )

        evidence_alignment = integrator_result.score
        anomaly_score = watcher_result.score
        source_reliability = (
            mean([self.graph.events[event_id].source_reliability for event_id in supporting])
            if supporting
            else 0.5
        )

        persistence = min(1.0, len(supporting) / 5)

        route_relevance = float(latest.attributes.get("logistics_route_relevance", 0.72))
        if "distance_nm" in latest.attributes:
            route_relevance = max(0.2, 1 - float(latest.attributes["distance_nm"]) / 10)

        cross_modal_support = (
            0.72
            if len({self.graph.events[event_id].modality for event_id in supporting}) > 1
            else 0.42
        )

        recent_steps = self.bridge.steps[-5:]
        recent_signal = mean(step.manifold_signal for step in recent_steps)
        recent_burst_support = min(1.0, sum(step.burst_count for step in recent_steps) / 3)

        final_anomaly_score = clamp((0.60 * anomaly_score) + (0.40 * recent_signal))
        final_evidence_alignment = clamp(
            max(evidence_alignment, recent_signal, federated_alignment.context_geodesic_score)
        )
        final_cross_modal = clamp(
            max(
                cross_modal_support,
                federated_alignment.cross_domain_support,
                0.50 + (0.20 * recent_burst_support),
            )
        )

        return [
            AlertCandidate(
                scenario_id=latest.scenario_id,
                tick=latest.tick,
                risk_type=risk_type,
                anomaly_score=final_anomaly_score,
                evidence_alignment=final_evidence_alignment,
                persistence=persistence,
                proximity_or_route_relevance=route_relevance,
                source_reliability=source_reliability,
                cross_modal_support=final_cross_modal,
                data_quality=skeptic_result.confidence,
                supporting_events=supporting,
                contradicting_events=contradicting,
                context_geodesic_alignment=federated_alignment.context_geodesic_score,
                federated_alignment=federated_alignment.as_trace(),
            )
        ]

    def build_alerts(self) -> list[AlertCard]:
        if not self.available or self.bridge is None or self.watcher is None:
            return super().build_alerts()

        candidates = self.get_alert_candidates()
        alerts: list[AlertCard] = []

        for index, candidate in enumerate(candidates, start=1):
            latest_step = self.bridge.steps[-1]
            epicenter_node = latest_step.epicenter_node

            # Evaluate with agents
            watcher_result = self.watcher.evaluate_event(
                self.bridge, self.graph.events[candidate.supporting_events[-1]]
            )
            integrator_result = self.integrator.evaluate_alignment(
                self.bridge, epicenter_node, candidate.supporting_events, candidate.tick
            )
            risk_result = self.risk_officer.evaluate_risk(
                self.bridge, epicenter_node, candidate.supporting_events, candidate.tick
            )
            skeptic_result = self.skeptic.evaluate_confidence(
                self.bridge, epicenter_node, candidate.contradicting_events, candidate.tick
            )
            explanation_data = self.explainer.explain_alert(
                self.bridge,
                epicenter_node,
                candidate.supporting_events,
                candidate.contradicting_events,
            )
            agent_evidence = {
                "watcher": _agent_result_evidence(
                    watcher_result,
                    "Observed manifold anomaly pressure at the latest supporting event.",
                ),
                "integrator": _agent_result_evidence(
                    integrator_result,
                    "Aligned supporting events through native topological projections.",
                ),
                "risk_officer": _agent_result_evidence(
                    risk_result,
                    "Estimated risk from hotspot pressure and optimizer priority.",
                ),
                "skeptic": _agent_result_evidence(
                    skeptic_result,
                    "Estimated benign-alternative pressure from statistician signals.",
                ),
                "explainer": _agent_evidence_item(
                    "explainer",
                    float(explanation_data["score"]),
                    float(explanation_data["confidence"]),
                    candidate.supporting_events + candidate.contradicting_events,
                    "Traced relational flow and projection lineage for the alert narrative.",
                    notes=["native graph navigation and projection lineage"],
                    trace=dict(explanation_data["trace"]),
                ),
            }
            agent_evidence["integrator"].notes.append("mission aggregate alignment")
            agent_evidence["integrator"].trace.update(
                {
                    "context_geodesic_score": round(candidate.context_geodesic_alignment, 3),
                    "active_domains": candidate.federated_alignment.get("active_domains", []),
                    "domain_contributions": candidate.federated_alignment.get(
                        "domain_contributions", {}
                    ),
                    "candidate_team": candidate.federated_alignment.get("candidate_team", []),
                }
            )

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

            confidence = score_confidence(
                ConfidenceInputs(
                    data_quality=candidate.data_quality,
                    source_reliability=candidate.source_reliability,
                    agent_agreement=0.80,
                    temporal_consistency=candidate.persistence,
                    replay_completeness=min(1.0, len(candidate.supporting_events) / 4),
                    benign_alternative_score=skeptic_result.score,
                )
            )

            alert_id = f"alert-{candidate.scenario_id}-{candidate.tick:04d}-{index}"
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
                    benign_alternative_score=skeptic_result.score,
                ),
                supporting_events=candidate.supporting_events,
                contradicting_events=candidate.contradicting_events,
                context_geodesic_alignment=round(candidate.context_geodesic_alignment, 3),
                federated_alignment=candidate.federated_alignment,
                agent_votes={role: evidence.score for role, evidence in agent_evidence.items()},
                agent_evidence=agent_evidence,
                explanation=explanation_data["explanation"],
            )
            alerts.append(alert)

        self.alerts = alerts
        return alerts

    def replay(self, alert_id: str) -> ReplayTrace:
        if not self.available or self.bridge is None or self.watcher is None:
            return super().replay(alert_id)

        alert = next((item for item in self.alerts if item.alert_id == alert_id), None)
        if alert is None:
            return ReplayTrace(alert_id=alert_id)

        timeline = []
        for event_id in alert.supporting_events:
            event = self.graph.events[event_id]
            ev_epicenter = self.event_epicenters.get(event_id, "unknown")
            timeline.append(
                ReplayStep(
                    tick=event.tick,
                    event_id=event_id,
                    state_delta=f"Attractor focus at node {ev_epicenter} energy increased",
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

        latest_step = self.bridge.steps[-1]
        epicenter_node = latest_step.epicenter_node or "unknown"
        explanation_data = self.explainer.explain_alert(
            self.bridge, epicenter_node, alert.supporting_events, alert.contradicting_events
        )

        return ReplayTrace(
            alert_id=alert.alert_id,
            timeline=timeline,
            context_summary={
                "who": entities,
                "what": alert.risk_type,
                "where": f"topological manifold node {epicenter_node}",
                "when": f"tick {timeline[0].tick if timeline else alert.tick} through {alert.tick}",
                "why_flagged": explanation_data["explanation"],
            },
        )
