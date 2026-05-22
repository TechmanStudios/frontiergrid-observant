"""Static demo dashboard export for generated artifacts."""

from __future__ import annotations

import argparse
import json
import re
from html import escape
from pathlib import Path
from typing import Any

from frontiergrid_observant.config import load_settings

ROLE_LABELS = {
    "watcher": "Watcher",
    "integrator": "Integrator",
    "risk_officer": "Risk Officer",
    "skeptic": "Skeptic",
    "explainer": "Explainer",
}
TRACE_KEYS = (
    "epicenter_node",
    "peak_resonance",
    "manifold_signal",
    "max_hotspot",
    "hotspot_total",
    "benign_alternative_score",
    "statistician_pressure",
    "lineage_weight",
    "cycle_count",
    "flux",
    "context_geodesic_score",
    "active_domains",
    "candidate_team",
)


def export_demo_dashboard(artifact_root: Path | None = None) -> Path:
    root = artifact_root or load_settings().artifact_root
    root.mkdir(parents=True, exist_ok=True)
    comparison_path = root / "fallback_vs_frontier_os_metrics.json"
    if not comparison_path.exists():
        raise FileNotFoundError(
            f"Comparison artifact not found: {comparison_path}. Run compare_substrates first."
        )

    comparison = json.loads(comparison_path.read_text(encoding="utf-8"))
    ablation_path = root / "ablation_study_metrics.json"
    ablation = (
        json.loads(ablation_path.read_text(encoding="utf-8")) if ablation_path.exists() else None
    )
    stress_path = root / "stress_study_metrics.json"
    stress = json.loads(stress_path.read_text(encoding="utf-8")) if stress_path.exists() else None
    progress_path = root / "monte_carlo_progress.json"
    progress = (
      json.loads(progress_path.read_text(encoding="utf-8"))
      if progress_path.exists()
      else None
    )
    alert_cards = _load_alert_cards(root)
    dashboard_path = root / "index.html"
    dashboard_path.write_text(
      render_demo_dashboard(comparison, alert_cards, ablation, stress, progress),
        encoding="utf-8",
    )
    return dashboard_path


def render_demo_dashboard(
    comparison: dict[str, Any],
    alert_cards: dict[str, dict[str, Any]],
    ablation: dict[str, Any] | None = None,
    stress: dict[str, Any] | None = None,
  progress: dict[str, Any] | None = None,
) -> str:
    scenarios = comparison.get("scenarios", [])
    native_complete = sum(
        1
        for scenario in scenarios
        if scenario.get("delta", {}).get("native_agent_evidence_complete")
    )
    native_available = sum(
        1
        for scenario in scenarios
        if scenario.get("substrates", {}).get("frontier_os", {}).get("substrate_available")
    )
    confidence_deltas = [
        scenario.get("delta", {}).get("confidence_delta")
        for scenario in scenarios
        if scenario.get("delta", {}).get("confidence_delta") is not None
    ]
    severity_deltas = [
        scenario.get("delta", {}).get("severity_delta")
        for scenario in scenarios
        if scenario.get("delta", {}).get("severity_delta") is not None
    ]

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>FrontierGrid-Observant Demo</title>
  <style>
{_dashboard_css()}
  </style>
</head>
<body>
  <main class="shell">
    <header class="topbar">
      <div>
        <p class="eyebrow">FrontierGrid-Observant</p>
        <h1>Risk Evidence Dashboard</h1>
      </div>
      <div class="run-meta">
        <span>Unclassified synthetic demo</span>
        <span>Seed {_html(comparison.get("seed"))}</span>
        <span>{_html(comparison.get("ticks"))} ticks</span>
      </div>
    </header>

    {_monte_carlo_progress(progress)}

    <section class="summary-grid" aria-label="Run summary">
      {_summary_tile("Scenarios", len(scenarios), "Synthetic challenge runs")}
      {_summary_tile("Native available", f"{native_available}/{len(scenarios)}", "Frontier_OS substrate")}
      {_summary_tile("Evidence complete", f"{native_complete}/{len(scenarios)}", "Five role alert cards")}
      {_summary_tile("Avg native delta", _average_delta(severity_deltas, confidence_deltas), "Severity / confidence")}
    </section>

    <section class="comparison-section">
      <div class="section-heading">
        <p class="eyebrow">Baseline Comparison</p>
        <h2>Fallback vs Frontier_OS</h2>
      </div>
      <div class="table-wrap">
        {_comparison_table(comparison)}
      </div>
    </section>

    {_ablation_section(ablation)}

  {_stress_section(stress)}

    <section class="scenario-section">
      <div class="section-heading">
        <p class="eyebrow">Alert Evidence</p>
        <h2>Native Role Review</h2>
      </div>
      {_scenario_tabs(scenarios)}
      <div class="scenario-panels">
        {_scenario_panels(scenarios, alert_cards)}
      </div>
    </section>
  </main>
  <script>
{_dashboard_js()}
  </script>
