# Adaptation Log

Use this log to record proposal and implementation decisions that change scope.

## 2026-05-19

Decision: Create FrontierGrid-Observant as a sibling repo instead of nesting it under Frontier_OS.

Reason: The Observant-AI effort needs a proposal-facing proprietary/SBIR posture, synthetic-data-only compliance notes, and a clean adapter boundary around Frontier_OS / Exciton-MoA AGPL/commercial licensing decisions.

Files affected: full repo scaffold.

Proposal impact: Presents the current work as a Phase I feasibility harness, not an operational defense system.

Keep / cut / defer: Keep deterministic fallback path; allow local ephemeral Frontier_OS / SOL / Exciton-MoA integration through adapters when useful; revisit distribution and data-rights language before release or submission.

## 2026-05-19: First Real Manifold Adapter

Decision: Wire `--substrate frontier_os` to the local Frontier_OS / Exciton-MoA manifold runtime instead of only detecting repo availability.

Reason: The Observant scenarios need a working manifold substrate so event fusion and risk scoring can be shaped by actual manifold computation.

Files affected: `frontiergrid_observant/runtime/manifold_bridge.py`, `frontiergrid_observant/runtime/frontier_os_adapter.py`, `frontiergrid_observant/runtime/base.py`, `frontiergrid_observant/demo/run_demo.py`, `frontiergrid_observant/eval/run_eval.py`, tests, docs.

Proposal impact: The prototype can now claim a first working adapter path that broadcasts Observant events into Frontier_OS / Exciton-MoA and exports manifold trace metrics.

Keep / cut / defer: Keep fallback as stable baseline; next work should improve scenario logic so alert timing and evaluation metrics use manifold dynamics more directly.

## 2026-05-20: Native Manifold Agent Loop And Uncertainty Escalation

Decision: Continue from the Antigravity handoff by treating the `frontier_os` substrate as the primary experimental path while keeping fallback available as an interface and safety baseline.

Reason: The local Frontier_OS / Exciton-MoA runtime now supports a 1,024-node manifold with `LatentMediator` projections and topological agent roles for watcher, integrator, risk officer, skeptic, and explainer behavior.

Files affected: `frontiergrid_observant/agents/`, `frontiergrid_observant/runtime/frontier_os_adapter.py`, `frontiergrid_observant/runtime/manifold_bridge.py`, `frontiergrid_observant/risk/risk_engine.py`, tests, docs.

Proposal impact: The prototype can describe native manifold-backed multi-agent review, plus explicit AI-risk escalation controls when moderate risk is paired with degraded data quality, weak source reliability, or strong benign-alternative pressure.

Keep / cut / defer: Keep the deterministic fallback path lean; keep native manifold work behind the adapter boundary; defer any public release language until licensing, data-rights, and export-control posture are reviewed.

## 2026-05-20: Side-By-Side Native Agent Evidence

Decision: Export structured alert-card evidence for watcher, integrator, risk officer, skeptic, and explainer roles while preserving the compact `agent_votes` map.

Reason: Demo artifacts need to show how each native role contributed to the alert instead of only reporting four scalar votes.

Files affected: alert schema, native agent traces, fallback and Frontier_OS adapters, demo tests, docs.

Proposal impact: Alert cards can now support side-by-side evidence review, including native manifold signals such as epicenter nodes, resonance, hotspot pressure, skeptic pressure, and explainer lineage metrics.

Keep / cut / defer: Keep the new payload deterministic and artifact-local; defer richer UI rendering until the demo presentation surface is selected.

## 2026-05-20: Fallback Versus Native Comparison Artifacts

Decision: Add a comparison exporter that runs every synthetic scenario through both fallback and Frontier_OS substrates and writes JSON plus Markdown artifacts.

Reason: The demo needs measured Phase I evidence showing how the native manifold path changes alert timing, risk/confidence values, status, metrics, and five-role evidence completeness.

Files affected: `frontiergrid_observant/eval/`, `scripts/export_demo_artifacts.py`, tests, docs.

Proposal impact: The build can now support a baseline-versus-native feasibility claim with replayable artifacts instead of only showing native alert cards in isolation.

Keep / cut / defer: Keep the comparison artifact deterministic and scenario-local; defer richer charts or UI cards until the presentation surface is selected.

## 2026-05-20: Static Demo Dashboard

Decision: Generate a self-contained `artifacts/demo/index.html` dashboard from the comparison metrics and alert-card artifacts.

Reason: The demo needs a presentation-ready surface that shows baseline/native comparison, alert status, and role evidence without requiring a web server or external services.

Files affected: `frontiergrid_observant/demo/dashboard.py`, `scripts/export_demo_artifacts.py`, tests, docs.

Proposal impact: The current build can be reviewed as a local static app and later deployed as a private static site after data-rights and native-runtime availability decisions.

Keep / cut / defer: Keep the app self-contained and artifact-driven; defer Render deployment until the private deployment path and Frontier_OS runtime availability are selected.

## 2026-05-26: Final Submission Audit & PDF Compilation Fixes

Decision: Audit and finalize the Phase I proposal package, update the `compile_submission_pdf.py` script to enforce repeating headers across all pages of Volume 2 and Volume 5, compile a separate Fundamental Research Disclosure PDF, and place all documents in the final final draft folder.

Reason: To satisfy strict BAA layout instructions (repeating headers containing SBC name, topic, and proposal number `N26BZ-NV023-0825` on all pages of Volume 2) and Navy submission requirements (separate Fundamental Research Disclosure PDF upload in Volume 5 for the DFARS 252.204-7000 waiver).

Files affected: `frontiergrid_observant/scripts/compile_submission_pdf.py`, `docs/submission/Techman Studios Fundamental Research Phase I Disclosure.pdf`, `finalDraft/` and `finalFinalDraft/` folders.

Proposal impact: Enforces 100% compliance with BAA guidelines, ensuring the package is safe from administrative rejections. The proposal has been successfully submitted and accepted on the DSIP portal.

Keep / cut / defer: Keep the repository private (recommended) to safeguard PII, cost proposal details, and ITAR-restricted technical descriptions.

