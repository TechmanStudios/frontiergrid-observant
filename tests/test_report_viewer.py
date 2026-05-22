"""Tests for the console report viewer.

See [test_report_viewer.py](file:///g:/aiDoW/DON/DON26BZ01-NVO23/frontiergrid-observant/tests/test_report_viewer.py).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from _pytest.capture import CaptureFixture

from rich.console import Console

from frontiergrid_observant.demo.report_viewer import main


def _mock_comparison() -> dict[str, Any]:
    return {
        "comparison": "fallback_vs_frontier_os",
        "seed": 149,
        "ticks": 12,
        "substrates": ["fallback", "frontier_os"],
        "expected_agent_roles": [
            "watcher",
            "integrator",
            "risk_officer",
            "skeptic",
            "explainer",
        ],
        "scenarios": [
            {
                "scenario_key": "scenario_01",
                "scenario_id": "scenario_01_maritime_shadowing",
                "seed": 149,
                "ticks": 12,
                "substrates": {
                    "fallback": _mock_substrate("fallback", 0.8, 0.7),
                    "frontier_os": _mock_substrate("frontier_os", 0.6, 0.5),
                },
                "delta": {
                    "alert_count_delta": 0,
                    "first_alert_tick_delta": 0,
                    "severity_delta": -0.2,
                    "confidence_delta": -0.2,
                    "native_agent_evidence_complete": True,
                },
            }
        ],
    }


def _mock_substrate(substrate: str, severity: float, confidence: float) -> dict[str, Any]:
    return {
        "substrate": substrate,
        "reported_substrate": substrate,
        "substrate_available": True,
        "event_count": 12,
        "alert_count": 1,
        "first_alert_tick": 11,
        "first_alert": {
            "alert_id": f"alert-{substrate}",
            "tick": 11,
            "title": "Potential shadowing pattern",
            "risk_type": "shadowing_pattern",
            "severity": severity,
            "confidence": confidence,
            "data_quality": 0.75,
            "status": "human_escalation_review",
            "agent_roles_present": [
                "explainer",
                "integrator",
                "risk_officer",
                "skeptic",
                "watcher",
            ],
            "all_agent_evidence_present": True,
        },
        "metrics": {
            "scenario_id": "scenario_01_maritime_shadowing",
            "substrate": substrate,
            "sensitivity": 0.5,
            "specificity": 1.0,
            "precision": 1.0,
            "miss_rate": 0.5,
            "false_discovery_rate": 0.0,
            "false_omission_rate": 0.0,
            "analytic_completeness": 0.74,
            "uniqueness": 0.72,
            "validity": 0.78,
            "consistency": 0.70,
            "accuracy_under_noise": 1.0,
        },
    }


def _mock_alerts() -> list[dict[str, Any]]:
    return [
        {
            "alert_id": "alert-scenario_01_maritime_shadowing-0029-1",
            "scenario_id": "scenario_01_maritime_shadowing",
            "tick": 29,
            "title": "Potential shadowing pattern",
            "risk_type": "shadowing_pattern",
            "severity": 0.758,
            "confidence": 0.594,
            "data_quality": 0.502,
            "status": "human_escalation_review",
            "supporting_events": ["evt-s01-0029"],
            "contradicting_events": [],
            "context_geodesic_alignment": 0.639,
            "agent_votes": {
                "watcher": 0.683,
                "integrator": 0.5,
                "risk_officer": 0.598,
                "skeptic": 0.498,
                "explainer": 1.0,
            },
            "agent_evidence": {
                "watcher": {
                    "agent_name": "watcher",
                    "score": 0.683,
                    "confidence": 0.77,
                    "evidence_event_ids": ["evt-s01-0029"],
                    "summary": "Observed manifold anomaly pressure.",
                    "notes": ["latest event manifold pressure"],
                    "trace": {
                        "event_id": "evt-s01-0029",
                        "epicenter_node": "node_0799",
                        "peak_resonance": 26.737,
                    },
                },
                "integrator": {
                    "agent_name": "integrator",
                    "score": 0.5,
                    "confidence": 0.912,
                    "evidence_event_ids": ["evt-s01-0029"],
                    "summary": "Aligned supporting events.",
                    "notes": ["native alignment projection"],
                    "trace": {
                        "epicenter_node": "node_0799",
                    },
                },
                "risk_officer": {
                    "agent_name": "risk_officer",
                    "score": 0.598,
                    "confidence": 0.8,
                    "evidence_event_ids": ["evt-s01-0029"],
                    "summary": "Estimated risk.",
                    "notes": ["hotspot pressure"],
                    "trace": {
                        "epicenter_node": "node_0799",
                    },
                },
                "skeptic": {
                    "agent_name": "skeptic",
                    "score": 0.498,
                    "confidence": 0.502,
                    "evidence_event_ids": [],
                    "summary": "Estimated benign alternatives.",
                    "notes": ["statistician pressure"],
                    "trace": {
                        "epicenter_node": "node_0799",
                    },
                },
                "explainer": {
                    "agent_name": "explainer",
                    "score": 1.0,
                    "confidence": 1.0,
                    "evidence_event_ids": ["evt-s01-0029"],
                    "summary": "Traced relational flow.",
                    "notes": ["navigation lineage"],
                    "trace": {
                        "epicenter_node": "node_0799",
                    },
                },
            },
            "explanation": "Test explanation.",
        }
    ]


def test_report_viewer_prints_summary(tmp_path: Path, capsys: CaptureFixture[str]) -> None:
    comp_file = tmp_path / "fallback_vs_frontier_os_metrics.json"
    comp_file.write_text(json.dumps(_mock_comparison()), encoding="utf-8")

    console = Console(width=200)
    main(["--summary", "--artifact-root", str(tmp_path)], console=console)
    captured = capsys.readouterr()

    assert "FrontierGrid-Observant Substrate Comparison" in captured.out
    assert "Maritime Shadowing" in captured.out
    assert "fallback" in captured.out
    assert "frontier_os" in captured.out
    assert "Complete" in captured.out


def test_report_viewer_prints_scenario_details(tmp_path: Path, capsys: CaptureFixture[str]) -> None:
    comp_file = tmp_path / "fallback_vs_frontier_os_metrics.json"
    comp_file.write_text(json.dumps(_mock_comparison()), encoding="utf-8")

    alerts_file = tmp_path / "scenario_01_maritime_shadowing_alerts.json"
    alerts_file.write_text(json.dumps(_mock_alerts()), encoding="utf-8")

    console = Console(width=200)
    main(["--scenario", "scenario_01", "--artifact-root", str(tmp_path)], console=console)
    captured = capsys.readouterr()

    assert "Scenario Detail: Maritime Shadowing" in captured.out
    assert "Potential shadowing pattern" in captured.out
    assert "Watcher Agent" in captured.out
    assert "Skeptic Agent" in captured.out
    assert "Test explanation." in captured.out


def test_report_viewer_missing_comparison_errors(tmp_path: Path, capsys: CaptureFixture[str]) -> None:
    main(["--artifact-root", str(tmp_path)])
    captured = capsys.readouterr()

    assert "Error: Comparison metrics file not found" in captured.out