</body>
</html>
"""


def _load_alert_cards(artifact_root: Path) -> dict[str, dict[str, Any]]:
    alert_cards: dict[str, dict[str, Any]] = {}
    for path in sorted(artifact_root.glob("*_alerts.json")):
        alerts = json.loads(path.read_text(encoding="utf-8"))
        if not alerts:
            continue
        first_alert = alerts[0]
        alert_cards[str(first_alert["scenario_id"])] = first_alert
    return alert_cards


def _summary_tile(label: str, value: Any, caption: str) -> str:
    return f"""
      <article class="summary-tile">
        <span>{_html(label)}</span>
        <strong>{_html(value)}</strong>
        <small>{_html(caption)}</small>
      </article>"""


def _monte_carlo_progress(progress: dict[str, Any] | None) -> str:
    if not progress:
        return ""
    percent = _percent(progress.get("percent_complete", 0.0))
    status = str(progress.get("status", "unknown"))
    completed_runs = progress.get("completed_runs", 0)
    total_runs = progress.get("runs", 0)
    current_run = progress.get("current_run")
    current_seed = progress.get("current_seed")
    samples_completed = progress.get("samples_completed", 0)
    total_samples = progress.get("total_samples", 0)
    updated_at = progress.get("updated_at", "n/a")
    message = progress.get("message", "Monte Carlo sweep status")
    run_text = f"{completed_runs} / {total_runs}"
    active_text = (
        f"Run {current_run} seed {current_seed}" if current_run else "No active run"
    )
    return f"""
    <section class="monte-carlo-progress" aria-label="Monte Carlo sweep progress">
      <div class="progress-head">
        <div>
          <p class="eyebrow">Monte Carlo Sweep</p>
          <h2>{_html(_label(status))}</h2>
        </div>
        {_status_pill(status)}
      </div>
      <div class="progress-meter-row">
        <div class="progress-meter" aria-label="{percent}% complete">
          <span style="width: {percent}%"></span>
        </div>
        <strong>{percent}%</strong>
      </div>
      <div class="progress-facts">
        {_progress_fact("Runs", run_text)}
        {_progress_fact("Active", active_text)}
        {_progress_fact("Samples", f"{samples_completed} / {total_samples}")}
        {_progress_fact("Updated", updated_at)}
      </div>
      <p>{_html(message)}</p>
    </section>"""


def _progress_fact(label: str, value: Any) -> str:
    return f"""
        <div class="progress-fact">
          <span>{_html(label)}</span>
          <strong>{_html(value)}</strong>
        </div>"""


def _comparison_table(comparison: dict[str, Any]) -> str:
    rows = []
    for scenario in comparison.get("scenarios", []):
        for substrate in comparison.get("substrates", []):
            result = scenario["substrates"][substrate]
            first_alert = result.get("first_alert") or {}
            metrics = result["metrics"]
            rows.append(
                "<tr>"
                f"<th>{_scenario_name(scenario['scenario_id'])}</th>"
                f"<td>{_substrate_badge(substrate, result.get('substrate_available'))}</td>"
                f"<td>{_html(result['alert_count'])}</td>"
                f"<td>{_html(_display(first_alert.get('tick')))}</td>"
                f"<td>{_score_cell(first_alert.get('severity'), 'severity')}</td>"
                f"<td>{_score_cell(first_alert.get('confidence'), 'confidence')}</td>"
                f"<td>{_score_cell(first_alert.get('context_geodesic_alignment'), 'quality')}</td>"
                f"<td>{_status_pill(first_alert.get('status'))}</td>"
                f"<td>{_score_cell(metrics.get('precision'), 'precision')}</td>"
                f"<td>{_score_cell(metrics.get('sensitivity'), 'sensitivity')}</td>"
                f"<td>{_evidence_state(first_alert)}</td>"
                "</tr>"
            )
    return (
        '<table class="comparison-table">'
        "<thead><tr>"
        "<th>Scenario</th><th>Substrate</th><th>Alerts</th><th>First tick</th>"
        "<th>Severity</th><th>Confidence</th><th>Alignment</th><th>Status</th><th>Precision</th>"
        "<th>Sensitivity</th><th>Evidence</th>"
        "</tr></thead>"
        f"<tbody>{''.join(rows)}</tbody>"
        "</table>"
    )


def _ablation_section(ablation: dict[str, Any] | None) -> str:
    if not ablation:
        return ""
    return f"""
    <section class="comparison-section">
      <div class="section-heading">
        <p class="eyebrow">Ablation Evidence</p>
        <h2>Rule, Sequential, Shared Context</h2>
      </div>
      <div class="table-wrap">
        {_ablation_table(ablation)}
      </div>
    </section>"""


def _ablation_table(ablation: dict[str, Any]) -> str:
    rows = []
    for scenario in ablation.get("scenarios", []):
        for mode in ablation.get("modes", []):
            result = scenario["modes"][mode]
            first_alert = result.get("first_alert") or {}
            metrics = result["metrics"]
            rows.append(
                "<tr>"
                f"<th>{_scenario_name(scenario['scenario_id'])}</th>"
                f'<td><span class="badge">{_html(_label(mode))}</span></td>'
                f"<td>{_html(result['alert_count'])}</td>"
                f"<td>{_html(_display(first_alert.get('tick')))}</td>"
                f"<td>{_score_cell(first_alert.get('context_geodesic_alignment'), 'quality')}</td>"
                f"<td>{_score_cell(metrics.get('active_domain_coverage'), 'quality')}</td>"
                f"<td>{_score_cell(metrics.get('precision'), 'precision')}</td>"
                f"<td>{_score_cell(metrics.get('sensitivity'), 'sensitivity')}</td>"
                f"<td>{_score_cell(metrics.get('false_discovery_rate'), 'severity')}</td>"
                f"<td>{_score_cell(metrics.get('analytic_completeness'), 'quality')}</td>"
                f"<td>{_evidence_state(first_alert)}</td>"
                "</tr>"
            )
    return (
        '<table class="comparison-table">'
        "<thead><tr>"
        "<th>Scenario</th><th>Mode</th><th>Alerts</th><th>First tick</th><th>Alignment</th><th>Domains</th>"
        "<th>Precision</th><th>Sensitivity</th><th>FDR</th>"
        "<th>Analytic completeness</th><th>Evidence</th>"
        "</tr></thead>"
        f"<tbody>{''.join(rows)}</tbody>"
        "</table>"
    )


def _stress_section(stress: dict[str, Any] | None) -> str:
    if not stress:
        return ""
    return f"""
    <section class="comparison-section">
      <div class="section-heading">
        <p class="eyebrow">Randomized Stress</p>
        <h2>Multi-Seed Mode Averages</h2>
      </div>
      <div class="table-wrap">
        {_stress_table(stress)}
      </div>
    </section>"""


def _stress_table(stress: dict[str, Any]) -> str:
    rows = []
    for mode in stress.get("modes", []):
        summary = stress.get("summary", {}).get(mode, {})
        rows.append(
            "<tr>"
            f'<th><span class="badge">{_html(_label(mode))}</span></th>'
            f"<td>{_html(summary.get('samples'))}</td>"
            f"<td>{_html(_display(summary.get('avg_first_alert_tick')))}</td>"
            f"<td>{_score_cell(summary.get('avg_context_geodesic_alignment'), 'quality')}</td>"
            f"<td>{_score_cell(summary.get('avg_active_domain_coverage'), 'quality')}</td>"
            f"<td>{_score_cell(summary.get('avg_precision'), 'precision')}</td>"
            f"<td>{_score_cell(summary.get('avg_sensitivity'), 'sensitivity')}</td>"
            f"<td>{_score_cell(summary.get('avg_false_discovery_rate'), 'severity')}</td>"
            f"<td>{_score_cell(summary.get('avg_analytic_completeness'), 'quality')}</td>"
            f"<td>{_html(_percent_text(summary.get('evidence_complete_rate')))}</td>"
            "</tr>"
        )
    return (
        '<table class="comparison-table">'
        "<thead><tr>"
        "<th>Mode</th><th>Samples</th><th>Avg first tick</th><th>Alignment</th><th>Domains</th>"
        "<th>Precision</th><th>Sensitivity</th><th>FDR</th>"
        "<th>Analytic completeness</th><th>Evidence complete</th>"
        "</tr></thead>"
        f"<tbody>{''.join(rows)}</tbody>"
        "</table>"
    )


def _scenario_tabs(scenarios: list[dict[str, Any]]) -> str:
    buttons = []
    for index, scenario in enumerate(scenarios):
        active = " is-active" if index == 0 else ""
        selected = "true" if index == 0 else "false"
        target = _scenario_dom_id(scenario["scenario_id"])
        buttons.append(
            f'<button class="tab{active}" type="button" data-target="{target}" '
            f'aria-selected="{selected}">{_scenario_name(scenario["scenario_id"])}</button>'
        )
    return f'<div class="tabs" role="tablist">{"".join(buttons)}</div>'


def _scenario_panels(
    scenarios: list[dict[str, Any]], alert_cards: dict[str, dict[str, Any]]
) -> str:
    panels = []
    for index, scenario in enumerate(scenarios):
        scenario_id = str(scenario["scenario_id"])
        alert = alert_cards.get(scenario_id)
        active = " is-active" if index == 0 else ""
        panels.append(
            f'<article class="scenario-panel{active}" id="{_scenario_dom_id(scenario_id)}">'
            f"{_scenario_header(scenario)}"
            f"{_alert_detail(alert)}"
            "</article>"
        )
    return "".join(panels)


def _scenario_header(scenario: dict[str, Any]) -> str:
    delta = scenario.get("delta", {})
    return f"""
      <div class="scenario-head">
        <div>
          <h3>{_scenario_name(scenario["scenario_id"])}</h3>
          <p>{_html(scenario["scenario_id"])}</p>
        </div>
        <div class="delta-grid">
          {_delta_chip("Tick delta", delta.get("first_alert_tick_delta"))}
          {_delta_chip("Severity", delta.get("severity_delta"))}
          {_delta_chip("Confidence", delta.get("confidence_delta"))}
        </div>
      </div>"""


def _alert_detail(alert: dict[str, Any] | None) -> str:
    if alert is None:
        return '<div class="empty-state">No alert artifact exported for this scenario.</div>'

    roles = alert.get("agent_evidence", {})
    role_cards = "".join(_role_card(role, roles.get(role, {})) for role in ROLE_LABELS)
    return f"""
      <div class="alert-summary">
        <div>
          <p class="eyebrow">{_html(alert.get("risk_type"))}</p>
          <h4>{_html(alert.get("title"))}</h4>
          <p>{_html(alert.get("explanation"))}</p>
        </div>
        <div class="alert-metrics">
          {_metric_block("Severity", alert.get("severity"), "severity")}
          {_metric_block("Confidence", alert.get("confidence"), "confidence")}
          {_metric_block("Data quality", alert.get("data_quality"), "quality")}
          {_metric_block("Alignment", alert.get("context_geodesic_alignment"), "quality")}
          {_status_pill(alert.get("status"))}
        </div>
      </div>
      <div class="role-grid">{role_cards}</div>"""


def _role_card(role: str, evidence: dict[str, Any]) -> str:
    score = evidence.get("score")
    confidence = evidence.get("confidence")
    trace_items = _trace_items(evidence.get("trace", {}))
    evidence_count = len(evidence.get("evidence_event_ids", []))
    return f"""
      <article class="role-card">
        <header>
          <span>{_html(ROLE_LABELS[role])}</span>
          <strong>{_html(_display(score))}</strong>
        </header>
        {_bar(score, role)}
        <p>{_html(evidence.get("summary", "No role evidence exported."))}</p>
        <dl>
          <div><dt>Confidence</dt><dd>{_html(_display(confidence))}</dd></div>
          <div><dt>Evidence</dt><dd>{_html(evidence_count)}</dd></div>
          {trace_items}
        </dl>
      </article>"""


def _trace_items(trace: dict[str, Any]) -> str:
    items = []
    for key in TRACE_KEYS:
        if key in trace:
            items.append(
                f"<div><dt>{_html(_label(key))}</dt><dd>{_html(_display(trace[key]))}</dd></div>"
            )
        if len(items) == 4:
            break
    return "".join(items)


def _metric_block(label: str, value: Any, kind: str) -> str:
    return f"""
      <div class="metric-block">
        <span>{_html(label)}</span>
        <strong>{_html(_display(value))}</strong>
        {_bar(value, kind)}
      </div>"""


def _score_cell(value: Any, kind: str) -> str:
    return f'<div class="score-cell"><span>{_html(_display(value))}</span>{_bar(value, kind)}</div>'


def _bar(value: Any, kind: str) -> str:
    return (
        f'<div class="bar bar-{_html(kind)}" aria-hidden="true">'
        f'<span style="width: {_percent(value)}%"></span></div>'
    )


def _substrate_badge(substrate: str, available: Any) -> str:
    availability = "available" if available else "safe mode"
    return f'<span class="badge badge-{_html(substrate)}">{_html(substrate)}</span><small>{availability}</small>'


def _status_pill(status: Any) -> str:
    status_text = str(status or "n/a")
    return f'<span class="status status-{_slug(status_text)}">{_html(_label(status_text))}</span>'


def _evidence_state(first_alert: dict[str, Any]) -> str:
    if not first_alert:
        return "n/a"
    evidence_complete = first_alert.get("all_agent_evidence_present") or first_alert.get(
        "expected_agent_evidence_complete"
    )
    return "complete" if evidence_complete else "partial"


def _delta_chip(label: str, value: Any) -> str:
    return f'<span class="delta-chip"><small>{_html(label)}</small><strong>{_html(_display(value))}</strong></span>'


def _average_delta(severity_deltas: list[float], confidence_deltas: list[float]) -> str:
    severity = sum(severity_deltas) / len(severity_deltas) if severity_deltas else 0.0
    confidence = sum(confidence_deltas) / len(confidence_deltas) if confidence_deltas else 0.0
    return f"{severity:+.3f} / {confidence:+.3f}"


def _display(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def _percent(value: Any) -> int:
    if not isinstance(value, int | float):
        return 0
    return round(max(0.0, min(1.0, float(value))) * 100)


def _percent_text(value: Any) -> str:
    if not isinstance(value, int | float):
        return "n/a"
    return f"{_percent(value)}%"


def _scenario_name(scenario_id: str) -> str:
    return _label(
        scenario_id.removeprefix("scenario_01_")
        .removeprefix("scenario_02_")
        .removeprefix("scenario_03_")
    )


def _scenario_dom_id(scenario_id: str) -> str:
    return f"panel-{_slug(scenario_id)}"


def _label(value: str) -> str:
    return value.replace("_", " ").strip().title()


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9-]+", "-", value.lower()).strip("-")


def _html(value: Any) -> str:
    return escape(_display(value))


def _dashboard_css() -> str:
    return """
