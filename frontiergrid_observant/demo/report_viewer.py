"""Console report viewer for simulation run results.

See [report_viewer.py](file:///g:/aiDoW/DON/DON26BZ01-NVO23/frontiergrid-observant/frontiergrid_observant/demo/report_viewer.py) for implementation details.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from rich import box
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.markdown import Markdown

from frontiergrid_observant.config import load_settings

# Curated HSL-tailored colors for modern dark-mode terminal visuals
COLOR_MAP = {
    "teal": "turquoise2",
    "amber": "gold3",
    "berry": "hot_pink",
    "blue": "deep_sky_blue1",
    "green": "spring_green3",
    "red": "light_coral",
    "grey": "grey53",
}

ROLE_LABELS = {
    "watcher": "Watcher Agent",
    "integrator": "Integrator Agent",
    "risk_officer": "Risk Officer Agent",
    "skeptic": "Skeptic Agent",
    "explainer": "Explainer Agent",
}


def make_metric_bar(value: Any, width: int = 10, color_name: str = "green") -> str:
    """Creates a visual progress bar representation for terminal rendering."""
    if value is None:
        return f"[{COLOR_MAP['grey']}]n/a[/{COLOR_MAP['grey']}]"
    try:
        val = float(value)
    except (ValueError, TypeError):
        return f"[{COLOR_MAP['grey']}]n/a[/{COLOR_MAP['grey']}]"

    val = max(0.0, min(1.0, val))
    filled = round(val * width)
    empty = width - filled
    color = COLOR_MAP.get(color_name, COLOR_MAP["green"])
    grey = COLOR_MAP["grey"]
    return f"[{color}]{'█' * filled}[/{color}][{grey}]{'░' * empty}[/{grey}]"


def _scenario_name(scenario_id: str) -> str:
    """Cleans up scenario ID to a readable title."""
    cleaned = re.sub(r"^scenario_\d+_", "", scenario_id)
    return cleaned.replace("_", " ").strip().title()


def print_summary_table(comparison_data: dict[str, Any], console: Console) -> None:
    """Prints the fallback-vs-native substrate comparison table."""
    teal = COLOR_MAP["teal"]
    table = Table(
        title=f"\n[bold {teal}]FrontierGrid-Observant Substrate Comparison[/bold {teal}]",
        box=box.DOUBLE_EDGE,
        border_style="grey37",
        title_style="bold",
    )

    table.add_column("Scenario", style="bold white", header_style="bold white")
    table.add_column("Substrate", header_style="bold white")
    table.add_column("Alerts", justify="right", header_style="bold white")
    table.add_column("First Tick", justify="right", header_style="bold white")
    table.add_column("Severity", header_style="bold white")
    table.add_column("Confidence", header_style="bold white")
    table.add_column("Alignment", header_style="bold white")
    table.add_column("Status", header_style="bold white")
    table.add_column("Precision", header_style="bold white")
    table.add_column("Sensitivity", header_style="bold white")
    table.add_column("Evidence", header_style="bold white")

    for scenario in comparison_data.get("scenarios", []):
        scenario_name = _scenario_name(scenario["scenario_id"])

        for substrate in ["fallback", "frontier_os"]:
            result = scenario.get("substrates", {}).get(substrate)
            if not result:
                continue

            sub_style = "green" if substrate == "fallback" else "teal"
            sub_color = COLOR_MAP[sub_style]
            sub_avail = result.get("substrate_available", False)
            avail_txt = " (avail)" if sub_avail else " (safe)"
            substrate_cell = f"[{sub_color}]{substrate}[/{sub_color}]{avail_txt}"

            alert_count = result.get("alert_count", 0)
            first_alert = result.get("first_alert") or {}

            tick = first_alert.get("tick")
            tick_str = str(tick) if tick is not None else "-"

            severity = first_alert.get("severity")
            severity_color = "red" if (severity or 0) >= 0.7 else ("amber" if (severity or 0) >= 0.5 else "green")
            severity_cell = (
                f"{make_metric_bar(severity, color_name=severity_color)} {severity:.3f}"
                if severity is not None
                else f"[{COLOR_MAP['grey']}]n/a[/{COLOR_MAP['grey']}]"
            )

            confidence = first_alert.get("confidence")
            confidence_color = "green" if (confidence or 0) >= 0.75 else ("amber" if (confidence or 0) >= 0.5 else "red")
            confidence_cell = (
                f"{make_metric_bar(confidence, color_name=confidence_color)} {confidence:.3f}"
                if confidence is not None
                else f"[{COLOR_MAP['grey']}]n/a[/{COLOR_MAP['grey']}]"
            )

            alignment = first_alert.get("context_geodesic_alignment")
            alignment_color = "teal" if (alignment or 0) >= 0.7 else ("amber" if (alignment or 0) >= 0.5 else "red")
            alignment_cell = (
                f"{make_metric_bar(alignment, color_name=alignment_color)} {alignment:.3f}"
                if alignment is not None
                else f"[{COLOR_MAP['grey']}]n/a[/{COLOR_MAP['grey']}]"
            )

            status = first_alert.get("status")
            if status:
                status_color = COLOR_MAP["amber"] if status == "human_escalation_review" else COLOR_MAP["green"]
                status_str = f"[bold {status_color}]{status.replace('_', ' ').title()}[/bold {status_color}]"
            else:
                status_str = f"[{COLOR_MAP['grey']}]-[/{COLOR_MAP['grey']}]"

            metrics = result.get("metrics") or {}
            precision = metrics.get("precision")
            precision_cell = (
                f"{make_metric_bar(precision, color_name='blue')} {precision:.3f}"
                if precision is not None
                else f"[{COLOR_MAP['grey']}]n/a[/{COLOR_MAP['grey']}]"
            )

            sensitivity = metrics.get("sensitivity")
            sensitivity_cell = (
                f"{make_metric_bar(sensitivity, color_name='blue')} {sensitivity:.3f}"
                if sensitivity is not None
                else f"[{COLOR_MAP['grey']}]n/a[/{COLOR_MAP['grey']}]"
            )

            is_complete = first_alert.get("all_agent_evidence_present") or first_alert.get(
                "expected_agent_evidence_complete", False
            )
            evidence_cell = (
                f"[bold {COLOR_MAP['green']}]Complete[/bold {COLOR_MAP['green']}]"
                if is_complete
                else (
                    f"[bold {COLOR_MAP['amber']}]Partial[/bold {COLOR_MAP['amber']}]"
                    if first_alert
                    else f"[{COLOR_MAP['grey']}]n/a[/{COLOR_MAP['grey']}]"
                )
            )

            table.add_row(
                scenario_name,
                substrate_cell,
                str(alert_count),
                tick_str,
                severity_cell,
                confidence_cell,
                alignment_cell,
                status_str,
                precision_cell,
                sensitivity_cell,
                evidence_cell,
            )

    console.print(table)


def render_trace_val(val: Any) -> str:
    """Formats trace values nicely for the console."""
    if isinstance(val, float):
        return f"{val:.3f}"
    if isinstance(val, list):
        return ", ".join(str(v) for v in val)
    if isinstance(val, dict):
        return ", ".join(f"{k}: {render_trace_val(v)}" for k, v in val.items())
    return str(val)


def print_agent_evidence_grid(alert: dict[str, Any], console: Console) -> None:
    """Renders agent evidence in a clean side-by-side / grid panel layout."""
    agent_evidence = alert.get("agent_evidence", {})
    if not agent_evidence:
        console.print(f"\n[bold {COLOR_MAP['amber']}]No agent evidence available in this alert.[/bold {COLOR_MAP['amber']}]")
        return

    # First row: Watcher, Integrator, Risk Officer
    row1_table = Table.grid(expand=True, padding=(0, 2))
    row1_table.add_column(ratio=1)
    row1_table.add_column(ratio=1)
    row1_table.add_column(ratio=1)

    # Second row: Skeptic, Explainer
    row2_table = Table.grid(expand=True, padding=(0, 2))
    row2_table.add_column(ratio=1)
    row2_table.add_column(ratio=1)

    panels = {}
    for role, label in ROLE_LABELS.items():
        evidence = agent_evidence.get(role, {})
        if not evidence:
            panels[role] = Panel(
                Text("No evidence recorded.", style=COLOR_MAP["grey"]),
                title=f"[bold grey53]{label}[/bold grey53]",
                border_style="grey37",
            )
            continue

        score = evidence.get("score")
        confidence = evidence.get("confidence")
        summary = evidence.get("summary", "No summary.")
        notes = evidence.get("notes", [])
        trace = evidence.get("trace", {})

        # Color scheme per agent role
        role_colors = {
            "watcher": COLOR_MAP["teal"],
            "integrator": COLOR_MAP["blue"],
            "risk_officer": COLOR_MAP["red"],
            "skeptic": COLOR_MAP["amber"],
            "explainer": COLOR_MAP["berry"],
        }
        role_color = role_colors.get(role, "white")

        # Build card content Group
        content_items = []
        score_str = f"{score:.3f}" if score is not None else "n/a"
        score_bar = make_metric_bar(score, color_name="green" if role != "risk_officer" else "red")
        content_items.append(Text.from_markup(f"Score:      {score_bar} ({score_str})"))

        conf_str = f"{confidence:.3f}" if confidence is not None else "n/a"
        conf_bar = make_metric_bar(confidence, color_name="green")
        content_items.append(Text.from_markup(f"Confidence: {conf_bar} ({conf_str})"))
        content_items.append(Text(""))
        content_items.append(Text(summary, style="italic"))

        if notes:
            content_items.append(Text("\nNotes:", style="bold"))
            for note in notes:
                content_items.append(Text(f" • {note}"))

        if trace:
            content_items.append(Text("\nTrace telemetry:", style="bold"))
            trace_table = Table(box=None, show_header=False, padding=(0, 1))
            trace_table.add_column("Key", style=COLOR_MAP["grey"])
            trace_table.add_column("Value", style="bold white")
            for k, v in trace.items():
                k_label = k.replace("_", " ").title()
                trace_table.add_row(k_label, render_trace_val(v))
            content_items.append(trace_table)

        panels[role] = Panel(
            Group(*content_items),
            title=f"[bold {role_color}]{label}[/bold {role_color}]",
            border_style=role_color,
            expand=True,
        )

    row1_table.add_row(panels["watcher"], panels["integrator"], panels["risk_officer"])
    row2_table.add_row(panels["skeptic"], panels["explainer"])

    console.print(f"\n[bold {COLOR_MAP['teal']}]Agent Multi-Agent Decision Evidence[/bold {COLOR_MAP['teal']}]")
    console.print(row1_table)
    console.print(row2_table)


def print_scenario_details(
    scenario_id: str,
    alerts: list[dict[str, Any]],
    comparison_data: dict[str, Any],
    artifact_root: Path,
    console: Console,
) -> None:
    """Renders details for a specific scenario run."""
    scen_name = _scenario_name(scenario_id)
    console.print(f"\n[bold {COLOR_MAP['teal']}]=== Scenario Detail: {scen_name} ===[/bold {COLOR_MAP['teal']}]")
    console.print(f"[grey53]Scenario ID: {scenario_id}[/grey53]")

    scenario_meta = None
    for s in comparison_data.get("scenarios", []):
        if s.get("scenario_id") == scenario_id:
            scenario_meta = s
            break

    if scenario_meta:
        delta = scenario_meta.get("delta", {})
        console.print(f"Seed: {scenario_meta.get('seed')} | Ticks: {scenario_meta.get('ticks')}")
        if delta:
            sev_delta = delta.get("severity_delta", 0)
            conf_delta = delta.get("confidence_delta", 0)
            tick_delta = delta.get("first_alert_tick_delta", 0)
            console.print(
                f"[bold]Native Substrate Deltas:[/bold] "
                f"Severity: [bold {COLOR_MAP['red'] if sev_delta > 0 else COLOR_MAP['green']}]{sev_delta:+.3f}[/] | "
                f"Confidence: [bold {COLOR_MAP['green'] if conf_delta > 0 else COLOR_MAP['red']}]{conf_delta:+.3f}[/] | "
                f"Tick Delta: {tick_delta:+.1f}"
            )

    if not alerts:
        console.print(f"\n[bold {COLOR_MAP['red']}]No alerts triggered in this scenario run.[/bold {COLOR_MAP['red']}]")
        return

    for idx, alert in enumerate(alerts, 1):
        alert_title = alert.get("title", "Untitled Alert")
        risk_type = alert.get("risk_type", "Unknown Risk")
        status = alert.get("status", "Unknown")
        severity = alert.get("severity")
        confidence = alert.get("confidence")
        data_quality = alert.get("data_quality")
        alignment = alert.get("context_geodesic_alignment")
        explanation = alert.get("explanation", "No explanation provided.")

        status_color = COLOR_MAP["amber"] if status == "human_escalation_review" else COLOR_MAP["green"]
        status_str = f"[bold {status_color}]{status.replace('_', ' ').title()}[/bold {status_color}]"

        alert_header = Table.grid(expand=True)
        alert_header.add_column()
        alert_header.add_column(justify="right")
        alert_header.add_row(
            Text.from_markup(f"[bold white]{idx}. {alert_title}[/bold white] ([italic]{risk_type}[/italic])"),
            Text.from_markup(f"Status: {status_str}"),
        )

        metrics_table = Table(box=box.SIMPLE, border_style="grey37", expand=True)
        metrics_table.add_column("Metric", style="bold")
        metrics_table.add_column("Visual Level")
        metrics_table.add_column("Value", justify="right")

        metrics_table.add_row(
            "Severity",
            make_metric_bar(severity, color_name="red"),
            f"{severity:.3f}" if severity is not None else "n/a",
        )
        metrics_table.add_row(
            "Confidence",
            make_metric_bar(confidence, color_name="green"),
            f"{confidence:.3f}" if confidence is not None else "n/a",
        )
        metrics_table.add_row(
            "Data Quality",
            make_metric_bar(data_quality, color_name="blue"),
            f"{data_quality:.3f}" if data_quality is not None else "n/a",
        )
        metrics_table.add_row(
            "Context Geodesic Alignment",
            make_metric_bar(alignment, color_name="teal"),
            f"{alignment:.3f}" if alignment is not None else "n/a",
        )

        alert_group = Group(
            alert_header,
            Text(""),
            Panel(Text(explanation), title="[bold]Explanation[/bold]", border_style="grey53"),
            Text(""),
            metrics_table,
        )

        console.print(
            Panel(
                alert_group,
                title=f"[bold {COLOR_MAP['amber']}]ALERT CARD[/bold {COLOR_MAP['amber']}]",
                border_style=COLOR_MAP["amber"],
            )
        )

        print_agent_evidence_grid(alert, console)

    replay_path = artifact_root / f"{scenario_id}_replay.md"
    if replay_path.exists():
        try:
            replay_text = replay_path.read_text(encoding="utf-8")
            timeline_part = replay_text
            if "## Timeline" in replay_text:
                timeline_part = replay_text.split("## Timeline", 1)[1].strip()

            console.print(f"\n[bold {COLOR_MAP['teal']}]Replay Timeline Trace[/bold {COLOR_MAP['teal']}]")
            console.print(Panel(Markdown(timeline_part), border_style="grey37"))
        except Exception as e:
            console.print(f"[grey53]Error loading replay timeline: {e}[/grey53]")


def main(argv: list[str] | None = None, console: Console | None = None) -> None:
    import sys
    try:
        if sys.stdout and sys.stdout.encoding != "utf-8":
            sys.stdout.reconfigure(encoding="utf-8")
        if sys.stderr and sys.stderr.encoding != "utf-8":
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

    parser = argparse.ArgumentParser(
        description="Beautiful terminal-based FrontierGrid-Observant report viewer."
    )
    parser.add_argument(
        "--artifact-root",
        type=Path,
        help="Path to the directory containing JSON artifacts.",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print the fallback-vs-native comparison summary table.",
    )
    parser.add_argument(
        "--scenario",
        type=str,
        help="Scenario ID (e.g. 'scenario_01' or 'scenario_01_maritime_shadowing') to print detailed alert and evidence cards.",
    )

    args = parser.parse_args(argv)
    if console is None:
        console = Console()

    settings = load_settings()
    artifact_root = args.artifact_root or settings.artifact_root

    comparison_path = artifact_root / "fallback_vs_frontier_os_metrics.json"
    if not comparison_path.exists():
        console.print(
            f"[bold red]Error: Comparison metrics file not found at {comparison_path}.[/bold red]\n"
            "Please make sure the simulations have been run and compare_substrates has generated the artifacts."
        )
        return

    try:
        comparison_data = json.loads(comparison_path.read_text(encoding="utf-8"))
    except Exception as e:
        console.print(f"[bold red]Error loading comparison JSON file: {e}[/bold red]")
        return

    if args.scenario:
        target_scenario = None
        for s in comparison_data.get("scenarios", []):
            scen_key = s.get("scenario_key", "")
            scen_id = s.get("scenario_id", "")
            if (
                args.scenario == scen_key
                or args.scenario == scen_id
                or scen_id.startswith(args.scenario)
            ):
                target_scenario = scen_id
                break

        if not target_scenario:
            console.print(
                f"[bold red]Error: Scenario '{args.scenario}' not found in comparison metrics.[/bold red]"
            )
            return

        alerts_path = artifact_root / f"{target_scenario}_alerts.json"
        alerts = []
        if alerts_path.exists():
            try:
                alerts = json.loads(alerts_path.read_text(encoding="utf-8"))
            except Exception as e:
                console.print(
                    f"[bold red]Warning: Error loading scenario alerts from {alerts_path}: {e}[/bold red]"
                )
        else:
            console.print(
                f"[bold yellow]Warning: Alerts file not found at {alerts_path}. Rendering scenario info only.[/bold yellow]"
            )

        print_scenario_details(target_scenario, alerts, comparison_data, artifact_root, console)
    else:
        print_summary_table(comparison_data, console)


if __name__ == "__main__":
    main()
