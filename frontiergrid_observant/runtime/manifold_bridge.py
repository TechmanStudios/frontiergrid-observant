"""Dynamic bridge into the local Frontier_OS / Exciton-MoA manifold runtime."""

from __future__ import annotations

import contextlib
import hashlib
import importlib
import io
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from frontiergrid_observant.schemas.events import ObservantEvent


def clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def resolve_frontier_os_root(frontier_os_root: Path | None = None) -> Path | None:
    local_root = Path(__file__).resolve().parent.parent / "exciton_moa"
    if local_root.exists():
        return local_root
    return None


@dataclass(frozen=True)
class ManifoldStep:
    target_coords: tuple[float, float, float]
    node_count: int
    edge_count: int
    active_node_count: int
    epicenter_node: str | None
    peak_resonance: float
    average_resonance: float
    burst_count: int
    max_hotspot: float
    tau_threshold: float
    manifold_signal: float
    scan_order_fingerprint: str

    def as_trace_metrics(self) -> dict[str, Any]:
        return {
            "target_coords": list(self.target_coords),
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "active_node_count": self.active_node_count,
            "epicenter_node": self.epicenter_node,
            "peak_resonance": self.peak_resonance,
            "average_resonance": self.average_resonance,
            "burst_count": self.burst_count,
            "max_hotspot": self.max_hotspot,
            "tau_threshold": self.tau_threshold,
            "manifold_signal": self.manifold_signal,
            "scan_order_fingerprint": self.scan_order_fingerprint,
        }


