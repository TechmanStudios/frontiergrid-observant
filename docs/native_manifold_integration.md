# Native Manifold Integration

This note preserves the current Antigravity handoff inside the FrontierGrid-Observant repo so the next build steps do not depend on external app state.

## Current Direction

The prototype now treats `--substrate frontier_os` as the primary experimental path for Observant-AI feasibility work. The fallback path remains useful for schema checks, deterministic demos, and safe-mode continuity, but the differentiating technical claim is the native Frontier_OS / Exciton-MoA bridge.

## Implemented Integration

- `frontiergrid_observant/config.py` defaults native Frontier_OS runs to a 1,024-node manifold.
- `frontiergrid_observant/runtime/manifold_bridge.py` resolves the local Exciton-MoA root, creates the manifold, registers a scenario-scoped `LatentMediator`, broadcasts event embeddings through `StatisticalPrism`, ignites exciton operators, scans telemetry, and returns trace metrics.
- `frontiergrid_observant/runtime/frontier_os_adapter.py` instantiates watcher, integrator, risk officer, skeptic, and explainer roles when the bridge is available.
- Native alerts now route moderate-risk cases to `human_escalation_review` when the skeptic/data-quality controls see degraded data quality, weak source reliability, or high benign-alternative pressure.

## Related Multi-Repo Work

- `../Frontier_OS-main/Frontier_OS-main/Exciton-MoA/scripts/decision_report_monitor.py` adds weekly decision-report regression monitoring.
- `../Frontier_OS-main/Frontier_OS-main/Exciton-MoA/blank_manifold/pre_check_tests/test_decision_report_monitor.py` covers monitor behavior and incident schema output.
- `../sol-main/sol-main/.github/workflows/sol-exciton-decision-monitor-weekly.yml` schedules the monitor after the weekly decision report workflow.

## Verified Commands

```powershell
python -m pytest g:\aiDoW\DON\DON26BZ01-NVO23\frontiergrid-observant
```

Latest observed result: `7 passed` before this note and risk-control update. Re-run after edits before relying on the branch state.

## Next Build Priorities

1. Add a small demo/report view that renders alert cards and fallback-versus-native comparison tables for presentation.
2. Add richer evaluation comparison fields for explanation completeness and source-grounded evidence density.
3. Keep proposal-facing language focused on contextual coherence, anomaly signals, data-quality warnings, and replayable audit trails.