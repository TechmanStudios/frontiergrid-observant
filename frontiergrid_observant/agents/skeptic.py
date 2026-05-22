"""Skeptic role: benign alternative exploration."""

from __future__ import annotations

from typing import Any

from frontiergrid_observant.agents.base import AgentResult, BaseAgent


class SkepticAgent(BaseAgent):
    name = "skeptic"

    def evaluate_confidence(
        self, bridge: Any, epicenter_node: str | None, contradicting_events: list[str], tick: int
    ) -> AgentResult:
        # The Skeptic uses The Statistician's pressure and variance to calculate false-positive risk.
        if epicenter_node is None:
            benign_score = min(0.65, len(contradicting_events) * 0.18)
            confidence = max(0.1, min(1.0, 1.0 - benign_score))
            return self.result(
                tick,
                benign_score,
                confidence,
                contradicting_events,
                notes=["fallback benign-alternative pressure"],
                trace={
                    "epicenter_node": epicenter_node,
                    "contradicting_event_count": len(contradicting_events),
                },
            )

        statistician_signal = None
        trace: dict[str, Any] = {
            "epicenter_node": epicenter_node,
            "contradicting_event_count": len(contradicting_events),
        }
        if bridge.mediator is not None:
            projections = bridge.mediator._blackboard.get(epicenter_node, [])
            for proj in projections:
                if proj.giant_name == "The Statistician":
                    statistician_signal = proj.vector

        if statistician_signal is not None:
            # Vector is [semantic_mass, semantic_pressure, 0.0]
            pressure = float(statistician_signal[1])
            benign_score = max(0.0, min(0.65, pressure * 0.15 + len(contradicting_events) * 0.18))
            trace["statistician_pressure"] = pressure
            trace["semantic_mass"] = float(statistician_signal[0])
        else:
            benign_score = min(0.65, len(contradicting_events) * 0.18)
            trace["statistician_signal"] = "unavailable"

        confidence = max(0.1, min(1.0, 1.0 - benign_score))
        trace["benign_alternative_score"] = benign_score
        return self.result(
            tick,
            benign_score,
            confidence,
            contradicting_events,
            notes=["native statistician pressure over contradictions"],
            trace=trace,
        )
