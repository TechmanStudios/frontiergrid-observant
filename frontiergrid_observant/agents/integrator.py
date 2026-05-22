"""Integrator role: multi-modal fusion."""

from __future__ import annotations

from typing import Any

from frontiergrid_observant.agents.base import AgentResult, BaseAgent


class IntegratorAgent(BaseAgent):
    name = "integrator"

    def evaluate_alignment(
        self, bridge: Any, epicenter_node: str | None, supporting_events: list[str], tick: int
    ) -> AgentResult:
        # The Integrator uses The Aligner's mode_signal and The Integrator's uncertainty.
        # It calculates the overall evidence alignment of the cluster.
        if epicenter_node is None or bridge.mediator is None:
            return self.result(
                tick,
                0.68,
                0.70,
                supporting_events,
                notes=["default alignment because no native epicenter was available"],
                trace={
                    "epicenter_node": epicenter_node,
                    "supporting_event_count": len(supporting_events),
                },
            )

        aligner_signal = None
        integrator_signal = None
        trace: dict[str, Any] = {
            "epicenter_node": epicenter_node,
            "supporting_event_count": len(supporting_events),
        }

        projections = bridge.mediator._blackboard.get(epicenter_node, [])
        for proj in projections:
            if proj.giant_name == "The Aligner":
                aligner_signal = proj.vector
            elif proj.giant_name == "The Integrator":
                integrator_signal = proj.vector

        if aligner_signal is not None:
            # aligner_signal = [mode_alignment, np.linalg.norm(semantic_mode), 1.0]
            mode_align = float(aligner_signal[0])
            alignment = max(0.0, min(1.0, 0.5 + 0.1 * mode_align))
            trace["aligner_mode_alignment"] = mode_align
            trace["aligner_vector_norm"] = float(aligner_signal[1])
        else:
            alignment = 0.68
            trace["aligner_signal"] = "unavailable"

        if integrator_signal is not None:
            # integrator_signal = [uncertainty, expansion_factor, norm(state_vector)]
            uncertainty = float(integrator_signal[0])
            confidence = max(0.0, min(1.0, 1.0 - 0.2 * uncertainty))
            trace["integrator_uncertainty"] = uncertainty
            trace["integrator_expansion_factor"] = float(integrator_signal[1])
        else:
            confidence = 0.70
            trace["integrator_signal"] = "unavailable"

        return self.result(
            tick,
            alignment,
            confidence,
            supporting_events,
            notes=["native alignment projection over supporting events"],
            trace=trace,
        )
