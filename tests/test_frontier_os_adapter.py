from pathlib import Path

from frontiergrid_observant.ingest.synthetic_generator import generate_scenario
from frontiergrid_observant.runtime.frontier_os_adapter import FrontierOSAdapter
from frontiergrid_observant.runtime.manifold_bridge import (
    FrontierManifoldBridge,
    resolve_frontier_os_root,
)

EXPECTED_AGENT_ROLES = {"watcher", "integrator", "risk_officer", "skeptic", "explainer"}


def _frontier_os_root() -> Path:
    root = resolve_frontier_os_root()
    assert root is not None
    return root


def test_frontier_manifold_bridge_runs_one_event() -> None:
    events = generate_scenario("scenario_01", seed=149, ticks=3)
    bridge = FrontierManifoldBridge(root=_frontier_os_root(), node_count=1024, tau_threshold=1.0)
    bridge.initialize(events[0].scenario_id)

    step = bridge.ingest_event(events[0])

    assert step.node_count == 1024
    assert step.edge_count > 0
    assert step.peak_resonance > 0
    assert 0 <= step.manifold_signal <= 1
    assert step.scan_order_fingerprint != "none"


def test_frontier_os_adapter_uses_real_manifold_when_available() -> None:
    events = generate_scenario("scenario_01", seed=149, ticks=6)
    adapter = FrontierOSAdapter(_frontier_os_root(), node_count=1024, tau_threshold=1.0)
    adapter.initialize(events[0].scenario_id)

    trace = adapter.ingest_event(events[0])
    state = adapter.get_context_state()

    assert adapter.available is True
    assert trace.substrate == "frontier_os"
    assert trace.manifold_metrics["node_count"] == 1024
    assert trace.manifold_metrics["peak_resonance"] > 0
    assert state.substrate_metrics["available"] is True


def test_frontier_os_alert_exports_native_agent_evidence() -> None:
    events = generate_scenario("scenario_01", seed=149, ticks=18)
    adapter = FrontierOSAdapter(_frontier_os_root(), node_count=128, tau_threshold=1.0)
    adapter.initialize(events[0].scenario_id)

    for event in events:
        adapter.ingest_event(event)

    alerts = adapter.build_alerts()
    alert = alerts[0].model_dump()

    assert set(alert["agent_evidence"]) == EXPECTED_AGENT_ROLES
    assert alert["agent_evidence"]["watcher"]["trace"]["epicenter_node"]
    assert "peak_resonance" in alert["agent_evidence"]["watcher"]["trace"]
    assert "hotspot_total" in alert["agent_evidence"]["risk_officer"]["trace"]
    assert "lineage_weight" in alert["agent_evidence"]["explainer"]["trace"]
    assert "sol_intuition" in alert["agent_evidence"]["integrator"]["trace"]
    assert "hunch" in alert["agent_evidence"]["integrator"]["trace"]["sol_intuition"]


def test_all_seven_giants_are_active_and_functional() -> None:
    events = generate_scenario("scenario_01", seed=149, ticks=15)
    adapter = FrontierOSAdapter(_frontier_os_root(), node_count=128, tau_threshold=1.0)
    adapter.initialize(events[0].scenario_id)

    # Ingest events to ignite excitons
    for event in events:
        adapter.ingest_event(event)

    # Verify that the mediator has recorded projections from the giants
    bridge = adapter.bridge
    assert bridge is not None
    assert bridge.mediator is not None

    # Collect all projecting giants that wrote to the blackboard
    projected_giants = set()
    for entries in bridge.mediator._blackboard.values():
        for entry in entries:
            projected_giants.add(entry.giant_name)

    expected_projected_giants = {
        "The Statistician",
        "The Optimizer",
        "The Graph Navigator",
        "The Linear Algebraist",
        "The Aligner",
        "The Integrator",
    }
    
    # Assert that all projecting giants are active and have recorded projections
    assert expected_projected_giants.issubset(projected_giants), f"Missing projected giants: {expected_projected_giants - projected_giants}"

    # Verify that the N-Body Solver has warped space (collapsed edges)
    collapsed_edges = [
        (u, v) for u, v, d in bridge.core.graph.edges(data=True) if d.get("collapsed") is True
    ]
    assert len(collapsed_edges) > 0, "N-Body Solver was not active (no collapsed edges found)"

