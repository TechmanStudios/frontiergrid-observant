"""Risk Officer role: threat assessment."""

from __future__ import annotations

from typing import Any

import numpy as np

from frontiergrid_observant.agents.base import AgentResult, BaseAgent


class RiskOfficerAgent(BaseAgent):
    name = "risk_officer"

    def evaluate_risk(
        self, bridge: Any, epicenter_node: str | None, supporting_events: list[str], tick: int
    ) -> AgentResult:
        # The Risk Officer uses The Optimizer's gradient/priority metric to calculate risk severity.
        if epicenter_node is None:
            return self.result(
                tick,
                0.5,
                0.8,
                supporting_events,
                notes=["default risk because no native epicenter was available"],
                trace={
                    "epicenter_node": epicenter_node,
                    "supporting_event_count": len(supporting_events),
                },
            )

        optimizer_signal = None
        trace: dict[str, Any] = {
            "epicenter_node": epicenter_node,
            "supporting_event_count": len(supporting_events),
        }
        if bridge.mediator is not None:
            projections = bridge.mediator._blackboard.get(epicenter_node, [])
            for proj in projections:
                if proj.giant_name == "The Optimizer":
                    optimizer_signal = proj.vector

        if optimizer_signal is not None:
            priority_metric = float(np.linalg.norm(optimizer_signal))
            severity = max(0.1, min(1.0, priority_metric / 2.0))
            trace["optimizer_priority_metric"] = priority_metric
        else:
            severity = 0.5
            trace["optimizer_signal"] = "unavailable"

        metrics = bridge.orchestrator.compute_local_hotspot(epicenter_node)
        h_total = metrics.get("H_total", 0.0)
        tau = getattr(bridge.orchestrator, "tau", 1.0)
        trace["hotspot_total"] = float(h_total)
        trace["tau_threshold"] = float(tau)

        risk_score = max(severity, min(1.0, h_total / max(tau * 2.0, 1e-9)))
        return self.result(
            tick,
            risk_score,
            0.8,
            supporting_events,
            notes=["native hotspot pressure and optimizer priority"],
            trace=trace,
        )
