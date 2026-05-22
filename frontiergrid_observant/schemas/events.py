"""Event schema for unclassified synthetic Observant-AI scenarios."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Location(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    confidence: float = Field(default=1.0, ge=0, le=1)


class GroundTruth(BaseModel):
    is_anomaly: bool = False
    risk_type: str = "nominal"
    severity: float = Field(default=0.0, ge=0, le=1)


class ObservantEvent(BaseModel):
    event_id: str
    scenario_id: str
    tick: int = Field(ge=0)
    timestamp: datetime
    domain: str
    modality: str
    source_id: str
    source_reliability: float = Field(ge=0, le=1)
    classification: str = "unclassified_synthetic"
    entity_refs: list[str] = Field(default_factory=list)
    location: Location | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)
    text: str | None = None
    ground_truth: GroundTruth | None = None

    @property
    def is_anomaly(self) -> bool:
        return bool(self.ground_truth and self.ground_truth.is_anomaly)

    @property
    def risk_type(self) -> str:
        if self.ground_truth:
            return self.ground_truth.risk_type
        return str(self.attributes.get("risk_type", "nominal"))
