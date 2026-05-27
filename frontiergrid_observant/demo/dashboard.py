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


def _load_scenario_events(data_root: Path, scenario_id: str) -> list[dict[str, Any]]:
    """Loads and parses the synthetic scenario events from a JSONL file."""
    path = data_root / "synthetic" / f"{scenario_id}.jsonl"
    events = []
    if path.exists():
        try:
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    events.append(json.loads(line))
        except Exception:
            pass
    return events


def _load_replay_timeline(artifact_root: Path, scenario_id: str) -> dict[int, list[str]]:
    """Loads and extracts tick-by-tick timeline state changes from a replay markdown file."""
    path = artifact_root / f"{scenario_id}_replay.md"
    timeline_notes = {}
    if path.exists():
        try:
            content = path.read_text(encoding="utf-8")
            if "## Timeline" in content:
                timeline_part = content.split("## Timeline", 1)[1].strip()
                for line in timeline_part.splitlines():
                    match = re.search(r"-\s*Tick\s*(\d+):(.*)", line)
                    if match:
                        tick = int(match.group(1))
                        note = match.group(2).strip()
                        timeline_notes.setdefault(tick, []).append(note)
        except Exception:
            pass
    return timeline_notes


def export_demo_dashboard(artifact_root: Path | None = None) -> Path:
    settings = load_settings()
    root = artifact_root or settings.artifact_root
    data_root = settings.data_root
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
    evidence_summary_path = root / "scenario_evidence_summary.json"
    evidence_summary = (
        json.loads(evidence_path.read_text(encoding="utf-8"))
        if evidence_summary_path.exists() and (evidence_path := evidence_summary_path)
        else None
    )
    alert_cards = _load_alert_cards(root)

    # Compile scenario events and trace notes to embed dynamically
    scenario_events = {}
    for scenario in comparison.get("scenarios", []):
        scenario_id = scenario["scenario_id"]
        events = _load_scenario_events(data_root, scenario_id)
        notes = _load_replay_timeline(root, scenario_id)
        for event in events:
            tick = event.get("tick")
            if tick in notes:
                event["replay_notes"] = notes[tick]
        scenario_events[scenario_id] = events

    dashboard_path = root / "index.html"
    dashboard_path.write_text(
      render_demo_dashboard(comparison, alert_cards, ablation, stress, progress, evidence_summary, scenario_events),
        encoding="utf-8",
    )
    return dashboard_path


