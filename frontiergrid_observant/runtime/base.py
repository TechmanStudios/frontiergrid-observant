"""Runtime adapter contracts."""

from __future__ import annotations

from typing import Any, Protocol

from pydantic import BaseModel, Field

from frontiergrid_observant.schemas.alerts import AlertCard
from frontiergrid_observant.schemas.events import ObservantEvent
from frontiergrid_observant.schemas.provenance import ReplayTrace


class SubstrateTrace(BaseModel):
    tick: int
    event_id: str
    substrate: str
    anomaly_score: float = Field(ge=0, le=1)
    data_quality: float = Field(ge=0, le=1)
    notes: list[str] = Field(default_factory=list)
    manifold_metrics: dict[str, Any] = Field(default_factory=dict)


class ContextState(BaseModel):
    scenario_id: str
    tick: int
    event_count: int
    active_risk_types: list[str] = Field(default_factory=list)
    data_quality: float = Field(default=1.0, ge=0, le=1)
    substrate_metrics: dict[str, Any] = Field(default_factory=dict)


class AlertCandidate(BaseModel):
    scenario_id: str
    tick: int
    risk_type: str
    anomaly_score: float = Field(ge=0, le=1)
    evidence_alignment: float = Field(ge=0, le=1)
    persistence: float = Field(ge=0, le=1)
    proximity_or_route_relevance: float = Field(ge=0, le=1)
    source_reliability: float = Field(ge=0, le=1)
    cross_modal_support: float = Field(ge=0, le=1)
    data_quality: float = Field(ge=0, le=1)
    supporting_events: list[str] = Field(default_factory=list)
    contradicting_events: list[str] = Field(default_factory=list)
    context_geodesic_alignment: float = Field(default=0.0, ge=0, le=1)
    federated_alignment: dict[str, Any] = Field(default_factory=dict)


class ReasoningSubstrate(Protocol):
    def initialize(self, scenario_id: str) -> None: ...

    def ingest_event(self, event: ObservantEvent) -> SubstrateTrace: ...

    def get_context_state(self) -> ContextState: ...

    def get_alert_candidates(self) -> list[AlertCandidate]: ...

    def build_alerts(self) -> list[AlertCard]: ...

    def replay(self, alert_id: str) -> ReplayTrace: ...