@dataclass
class FrontierManifoldBridge:
    root: Path
    node_count: int = 128
    tau_threshold: float = 1.0
    seed: int = 149
    suppress_output: bool = True
    core: Any | None = None
    prism: Any | None = None
    engine: Any | None = None
    orchestrator: Any | None = None
    mediator: Any | None = None
    np: Any | None = None
    steps: list[ManifoldStep] = field(default_factory=list)

    def initialize(self, scenario_id: str) -> None:
        modules = self._load_modules()
        scenario_seed = self._scenario_seed(scenario_id)
        config = modules["BlankManifoldConfig"](
            base_node_count=self.node_count,
            dimensionality=3,
        )
        self.core = modules["BlankManifoldCore"](config=config, seed=scenario_seed)
        with self._quiet():
            self.core.generate_manifold()
        mediator_state = self.root / "working_data" / f"mediator_{scenario_id}.json"
        self.mediator = modules["LatentMediator"](self.core, state_path=mediator_state)
        self.prism = modules["StatisticalPrism"](self.core)
        self.engine = modules["ExcitonEngine"](self.core, mediator=self.mediator)
        self.orchestrator = modules["OntologicalOrchestrator"](
            self.core,
            tau_threshold=self.tau_threshold,
            mediator=self.mediator,
            manifold_id=scenario_id,
        )
        self.steps = []

    def ingest_event(self, event: ObservantEvent) -> ManifoldStep:
        if (
            self.core is None
            or self.prism is None
            or self.engine is None
            or self.orchestrator is None
        ):
            raise RuntimeError("Frontier manifold bridge is not initialized")
        if self.np is None:
            raise RuntimeError("NumPy is unavailable for Frontier manifold bridge")

        embedding = self.event_to_embedding(event)
        with self._quiet():
            target_coords = self.prism.global_resonance_broadcast(embedding)
            self.engine.ignite_excitons(target_coords)
            bursts = self.orchestrator.scan_manifold()

        step = self._collect_step(target_coords=target_coords, bursts=bursts)
        self.steps.append(step)
        return step

    def event_to_embedding(self, event: ObservantEvent):
        if self.np is None:
            raise RuntimeError("NumPy is unavailable for Frontier manifold bridge")

        severity = event.ground_truth.severity if event.ground_truth else 0.0
        data_quality = float(event.attributes.get("data_quality", event.source_reliability))
        attribute_pressure = 0.0
        attribute_count = 0
        for key in sorted(event.attributes):
            value = event.attributes[key]
            if isinstance(value, bool):
                attribute_pressure += 1.0 if value else 0.0
            elif isinstance(value, int | float):
                attribute_pressure += clamp(abs(float(value)) / 100.0)
            elif isinstance(value, str):
                attribute_pressure += self._stable_unit(f"{key}:{value}")
            attribute_count += 1
        attribute_signal = attribute_pressure / attribute_count if attribute_count else 0.0

        semantic_signal = clamp(
            (0.35 * severity)
            + (0.20 * event.source_reliability)
            + (0.20 * data_quality)
            + (0.15 * attribute_signal)
            + (0.10 * self._stable_unit(event.risk_type))
        )
        center = -0.12 + (0.42 * semantic_signal)
        spread = 0.035 + (0.10 * clamp((severity + (1.0 - data_quality)) / 2.0))
        harmonic = self.np.asarray(
            [
                -1.0,
                -0.75,
                -0.50,
                -0.25,
                0.0,
                0.25,
                0.50,
                0.75,
                1.0,
                1.0,
                0.75,
                0.50,
                0.25,
                0.0,
                -0.25,
                -0.50,
                -0.75,
                -1.0,
            ],
            dtype=float,
        )
        jitter = self.np.asarray(
            [
                (self._stable_unit(f"{event.event_id}:{index}") - 0.5) * spread * 0.08
                for index in range(harmonic.size)
            ],
            dtype=float,
        )
        return center + (spread * harmonic) + jitter

    def summary(self) -> dict[str, Any]:
        if not self.steps:
            return {"available": True, "event_count": 0, "node_count": self.node_count}
        recent = self.steps[-8:]
        return {
            "available": True,
            "event_count": len(self.steps),
            "node_count": recent[-1].node_count,
            "edge_count": recent[-1].edge_count,
            "latest_peak_resonance": recent[-1].peak_resonance,
            "latest_burst_count": recent[-1].burst_count,
            "latest_manifold_signal": recent[-1].manifold_signal,
            "average_recent_signal": round(
                sum(step.manifold_signal for step in recent) / len(recent), 6
            ),
            "scan_order_fingerprint": recent[-1].scan_order_fingerprint,
        }

    def _load_modules(self) -> dict[str, Any]:
        import numpy as np
        self.np = np
        
        from frontiergrid_observant.exciton_moa.blank_config import BlankManifoldConfig
        from frontiergrid_observant.exciton_moa.blank_manifold_core import BlankManifoldCore
        from frontiergrid_observant.exciton_moa.transducer import StatisticalPrism
        from frontiergrid_observant.exciton_moa.excitons import ExcitonEngine
        from frontiergrid_observant.exciton_moa.telemetry import OntologicalOrchestrator
        from frontiergrid_observant.exciton_moa.latent_mediator import LatentMediator

        return {
            "BlankManifoldConfig": BlankManifoldConfig,
            "BlankManifoldCore": BlankManifoldCore,
            "StatisticalPrism": StatisticalPrism,
            "ExcitonEngine": ExcitonEngine,
            "OntologicalOrchestrator": OntologicalOrchestrator,
            "LatentMediator": LatentMediator,
        }

    def _collect_step(
        self, target_coords: Any, bursts: list[tuple[str, dict[str, Any]]]
    ) -> ManifoldStep:
        if self.core is None or self.orchestrator is None or self.np is None:
            raise RuntimeError("Frontier manifold bridge is not initialized")

        node_resonance = [
            float(data.get("resonance_accumulator", 0.0))
            for _, data in self.core.graph.nodes(data=True)
        ]
        peak_resonance = max(node_resonance, default=0.0)
        average_resonance = float(self.np.mean(node_resonance)) if node_resonance else 0.0
        active_nodes = [value for value in node_resonance if value > 0.1]
        epicenter_node = None
        if node_resonance:
            nodes = list(self.core.graph.nodes)
            epicenter_node = str(nodes[int(self.np.argmax(node_resonance))])

        hotspot_values = [float(metrics.get("H_total", 0.0)) for _, metrics in bursts]
        if not hotspot_values and epicenter_node is not None:
            hotspot_values.append(
                float(self.orchestrator.compute_local_hotspot(epicenter_node).get("H_total", 0.0))
            )
        max_hotspot = max(hotspot_values, default=0.0)
        tau = float(getattr(self.orchestrator, "tau", self.tau_threshold) or self.tau_threshold)
        burst_pressure = clamp(len(bursts) / max(1.0, self.node_count * 0.05))
        hotspot_pressure = clamp(max_hotspot / max(tau, 1e-9))
        resonance_pressure = clamp(peak_resonance)
        manifold_signal = clamp(
            (0.45 * resonance_pressure) + (0.35 * hotspot_pressure) + (0.20 * burst_pressure)
        )
        target = tuple(float(value) for value in self.np.asarray(target_coords, dtype=float)[:3])
        return ManifoldStep(
            target_coords=target,
            node_count=int(self.core.graph.number_of_nodes()),
            edge_count=int(self.core.graph.number_of_edges()),
            active_node_count=len(active_nodes),
            epicenter_node=epicenter_node,
            peak_resonance=round(peak_resonance, 6),
            average_resonance=round(average_resonance, 6),
            burst_count=len(bursts),
            max_hotspot=round(max_hotspot, 6),
            tau_threshold=round(tau, 6),
            manifold_signal=round(manifold_signal, 6),
            scan_order_fingerprint=str(
                getattr(self.orchestrator, "last_scan_order_fingerprint", "none")
            ),
        )

    def _quiet(self):
        if self.suppress_output:
            return contextlib.redirect_stdout(io.StringIO())
        return contextlib.nullcontext()

    def _scenario_seed(self, scenario_id: str) -> int:
        digest = hashlib.sha256(scenario_id.encode("utf-8")).hexdigest()
        return self.seed + int(digest[:8], 16) % 10_000

    def _stable_unit(self, value: str) -> float:
        digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
        return int(digest[:8], 16) / 0xFFFFFFFF
