import json

from frontiergrid_observant.demo.run_demo import run_demo

EXPECTED_AGENT_ROLES = {"watcher", "integrator", "risk_officer", "skeptic", "explainer"}


def test_demo_returns_alert_payload() -> None:
    payload = run_demo(scenario="scenario_01", seed=149, ticks=18)

    assert payload["scenario_id"] == "scenario_01_maritime_shadowing"
    assert payload["event_count"] == 18
    assert payload["alerts"]
    alert = payload["alerts"][0]
    assert set(alert["agent_evidence"]) == EXPECTED_AGENT_ROLES
    assert set(alert["agent_votes"]) == EXPECTED_AGENT_ROLES
    assert alert["agent_evidence"]["explainer"]["summary"]


def test_degraded_comms_routes_uncertainty_to_human_review() -> None:
    payload = run_demo(scenario="scenario_03", seed=149, ticks=18)

    assert payload["scenario_id"] == "scenario_03_degraded_comms_decoy"
    assert payload["alerts"]
    assert payload["alerts"][0]["status"] == "human_escalation_review"


def test_demo_export_writes_agent_evidence_to_alert_cards(tmp_path) -> None:
    payload = run_demo(
        scenario="scenario_01",
        seed=149,
        ticks=18,
        export=True,
        artifact_root=tmp_path,
    )
    alerts_path = tmp_path / f"{payload['scenario_id']}_alerts.json"

    alerts = json.loads(alerts_path.read_text(encoding="utf-8"))

    assert set(alerts[0]["agent_evidence"]) == EXPECTED_AGENT_ROLES
    for role in EXPECTED_AGENT_ROLES:
        evidence = alerts[0]["agent_evidence"][role]
        assert evidence["agent_name"] == role
        assert 0 <= evidence["score"] <= 1
        assert 0 <= evidence["confidence"] <= 1
        assert evidence["summary"]
        assert isinstance(evidence["trace"], dict)
