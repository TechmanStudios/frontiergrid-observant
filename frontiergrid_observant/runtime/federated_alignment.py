"""Federated domain-manifold alignment for mission-level context fusion."""

from __future__ import annotations

from statistics import mean
from typing import Any

from pydantic import BaseModel, Field

from frontiergrid_observant.context.context_graph import ContextGraph
from frontiergrid_observant.runtime.base import SubstrateTrace
from frontiergrid_observant.schemas.events import ObservantEvent

DOMAIN_ALIASES = {
    "ais": "sea",
    "cyber": "cyber",
    "cyber_network": "cyber",
    "land": "land",
    "littoral": "land",
    "maritime": "sea",
    "network": "cyber",
    "space": "space",
    "weather": "air",
}


def clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class DomainManifoldState(BaseModel):
    domain: str
    event_count: int = 0
    last_tick: int = 0
    anomaly_pressure: float = Field(default=0.0, ge=0, le=1)
    source_quality: float = Field(default=1.0, ge=0, le=1)
    data_quality: float = Field(default=1.0, ge=0, le=1)
    hotspot_pressure: float = Field(default=0.0, ge=0, le=1)
    contradiction_pressure: float = Field(default=0.0, ge=0, le=1)
    active_risk_types: list[str] = Field(default_factory=list)
    active_modalities: list[str] = Field(default_factory=list)
    recent_event_ids: list[str] = Field(default_factory=list)

    def record(self, event: ObservantEvent, trace: SubstrateTrace) -> None:
        self.event_count += 1
        self.last_tick = max(self.last_tick, event.tick)
        self.anomaly_pressure = _running_average(
            self.anomaly_pressure, self.event_count, trace.anomaly_score
        )
        self.source_quality = _running_average(
            self.source_quality, self.event_count, event.source_reliability
        )
        self.data_quality = _running_average(self.data_quality, self.event_count, trace.data_quality)
        self.hotspot_pressure = _running_average(
            self.hotspot_pressure, self.event_count, _hotspot_pressure(trace)
        )
        self.contradiction_pressure = _running_average(
            self.contradiction_pressure, self.event_count, _contradiction_pressure(event)
        )
        if event.risk_type != "nominal" and event.risk_type not in self.active_risk_types:
            self.active_risk_types.append(event.risk_type)
        if event.modality not in self.active_modalities:
            self.active_modalities.append(event.modality)
        self.recent_event_ids = [*self.recent_event_ids, event.event_id][-8:]

    def contribution_for(self, event_ids: list[str]) -> float:
        overlap = len(set(event_ids).intersection(self.recent_event_ids))
        evidence_presence = clamp(overlap / max(1, len(event_ids)))
        return clamp(
            (0.30 * self.anomaly_pressure)
            + (0.25 * self.hotspot_pressure)
            + (0.20 * self.source_quality)
            + (0.15 * self.data_quality)
            + (0.10 * evidence_presence)
            - (0.20 * self.contradiction_pressure)
        )


class MissionAggregateAlignment(BaseModel):
    risk_type: str
    active_domains: list[str] = Field(default_factory=list)
    supporting_domains: dict[str, list[str]] = Field(default_factory=dict)
    domain_contributions: dict[str, float] = Field(default_factory=dict)
    context_geodesic_score: float = Field(default=0.0, ge=0, le=1)
    cross_domain_support: float = Field(default=0.0, ge=0, le=1)
    temporal_coherence: float = Field(default=0.0, ge=0, le=1)
    source_quality: float = Field(default=1.0, ge=0, le=1)
    data_quality: float = Field(default=1.0, ge=0, le=1)
    contradiction_pressure: float = Field(default=0.0, ge=0, le=1)
    uncertainty_pressure: float = Field(default=0.0, ge=0, le=1)
    candidate_team: list[str] = Field(default_factory=list)

    def as_trace(self) -> dict[str, Any]:
        return self.model_dump()


