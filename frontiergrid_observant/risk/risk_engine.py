"""Deterministic risk and confidence formulas for the Phase I fallback path."""

from __future__ import annotations

from pydantic import BaseModel, Field

from frontiergrid_observant.schemas.alerts import AlertStatus


def clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


class RiskInputs(BaseModel):
    anomaly_score: float = Field(ge=0, le=1)
    evidence_alignment: float = Field(ge=0, le=1)
    persistence: float = Field(ge=0, le=1)
    proximity_or_route_relevance: float = Field(ge=0, le=1)
    source_reliability: float = Field(ge=0, le=1)
    cross_modal_support: float = Field(ge=0, le=1)


class ConfidenceInputs(BaseModel):
    data_quality: float = Field(ge=0, le=1)
    source_reliability: float = Field(ge=0, le=1)
    agent_agreement: float = Field(ge=0, le=1)
    temporal_consistency: float = Field(ge=0, le=1)
    replay_completeness: float = Field(ge=0, le=1)
    benign_alternative_score: float = Field(default=0.0, ge=0, le=1)


def score_risk(inputs: RiskInputs) -> float:
    return clamp(
        0.30 * inputs.anomaly_score
        + 0.25 * inputs.evidence_alignment
        + 0.15 * inputs.persistence
        + 0.15 * inputs.proximity_or_route_relevance
        + 0.10 * inputs.source_reliability
        + 0.05 * inputs.cross_modal_support
    )


def score_confidence(inputs: ConfidenceInputs) -> float:
    confidence = (
        0.35 * inputs.data_quality
        + 0.25 * inputs.source_reliability
        + 0.20 * inputs.agent_agreement
        + 0.10 * inputs.temporal_consistency
        + 0.10 * inputs.replay_completeness
    )
    return clamp(confidence * (1 - 0.35 * inputs.benign_alternative_score))


def status_for(
    severity: float,
    confidence: float,
    *,
    data_quality: float = 1.0,
    source_reliability: float = 1.0,
    benign_alternative_score: float = 0.0,
) -> AlertStatus:
    uncertainty_control = severity >= 0.48 and (
        data_quality <= 0.68 or source_reliability <= 0.68 or benign_alternative_score >= 0.55
    )
    if uncertainty_control:
        return "human_escalation_review"
    if severity >= 0.78 and confidence >= 0.70:
        return "human_escalation_review"
    if severity >= 0.48 and confidence >= 0.45:
        return "review_recommended"
    return "observe"
