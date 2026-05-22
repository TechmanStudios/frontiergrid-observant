"""Alert card schema for risk review outputs."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

AlertStatus = Literal["observe", "review_recommended", "human_escalation_review"]


class AgentVote(BaseModel):
    agent_name: str
    score: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)


class AgentEvidence(BaseModel):
    agent_name: str
    score: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    evidence_event_ids: list[str] = Field(default_factory=list)
    summary: str
    notes: list[str] = Field(default_factory=list)
    trace: dict[str, Any] = Field(default_factory=dict)


class AlertCard(BaseModel):
    alert_id: str
    scenario_id: str
    tick: int = Field(ge=0)
    title: str
    risk_type: str
    severity: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    data_quality: float = Field(ge=0, le=1)
    status: AlertStatus
    supporting_events: list[str] = Field(default_factory=list)
    contradicting_events: list[str] = Field(default_factory=list)
    context_geodesic_alignment: float = Field(default=0.0, ge=0, le=1)
    federated_alignment: dict[str, Any] = Field(default_factory=dict)
    agent_votes: dict[str, float] = Field(default_factory=dict)
    agent_evidence: dict[str, AgentEvidence] = Field(default_factory=dict)
    explanation: str
