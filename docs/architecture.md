# Architecture

FrontierGrid-Observant uses an adapter-first architecture. The fallback path remains deterministic and runnable without external services. The first Frontier_OS / Exciton-MoA path dynamically imports the local manifold runtime and runs one broadcast, exciton ignition, and telemetry scan per Observant event.

```text
Synthetic / sanitized event streams
        |
        v
Event schema and normalizer
        |
        v
Context graph + provenance store
        |
        v
Reasoning substrate adapter
  - FallbackAdapter, deterministic Python
        - FrontierOSAdapter, local manifold bridge
        |
        v
Federated domain alignment
  - Sea / Space / Air / Land / Cyber domain state
  - Mission-level aggregate alignment
  - Context-geodesic ordering signal
        |
        v
Agent roles
  - Watcher
  - Integrator
  - Risk Officer
  - Skeptic
  - Explainer
  - Coordinator
        |
        v
Risk cards + replay traces + metrics artifacts
```

## Adapter Contract

The substrate adapter boundary is intentionally narrow:

```python
class ReasoningSubstrate:
    def initialize(self, scenario_id: str) -> None: ...
    def ingest_event(self, event: ObservantEvent) -> SubstrateTrace: ...
    def get_context_state(self) -> ContextState: ...
    def get_alert_candidates(self) -> list[AlertCandidate]: ...
    def replay(self, alert_id: str) -> ReplayTrace: ...
```

## Federated Domain Manifolds

FrontierGrid-Observant now treats distributed Observant-AI teaming as a federated alignment problem. Each normalized event is assigned to a canonical domain-local state such as sea, space, air, land, or cyber. The runtime maintains lightweight domain-manifold summaries for anomaly pressure, source quality, data quality, hotspot pressure, contradiction pressure, active modalities, active risk types, and recent event IDs.

A mission-level aggregate alignment layer then evaluates candidate alert paths across those domain summaries. The aggregate computes a context-geodesic score from domain coverage, temporal coherence, source quality, data quality, domain contribution, and contradiction pressure. This score is exported on alert cards as `context_geodesic_alignment` and in the integrator trace as active domains, domain contributions, and the temporary candidate agent team.

This keeps the Phase I implementation bounded and auditable while preserving the intended design choice: domain agents do not merely exchange free-form messages; they self-organize around measured contextual alignment, uncertainty, and contradiction signals.

## Related Repo Integration Notes

The active integration path lives in `frontiergrid_observant/runtime/manifold_bridge.py` and `frontiergrid_observant/runtime/frontier_os_adapter.py`.

Current event flow for `--substrate frontier_os`:

1. Resolve `FRONTIER_OS_ROOT` or the sibling backup repo path.
2. Dynamically import `BlankManifoldCore`, `StatisticalPrism`, `ExcitonEngine`, and `OntologicalOrchestrator`.
3. Generate a small deterministic manifold, defaulting to `FRONTIER_OS_NODE_COUNT=128`.
4. Convert each Observant event into a calibrated embedding.
5. Broadcast through `StatisticalPrism.global_resonance_broadcast()`.
6. Run `ExcitonEngine.ignite_excitons()`.
7. Run `OntologicalOrchestrator.scan_manifold()`.
8. Feed target coordinates, active node count, peak resonance, hotspot pressure, burst count, and scan-order fingerprint back into `SubstrateTrace.manifold_metrics` and `ContextState.substrate_metrics`.

Frontier_OS backup components identified for future optional integration:

- `../Frontier_OS-main/Frontier_OS-main/Exciton-MoA/hardWare/blank_manifold_core.py`: `BlankManifoldCore`.
- `../Frontier_OS-main/Frontier_OS-main/Exciton-MoA/transDucer/statisticalPrism.py`: `StatisticalPrism`.
- `../Frontier_OS-main/Frontier_OS-main/Exciton-MoA/firmWare/ExcitonEngine/excitons.py`: `ExcitonEngine` and the seven contextual operators.
- `../Frontier_OS-main/Frontier_OS-main/Exciton-MoA/teleMetry/telemetry.py`: `OntologicalOrchestrator`.
- `../Frontier_OS-main/Frontier_OS-main/Exciton-MoA/entangled_manifolds.py`: `EntangledSOLPair`.
- `../Frontier_OS-main/Frontier_OS-main/Exciton-MoA/teleMetry/hippocampalReplay.py`: `HippocampalReplay`.

SOL backup components that can inform semantic graph design:

- `../sol-main/sol-main/tools/sol-core/sol_engine.py`.
- `../sol-main/sol-main/tools/sol-core/default_graph.json`.
- `../sol-main/sol-main/tools/sol-hippocampus/memory_store.py`.
- `../sol-main/sol-main/tools/analysis/metrics.py`.

For this local ephemeral prototype, Techman Studios-owned Frontier_OS / SOL / Exciton-MoA integration is authorized when useful. Keep integration behind the adapter boundary where practical because the backup layout is double-nested and imported dynamically through `sys.path`. Revisit final licensing, data-rights, and distribution language before public release or proposal delivery.
