from datetime import UTC, datetime

from frontiergrid_observant.ingest.synthetic_generator import SCENARIOS, generate_scenario
from frontiergrid_observant.runtime.federated_alignment import canonical_domain
from frontiergrid_observant.schemas.events import GroundTruth, Location, ObservantEvent


def test_observant_event_accepts_unclassified_synthetic_record() -> None:
    event = ObservantEvent(
        event_id="evt-test-001",
        scenario_id="scenario_test",
        tick=1,
        timestamp=datetime(2026, 5, 20, tzinfo=UTC),
        domain="maritime",
        modality="track",
        source_id="synthetic_feed",
        source_reliability=0.8,
        entity_refs=["vessel_alpha"],
        location=Location(lat=30.0, lon=-80.0, confidence=0.7),
        ground_truth=GroundTruth(is_anomaly=True, risk_type="shadowing_pattern", severity=0.6),
    )

    assert event.is_anomaly is True
    assert event.risk_type == "shadowing_pattern"
    assert event.classification == "unclassified_synthetic"


def test_builtin_scenarios_are_cross_domain() -> None:
    for scenario in SCENARIOS:
        events = generate_scenario(scenario, seed=149, ticks=20)
        anomaly_domains = {
            canonical_domain(event.domain) for event in events if event.is_anomaly
        }
        assert len(anomaly_domains) >= 4


def test_cross_domain_ambiguity_uses_all_core_domains() -> None:
    events = generate_scenario("scenario_04", seed=149, ticks=20)
    anomaly_domains = {canonical_domain(event.domain) for event in events if event.is_anomaly}

    assert anomaly_domains == {"air", "cyber", "land", "sea", "space"}


def test_unknown_unknown_scenario_injects_novelty_across_domains() -> None:
    events = generate_scenario("scenario_05", seed=149, ticks=20)
    anomaly_events = [event for event in events if event.is_anomaly]
    anomaly_domains = {canonical_domain(event.domain) for event in anomaly_events}
    novelty_events = [
        event for event in anomaly_events if event.attributes.get("unknown_unknown_marker")
    ]

    assert anomaly_domains == {"air", "cyber", "land", "sea", "space"}
    assert len(novelty_events) == 1
    assert anomaly_events[0].risk_type == "unknown_unknown_injection"
