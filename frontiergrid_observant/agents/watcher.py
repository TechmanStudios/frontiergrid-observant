"""Watcher role: local anomaly detection."""

from __future__ import annotations

from typing import Any

from frontiergrid_observant.agents.base import AgentResult, BaseAgent


class WatcherAgent(BaseAgent):
    name = "watcher"

    def evaluate_event(self, bridge: Any, event: Any) -> AgentResult:
        # The Watcher looks at the latest ManifoldStep to detect anomalies.
        # It uses the peak resonance and max hotspot values.
        if not bridge.steps:
            score = 0.0
            trace = {"event_id": event.event_id, "manifold_step": "unavailable"}
        else:
            step = bridge.steps[-1]
            score = float(step.manifold_signal)
            trace = {
                "event_id": event.event_id,
                "epicenter_node": step.epicenter_node,
                "peak_resonance": step.peak_resonance,
                "max_hotspot": step.max_hotspot,
                "burst_count": step.burst_count,
                "manifold_signal": step.manifold_signal,
            }

        confidence = float(event.attributes.get("data_quality", event.source_reliability))
        return self.result(
            event.tick,
            score,
            confidence,
            [event.event_id],
            notes=["latest event manifold pressure"],
            trace=trace,
        )
