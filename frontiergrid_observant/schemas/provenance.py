"""Provenance and replay schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class EvidenceRef(BaseModel):
    event_id: str
    role: str
    summary: str


class ReplayStep(BaseModel):
    tick: int = Field(ge=0)
    event_id: str
    state_delta: str
    dominant_agent: str
    confidence_delta: float


class ReplayTrace(BaseModel):
    alert_id: str
    timeline: list[ReplayStep] = Field(default_factory=list)
    context_summary: dict[str, Any] = Field(default_factory=dict)

    def to_markdown(self) -> str:
        lines = [f"# Replay Trace: {self.alert_id}", ""]
        if self.context_summary:
            lines.append("## Context Summary")
            for key, value in self.context_summary.items():
                lines.append(f"- {key}: {value}")
            lines.append("")
        lines.append("## Timeline")
        for step in self.timeline:
            lines.append(
                f"- Tick {step.tick}: `{step.event_id}` changed state: {step.state_delta} "
                f"({step.dominant_agent}, confidence delta {step.confidence_delta:+.2f})"
            )
        return "\n".join(lines).strip() + "\n"
