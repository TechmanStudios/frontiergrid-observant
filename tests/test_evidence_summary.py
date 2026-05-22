import json

from frontiergrid_observant.eval.evidence_summary import (
    build_evidence_summary,
    write_evidence_summary_artifacts,
)
from frontiergrid_observant.eval.stress_study import build_stress_study


def test_evidence_summary_highlights_unknown_unknown_shared_context(tmp_path) -> None:
    stress = build_stress_study(
        seed=149,
        runs=1,
        ticks=20,
        scenarios=["scenario_05"],
        modes=("rule_only", "centralized_sequential", "fallback_shared_context"),
    )

    summary = build_evidence_summary(stress)
    metrics_path, report_path = write_evidence_summary_artifacts(summary, tmp_path)

    assert summary["summary"] == "observant_scenario_evidence_summary"
    assert summary["unknown_unknown_check"]["status"] == "supported"
    assert summary["unknown_unknown_check"]["baseline_modes_missed"] is True
    assert summary["unknown_unknown_check"]["shared_context_detected"] is True
    assert (
        summary["unknown_unknown_check"]["mode_results"]["rule_only"]["detection_rate"]
        == 0.0
    )
    assert (
        summary["unknown_unknown_check"]["mode_results"]["fallback_shared_context"][
            "detection_rate"
        ]
        == 1.0
    )

    exported = json.loads(metrics_path.read_text(encoding="utf-8"))
    report = report_path.read_text(encoding="utf-8")
    assert exported["summary"] == "observant_scenario_evidence_summary"
    assert "Scenario Evidence Summary" in report
    assert "Unknown-Unknown Check" in report
    assert "Detected through shared context" in report