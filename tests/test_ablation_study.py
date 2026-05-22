import json

from frontiergrid_observant.eval import ablation_study
from frontiergrid_observant.ingest.synthetic_generator import SCENARIOS


def test_ablation_study_exports_rule_and_sequential_baselines(tmp_path) -> None:
    study = ablation_study.build_ablation_study(
        seed=149,
        ticks=18,
        modes=("rule_only", "centralized_sequential"),
    )
    metrics_path, report_path = ablation_study.write_ablation_artifacts(study, tmp_path)

    assert study["study"] == "observant_ablation_study"
    assert {scenario["scenario_key"] for scenario in study["scenarios"]} == set(SCENARIOS)
    for scenario in study["scenarios"]:
        assert set(scenario["modes"]) == {"rule_only", "centralized_sequential"}
        assert "centralized_sequential" in scenario["deltas_vs_rule_only"]
        for result in scenario["modes"].values():
            assert "metrics" in result
            assert "analytic_completeness" in result["metrics"]

    exported = json.loads(metrics_path.read_text(encoding="utf-8"))
    report = report_path.read_text(encoding="utf-8")
    assert exported["modes"] == ["rule_only", "centralized_sequential"]
    assert "Observant-AI Ablation Study" in report
    assert "Deltas vs Rule-Only" in report


def test_fallback_shared_context_has_complete_expected_evidence() -> None:
    study = ablation_study.build_ablation_study(
        seed=149,
        ticks=18,
        scenarios=["scenario_01"],
        modes=("fallback_shared_context",),
    )

    result = study["scenarios"][0]["modes"]["fallback_shared_context"]

    assert result["alert_count"] > 0
    assert result["first_alert"]["expected_agent_evidence_complete"] is True
    assert set(result["first_alert"]["agent_roles_present"]) == set(
        ablation_study.EXPECTED_AGENT_ROLES
    )


def test_unknown_unknown_injection_requires_shared_context() -> None:
    study = ablation_study.build_ablation_study(
        seed=149,
        ticks=20,
        scenarios=["scenario_05"],
        modes=("rule_only", "centralized_sequential", "fallback_shared_context"),
    )

    modes = study["scenarios"][0]["modes"]

    assert modes["rule_only"]["alert_count"] == 0
    assert modes["centralized_sequential"]["alert_count"] == 0
    assert modes["fallback_shared_context"]["alert_count"] > 0
    assert modes["fallback_shared_context"]["first_alert"]["risk_type"] == "unknown_unknown_injection"
    assert modes["fallback_shared_context"]["first_alert"]["status"] == "human_escalation_review"
    assert modes["fallback_shared_context"]["metrics"]["active_domain_coverage"] >= 0.8
