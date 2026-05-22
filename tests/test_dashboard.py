import json

from frontiergrid_observant.demo.dashboard import export_demo_dashboard, render_demo_dashboard


def _comparison() -> dict[str, object]:
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
                    "fallback": _substrate("fallback", 0.8, 0.7),
                    "frontier_os": _substrate("frontier_os", 0.6, 0.5),
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


def _substrate(substrate: str, severity: float, confidence: float) -> dict[str, object]:
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
            "status": "review_recommended",
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


def _alert_card() -> dict[str, object]:
    return {
        "alert_id": "alert-scenario_01_maritime_shadowing-frontier_os",
        "scenario_id": "scenario_01_maritime_shadowing",
        "tick": 11,
        "title": "Potential shadowing pattern",
        "risk_type": "shadowing_pattern",
        "severity": 0.6,
        "confidence": 0.5,
        "data_quality": 0.75,
        "status": "review_recommended",
        "supporting_events": ["evt-s01-0011"],
        "contradicting_events": [],
        "agent_votes": {role: 0.5 for role in _roles()},
        "agent_evidence": {
            role: {
                "agent_name": role,
                "score": 0.5,
                "confidence": 0.6,
                "evidence_event_ids": ["evt-s01-0011"],
                "summary": f"{role} evidence summary",
                "notes": [],
                "trace": {"epicenter_node": "node_0001", "peak_resonance": 0.42},
            }
            for role in _roles()
        },
        "explanation": "Synthetic alert explanation.",
    }


def _roles() -> tuple[str, ...]:
    return ("watcher", "integrator", "risk_officer", "skeptic", "explainer")


def _ablation() -> dict[str, object]:
    return {
        "study": "observant_ablation_study",
        "seed": 149,
        "ticks": 12,
        "modes": ["rule_only", "fallback_shared_context"],
        "mode_descriptions": {
            "rule_only": "Event-local rules.",
            "fallback_shared_context": "Shared context.",
        },
        "expected_agent_roles": list(_roles()),
        "interpretation_guardrail": "Synthetic scenario-local evidence.",
        "scenarios": [
            {
                "scenario_key": "scenario_01",
                "scenario_id": "scenario_01_maritime_shadowing",
                "seed": 149,
                "ticks": 12,
                "modes": {
                    "rule_only": _ablation_mode("rule_only", 0.25, False),
                    "fallback_shared_context": _ablation_mode(
                        "fallback_shared_context", 0.95, True
                    ),
                },
                "deltas_vs_rule_only": {},
            }
        ],
    }


def _stress() -> dict[str, object]:
    return {
        "study": "observant_randomized_stress_study",
        "seed": 149,
        "runs": 2,
        "ticks": 12,
        "modes": ["rule_only", "fallback_shared_context"],
        "summary": {
            "rule_only": _stress_summary(0.5, 0.25, 0.0),
            "fallback_shared_context": _stress_summary(1.0, 0.95, 1.0),
        },
        "deltas_vs_rule_only": {},
        "records": [],
    }


def _progress() -> dict[str, object]:
    return {
        "artifact": "monte_carlo_progress",
        "status": "running",
        "message": "Running stress run 2 of 25.",
        "seed": 149,
        "seed_stride": 100,
        "ticks": 30,
        "runs": 25,
        "completed_runs": 1,
        "current_run": 2,
        "current_seed": 249,
        "last_completed_seed": 149,
        "scenarios": ["scenario_01"],
        "modes": ["rule_only", "fallback_shared_context"],
        "samples_completed": 10,
        "total_samples": 250,
        "percent_complete": 0.04,
        "started_at": "2026-05-21T12:00:00+00:00",
        "updated_at": "2026-05-21T12:04:00+00:00",
        "partial_summary": {},
    }


def _stress_summary(
    precision: float, analytic_completeness: float, evidence_complete_rate: float
) -> dict[str, object]:
    return {
        "samples": 2,
        "avg_alert_count": 1.0,
        "avg_first_alert_tick": 10.0,
        "avg_first_alert_severity": 0.6,
        "avg_first_alert_confidence": 0.7,
        "evidence_complete_rate": evidence_complete_rate,
        "avg_precision": precision,
        "avg_sensitivity": 0.5,
        "avg_miss_rate": 0.5,
        "avg_false_discovery_rate": 0.0,
        "avg_analytic_completeness": analytic_completeness,
        "avg_validity": 0.8,
        "avg_consistency": 0.7,
    }


def _ablation_mode(mode: str, analytic_completeness: float, complete: bool) -> dict[str, object]:
    return {
        "mode": mode,
        "description": mode,
        "reported_substrate": mode,
        "event_count": 12,
        "alert_count": 1,
        "first_alert_tick": 10,
        "first_alert": {
            "alert_id": f"alert-{mode}",
            "tick": 10,
            "title": "Potential shadowing pattern",
            "risk_type": "shadowing_pattern",
            "severity": 0.6,
            "confidence": 0.7,
            "data_quality": 0.8,
            "status": "review_recommended",
            "agent_roles_present": list(_roles()) if complete else ["rule_engine"],
            "expected_agent_evidence_complete": complete,
        },
        "metrics": {
            "scenario_id": "scenario_01_maritime_shadowing",
            "substrate": mode,
            "sensitivity": 0.5,
            "specificity": 1.0,
            "precision": 1.0,
            "miss_rate": 0.5,
            "false_discovery_rate": 0.0,
            "false_omission_rate": 0.0,
            "analytic_completeness": analytic_completeness,
            "uniqueness": 0.7,
            "validity": 0.8,
            "consistency": 0.7,
            "accuracy_under_noise": 1.0,
        },
    }


def test_render_demo_dashboard_includes_comparison_and_role_evidence() -> None:
    html = render_demo_dashboard(
        _comparison(),
        {"scenario_01_maritime_shadowing": _alert_card()},
        _ablation(),
        _stress(),
        _progress(),
    )

    assert "Risk Evidence Dashboard" in html
    assert "Monte Carlo Sweep" in html
    assert "1 / 25" in html
    assert "Run 2 seed 249" in html
    assert "Fallback vs Frontier_OS" in html
    assert "Rule, Sequential, Shared Context" in html
    assert "Multi-Seed Mode Averages" in html
    assert "Maritime Shadowing" in html
    assert "Watcher" in html
    assert "Risk Officer" in html
    assert "node_0001" in html


def test_export_demo_dashboard_writes_index_html(tmp_path) -> None:
    (tmp_path / "fallback_vs_frontier_os_metrics.json").write_text(
        json.dumps(_comparison()), encoding="utf-8"
    )
    (tmp_path / "scenario_01_maritime_shadowing_alerts.json").write_text(
        json.dumps([_alert_card()]), encoding="utf-8"
    )
    (tmp_path / "ablation_study_metrics.json").write_text(json.dumps(_ablation()), encoding="utf-8")
    (tmp_path / "stress_study_metrics.json").write_text(json.dumps(_stress()), encoding="utf-8")
    (tmp_path / "monte_carlo_progress.json").write_text(
        json.dumps(_progress()), encoding="utf-8"
    )

    dashboard_path = export_demo_dashboard(tmp_path)

    assert dashboard_path == tmp_path / "index.html"
    html = dashboard_path.read_text(encoding="utf-8")
    assert "Native Role Review" in html
    assert "Monte Carlo Sweep" in html
    assert "Rule Only" in html
    assert "Randomized Stress" in html
