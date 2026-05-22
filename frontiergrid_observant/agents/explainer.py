"""Explainer role: narrative reporting."""

from __future__ import annotations

from typing import Any

from frontiergrid_observant.agents.base import BaseAgent


class ExplainerAgent(BaseAgent):
    name = "explainer"

    def explain_alert(
        self,
        bridge: Any,
        epicenter_node: str | None,
        supporting_events: list[str],
        contradicting_events: list[str],
    ) -> dict[str, Any]:
        # Explainer uses The Graph Navigator and The Linear Algebraist's projections
        # to trace explicit relational links (lineage) and generate a summary.
        if epicenter_node is None:
            support_text = (
                ", ".join(supporting_events) if supporting_events else "no supporting events"
            )
            contradiction_text = (
                ", ".join(contradicting_events)
                if contradicting_events
                else "no recent nominal contradiction"
            )
            return {
                "explanation": f"Alert triggered with no specific epicenter. Bounded by: {contradiction_text}. Support: {support_text}.",
                "score": min(1.0, len(supporting_events) / 4),
                "confidence": 0.55,
                "cycle_count": 0.0,
                "flux": 0.0,
                "lineage_weight": 0.0,
                "trace": {
                    "epicenter_node": epicenter_node,
                    "supporting_event_count": len(supporting_events),
                    "contradicting_event_count": len(contradicting_events),
                },
            }

        navigator_signal = None
        algebraist_signal = None
        if bridge.mediator is not None:
            projections = bridge.mediator._blackboard.get(epicenter_node, [])
            for proj in projections:
                if proj.giant_name == "The Graph Navigator":
                    navigator_signal = proj.vector
                elif proj.giant_name == "The Linear Algebraist":
                    algebraist_signal = proj.vector

        cycle_count = float(navigator_signal[0]) if navigator_signal is not None else 0.0
        flux = float(navigator_signal[1]) if navigator_signal is not None else 0.0
        lineage_weight = (
            float(sum(abs(float(value)) for value in algebraist_signal))
            if algebraist_signal is not None
            else 0.0
        )

        support_text = ", ".join(supporting_events) if supporting_events else "no supporting events"
        contradiction_text = (
            ", ".join(contradicting_events)
            if contradicting_events
            else "no recent nominal contradiction"
        )

        explanation = (
            f"The alert is triggered over a topological attractor centered at node {epicenter_node}. "
            f"Relational flow tracing verified {int(cycle_count)} cycles with {flux:.2f} residual flux. "
            f"Linear projection weight is {lineage_weight:.2f}. "
            f"Supporting evidence includes events: {support_text}. Bounded by: {contradiction_text}."
        )
        score = min(1.0, len(supporting_events) / 4)
        confidence = min(
            1.0,
            0.55
            + min(cycle_count / 20.0, 0.15)
            + min(abs(flux) / 10.0, 0.15)
            + min(lineage_weight / 10.0, 0.15),
        )

        return {
            "explanation": explanation,
            "score": score,
            "confidence": confidence,
            "cycle_count": cycle_count,
            "flux": flux,
            "lineage_weight": lineage_weight,
            "trace": {
                "epicenter_node": epicenter_node,
                "cycle_count": cycle_count,
                "flux": flux,
                "lineage_weight": lineage_weight,
                "supporting_event_count": len(supporting_events),
                "contradicting_event_count": len(contradicting_events),
            },
        }