class FederatedDomainAlignment:
    """Tracks domain-local state and computes mission-level alignment signals."""

    def __init__(self) -> None:
        self.domains: dict[str, DomainManifoldState] = {}
        self.last_alignment = MissionAggregateAlignment(risk_type="nominal")

    def record_event(self, event: ObservantEvent, trace: SubstrateTrace) -> dict[str, Any]:
        domain = canonical_domain(event.domain)
        state = self.domains.setdefault(domain, DomainManifoldState(domain=domain))
        state.record(event, trace)
        self.last_alignment = self._mission_snapshot()
        return {
            "domain_manifold": state.model_dump(),
            "mission_aggregate": self.last_alignment.as_trace(),
        }

    def alignment_for_candidate(
        self,
        risk_type: str,
        tick: int,
        supporting_events: list[str],
        contradicting_events: list[str],
        graph: ContextGraph,
    ) -> MissionAggregateAlignment:
        supporting_by_domain: dict[str, list[str]] = {}
        support_records = []
        for event_id in supporting_events:
            event = graph.events.get(event_id)
            if event is None:
                continue
            domain = canonical_domain(event.domain)
            supporting_by_domain.setdefault(domain, []).append(event_id)
            support_records.append(event)

        domains = sorted(supporting_by_domain)
        domain_count = len(domains)
        domain_coverage = clamp(domain_count / 3)
        cross_domain_support = clamp(0.35 + (0.65 * domain_coverage)) if domain_count else 0.0
        temporal_coherence = _temporal_coherence([event.tick for event in support_records], tick)
        source_quality = mean([event.source_reliability for event in support_records]) if support_records else 0.0
        data_quality = (
            mean(
                [
                    float(event.attributes.get("data_quality", event.source_reliability))
                    for event in support_records
                ]
            )
            if support_records
            else 0.0
        )
        contradiction_pressure = clamp(len(contradicting_events) / 3)
        uncertainty_pressure = clamp(
            (0.45 * (1.0 - source_quality))
            + (0.35 * (1.0 - data_quality))
            + (0.20 * contradiction_pressure)
        )
        domain_contributions = {
            domain: round(self.domains[domain].contribution_for(event_ids), 3)
            for domain, event_ids in supporting_by_domain.items()
            if domain in self.domains
        }
        contribution_mean = mean(domain_contributions.values()) if domain_contributions else 0.0
        context_geodesic_score = clamp(
            (0.24 * domain_coverage)
            + (0.22 * temporal_coherence)
            + (0.18 * source_quality)
            + (0.16 * data_quality)
            + (0.20 * contribution_mean)
            - (0.18 * contradiction_pressure)
        )
        alignment = MissionAggregateAlignment(
            risk_type=risk_type,
            active_domains=domains,
            supporting_domains=supporting_by_domain,
            domain_contributions=domain_contributions,
            context_geodesic_score=round(context_geodesic_score, 3),
            cross_domain_support=round(cross_domain_support, 3),
            temporal_coherence=round(temporal_coherence, 3),
            source_quality=round(source_quality, 3),
            data_quality=round(data_quality, 3),
            contradiction_pressure=round(contradiction_pressure, 3),
            uncertainty_pressure=round(uncertainty_pressure, 3),
            candidate_team=_candidate_team(domains, context_geodesic_score, uncertainty_pressure),
        )
        self.last_alignment = alignment
        return alignment

    def summary(self) -> dict[str, Any]:
        return {
            "domain_count": len(self.domains),
            "domain_manifolds": {
                domain: state.model_dump() for domain, state in sorted(self.domains.items())
            },
            "mission_aggregate_alignment": self.last_alignment.as_trace(),
        }

    def _mission_snapshot(self) -> MissionAggregateAlignment:
        domains = sorted(self.domains)
        if not domains:
            return MissionAggregateAlignment(risk_type="nominal")
        contributions = {
            domain: round(state.contribution_for(state.recent_event_ids), 3)
            for domain, state in self.domains.items()
        }
        active_risks = [risk for state in self.domains.values() for risk in state.active_risk_types]
        risk_type = active_risks[-1] if active_risks else "nominal"
        source_quality = mean([state.source_quality for state in self.domains.values()])
        data_quality = mean([state.data_quality for state in self.domains.values()])
        contradiction_pressure = mean(
            [state.contradiction_pressure for state in self.domains.values()]
        )
        score = clamp(
            (0.35 * min(1.0, len(domains) / 3))
            + (0.25 * mean(contributions.values()))
            + (0.20 * source_quality)
            + (0.20 * data_quality)
            - (0.15 * contradiction_pressure)
        )
        return MissionAggregateAlignment(
            risk_type=risk_type,
            active_domains=domains,
            domain_contributions=contributions,
            context_geodesic_score=round(score, 3),
            cross_domain_support=round(clamp(len(domains) / 3), 3),
            source_quality=round(source_quality, 3),
            data_quality=round(data_quality, 3),
            contradiction_pressure=round(contradiction_pressure, 3),
            uncertainty_pressure=round(
                clamp((0.45 * (1.0 - source_quality)) + (0.35 * (1.0 - data_quality))), 3
            ),
            candidate_team=_candidate_team(domains, score, 1.0 - data_quality),
        )


def canonical_domain(domain: str) -> str:
    key = domain.strip().lower().replace(" ", "_").replace("-", "_")
    return DOMAIN_ALIASES.get(key, key or "unknown")


def _running_average(current: float, count: int, value: float) -> float:
    if count <= 1:
        return clamp(value)
    return clamp(((current * (count - 1)) + value) / count)


def _hotspot_pressure(trace: SubstrateTrace) -> float:
    metrics = trace.manifold_metrics
    if "manifold_signal" in metrics:
        return clamp(float(metrics["manifold_signal"]))
    if "mission_aggregate" in metrics:
        return clamp(float(metrics["mission_aggregate"].get("context_geodesic_score", 0.0)))
    return clamp((0.65 * trace.anomaly_score) + (0.35 * (1.0 - trace.data_quality)))


def _contradiction_pressure(event: ObservantEvent) -> float:
    if event.risk_type != "nominal":
        return 0.0
    markers = {"routine_transit", "stable", "nominal", "expected"}
    if any(str(value).lower() in markers for value in event.attributes.values()):
        return 0.5
    return 0.25


def _temporal_coherence(ticks: list[int], current_tick: int) -> float:
    if not ticks:
        return 0.0
    span = max(max(ticks) - min(ticks), current_tick - min(ticks))
    return clamp(1.0 - (span / 12.0))


def _candidate_team(
    active_domains: list[str], context_geodesic_score: float, uncertainty_pressure: float
) -> list[str]:
    team = [f"{domain}_domain_agent" for domain in active_domains]
    team.extend(["watcher", "integrator"])
    if context_geodesic_score >= 0.55:
        team.append("risk_officer")
    if uncertainty_pressure >= 0.25:
        team.append("skeptic")
    team.append("explainer")
    return team