def render_demo_dashboard(
    comparison: dict[str, Any],
    alert_cards: dict[str, dict[str, Any]],
    ablation: dict[str, Any] | None = None,
    stress: dict[str, Any] | None = None,
    progress: dict[str, Any] | None = None,
    evidence_summary: dict[str, Any] | None = None,
    scenario_events: dict[str, list[dict[str, Any]]] | None = None,
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

    # Package all metrics for browser execution
    packaged_data = {
        "comparison": comparison,
        "alert_cards": alert_cards,
        "ablation": ablation,
        "stress": stress,
        "progress": progress,
        "evidence_summary": evidence_summary,
        "scenario_events": scenario_events,
    }

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>FrontierGrid-Observant Interactive Demo</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;600;700;800&display=swap" rel="stylesheet">
  <style>
{_dashboard_css()}
  </style>
</head>
<body>
  <div class="app-layout">
    <!-- Left Sidebar -->
    <aside class="sidebar glass-panel">
      <div class="brand">
        <div class="brand-glow"></div>
        <div class="brand-title">
          <h2>OBSERVANT-AI</h2>
          <span>Phase I Proof-of-Concept</span>
        </div>
      </div>
      <nav class="sidebar-menu">
        <button class="menu-item active" data-section="overview-section" aria-label="Run Overview">
          <svg viewBox="0 0 24 24"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/></svg>
          Run Overview
        </button>
        <button class="menu-item" data-section="comparison-section" aria-label="Substrate Comparison">
          <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17h-2v-2h2v2zm2.07-7.75l-.9.92C13.45 12.9 13 13.5 13 15h-2v-.5c0-1.1.45-2.1 1.17-2.83l1.24-1.26c.37-.36.59-.86.59-1.41 0-1.1-.9-2-2-2s-2 .9-2 2H7c0-2.76 2.24-5 5-5s5 2.24 5 5c0 1.04-.42 1.99-1.07 2.75z"/></svg>
          Substrate Comparison
        </button>
        {"" if ablation is None else f'''
        <button class="menu-item" data-section="ablation-section" aria-label="Ablation Study">
          <svg viewBox="0 0 24 24"><path d="M4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm16-4H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H8V4h12v12z"/></svg>
          Ablation Study
        </button>
        '''}
        {"" if stress is None else f'''
        <button class="menu-item" data-section="stress-section" aria-label="Randomized Stress">
          <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.53c-.26-.81-1-1.4-1.9-1.4h-1v-3c0-.55-.45-1-1-1h-6v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.4z"/></svg>
          Randomized Stress
        </button>
        '''}
        <button class="menu-item" data-section="explorer-section" aria-label="Scenario Explorer">
          <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>
          Scenario Explorer
        </button>
      </nav>
      <div class="sidebar-footer">
        <span>UNCLASSIFIED DEMO</span>
      </div>
    </aside>

    <!-- Main Workspace -->
    <main class="shell">
      <header class="topbar glass-panel">
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

      <!-- SECTION 1: RUN OVERVIEW -->
      <section id="overview-section" class="section-pane active">
        {_monte_carlo_progress(progress)}

        <div class="summary-grid" aria-label="Run summary">
          {_summary_tile("Scenarios", len(scenarios), "Synthetic challenge runs")}
          {_summary_tile("Native available", f"{native_available}/{len(scenarios)}", "Frontier_OS substrate")}
          {_summary_tile("Evidence complete", f"{native_complete}/{len(scenarios)}", "Five role alert cards")}
          {_summary_tile("Avg native delta", _average_delta(severity_deltas, confidence_deltas), "Severity / confidence")}
        </div>

        {"" if evidence_summary is None else f'''
        <div class="glass-panel text-block findings-card">
          <div class="section-heading">
            <p class="eyebrow">Proof-Thread Benchmarks</p>
            <h2>Key Evaluation Findings</h2>
          </div>
          <ul class="findings-list">
            {"".join(f"<li>{_html(finding)}</li>" for finding in evidence_summary.get("key_findings", []))}
          </ul>
        </div>
        '''}
      </section>

      <!-- SECTION 2: SUBSTRATE COMPARISON -->
      <section id="comparison-section" class="section-pane">
        <div class="glass-panel">
          <div class="section-heading">
            <p class="eyebrow">Baseline Comparison</p>
            <h2>Fallback vs Frontier_OS</h2>
          </div>
          <div class="table-wrap">
            {_comparison_table(comparison)}
          </div>
        </div>

        <div class="section-heading" style="margin-top:24px;">
          <p class="eyebrow">Visual Analytics</p>
          <h2>Substrate Performance Comparison</h2>
        </div>
        <div id="comparison-charts" class="charts-grid"></div>
      </section>

      <!-- SECTION 3: ABLATION STUDY -->
      {_ablation_section(ablation)}

      <!-- SECTION 4: STRESS STUDY -->
      {_stress_section(stress)}

      <!-- SECTION 5: SCENARIO EXPLORER -->
      <section id="explorer-section" class="section-pane">
        <div class="glass-panel" style="padding:16px;">
          <div class="section-heading">
            <p class="eyebrow">Alert Evidence</p>
            <h2>Native Role Review</h2>
          </div>
          
          {_scenario_tabs(scenarios)}

          <!-- INTERACTIVE PLAYBACK TIMELINE CONTROL -->
          <div class="timeline-container glass-panel">
            <div class="timeline-controls">
              <span class="timeline-title">Scenario Event Timeline</span>
              <div class="controls-group">
                <button id="btn-prev" class="ctrl-btn" title="Previous Tick">&lt;</button>
                <button id="btn-play" class="ctrl-btn play-btn" title="Play Replay">Play</button>
                <button id="btn-next" class="ctrl-btn" title="Next Tick">&gt;</button>
                <span id="speed-indicator" class="badge">1.5s</span>
              </div>
            </div>
            
            <div class="scrubber-track-container">
              <div class="scrubber-labels">
                <span>Start (Tick 0)</span>
                <span id="current-tick-lbl">Tick 0</span>
                <span>End (Tick 29)</span>
              </div>
              <div class="scrubber-rail">
                <div id="scrubber-progress" class="scrubber-progress-fill"></div>
                <div id="timeline-ticks" class="timeline-ticks-row">
                  <!-- JS builds tick markers here -->
                </div>
              </div>
            </div>
          </div>

          <!-- DUAL WORKSPACE: LEFT EVENT INSPECTOR, RIGHT SCENARIO ALERT DETAILS -->
          <div class="workspace-grid">
            <!-- Left Panel: Event Inspector -->
            <article class="glass-panel event-inspector">
              <header class="panel-header">
                <h3>Event Detail Inspector</h3>
                <span id="event-tick-badge" class="badge">Tick --</span>
              </header>
              <div id="event-inspect-content" class="inspector-body">
                <div class="empty-state">Select a tick on the timeline to inspect the raw incoming sensor log.</div>
              </div>
            </article>

            <!-- Right Panel: Dynamic Scenario Alerts -->
            <div class="scenario-panels">
              {_scenario_panels(scenarios, alert_cards)}
            </div>
          </div>

        </div>
      </section>
    </main>
  </div>

  <script>
    window.dashboardData = {json.dumps(packaged_data, default=str)};
    {_dashboard_js()}
  </script>
</body>
</html>
"""


def _load_alert_cards(artifact_root: Path) -> dict[str, dict[str, Any]]:
    alert_cards: dict[str, dict[str, Any]] = {}
    for path in sorted(artifact_root.glob("*_alerts.json")):
        try:
            alerts = json.loads(path.read_text(encoding="utf-8"))
            if not alerts:
                continue
            first_alert = alerts[0]
            alert_cards[str(first_alert["scenario_id"])] = first_alert
        except Exception:
            pass
    return alert_cards


def _summary_tile(label: str, value: Any, caption: str) -> str:
    return f"""
      <article class="summary-tile glass-panel">
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
    <section class="monte-carlo-progress glass-panel" aria-label="Monte Carlo sweep progress">
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
    <section id="ablation-section" class="section-pane">
      <div class="glass-panel">
        <div class="section-heading">
          <p class="eyebrow">Ablation Evidence</p>
          <h2>Rule, Sequential, Shared Context</h2>
        </div>
        <div class="table-wrap">
          {_ablation_table(ablation)}
        </div>
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
    <section id="stress-section" class="section-pane">
      <div class="glass-panel">
        <div class="section-heading">
          <p class="eyebrow">Randomized Stress</p>
          <h2>Multi-Seed Mode Averages</h2>
        </div>
        <div class="table-wrap">
          {_stress_table(stress)}
        </div>
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
    
    role_theme_class = f"role-card-{role}"
    return f"""
      <article class="role-card glass-panel {role_theme_class}" data-role="{role}">
        <header>
          <span>{_html(ROLE_LABELS[role])}</span>
          <strong>{_html(_display(score))}</strong>
        </header>
        {_bar(score, role)}
        <p class="role-summary-txt">{_html(evidence.get("summary", "No role evidence exported."))}</p>
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
      <div class="metric-block glass-panel">
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
        .removeprefix("scenario_04_")
        .removeprefix("scenario_05_")
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
  --bg: #06090e;
  --surface: rgba(18, 26, 38, 0.45);
  --surface-strong: rgba(26, 38, 57, 0.65);
  --surface-soft: rgba(10, 15, 26, 0.5);
  --ink: #f3f4f6;
  --muted: #9ca3af;
  --line: rgba(255, 255, 255, 0.08);
  --teal: #00f2fe;
  --teal-glow: rgba(0, 242, 254, 0.3);
  --amber: #f59e0b;
  --amber-glow: rgba(245, 158, 11, 0.3);
  --berry: #ec4899;
  --berry-glow: rgba(236, 72, 153, 0.3);
  --blue: #3b82f6;
  --blue-glow: rgba(59, 130, 246, 0.3);
  --green: #10b981;
  --green-glow: rgba(16, 185, 129, 0.3);
  --red: #ef4444;
  --red-glow: rgba(239, 68, 68, 0.3);
  --purple: #8b5cf6;
  --purple-glow: rgba(139, 92, 246, 0.3);
}

* { box-sizing: border-box; }
body {
  margin: 0;
  background-color: var(--bg);
  background-image: 
    radial-gradient(circle at 10% 20%, rgba(13, 21, 37, 0.85) 0%, rgba(6, 9, 14, 1) 90%),
    radial-gradient(circle at 80% 85%, rgba(16, 31, 58, 0.35) 0%, rgba(6, 9, 14, 1) 80%);
  background-attachment: fixed;
  color: var(--ink);
  font-family: 'Inter', system-ui, sans-serif;
  line-height: 1.5;
}

.app-layout {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 280px;
  flex-shrink: 0;
  border-right: 1px solid var(--line);
  background: rgba(8, 12, 18, 0.7);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  padding: 24px 18px;
  display: flex;
  flex-direction: column;
  gap: 28px;
  height: 100vh;
  position: sticky;
  top: 0;
  z-index: 100;
}

.sidebar .brand {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px;
}

.brand-glow {
  position: absolute;
  top: -10px;
  left: -10px;
  width: 50px;
  height: 50px;
  background: radial-gradient(circle, var(--teal) 0%, transparent 70%);
  opacity: 0.15;
  filter: blur(5px);
}

.brand-title h2 {
  font-family: 'Outfit', sans-serif;
  font-size: 1.25rem;
  font-weight: 800;
  margin: 0;
  background: linear-gradient(135deg, var(--teal) 0%, var(--blue) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: 1px;
}

.brand-title span {
  font-size: 0.68rem;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 1.5px;
  font-weight: 700;
}

.sidebar-menu {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}

.menu-item {
  appearance: none;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 10px;
  color: var(--muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 11px 14px;
  font-family: inherit;
  font-size: 0.9rem;
  font-weight: 600;
  text-align: left;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.menu-item svg {
  width: 18px;
  height: 18px;
  fill: currentColor;
}

.menu-item:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--ink);
}

.menu-item.active {
  background: var(--surface-strong);
  border-color: var(--line);
  color: var(--teal);
  box-shadow: 0 4px 15px rgba(0, 242, 254, 0.08);
}

.sidebar-footer {
  font-size: 0.65rem;
  color: var(--muted);
  text-align: center;
  font-weight: 800;
  letter-spacing: 1.5px;
  padding-top: 10px;
  border-top: 1px solid var(--line);
}

.shell {
  flex: 1;
  max-width: 1440px;
  margin: 0 auto;
  padding: 32px;
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.glass-panel {
  background: var(--surface);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid var(--line);
  border-radius: 14px;
  box-shadow: 0 10px 40px 0 rgba(0, 0, 0, 0.4);
  padding: 24px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.glass-panel:hover {
  border-color: rgba(255, 255, 255, 0.12);
}

.section-pane {
  display: none;
  animation: fadeIn 0.4s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

.section-pane.active {
  display: flex;
  flex-direction: column;
  gap: 28px;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 28px;
}

.eyebrow {
  margin: 0 0 6px;
  color: var(--teal);
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 2px;
  text-transform: uppercase;
}

h1, h2, h3, h4 {
  font-family: 'Outfit', sans-serif;
  margin: 0;
  letter-spacing: -0.01em;
}

h1 { font-size: 2.2rem; font-weight: 800; }
h2 { font-size: 1.5rem; font-weight: 700; }
h3 { font-size: 1.15rem; font-weight: 600; }
h4 { font-size: 1rem; font-weight: 600; }

.run-meta {
  display: flex;
  gap: 12px;
}

.run-meta span, .badge, .status, .delta-chip {
  background: var(--surface-soft);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 6px 12px;
  font-size: 0.8rem;
  font-weight: 700;
}

.badge {
  display: inline-block;
}

.monte-carlo-progress {
  padding: 24px;
}

.progress-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.progress-meter-row {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 18px;
}

.progress-meter {
  flex: 1;
  height: 12px;
  border-radius: 99px;
  background: rgba(255, 255, 255, 0.05);
  overflow: hidden;
  border: 1px solid var(--line);
}

.progress-meter span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--teal) 0%, var(--blue) 100%);
  box-shadow: 0 0 10px var(--teal-glow);
}

.progress-facts {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  margin-top: 20px;
}

.progress-fact {
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.progress-fact span {
  color: var(--muted);
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.progress-fact strong {
  font-size: 0.95rem;
  font-weight: 700;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 20px;
}

.summary-tile {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 116px;
  justify-content: center;
}

.summary-tile span {
  color: var(--muted);
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.summary-tile strong {
  font-size: 1.65rem;
  font-weight: 800;
}

.summary-tile small {
  color: var(--muted);
  font-size: 0.75rem;
}

.findings-card {
  border-left: 4px solid var(--teal);
}

.findings-list {
  margin: 16px 0 0 0;
  padding-left: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.findings-list li {
  color: var(--muted);
  font-size: 0.92rem;
}

.table-wrap {
  margin-top: 18px;
  overflow-x: auto;
}

.comparison-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 1040px;
}

.comparison-table th, .comparison-table td {
  border-bottom: 1px solid var(--line);
  padding: 14px 12px;
  text-align: left;
  vertical-align: middle;
}

.comparison-table th {
  font-size: 0.85rem;
  font-weight: 600;
}

.comparison-table thead th {
  color: var(--muted);
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  background: var(--surface-soft);
}

.comparison-table tbody tr:hover {
  background: rgba(255, 255, 255, 0.02);
}

.comparison-table small {
  display: block;
  color: var(--muted);
  margin-top: 4px;
}

.badge-frontier_os {
  border-color: rgba(80, 214, 207, 0.35);
  color: var(--teal);
  box-shadow: 0 2px 8px rgba(80, 214, 207, 0.05);
}

.badge-fallback {
  border-color: rgba(142, 181, 255, 0.35);
  color: var(--blue);
}

.score-cell {
  min-width: 110px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.bar {
  height: 6px;
  border-radius: 99px;
  background: rgba(255, 255, 255, 0.05);
  overflow: hidden;
  border: 1px solid var(--line);
}

.bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--teal);
}

.bar-severity span { background: var(--amber); }
.bar-confidence span { background: var(--blue); }
.bar-quality span { background: var(--green); }
.bar-precision span { background: var(--teal); }
.bar-sensitivity span { background: var(--red); }

.bar-watcher span { background: var(--teal); }
.bar-integrator span { background: var(--blue); }
.bar-risk_officer span { background: var(--red); }
.bar-skeptic span { background: var(--purple); }
.bar-explainer span { background: var(--berry); }

.status {
  display: inline-flex;
  align-items: center;
  font-weight: 700;
}

.status-human-escalation-review {
  color: #ffd091;
  background: rgba(58, 37, 15, 0.4);
  border-color: #8f6225;
}

.status-review-recommended {
  color: #bfd6ff;
  background: rgba(23, 40, 66, 0.4);
  border-color: #466998;
}

.status-complete {
  color: var(--green);
  background: rgba(16, 185, 129, 0.1);
  border-color: var(--green-glow);
}

.status-partial {
  color: var(--amber);
  background: rgba(245, 158, 11, 0.1);
  border-color: var(--amber-glow);
}

.tabs {
  display: flex;
  gap: 10px;
  margin: 18px 0;
  overflow-x: auto;
  padding-bottom: 4px;
}

.tab {
  appearance: none;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: var(--surface-soft);
  color: var(--muted);
  cursor: pointer;
  padding: 10px 16px;
  font-family: inherit;
  font-weight: 700;
  white-space: nowrap;
  transition: all 0.25s ease;
}

.tab:hover {
  color: var(--ink);
  background: rgba(255, 255, 255, 0.05);
}

.tab.is-active {
  border-color: var(--teal);
  color: var(--teal);
  background: rgba(0, 242, 254, 0.08);
  box-shadow: 0 4px 15px rgba(0, 242, 254, 0.08);
}

.scenario-panel {
  display: none;
  flex-direction: column;
  gap: 20px;
}

.scenario-panel.is-active {
  display: flex;
}

.scenario-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--line);
  padding-bottom: 18px;
}

.scenario-head h3 {
  font-size: 1.35rem;
  font-weight: 700;
}

.scenario-head p {
  margin: 4px 0 0;
  font-size: 0.85rem;
  color: var(--muted);
}

.delta-grid {
  display: flex;
  gap: 12px;
}

.delta-chip {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 100px;
  align-items: center;
  justify-content: center;
}

.delta-chip small {
  color: var(--muted);
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.alert-summary {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  padding: 20px;
  border: 1px solid var(--line);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.01);
}

.alert-summary h4 {
  font-size: 1.15rem;
  font-weight: 700;
  margin-bottom: 8px;
}

.alert-summary p {
  margin: 0;
  color: var(--muted);
  font-size: 0.9rem;
  line-height: 1.5;
}

.alert-metrics {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  min-width: 320px;
  flex-shrink: 0;
}

.metric-block {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.metric-block span {
  color: var(--muted);
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.metric-block strong {
  font-size: 1.1rem;
  font-weight: 700;
}

.role-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 16px;
}

.role-card {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 270px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.role-card header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.role-card header span {
  font-weight: 800;
  font-size: 0.95rem;
  font-family: 'Outfit', sans-serif;
}

.role-card header strong {
  font-size: 1.1rem;
}

.role-card p.role-summary-txt {
  margin: 0;
  font-size: 0.8rem;
  color: var(--muted);
  flex: 1;
}

.role-card dl {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 0;
  border-top: 1px solid var(--line);
  padding-top: 12px;
}

.role-card dl div {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.role-card dt {
  color: var(--muted);
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
}

.role-card dd {
  margin: 0;
  font-size: 0.75rem;
  font-weight: 700;
}

/* Custom indicator lines on role cards */
.role-card-watcher { border-top: 3px solid var(--teal); }
.role-card-integrator { border-top: 3px solid var(--blue); }
.role-card-risk_officer { border-top: 3px solid var(--red); }
.role-card-skeptic { border-top: 3px solid var(--purple); }
.role-card-explainer { border-top: 3px solid var(--berry); }

/* Glowing highlight state for contributing roles */
.role-card.active-contribution {
  box-shadow: 0 0 20px rgba(255, 255, 255, 0.1);
  transform: translateY(-4px);
  border-color: rgba(255, 255, 255, 0.25);
}
.role-card.active-contribution.role-card-watcher { box-shadow: 0 0 20px rgba(0, 242, 254, 0.2); }
.role-card.active-contribution.role-card-integrator { box-shadow: 0 0 20px rgba(59, 130, 246, 0.2); }
.role-card.active-contribution.role-card-risk_officer { box-shadow: 0 0 20px rgba(239, 68, 68, 0.2); }
.role-card.active-contribution.role-card-skeptic { box-shadow: 0 0 20px rgba(139, 92, 246, 0.2); }
.role-card.active-contribution.role-card-explainer { box-shadow: 0 0 20px rgba(236, 72, 153, 0.2); }

.empty-state {
  border: 1px dashed var(--line);
  border-radius: 12px;
  padding: 32px;
  color: var(--muted);
  text-align: center;
  font-size: 0.9rem;
}

/* INTERACTIVE SCRUBBER TIMELINE STYLING */
.timeline-container {
  padding: 20px;
  margin: 12px 0 24px 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.timeline-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.timeline-title {
  font-family: 'Outfit', sans-serif;
  font-size: 1.05rem;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.controls-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.ctrl-btn {
  background: var(--surface-soft);
  border: 1px solid var(--line);
  border-radius: 6px;
  color: var(--ink);
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 700;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.ctrl-btn:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.2);
}

.ctrl-btn.play-btn {
  width: 70px;
  background: rgba(0, 242, 254, 0.08);
  border-color: rgba(0, 242, 254, 0.3);
  color: var(--teal);
}

.ctrl-btn.play-btn:hover {
  background: rgba(0, 242, 254, 0.15);
  border-color: var(--teal);
}

.scrubber-track-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.scrubber-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.72rem;
  color: var(--muted);
  font-weight: 600;
}

#current-tick-lbl {
  color: var(--teal);
  font-weight: 700;
  font-size: 0.8rem;
}

.scrubber-rail {
  position: relative;
  height: 8px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  border: 1px solid var(--line);
  display: flex;
  align-items: center;
}

.scrubber-progress-fill {
  position: absolute;
  left: 0;
  height: 100%;
  background: linear-gradient(90deg, rgba(0, 242, 254, 0.1) 0%, rgba(0, 242, 254, 0.4) 100%);
  border-radius: 4px;
  width: 0%;
}

.timeline-ticks-row {
  position: absolute;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-between;
  padding: 0 4px;
}

.tick-node {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #374151;
  border: 2px solid var(--bg);
  cursor: pointer;
  z-index: 5;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

.tick-node:hover {
  transform: scale(1.3);
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
}

.tick-node.active {
  transform: scale(1.4);
  background: #fff !important;
  border-color: var(--teal) !important;
  box-shadow: 0 0 12px var(--teal);
}

/* Domain coloring for tick nodes */
.node-maritime { background: var(--blue); }
.node-space { background: var(--purple); }
.node-air { background: var(--teal); }
.node-land { background: var(--green); }
.node-cyber { background: var(--red); }

/* Anomaly tick indicator (pulses) */
.tick-node.is-anomaly::after {
  content: '';
  position: absolute;
  top: -6px;
  left: -6px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 2px solid var(--red);
  opacity: 0;
  animation: pulseNode 2s infinite;
  pointer-events: none;
}

@keyframes pulseNode {
  0% { transform: scale(0.6); opacity: 0.8; }
  100% { transform: scale(1.4); opacity: 0; }
}

/* DYNAMIC TIMELINE WORKSPACE */
.workspace-grid {
  display: grid;
  grid-template-columns: 340px 1fr;
  gap: 20px;
  margin-top: 10px;
}

.event-inspector {
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: rgba(10, 15, 26, 0.65);
  border-color: rgba(255, 255, 255, 0.06);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--line);
  padding-bottom: 12px;
}

.panel-header h3 {
  font-size: 1.05rem;
}

.inspector-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
  font-size: 0.85rem;
  overflow-y: auto;
  max-height: 480px;
  padding-right: 4px;
}

.inspector-body::-webkit-scrollbar { width: 4px; }
.inspector-body::-webkit-scrollbar-thumb { background: var(--line); border-radius: 4px; }

.inspect-section {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.inspect-section h5 {
  margin: 0;
  font-size: 0.72rem;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.inspect-section p {
  margin: 0;
  color: var(--ink);
  line-height: 1.4;
}

.inspect-badge-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.inspector-attr-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  background: rgba(255, 255, 255, 0.01);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 10px;
}

.inspector-attr-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.inspector-attr-item span {
  font-size: 0.62rem;
  color: var(--muted);
  text-transform: uppercase;
}

.inspector-attr-item strong {
  font-size: 0.8rem;
  color: var(--ink);
}

.inspect-telemetry-box {
  background: rgba(0, 242, 254, 0.03);
  border: 1px solid rgba(0, 242, 254, 0.15);
  border-radius: 8px;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.inspect-telemetry-item {
  display: flex;
  gap: 8px;
  align-items: flex-start;
  color: var(--teal);
  line-height: 1.35;
  font-size: 0.78rem;
}

.inspect-telemetry-item::before {
  content: '⚡';
  font-size: 0.75rem;
}

.inspect-anomaly-card {
  border-radius: 8px;
  padding: 12px;
  border: 1px solid transparent;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.inspect-anomaly-card.nominal {
  background: rgba(16, 185, 129, 0.05);
  border-color: rgba(16, 185, 129, 0.2);
  color: var(--green);
}

.inspect-anomaly-card.anomaly {
  background: rgba(239, 68, 68, 0.05);
  border-color: rgba(239, 68, 68, 0.2);
  color: var(--red);
}

.inspect-anomaly-card header {
  font-weight: 800;
  font-size: 0.8rem;
  text-transform: uppercase;
}

/* DYNAMIC COMPARATIVE CHARTS */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-top: 14px;
}

.chart-card {
  padding: 18px;
}

.chart-wrapper {
  margin-top: 16px;
  height: 240px;
}

.chart-bar-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 12px;
}

.chart-bar-label {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: var(--muted);
  font-weight: 600;
}

.chart-bar-track {
  height: 20px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--line);
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

.chart-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.8s ease-in-out;
}

.chart-bar-fill.bar-fallback {
  background: linear-gradient(90deg, rgba(59, 130, 246, 0.3) 0%, var(--blue) 100%);
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.2);
}

.chart-bar-fill.bar-native {
  background: linear-gradient(90deg, rgba(0, 242, 254, 0.3) 0%, var(--teal) 100%);
  box-shadow: 0 0 10px rgba(0, 242, 254, 0.2);
}

@media (max-width: 1100px) {
  .sidebar { width: 72px; padding: 24px 10px; }
  .brand-title, .sidebar-footer { display: none; }
  .menu-item span { display: none; }
  .menu-item { justify-content: center; padding: 12px; }
  .summary-grid, .progress-facts { grid-template-columns: repeat(2, 1fr); }
  .role-grid { grid-template-columns: repeat(2, 1fr); }
  .workspace-grid { grid-template-columns: 1fr; }
  .charts-grid { grid-template-columns: 1fr; }
}

@media (max-width: 680px) {
  .app-layout { flex-direction: column; }
  .sidebar { width: 100%; height: auto; position: relative; border-right: none; border-bottom: 1px solid var(--line); padding: 16px; }
  .sidebar-menu { flex-direction: row; justify-content: space-around; }
  .shell { padding: 16px; }
  .summary-grid, .progress-facts, .role-grid, .delta-grid, .alert-metrics { grid-template-columns: 1fr; }
  h1 { font-size: 1.7rem; }
  .topbar { flex-direction: column; align-items: flex-start; gap: 12px; }
}
""".strip()


def _dashboard_js() -> str:
    return """
// Tab elements selection
const sectionButtons = document.querySelectorAll('.menu-item');
const sectionPanes = document.querySelectorAll('.section-pane');

// Timeline playback state variables
let activeScenarioId = 'scenario_01_maritime_shadowing';
let currentTickIndex = 0;
let playbackInterval = null;
const playbackSpeed = 1500; // 1.5s per tick

// Domain labels mapping
const DOMAIN_LABELS = {
  "maritime": "Maritime Domain",
  "sea": "Sea Domain",
  "space": "Space Domain",
  "air": "Air Domain",
  "land": "Land Domain",
  "cyber": "Cyber Domain",
  "cyber_network": "Cyber Domain"
};

// Initialize everything on load
document.addEventListener('DOMContentLoaded', () => {
  setupSectionRouting();
  setupScenarioTabs();
  
  // Default scenario selection
  const comparison = window.dashboardData.comparison;
  if (comparison && comparison.scenarios && comparison.scenarios.length > 0) {
    activeScenarioId = comparison.scenarios[0].scenario_id;
  }
  
  initializeScenario(activeScenarioId);
  setupPlaybackControls();
  renderComparisonCharts();
});

// Section Navigation Toggle (Run Overview, Substrate Comparison, Ablation, Stress, Explorer)
function setupSectionRouting() {
  sectionButtons.forEach((btn) => {
    btn.addEventListener('click', () => {
      sectionButtons.forEach((item) => item.classList.remove('active'));
      sectionPanes.forEach((pane) => pane.classList.remove('active'));
      
      btn.classList.add('active');
      const targetSection = btn.dataset.section;
      const targetPane = document.getElementById(targetSection);
      if (targetPane) {
        targetPane.classList.add('active');
      }
      
      // Pause playback if navigating away from Explorer
      if (targetSection !== 'explorer-section') {
        pausePlayback();
      }
    });
  });
}

// Scenario Tab triggers (Maritime Shadowing, Littoral Hazard, etc.)
function setupScenarioTabs() {
  const scenarioTabs = document.querySelectorAll('.tab');
  const scenarioPanels = document.querySelectorAll('.scenario-panel');
  
  scenarioTabs.forEach((tab) => {
    tab.addEventListener('click', () => {
      scenarioTabs.forEach((item) => {
        item.classList.remove('is-active');
        item.setAttribute('aria-selected', 'false');
      });
      scenarioPanels.forEach((panel) => panel.classList.remove('is-active'));
      
      tab.classList.add('is-active');
      tab.setAttribute('aria-selected', 'true');
      
      // Get target scenario panel
      const targetId = tab.dataset.target;
      const targetPanel = document.getElementById(targetId);
      if (targetPanel) {
        targetPanel.classList.add('is-active');
      }
      
      // Look up scenario ID from panel slug
      // e.g. panel-scenario-01-maritime-shadowing -> scenario_01_maritime_shadowing
      const scenarioId = lookupScenarioIdFromSlug(targetId);
      if (scenarioId) {
        activeScenarioId = scenarioId;
        initializeScenario(activeScenarioId);
      }
    });
  });
}

function lookupScenarioIdFromSlug(slug) {
  const clean = slug.replace('panel-', '');
  // Map clean slug back to keys in scenarioEvents
  for (const key in window.dashboardData.scenario_events) {
    if (key.toLowerCase().replace(/_/g, '-') === clean) {
      return key;
    }
  }
  return null;
}

// Initialize specific scenario timeline and default details
function initializeScenario(scenarioId) {
  pausePlayback();
  currentTickIndex = 0;
  
  const events = window.dashboardData.scenario_events[scenarioId] || [];
  renderTimelineTicks(events);
  updateActiveTick(currentTickIndex, scenarioId);
}

// Render the 30 interactive dots on timeline rail
function renderTimelineTicks(events) {
  const ticksContainer = document.getElementById('timeline-ticks');
  if (!ticksContainer) return;
  
  ticksContainer.innerHTML = '';
  events.forEach((evt, idx) => {
    const node = document.createElement('button');
    node.type = 'button';
    node.className = `tick-node node-${evt.domain.toLowerCase()}`;
    node.title = `Tick ${evt.tick}: ${evt.text.substring(0, 40)}...`;
    
    // Add pulse animation trigger if event is anomaly
    if (evt.ground_truth && evt.ground_truth.is_anomaly) {
      node.classList.add('is-anomaly');
    }
    
    node.addEventListener('click', () => {
      pausePlayback();
      currentTickIndex = idx;
      updateActiveTick(currentTickIndex, activeScenarioId);
    });
    
    ticksContainer.appendChild(node);
  });
}

// Setup play / pause / step controls
function setupPlaybackControls() {
  const btnPrev = document.getElementById('btn-prev');
  const btnPlay = document.getElementById('btn-play');
  const btnNext = document.getElementById('btn-next');
  
  if (!btnPrev || !btnPlay || !btnNext) return;
  
  btnPrev.addEventListener('click', () => {
    pausePlayback();
    stepTick(-1);
  });
  
  btnNext.addEventListener('click', () => {
    pausePlayback();
    stepTick(1);
  });
  
  btnPlay.addEventListener('click', () => {
    if (playbackInterval) {
      pausePlayback();
    } else {
      startPlayback();
    }
  });
}

function stepTick(delta) {
  const events = window.dashboardData.scenario_events[activeScenarioId] || [];
  if (events.length === 0) return;
  
  currentTickIndex = (currentTickIndex + delta + events.length) % events.length;
  updateActiveTick(currentTickIndex, activeScenarioId);
}

function startPlayback() {
  const btnPlay = document.getElementById('btn-play');
  if (!btnPlay) return;
  
  btnPlay.textContent = 'Pause';
  btnPlay.classList.add('glow-cyan');
  
  playbackInterval = setInterval(() => {
    stepTick(1);
  }, playbackSpeed);
}

function pausePlayback() {
  const btnPlay = document.getElementById('btn-play');
  if (!btnPlay || !playbackInterval) return;
  
  clearInterval(playbackInterval);
  playbackInterval = null;
  btnPlay.textContent = 'Play';
  btnPlay.classList.remove('glow-cyan');
}

// Update the event inspector and highlight active agent roles on tick change
function updateActiveTick(tickIndex, scenarioId) {
  // Update timeline dot selection
  const nodes = document.querySelectorAll('#timeline-ticks .tick-node');
  nodes.forEach((node, idx) => {
    if (idx === tickIndex) {
      node.classList.add('active');
    } else {
      node.classList.remove('active');
    }
  });
  
  // Update scrubber progress bar fill
  const scrubberProgress = document.getElementById('scrubber-progress');
  if (scrubberProgress && nodes.length > 0) {
    const pct = (tickIndex / (nodes.length - 1)) * 100;
    scrubberProgress.style.width = `${pct}%`;
  }
  
  // Update labels
  const lblTick = document.getElementById('current-tick-lbl');
  if (lblTick) lblTick.textContent = `Tick ${tickIndex}`;
  
  const tickBadge = document.getElementById('event-tick-badge');
  if (tickBadge) tickBadge.textContent = `Tick ${tickIndex}`;
  
  // Load Event Details
  const events = window.dashboardData.scenario_events[scenarioId] || [];
  const event = events[tickIndex];
  const inspectBody = document.getElementById('event-inspect-content');
  
  if (!event || !inspectBody) return;
  
  // Format attributes
  let attrsHTML = '';
  if (event.attributes) {
    for (const [key, value] of Object.entries(event.attributes)) {
      const displayKey = key.replace(/_/g, ' ').toUpperCase();
      let displayValue = typeof value === 'number' ? value.toFixed(2) : String(value);
      attrsHTML += `
        <div class="inspector-attr-item">
          <span>${escapeHTML(displayKey)}</span>
          <strong>${escapeHTML(displayValue)}</strong>
        </div>`;
    }
  }
  
  // Ground truth risk indicators
  const isAnomaly = event.ground_truth && event.ground_truth.is_anomaly;
  const severity = event.ground_truth ? event.ground_truth.severity : 0.0;
  const riskTypeLabel = event.ground_truth ? event.ground_truth.risk_type.replace(/_/g, ' ') : 'nominal';
  
  const groundTruthHTML = isAnomaly 
    ? `<div class="inspect-anomaly-card anomaly">
         <header>ALERT FLAG DETECTED</header>
         <p>Risk: <strong>${escapeHTML(riskTypeLabel)}</strong></p>
         <p>Severity Score: <strong>${severity.toFixed(3)}</strong></p>
       </div>`
    : `<div class="inspect-anomaly-card nominal">
         <header>NOMINAL OPERATION</header>
         <p>No anomalous patterns reported.</p>
       </div>`;
       
  // Replay trace state updates
  let telemetryHTML = '';
  if (event.replay_notes && event.replay_notes.length > 0) {
    telemetryHTML = `
      <div class="inspect-section">
        <h5>SOL Attraction Trace</h5>
        <div class="inspect-telemetry-box">
          ${event.replay_notes.map(note => `
            <div class="inspect-telemetry-item">${escapeHTML(note)}</div>
          `).join('')}
        </div>
      </div>`;
  }
  
  // Populate the inspector pane
  const rel = event.source_reliability ? event.source_reliability.toFixed(2) : 'n/a';
  const loc = event.location ? `${event.location.lat.toFixed(3)}, ${event.location.lon.toFixed(3)} (conf: ${event.location.confidence.toFixed(2)})` : 'n/a';
  
  inspectBody.innerHTML = `
    <div class="inspect-section">
      <h5>Text Narrative</h5>
      <p style="font-weight: 500; font-size:0.95rem; color:#fff;">"${escapeHTML(event.text)}"</p>
    </div>
    
    <div class="inspect-section">
      <h5>Source Context</h5>
      <p>Source ID: <strong>${escapeHTML(event.source_id)}</strong> (reliability: ${rel})</p>
      <p>Modality: <span class="badge" style="padding: 2px 6px; font-size:0.75rem;">${escapeHTML(event.modality)}</span></p>
      <p>Location coordinates: <strong>${escapeHTML(loc)}</strong></p>
    </div>
    
    <div class="inspect-section">
      <h5>Event Attributes</h5>
      <div class="inspector-attr-grid">
        ${attrsHTML || '<div style="color:var(--muted)">None</div>'}
      </div>
    </div>

    <div class="inspect-section">
      <h5>Domain Classification</h5>
      <div class="inspect-badge-row">
        <span class="badge badge-frontier_os">${escapeHTML(DOMAIN_LABELS[event.domain.toLowerCase()] || event.domain)}</span>
      </div>
    </div>
    
    <div class="inspect-section">
      <h5>Ground Truth Flag</h5>
      ${groundTruthHTML}
    </div>
    
    ${telemetryHTML}
  `;
  
  // Highlight active role card based on contribution traces
  highlightRoleContribution(event);
}

// Highlight the specific agent card that was active at this tick
function highlightRoleContribution(event) {
  // Clear existing highlights
  const roleCards = document.querySelectorAll('.role-card');
  roleCards.forEach(card => card.classList.remove('active-contribution'));
  
  if (event.replay_notes && event.replay_notes.length > 0) {
    event.replay_notes.forEach(note => {
      // e.g. "watcher, confidence delta +0.05"
      const lowerNote = note.toLowerCase();
      for (const role in ROLE_LABELS) {
        if (lowerNote.includes(role)) {
          // Select role cards for this specific scenario
          const targetCard = document.querySelector(`.scenario-panel.is-active .role-card[data-role="${role}"]`);
          if (targetCard) {
            targetCard.classList.add('active-contribution');
          }
        }
      }
    });
  }
}

// Render dynamic side-by-side SVG comparison charts
function renderComparisonCharts() {
  const chartsContainer = document.getElementById('comparison-charts');
  if (!chartsContainer) return;
  
  const scenarios = window.dashboardData.comparison.scenarios || [];
  chartsContainer.innerHTML = '';
  
  scenarios.forEach(scen => {
    const card = document.createElement('article');
    card.className = 'glass-panel chart-card';
    
    const title = document.createElement('h3');
    title.textContent = scen.scenario_id.replace('scenario_01_', '').replace('scenario_02_', '').replace('scenario_03_', '').replace('scenario_04_', '').replace('scenario_05_', '').replace(/_/g, ' ').toUpperCase();
    title.style.marginBottom = '14px';
    title.style.borderBottom = '1px solid var(--line)';
    title.style.paddingBottom = '8px';
    card.appendChild(title);
    
    const fallback = scen.substrates.fallback || {};
    const frontier = scen.substrates.frontier_os || {};
    
    const fallbackAlert = fallback.first_alert || {};
    const frontierAlert = frontier.first_alert || {};
    
    const fallbackAlign = fallbackAlert.context_geodesic_alignment !== undefined ? fallbackAlert.context_geodesic_alignment : 0.0;
    const frontierAlign = frontierAlert.context_geodesic_alignment !== undefined ? frontierAlert.context_geodesic_alignment : 0.0;
    
    const fallbackPrec = fallback.metrics ? fallback.metrics.precision || 0.0 : 0.0;
    const frontierPrec = frontier.metrics ? frontier.metrics.precision || 0.0 : 0.0;
    
    const fallbackSens = fallback.metrics ? fallback.metrics.sensitivity || 0.0 : 0.0;
    const frontierSens = frontier.metrics ? frontier.metrics.sensitivity || 0.0 : 0.0;
    
    card.innerHTML += `
      <h3>${escapeHTML(title.textContent)}</h3>
      <div style="display:flex; flex-direction:column; gap:16px; margin-top:14px;">
        ${createBarChartHTML('Geodesic Alignment', fallbackAlign, frontierAlign)}
        ${createBarChartHTML('Precision', fallbackPrec, frontierPrec)}
        ${createBarChartHTML('Sensitivity', fallbackSens, frontierSens)}
      </div>
    `;
    
    chartsContainer.appendChild(card);
  });
}

function createBarChartHTML(metricName, fallbackVal, nativeVal) {
  return `
    <div class="chart-bar-group">
      <div class="chart-bar-label">
        <span>${metricName}</span>
        <span>Fallback: ${fallbackVal.toFixed(3)} | Native: ${nativeVal.toFixed(3)}</span>
      </div>
      <div style="display:flex; flex-direction:column; gap:6px; margin-top:4px;">
        <div class="chart-bar-track">
          <div class="chart-bar-fill bar-fallback" style="width: ${fallbackVal * 100}%"></div>
        </div>
        <div class="chart-bar-track">
          <div class="chart-bar-fill bar-native" style="width: ${nativeVal * 100}%"></div>
        </div>
      </div>
    </div>
  `;
}

function escapeHTML(str) {
  if (typeof str !== 'string') return '';
  return str.replace(/[&<>'"]/g, 
    tag => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      "'": '&#39;',
      '"': '&quot;'
    }[tag] || tag)
  );
}
""".strip()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Export the static demo dashboard.")
    parser.add_argument("--artifact-root", type=Path, default=None)
    args = parser.parse_args(argv)
    dashboard_path = export_demo_dashboard(args.artifact_root)
    print(json.dumps({"dashboard": str(dashboard_path)}, indent=2))


if __name__ == "__main__":
    main()
