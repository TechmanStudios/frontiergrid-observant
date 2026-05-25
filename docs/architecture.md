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

The codebase has been fully consolidated into a single working workspace. All components from the external `Frontier_OS` and `SOL` repositories are natively integrated into the package structure, removing dynamic imports and path modifications:

1. **SOLEngine Subpackage**: Nested under [frontiergrid_observant/sol/](file:///g:/aiDoW/DON/DON26BZ01-NVO23/frontiergrid-observant/frontiergrid_observant/sol/).
2. **Exciton-MoA Subpackage**: Nested under [frontiergrid_observant/exciton_moa/](file:///g:/aiDoW/DON/DON26BZ01-NVO23/frontiergrid-observant/frontiergrid_observant/exciton_moa/).

### Event Flow for `--substrate frontier_os` (Observant-SOL Integration)

1. Convert each incoming Observant event into a calibrated embedding.
2. Broadcast the embedding through the `StatisticalPrism` to locate the resonance coordinates in the 3D space.
3. Ignite exciton operators using `ExcitonEngine`.
4. Scan the manifold using the `OntologicalOrchestrator` to capture local resonance hotspots.
5. Step the `SOLEngine` by injecting normalized risk and metadata signals to update belief states.
6. Feed the resulting manifold metrics (peak resonance, active node counts, coordinates, etc.) and low-entropy `sol_intuition` consensus details directly into the multi-agent reasoning trace.
