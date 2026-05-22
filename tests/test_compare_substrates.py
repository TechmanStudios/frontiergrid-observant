import json

from frontiergrid_observant.eval import compare_substrates
from frontiergrid_observant.ingest.synthetic_generator import SCENARIOS, generate_scenario


def test_comparison_artifacts_include_all_scenarios_and_substrates(monkeypatch, tmp_path) -> None:
    def fake_run_demo(
        scenario: str,
        substrate: str,
        seed: int,
        ticks: int,
    ) -> dict[str, object]:
        events = generate_scenario(scenario, seed=seed, ticks=ticks)
        scenario_id = events[0].scenario_id
        severity = 0.5 if substrate == "fallback" else 0.6
        return {
            "scenario_id": scenario_id,
            "substrate": substrate,
            "event_count": len(events),
            "context": {"substrate_metrics": {"available": substrate == "frontier_os"}},
            "alerts": [
                {
                    "alert_id": f"alert-{scenario_id}-{substrate}",
                    "scenario_id": scenario_id,
                    "tick": ticks - 1,
                    "title": "Synthetic comparison alert",
                    "risk_type": "comparison_test",
                    "severity": severity,
                    "confidence": 0.7,
                    "data_quality": 0.8,
                    "status": "review_recommended",
                    "supporting_events": [events[-1].event_id],
                    "contradicting_events": [],
                    "agent_votes": {
                        role: severity for role in compare_substrates.EXPECTED_AGENT_ROLES
                    },
                    "agent_evidence": {
                        role: {
                            "agent_name": role,
                            "score": severity,
                            "confidence": 0.7,
                            "evidence_event_ids": [events[-1].event_id],
                            "summary": f"{role} evidence",
                            "notes": [],
                            "trace": {},
                        }
                        for role in compare_substrates.EXPECTED_AGENT_ROLES
                    },
                    "explanation": "Synthetic comparison explanation.",
                }
            ],
        }

    monkeypatch.setattr(compare_substrates, "run_demo", fake_run_demo)

    comparison = compare_substrates.build_substrate_comparison(seed=149, ticks=12)
    metrics_path, report_path = compare_substrates.write_comparison_artifacts(comparison, tmp_path)

    assert {scenario["scenario_key"] for scenario in comparison["scenarios"]} == set(SCENARIOS)
    for scenario in comparison["scenarios"]:
        assert set(scenario["substrates"]) == {"fallback", "frontier_os"}
        assert scenario["delta"]["native_agent_evidence_complete"] is True

    exported = json.loads(metrics_path.read_text(encoding="utf-8"))
    report = report_path.read_text(encoding="utf-8")
    assert len(exported["scenarios"]) == len(SCENARIOS)
    assert "Fallback vs Frontier_OS Comparison" in report
    assert "Native Delta" in report
