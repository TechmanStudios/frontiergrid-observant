from datetime import UTC, datetime

from frontiergrid_observant.runtime.fallback_adapter import FallbackAdapter
from frontiergrid_observant.runtime.federated_alignment import canonical_domain
from frontiergrid_observant.schemas.events import GroundTruth, ObservantEvent


def _event(
    event_id: str,
    tick: int,
    domain: str,
    modality: str,
    reliability: float = 0.82,
    data_quality: float = 0.78,
) -> ObservantEvent:
    return ObservantEvent(
        event_id=event_id,
        scenario_id="federated_scenario",
        tick=tick,
        timestamp=datetime(2026, 5, 20, 13, tick, tzinfo=UTC),
        domain=domain,
        modality=modality,
        source_id=f"synthetic_{domain}_source",
        source_reliability=reliability,
        entity_refs=["vessel_alpha", "route_corridor_a"],
        attributes={"data_quality": data_quality, "alignment_score": 0.74},
        text="Synthetic cross-domain support for a shared anomaly hypothesis.",
        ground_truth=GroundTruth(
            is_anomaly=True,
            risk_type="shadowing_pattern",
            severity=0.72,
        ),
    )


def test_canonical_domain_maps_operational_aliases() -> None:
    assert canonical_domain("maritime") == "sea"
    assert canonical_domain("cyber_network") == "cyber"
    assert canonical_domain("littoral") == "land"


def test_fallback_adapter_exports_federated_alignment() -> None:
    adapter = FallbackAdapter()
    adapter.initialize("federated_scenario")
    events = [
        _event("evt-fed-0001", 1, "maritime", "track"),
        _event("evt-fed-0002", 2, "space", "imagery_metadata"),
        _event("evt-fed-0003", 3, "cyber_network", "network_status", data_quality=0.70),
        _event("evt-fed-0004", 4, "maritime", "operator_note"),
    ]

    for event in events:
        adapter.ingest_event(event)

    context = adapter.get_context_state().model_dump()
    alerts = adapter.build_alerts()

    federation = context["substrate_metrics"]["federated_domain_alignment"]
    aggregate = alerts[0].agent_evidence["integrator"].trace

    assert federation["domain_count"] == 3
    assert set(federation["domain_manifolds"]) == {"cyber", "sea", "space"}
    assert alerts[0].context_geodesic_alignment > 0.65
    assert set(aggregate["active_domains"]) == {"cyber", "sea", "space"}
    assert "risk_officer" in aggregate["candidate_team"]
    assert aggregate["domain_contributions"]