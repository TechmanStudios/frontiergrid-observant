# Evidence Claims Matrix

This matrix converts the current 25-run synthetic evidence package into proposal-safe claims. It is intended to guide Volume 2 language, figures, and reviewer-facing summaries without overstating maturity.

## Current Baseline

| Item | Value |
| --- | --- |
| Evidence package | 25-run Monte Carlo-style synthetic stress sweep |
| Samples | 500 total; 125 per mode |
| Scenarios | Five cross-domain scenarios, including coordinated ambiguity and unknown-unknown injection |
| Baselines | Rule-only and centralized sequential |
| Candidate modes | Fallback shared context and native manifold shared context |
| Guardrail | Synthetic, unclassified Phase I feasibility evidence only |

## Claims Matrix

| Proposal claim | Evidence anchor | Reviewer-facing phrasing | Guardrail |
| --- | --- | --- | --- |
| Shared contextual state-space improves cross-domain stress response relative to brittle event-local rules. | Shared-context modes reached 100% detection across 125 samples per mode, versus 60% for rule-only and 88% for centralized sequential. Shared-context miss rate was 0.000 versus 0.414 for rule-only and 0.175 for centralized sequential. | "The testbed provides a measurable feasibility path for distributed contextual fusion: under the current synthetic stress sweep, shared-context modes eliminated synthetic misses observed in the rule-only and centralized baselines." | Do not claim operational detection performance or real-world accuracy. |
| Role-specialized agents preserve auditability and explanation completeness. | Evidence completeness was 100% for fallback and native shared-context modes, and 0% for rule-only and centralized sequential modes. Analytic completeness was 0.995 for shared-context modes versus 0.203 rule-only and 0.798 centralized sequential. | "The architecture produces replayable role-separated evidence for watcher, integrator, risk officer, skeptic, explainer, and coordinator review rather than only a scalar score." | Role evidence is prototype evidence, not a certified analytic workflow. |
| Federated domain manifolds provide a measurable design basis for mission-level aggregate alignment. | Shared-context active-domain coverage averaged 0.965. Context-geodesic alignment averaged 0.718 for fallback shared context and 0.496 for native manifold shared context. | "Domain-local contextual summaries feed a mission-level aggregate alignment signal that can be measured, replayed, and calibrated." | Alignment is an internal feasibility metric; do not represent it as a fielded tactical confidence measure. |
| The unknown-unknown scenario supports the need for continuous shared-state interpretation. | Scenario 05: rule-only detection 0%; centralized sequential detection 40% at average first tick 21.400 with 0% evidence completeness; both shared-context modes detection 100% at average first tick 13.000 with 100% evidence completeness. | "When individual novelty cues were weak but cross-domain echoes accumulated, shared-context modes detected the synthetic unknown-unknown case earlier and with complete role evidence." | The scenario is synthetic and should be framed as a feasibility stressor, not proof of open-world anomaly detection. |
| The design can reduce false discovery while preserving sensitivity in the current synthetic suite. | Shared-context precision and sensitivity were both 1.000, miss rate 0.000, and FDR 0.000 across the 25-run stress package. Rule-only FDR was 0.030 with sensitivity 0.586. | "The current artifact demonstrates a calibration target: preserve false-discovery control while improving sensitivity and explanation completeness under noisy cross-domain conditions." | Avoid claiming this tradeoff will hold on real data until Phase I/II evaluation expands. |
| Native Frontier_OS / Exciton-MoA integration is feasible behind the same adapter boundary. | Native manifold shared context matched fallback shared context on detection, precision, sensitivity, miss rate, FDR, and analytic completeness in the 25-run stress package, while exposing native alignment and team-completeness traces. | "The adapter-first architecture allows deterministic fallback and native manifold experiments to be compared under the same event schema, metrics harness, and dashboard artifacts." | Do not claim the native path is fully optimized; calibration remains a Phase I technical risk. |
| Human-review and AI-risk escalation controls remain central to the design. | Alert cards include confidence, data quality, skeptic pressure, role evidence, source IDs, and replay traces. Degraded or ambiguous cases can route to human review. | "The prototype is designed to support trusted human-AI teaming by exposing why an alert was raised, what evidence contradicted it, and when uncertainty should limit automation." | Do not imply autonomous command decisions, targeting, or operational tasking. |

## Compact Volume 2 Insert

In a 25-run synthetic Monte Carlo-style stress sweep across five cross-domain scenarios and four evaluation modes, shared-context modes achieved 100% synthetic-scenario detection, 1.000 precision, 1.000 sensitivity, 0.000 miss rate, 0.000 false discovery rate, 0.995 analytic completeness, and 100% role-evidence completeness. Rule-only and centralized sequential baselines were useful but less complete: rule-only detection was 60% with 0.414 miss rate, while centralized sequential detection was 88% with 0.175 miss rate and 0% complete role evidence. In the unknown-unknown injection scenario, rule-only missed the weak novelty stream, centralized sequential detected only 40% of runs and did so late, while both shared-context modes detected 100% of runs at average first tick 13.000 with complete role evidence. These results support Phase I feasibility and calibration planning only; they do not claim operational performance.

## Recommended Figure Or Table

Use one compact table with these columns: Mode, Detection, Precision, Sensitivity, Miss Rate, FDR, Analytic Completeness, Evidence Complete. Follow it with a one-sentence unknown-unknown callout. This should fit inside Volume 2 better than a dashboard screenshot and will be easier for reviewers to score.