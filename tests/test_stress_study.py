import json

import pytest

from frontiergrid_observant.eval import stress_study
from frontiergrid_observant.ingest.synthetic_generator import SCENARIOS


def test_stress_study_aggregates_multiple_runs(tmp_path) -> None:
    study = stress_study.build_stress_study(
        seed=149,
        runs=2,
        ticks=18,
        modes=("rule_only", "centralized_sequential"),
    )
    metrics_path, report_path = stress_study.write_stress_artifacts(study, tmp_path)

    assert study["study"] == "observant_randomized_stress_study"
    assert study["runs"] == 2
    assert len(study["records"]) == 2 * len(SCENARIOS) * 2
    assert study["summary"]["rule_only"]["samples"] == 2 * len(SCENARIOS)
    assert "centralized_sequential" in study["deltas_vs_rule_only"]
    assert "avg_precision" in study["summary"]["centralized_sequential"]

    exported = json.loads(metrics_path.read_text(encoding="utf-8"))
    report = report_path.read_text(encoding="utf-8")
    assert exported["runs"] == 2
    assert "Observant-AI Randomized Stress Study" in report
    assert "Mode Averages" in report


def test_stress_study_writes_progress_artifact(tmp_path) -> None:
    study = stress_study.build_stress_study(
        seed=149,
        runs=1,
        ticks=12,
        modes=("rule_only",),
        progress_artifact_root=tmp_path,
    )

    progress_path = tmp_path / stress_study.PROGRESS_FILENAME
    progress = json.loads(progress_path.read_text(encoding="utf-8"))

    assert study["runs"] == 1
    assert progress["status"] == "completed"
    assert progress["completed_runs"] == 1
    assert progress["percent_complete"] == 1.0
    assert progress["samples_completed"] == len(SCENARIOS)
    assert progress["total_samples"] == len(SCENARIOS)


def test_stress_study_rejects_zero_runs() -> None:
    with pytest.raises(ValueError, match="runs"):
        stress_study.build_stress_study(runs=0)
