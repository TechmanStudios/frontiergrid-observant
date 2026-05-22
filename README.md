# FrontierGrid-Observant

FrontierGrid-Observant is an unclassified Phase I feasibility testbed for DON26BZ01-NV023 Observant-AI: risk-aware regenerative AI-based multimodal visual-tactical monitoring, understanding, alerting, and assistance.

The project adapts Techman Studios' SOL / Frontier_OS / Exciton-MoA research direction into a controlled synthetic-data environment for evaluating multi-agent contextual fusion, risk scoring, alert prioritization, and replayable explanations under noisy cross-domain event streams.

This repository is not an operational defense system and does not provide real-world targeting, weapon employment, or tactical maneuver recommendations. Prototype output should use review-oriented language such as risk alert, confidence score, analyst review recommended, contextual explanation, and possible anomaly cluster.

## Current Status

Early repo scaffold for a proposal-oriented Phase I prototype with a first real Frontier_OS / Exciton-MoA manifold adapter path, federated domain-alignment metrics, and a 1,024-node native manifold test configuration.

The deterministic fallback harness still runs without classified data, external sensors, or direct dependency on the Frontier_OS runtime. The `frontier_os` substrate dynamically imports the local Frontier_OS / Exciton-MoA manifold, broadcasts Observant events through the StatisticalPrism, ignites exciton operators, scans telemetry, and feeds manifold metrics back into the alert pipeline. Current native-mode notes are captured in [docs/native_manifold_integration.md](docs/native_manifold_integration.md).

## Quickstart

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e ".[dev]"
python -m scripts.create_synthetic_data --all
python -m frontiergrid_observant.demo.run_demo --scenario scenario_01 --export
python -m frontiergrid_observant.demo.run_demo --scenario scenario_01 --substrate frontier_os --export
python -m frontiergrid_observant.eval.run_eval --all
pytest
```

## Prototype Scope

The Phase I MVP is designed to show that synthetic cross-domain events can be:

- Ingested through a common unclassified event schema.
- Fused into a shared contextual state.
- Organized into Sea, Space, Air, Land, and Cyber style domain summaries for mission-level aggregate alignment.
- Broadcast into the local Frontier_OS / Exciton-MoA manifold when `--substrate frontier_os` is selected.
- Traced with manifold metrics such as target coordinates, active node count, peak resonance, hotspot pressure, burst count, and scan-order fingerprint.
- Scored for risk, confidence, uncertainty, and data quality.
- Reviewed by lightweight multi-agent roles: watcher, integrator, risk officer, skeptic, explainer, and coordinator.
- Routed to human review when moderate risk coincides with degraded data quality, weak source reliability, or strong skeptic pressure.
- Exported as replayable alert, context, and metrics artifacts.

## Challenge Scenarios

1. Cross-domain maritime shadowing and ambiguous intent.
2. Cross-domain littoral hazard escalation.
3. Cross-domain degraded communications with decoy behavior.
4. Cross-domain coordinated ambiguity where no single domain is decisive alone.
5. Unknown-unknown state-space injection with weak cross-domain echoes.

Every built-in scenario rotates synthetic anomaly evidence across multiple domains so the federated aggregate manifold, context-geodesic alignment score, and self-organizing agent-team traces are exercised by default. The fifth scenario deliberately keeps individual novelty cues below local rule thresholds so the shared state-space path can be evaluated against an unknown-unknown style disturbance.

All built-in scenarios must remain synthetic, repeatable, and unclassified. OSINT-style data may be added later only after sanitization and compliance review.

## Repository Map

```text
frontiergrid_observant/        Python package
  agents/                      Lightweight deterministic agent roles
  context/                     Context graph and provenance state
  demo/                        Demo runner and artifact export
  eval/                        Metrics and baseline evaluation harness
  explain/                     Replay and explanation generation
  ingest/                      Loaders and synthetic data generation
  risk/                        Risk, confidence, and escalation controls
  runtime/                     Substrate adapters and coordination contracts
  schemas/                     Typed event, alert, provenance, and metric models
data/                          Synthetic datasets and JSON schemas
docs/                          Architecture, compliance, proposal support
scripts/                       Local utility commands
tests/                         Focused pytest coverage
artifacts/                     Generated demo outputs, gitignored by default
```

## Licensing Posture

This scaffold is private/proprietary by default while SBIR data-rights, export-control, and Techman Studios IP assertions are finalized. See [LICENSE.md](LICENSE.md) and [docs/submission/data_rights_notes.md](docs/submission/data_rights_notes.md).

No Frontier_OS / Exciton-MoA code is vendored into this scaffold at setup time. Because these are Techman Studios-owned repos, local ephemeral integration can proceed inside this workspace when useful. Public release, proposal submission, or third-party distribution should revisit final licensing and data-rights language before anything leaves the workspace.

## Compliance Guardrails

- Keep Phase I data unclassified and synthetic unless approved otherwise.
- Do not commit CUI, classified data, sensitive operational data, credentials, or proprietary third-party data.
- Treat DON26BZ01-NV023 as ITAR/EAR-sensitive for planning and access-control purposes.
- Maintain CMMC Level 2 self-assessment readiness notes for contract preparation.
- Keep proposal abstracts free of proprietary or classified detail.

## Proposal Support

The `docs/submission/` directory contains first-pass proposal support material for a 10-page Volume 2 technical narrative, Phase I SOW, anticipated benefits, commercialization, and data-rights notes.

These files are working drafts, not legal or contracting advice.
