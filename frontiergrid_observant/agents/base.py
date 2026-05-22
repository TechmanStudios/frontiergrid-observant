"""Base agent result schema."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AgentResult(BaseModel):
    agent_name: str
    tick: int = Field(ge=0)
    score: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    evidence_event_ids: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    trace: dict[str, Any] = Field(default_factory=dict)


class BaseAgent:
    name = "base"

    def result(
        self,
        tick: int,
        score: float,
        confidence: float,
        evidence: list[str],
        notes: list[str] | None = None,
        trace: dict[str, Any] | None = None,
    ) -> AgentResult:
        return AgentResult(
            agent_name=self.name,
            tick=tick,
            score=score,
            confidence=confidence,
            evidence_event_ids=evidence,
            notes=notes or [],
            trace=trace or {},
        )