:root {
  color-scheme: dark;
  --bg: #0b1014;
  --surface: #121922;
  --surface-strong: #1b2733;
  --surface-soft: #0f151c;
  --ink: #e8eef2;
  --muted: #a6b3bd;
  --line: #293743;
  --teal: #50d6cf;
  --amber: #f1b24a;
  --berry: #e2779f;
  --blue: #8eb5ff;
  --green: #9ed97e;
  --red: #ff8a7a;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--ink); }
.shell { width: min(1440px, calc(100% - 32px)); margin: 0 auto; padding: 24px 0 40px; }
.topbar, .section-heading, .scenario-head, .alert-summary { display: flex; align-items: flex-start; justify-content: space-between; gap: 20px; }
.topbar { padding: 10px 0 18px; border-bottom: 1px solid var(--line); }
.eyebrow { margin: 0 0 6px; color: var(--teal); font-size: 0.75rem; font-weight: 800; letter-spacing: 0; text-transform: uppercase; }
h1, h2, h3, h4 { margin: 0; letter-spacing: 0; }
h1 { font-size: 2rem; }
h2 { font-size: 1.25rem; }
h3 { font-size: 1.1rem; }
h4 { font-size: 1rem; }
p { color: var(--muted); line-height: 1.45; }
.run-meta { display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 8px; }
.run-meta span, .badge, .status, .delta-chip { border: 1px solid var(--line); border-radius: 8px; background: var(--surface-strong); padding: 7px 9px; font-size: 0.8rem; font-weight: 700; }
.monte-carlo-progress { margin: 18px 0 0; padding: 16px; border: 1px solid var(--line); border-radius: 8px; background: var(--surface); }
.progress-head, .progress-meter-row { display: flex; align-items: center; justify-content: space-between; gap: 16px; }
.progress-meter-row { margin-top: 14px; }
.progress-meter { flex: 1; height: 14px; border-radius: 999px; background: var(--surface-strong); overflow: hidden; border: 1px solid var(--line); }
.progress-meter span { display: block; height: 100%; border-radius: inherit; background: var(--teal); }
.progress-meter-row strong { min-width: 54px; text-align: right; font-size: 1.1rem; }
.progress-facts { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; margin-top: 12px; }
.progress-fact { border: 1px solid var(--line); border-radius: 8px; padding: 10px; background: var(--surface-soft); display: grid; gap: 5px; min-height: 70px; }
.progress-fact span { color: var(--muted); font-size: 0.72rem; font-weight: 800; text-transform: uppercase; }
.progress-fact strong { overflow-wrap: anywhere; font-size: 0.9rem; }
.monte-carlo-progress p { margin: 12px 0 0; }
.summary-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin: 18px 0 24px; }
.summary-tile, .comparison-section, .scenario-section { background: var(--surface); border: 1px solid var(--line); border-radius: 8px; }
.summary-tile { padding: 14px; display: grid; gap: 7px; min-height: 112px; }
.summary-tile span, .summary-tile small { color: var(--muted); }
.summary-tile strong { font-size: 1.45rem; }
.comparison-section, .scenario-section { padding: 18px; margin-top: 16px; }
.table-wrap { margin-top: 14px; overflow-x: auto; }
.comparison-table { width: 100%; border-collapse: collapse; min-width: 1040px; }
.comparison-table th, .comparison-table td { border-bottom: 1px solid var(--line); padding: 11px 10px; text-align: left; vertical-align: middle; }
.comparison-table th { font-size: 0.82rem; }
.comparison-table thead th { color: var(--muted); font-size: 0.72rem; text-transform: uppercase; background: var(--surface-soft); }
.comparison-table tbody tr:hover { background: rgba(80, 214, 207, 0.06); }
.comparison-table small { display: block; color: var(--muted); margin-top: 4px; }
.badge { display: inline-flex; padding: 5px 8px; }
.badge-frontier_os { border-color: rgba(80, 214, 207, 0.45); color: var(--teal); }
.badge-fallback { border-color: rgba(142, 181, 255, 0.45); color: var(--blue); }
.score-cell { min-width: 104px; display: grid; gap: 6px; }
.bar { height: 8px; border-radius: 999px; background: var(--surface-strong); overflow: hidden; }
.bar span { display: block; height: 100%; border-radius: inherit; background: var(--teal); }
.bar-severity span, .bar-risk_officer span { background: var(--amber); }
.bar-confidence span, .bar-integrator span { background: var(--blue); }
.bar-quality span, .bar-explainer span { background: var(--green); }
.bar-skeptic span { background: var(--berry); }
.bar-precision span { background: var(--teal); }
.bar-sensitivity span { background: var(--red); }
.status { display: inline-flex; align-items: center; color: var(--ink); background: var(--surface-strong); }
.status-human-escalation-review { color: #ffd091; background: #3a250f; border-color: #8f6225; }
.status-review-recommended { color: #bfd6ff; background: #172842; border-color: #466998; }
.tabs { display: flex; gap: 8px; margin: 16px 0; overflow-x: auto; padding-bottom: 2px; }
.tab { appearance: none; border: 1px solid var(--line); border-radius: 8px; background: var(--surface); color: var(--ink); cursor: pointer; padding: 9px 12px; font: inherit; font-weight: 800; white-space: nowrap; }
.tab.is-active { border-color: var(--teal); color: var(--teal); background: rgba(80, 214, 207, 0.12); }
.scenario-panel { display: none; border-top: 1px solid var(--line); padding-top: 16px; }
.scenario-panel.is-active { display: block; }
.scenario-head p { margin: 4px 0 0; }
.delta-grid { display: grid; grid-template-columns: repeat(3, minmax(104px, 1fr)); gap: 8px; }
.delta-chip { display: grid; gap: 3px; min-width: 104px; }
.delta-chip small { color: var(--muted); }
.alert-summary { align-items: stretch; margin-top: 14px; padding: 14px; border: 1px solid var(--line); border-radius: 8px; background: var(--surface-soft); }
.alert-summary p { margin-bottom: 0; }
.alert-metrics { display: grid; grid-template-columns: repeat(2, minmax(130px, 1fr)); gap: 10px; min-width: 300px; }
.metric-block { display: grid; gap: 6px; border: 1px solid var(--line); border-radius: 8px; padding: 10px; background: var(--surface); }
.metric-block span { color: var(--muted); font-size: 0.78rem; font-weight: 700; }
.role-grid { display: grid; grid-template-columns: repeat(5, minmax(180px, 1fr)); gap: 12px; margin-top: 12px; }
.role-card { border: 1px solid var(--line); border-radius: 8px; background: var(--surface); padding: 12px; display: grid; gap: 10px; min-height: 250px; }
.role-card header { display: flex; justify-content: space-between; gap: 10px; align-items: baseline; }
.role-card header span { font-weight: 900; }
.role-card p { margin: 0; font-size: 0.86rem; }
.role-card dl { display: grid; gap: 8px; margin: 0; }
.role-card dl div { display: flex; justify-content: space-between; gap: 10px; border-top: 1px solid var(--line); padding-top: 7px; }
.role-card dt { color: var(--muted); font-size: 0.72rem; font-weight: 800; text-transform: uppercase; }
.role-card dd { margin: 0; max-width: 56%; overflow-wrap: anywhere; text-align: right; font-size: 0.78rem; }
.empty-state { border: 1px solid var(--line); border-radius: 8px; padding: 18px; color: var(--muted); }

@media (max-width: 1100px) {
  .summary-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .progress-facts { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .role-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .alert-summary { display: grid; }
  .alert-metrics { min-width: 0; }
}

@media (max-width: 680px) {
  .shell { width: min(100% - 20px, 1440px); padding-top: 14px; }
  .topbar, .section-heading, .scenario-head { display: grid; }
  .progress-head, .progress-meter-row { display: grid; }
  .run-meta { justify-content: flex-start; }
  .summary-grid, .progress-facts, .role-grid, .delta-grid, .alert-metrics { grid-template-columns: 1fr; }
  h1 { font-size: 1.55rem; }
}
""".strip()


def _dashboard_js() -> str:
    return """
const tabs = document.querySelectorAll('.tab');
const panels = document.querySelectorAll('.scenario-panel');

tabs.forEach((tab) => {
  tab.addEventListener('click', () => {
    tabs.forEach((item) => {
      item.classList.remove('is-active');
      item.setAttribute('aria-selected', 'false');
    });
    panels.forEach((panel) => panel.classList.remove('is-active'));
    tab.classList.add('is-active');
    tab.setAttribute('aria-selected', 'true');
    const target = document.getElementById(tab.dataset.target);
    if (target) {
      target.classList.add('is-active');
    }
  });
});
""".strip()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Export the static demo dashboard.")
    parser.add_argument("--artifact-root", type=Path, default=None)
    args = parser.parse_args(argv)
    dashboard_path = export_demo_dashboard(args.artifact_root)
    print(json.dumps({"dashboard": str(dashboard_path)}, indent=2))


if __name__ == "__main__":
    main()
