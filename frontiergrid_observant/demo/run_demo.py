"""Console demo runner for synthetic Observant-AI scenarios."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from frontiergrid_observant.config import load_settings
from frontiergrid_observant.explain.replay import write_replay_markdown
from frontiergrid_observant.ingest.synthetic_generator import SCENARIOS, generate_scenario
from frontiergrid_observant.runtime.fallback_adapter import FallbackAdapter
from frontiergrid_observant.runtime.frontier_os_adapter import FrontierOSAdapter


def run_demo(
    scenario: str = "scenario_01",
    substrate: str = "fallback",
    seed: int = 149,
    ticks: int = 30,
    export: bool = False,
    artifact_root: Path | None = None,
) -> dict[str, object]:
    settings = load_settings()
    adapter = (
        FrontierOSAdapter(
            settings.frontier_os_root,
            node_count=settings.frontier_os_node_count,
            tau_threshold=settings.frontier_os_tau_threshold,
        )
        if substrate == "frontier_os"
        else FallbackAdapter()
    )
    events = generate_scenario(scenario, seed=seed, ticks=ticks)
    adapter.initialize(events[0].scenario_id)
    for event in events:
        adapter.ingest_event(event)
    alerts = adapter.build_alerts()
    context = adapter.get_context_state()
    payload = {
        "scenario_id": events[0].scenario_id,
        "substrate": adapter.substrate_name,
        "event_count": len(events),
        "context": context.model_dump(),
        "alerts": [alert.model_dump() for alert in alerts],
    }
    if export:
        root = artifact_root or settings.artifact_root
        _export_payload(payload, adapter, root)
    return payload


def _export_payload(
    payload: dict[str, object], adapter: FallbackAdapter, artifact_root: Path
) -> None:
    artifact_root.mkdir(parents=True, exist_ok=True)
    scenario_id = str(payload["scenario_id"])
    alerts_path = artifact_root / f"{scenario_id}_alerts.json"
    alerts_path.write_text(json.dumps(payload["alerts"], indent=2, default=str), encoding="utf-8")
    context_path = artifact_root / f"{scenario_id}_context.json"
    context_path.write_text(json.dumps(payload["context"], indent=2, default=str), encoding="utf-8")
    alerts = adapter.alerts
    if alerts:
        trace = adapter.replay(alerts[0].alert_id)
        write_replay_markdown(trace, artifact_root / f"{scenario_id}_replay.md")
    report = [
        "# FrontierGrid-Observant Demo Report",
        "",
        f"Scenario: {scenario_id}",
        f"Substrate: {payload['substrate']}",
        f"Events: {payload['event_count']}",
        f"Alerts: {len(alerts)}",
        "",
    ]
    for alert in alerts:
        report.extend([f"## {alert.title}", "", alert.explanation, ""])
    (artifact_root / "frontiergrid_observant_demo_report.md").write_text(
        "\n".join(report), encoding="utf-8"
    )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Run a FrontierGrid-Observant synthetic scenario demo."
    )
    parser.add_argument("--scenario", default="scenario_01", choices=sorted(SCENARIOS))
    parser.add_argument("--substrate", default="fallback", choices=["fallback", "frontier_os"])
    parser.add_argument("--seed", type=int, default=149)
    parser.add_argument("--ticks", type=int, default=30)
    parser.add_argument("--export", action="store_true")
    args = parser.parse_args(argv)
    payload = run_demo(
        scenario=args.scenario,
        substrate=args.substrate,
        seed=args.seed,
        ticks=args.ticks,
        export=args.export,
    )
    print(json.dumps(payload, indent=2, default=str))


if __name__ == "__main__":
    main()
