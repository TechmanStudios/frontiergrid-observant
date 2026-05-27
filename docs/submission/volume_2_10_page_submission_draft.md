# Volume 2 Technical Proposal: FrontierGrid-Observant

**Topic**: DON26BZ01-NV023 Observant-AI  
**Offeror**: Techman Studios  
**Proposal Title**: Observant-SOL  
**Status**: Restructured to match the Navy Phase I Conventional Topic template.

---

This proposal includes data that must not be disclosed outside the Government and must not be duplicated, used, or disclosed—in whole or in part—for any purpose other than to evaluate this proposal. If, however, a contract is awarded to this proposing SBC as a result of—or in connection with—the submission of this data, the Government has the right to duplicate, use, or disclose the data to the extent provided in the resulting contract. This restriction does not limit the Government's right to use information contained in this data if it is obtained from another source without restriction. The data subject to this restriction are contained in all pages of this volume.

---

## 1.0 Description of Proposed Phase I Technical Effort

Naval ISRT operations increasingly depend on fragmented, time-sensitive observations from maritime tracks, air and space assets, cyber/network telemetry, logistics reports, weather context, operator notes, and autonomous systems. The operational challenge is not simply data volume. The difficult cases arise when evidence is incomplete, contradictory, delayed, degraded, or intentionally deceptive. In those conditions, conventional centralized risk analysis can become brittle: rules fire late, score-only outputs obscure uncertainty, and analysts may receive alerts without a traceable account of how the system fused cross-domain evidence.

DON26BZ01-NV023 calls for Observant-AI: risk-aware regenerative AI-based multimodal visual-tactical monitoring, understanding, alerting, and assistance. The topic envisions distributed mission-focused AI agents that self-organize, share insights through ad hoc networking, form mission-oriented collaborative teams, process multidomain anomalous events, and provide natural-language explanations and risk escalation controls. The topic also asks Phase I performers to determine feasibility using three compelling challenge problems, relevant datasets, end-to-end performance assessment, and metrics including sensitivity, specificity, precision, miss rate, false discovery rate, false omission rate, analytic completeness, uniqueness, validity, consistency, and accuracy under noisy data.

Techman Studios proposes FrontierGrid-Observant, an unclassified Phase I feasibility testbed for multi-agent contextual fusion and risk-aware alerting under noisy cross-domain conditions. The effort adapts prior SOL, Frontier_OS, and Exciton-MoA research into a controlled Observant-AI prototype that uses synthetic and approved public-style data only during Phase I. The goal is not to deliver an operational command-and-control system in Phase I. The goal is to determine whether a shared contextual state-space and role-specialized agents can improve event fusion, uncertainty handling, alert prioritization, and replayable explanation where conventional risk pipelines tend to lose context.

FrontierGrid-Observant treats that agent-team requirement as a substrate problem, not only a workflow problem. Rather than scripting a fixed chain of agents or routing every observation through one central scorer, the proposed testbed represents events, entities, sources, and candidate hypotheses inside a shared contextual state-space. Mission-focused agents then read and write role-specific evidence against that shared state. A watcher detects anomaly pressure, an integrator evaluates cross-domain coherence, a risk officer evaluates severity and escalation posture, a skeptic tests benign alternatives and data-quality limits, an explainer preserves provenance, and a coordinator consolidates the alert package. Team formation is therefore driven by measured contextual alignment, contradiction, uncertainty, and hotspot pressure rather than by static task routing alone.

## 1.1 Phase I Technical Objectives

The Phase I objectives are to:

1. Define at least three Navy-relevant cross-domain challenge problems involving littoral operations, navigation risk, ambiguous shadowing, degraded communications, decoy behavior, coordinated ambiguity, sudden unknown-unknown injections, and conflicting data quality.
2. Build an unclassified common event schema for track, text, network, weather, logistics, sensor metadata, and contextual reports.
3. Implement a deterministic fallback reasoning substrate and an experimental Frontier_OS / Exciton-MoA native substrate behind the same adapter contract.
4. Implement mission-focused agent roles: watcher, integrator, risk officer, skeptic, explainer, and coordinator.
5. Generate alert cards that include severity, confidence, data quality, supporting event IDs, review status, role-specific evidence, and replayable traces.
6. Evaluate the prototype against rule-only, centralized sequential-agent, fallback shared-context, and native shared-context baselines using the topic's classification and explanation-quality metrics plus federated alignment metrics.
7. Produce an end-to-end initial prototype, T&E results, demonstration artifacts, Phase II plan, and final report material.

The central technical question is whether Sol-derived manifold dynamics can provide a better substrate for adaptive self-organizing interpretation than a single centralized scoring pipeline. In this proposal, the internal term "manifold dynamics" is treated as a distributed contextual state-space: events are projected into shared contextual coordinates, local coherence and hotspot pressure are measured, and specialized agents use those signals to form risk, uncertainty, and explanation evidence. A key Phase I concept is context-geodesic ordering and alignment: candidate evidence chains are ranked by the most coherent path through mission context, time, entity relationships, source reliability, and cross-domain support, while incoherent or weakly aligned paths increase skeptic pressure and may route the alert to human review. The current software design implements this as federated domain-local summaries for Sea, Space, Air, Land, and Cyber-style inputs feeding a mission-level aggregate alignment score exported on alert cards and role traces.

## 1.2 Phase I (Base and Option) Statement of Work

### Base Period (Months 1–6)

*   **Task 1: Requirements and Challenge Scenario Definition (Month 1).** Techman Studios will refine at least three unclassified Phase I challenge problems: cross-domain maritime shadowing with ambiguous intent, cross-domain littoral hazard escalation, and cross-domain degraded communications with decoy behavior, along with coordinated cross-domain ambiguity where no single domain is decisive alone, and a sudden unknown-unknown event injection. Each scenario will define entities, event streams, expected anomaly intervals, data-quality conditions, and ground-truth labels for evaluation. Deliverable: Scenario brief and evaluation assumptions.
*   **Task 2: Architecture and Interface Design (Month 2).** Techman Studios will define the FrontierGrid-Observant architecture, including event normalization, context graph, provenance store, reasoning substrate adapter, agent roles, risk engine, explanation generator, metrics harness, and demo artifacts. The adapter will keep deterministic fallback behavior available while allowing controlled experiments with Frontier_OS / Exciton-MoA local manifold components. Deliverable: System architecture document and adapter contract.
*   **Task 3: Synthetic Data and Event Schema (Months 2–3).** Techman Studios will build synthetic, unclassified event streams and JSON schemas for the challenge problems. Data types will include track-style movement, maritime/littoral context, space/overhead-style metadata, air/weather/ISR context, network/degraded communications indicators, logistics/context notes, and text-report events. The schema will include source reliability, data quality, location/time, entity IDs, event type, attributes, and provenance fields. Deliverable: Synthetic datasets, schema documentation, and validation tests.
*   **Task 4: Prototype Multi-Agent Contextual Fusion Harness (Months 3–4).** Techman Studios will implement the initial prototype harness. The fallback substrate will provide deterministic event fusion and risk evaluation. The native experimental substrate will broadcast event embeddings through a local Frontier_OS / Exciton-MoA manifold runtime, collect contextual coherence and hotspot telemetry, and expose those metrics through the same Observant-AI adapter boundary. Lightweight roles will evaluate events from different mission-relevant perspectives: watcher for anomaly pressure, integrator for cross-source coherence, risk officer for severity and escalation, skeptic for benign alternatives and data-quality pressure, explainer for source-grounded narrative, and coordinator for final status handling. The harness will maintain federated domain-manifold summaries for Sea, Space, Air, Land, and Cyber style inputs, then test whether mission-level context-geodesic ordering improves agent teaming by prioritizing the evidence paths and agent roles most aligned with the emerging mission context. Deliverable: Initial deterministic and adapter-backed prototype.
*   **Task 5: Risk Scoring and Explanation Replay (Months 4–5).** Techman Studios will implement alert cards and replay traces. Each alert will include risk type, severity, confidence, data quality, source-grounded supporting events, status, and role-separated evidence. The skeptic and data-quality controls will route moderate-risk cases to human review when confidence, source reliability, or data quality is insufficient. Deliverable: Alert-card artifacts, replay traces, and escalation-control logic.
*   **Task 6: Testing and Evaluation (Months 5–6).** Techman Studios will run repeatable evaluations across the cross-domain challenge problems. Metrics will include sensitivity, specificity, precision, miss rate, false discovery rate, false omission rate, analytic completeness, uniqueness, validity, consistency, and accuracy under noisy data. The evaluation will also track context-geodesic alignment, active-domain coverage, domain contribution balance, candidate-team completeness, and uncertainty pressure. The evaluation will compare rule-only, centralized sequential-agent, fallback shared-context, and native shared-context behavior where feasible. Deliverable: T&E report with metric tables, scenario assumptions, limitations, and recommended Phase II improvements.
*   **Task 7: Final Report and Phase II Plan (Month 6).** Techman Studios will document the prototype, tests, findings, limitations, and transition path. Deliverable: Final report material, demo artifacts, data-rights assertions, and Phase II roadmap.

### Option Period (Months 7–12)

*   **Task 8: Expanded Scenarios and Data-Quality Stress Testing (Months 7–8).** If the Phase I Option is exercised, Techman Studios will expand the synthetic scenario set and run additional Monte Carlo-style variations involving delayed reports, conflicting sources, deceptive signatures, sparse observations, and sudden unknown-unknown event injections. Deliverable: Expanded robustness report and updated metric tables.
*   **Task 9: Frontier_OS / Exciton-MoA Adapter Experiment (Months 9–10).** Techman Studios will mature the native substrate experiment behind the established adapter boundary. Work will focus on calibrating event embeddings, improving early anomaly sensitivity, preserving low false-discovery behavior, refining context-geodesic alignment signals, and exporting richer manifold telemetry for the watcher, integrator, risk officer, skeptic, and explainer roles. Deliverable: Safe-mode adapter prototype and comparison artifacts.
*   **Task 10: Transition and Interface Planning (Months 11–12).** Techman Studios will define Phase II interface requirements, data-governance assumptions, cybersecurity/export-control considerations, and transition-risk-reduction steps for future integration with approved ISR processing, maritime tactical command-and-control, or human-AI teaming evaluation environments. Deliverable: Interface requirements and Phase II transition package.

## 1.3 Related Work

FrontierGrid-Observant builds on three Techman Studios research directions. SOL contributes a semantic/contextual design layer for meaning-centric graphs, support and contradiction relations, memory, and agent role patterns. Frontier_OS contributes the system boundary for agentic computation and adapter-first runtime integration. Exciton-MoA contributes experimental manifold components: a blank manifold core, statistical transduction, contextual operators, telemetry scanning, hotspot detection, and replay concepts. In this proposal these concepts are translated into defense-facing engineering language: distributed contextual state-space, specialized contextual inference operators, contextual coherence signals, alert consolidation, and replayable audit traces.

The key technical differentiator is manifold-native agentic computation for distributed collaboration. Conventional ISRT exploitation architectures commonly serialize observations through rule stacks, centralized fusion services, or sequential prompt chains. Those approaches can work when the operating picture is clean, but they can become fragile when evidence arrives out of order, when communications degrade, when a decoy partially matches a threat pattern, or when multiple domains provide conflicting signals. FrontierGrid-Observant instead investigates whether a shared contextual state-space can act as the coordination surface for an Observant-AI team. Each agent maintains a mission role, but the shared substrate supplies the ordering signal: what evidence is near or far in context, what evidence coheres across domains, what evidence contradicts the dominant hypothesis, and what gaps should lower confidence.

This is where context-geodesic ordering and alignment become valuable to the Volume 2 technical argument. In reviewer-facing terms, the system attempts to order candidate interpretations by the shortest coherent path through the current mission context rather than by a single threshold, keyword match, or isolated model confidence. A vessel-track deviation, a degraded communications burst, a weather shift, a logistics note, and an operator text report may be weak or ambiguous in isolation; on the shared state-space, they can either align into an emerging hotspot or remain separated by contradiction, poor source quality, or temporal mismatch. The resulting alignment signal can activate the appropriate collaborative team, preserve dissenting role evidence, and make alert consolidation more transparent. The current software design implements this as federated domain-local summaries feeding a mission-level aggregate alignment score that is exported on alert cards and replayable role traces.

Current local artifacts show the architecture is feasible enough to evaluate. The prototype runs five synthetic cross-domain scenarios end to end, compares fallback and native Frontier_OS substrates, exports role-separated evidence, runs four-mode ablation studies, runs randomized stress studies, exports a scenario evidence summary, and generates a static dashboard from repeatable artifacts. The current frozen baseline is a 25-run synthetic Monte Carlo-style sweep across five scenarios and four evaluation modes, for 500 total samples.

| Mode | Detection | Precision | Sensitivity | Miss rate | FDR | Analytic completeness | Evidence complete |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Rule-only | 60% | 0.570 | 0.586 | 0.414 | 0.030 | 0.203 | 0% |
| Centralized sequential | 88% | 0.880 | 0.825 | 0.175 | 0.000 | 0.798 | 0% |
| Fallback shared context | 100% | 1.000 | 1.000 | 0.000 | 0.000 | 0.995 | 100% |
| Native manifold shared context | 100% | 1.000 | 1.000 | 0.000 | 0.000 | 0.995 | 100% |

In the unknown-unknown injection scenario, rule-only missed the weak novelty stream, centralized sequential detected only 40% of runs at average first tick 21.400 and 0% complete role evidence, while both shared-context modes detected 100% of runs at average first tick 13.000 with complete role evidence. These results are synthetic feasibility and calibration evidence, not operational performance claims. They support the thesis that a shared contextual state-space can preserve uncertainty, role evidence, and cross-domain alignment where brittle centralized risk scoring tends to lose context.

## 2.0 Key Personnel

Techman Studios proposes a highly qualified, single-investigator approach to execute the FrontierGrid-Observant project:

*   **Bryan Tucker (Principal Investigator & Lead Systems Engineer)**: 100% effort (Base & Option). Mr. Tucker is the Founder and Lead AI Systems Engineer at Techman Studios. He is a US Army National Guard combat veteran (served in Operation Iraqi Freedom, awarded the Combat Infantryman Badge and Army Meritorious Service Medal). He has extensive experience in systems engineering, AI agent pipeline design, and knowledge engineering. At Techman Studios, he leads the architecting and deployment of multi-agent cognitive systems, specializing in vector database retrieval-augmented generation (RAG) pipelines, context grounding, and LLM integrations. His technical background includes systems engineering, IT support (Honda Manufacturing of Alabama), and technology studies at Jacksonville State University. As the sole key person and system architect, Mr. Tucker will dedicate 100% of his project labor to cover all technical, AI/simulation development, and security/compliance roles for both the Base and Option periods. (Full disclosures of US citizenship are included in Volume 5.)

## 3.0 Commercialization/Transition Plan Summary

### Defense Handoff & Customer Handoff Strategy
The primary defense commercialization path involves:
1. **Naval ISRT & C2 Integration:** Engaging Navy stakeholders (specifically ONR, NAVSEA, and NAVAIR) around T&E evidence, interface requirements, and Phase II prototype fit. The testbed's output (alert cards, replay traces) is designed to integrate into future maritime tactical command-and-control.
2. **Human-AI Teaming Evaluation Environments:** Providing the prototype's metrics harness and explanation traces as a standardized testbed for measuring analyst trust, decision latencies, and escalation control behaviors.

### Dual-Use Commercial Markets
Commercial applications include:
1. **Maritime Logistics Anomaly Detection:** Tracking vessel route-parallel behaviors, delays, and port metadata for supply chain security.
2. **Critical Infrastructure & Utility Monitoring:** Integrating SCADA, weather, text-based logs, and sensor alerts to prevent false alarms and provide explainable risk escalation.
3. **Enterprise Operations & Risk Intelligence:** Fusing all-source market intelligence, network status, and operational metrics into source-grounded dashboards.

### Phase II & Phase III Roadmap
The Phase I Base period establishes feasibility by measuring context-weighted reasoning against baselines. The Phase I Option period bridges toward Phase II by:
1. Conducting expanded Monte Carlo data-quality stress tests (Task 8).
2. Calibrating the native Frontier_OS manifold adapter for low-latency anomaly tracking (Task 9).
3. Defining interface requirements, data-governance models, and cybersecurity/export-control controls for Phase II transition targets (Task 10).

Phase II would focus on building a hardened proof-of-concept prototype running on approved military data, with TRL advancement and a plan for Phase III transition into a Program of Record (POR) or civilian security systems.

## Facilities/Equipment

Techman Studios will perform Phase I work using company-controlled software development workstations and private repositories configured for secure, unclassified synthetic-data research. Phase I will not require classified data, Government Furnished Equipment, live operational feeds, or hardware procurement beyond normal software development resources. The workstations are equipped with modern GPUs suitable for local LLM inference testing, data generation, and running the 1,024-node pristine hyperbolic lattice.

All company facilities where the proposed work will be performed meet applicable environmental laws and regulations of Federal, state, and local Governments. Specifically, operations involve only standard custom software development and do not produce airborne emissions, waterborne effluents, solid/bulk waste, or require the handling/storage of toxic or hazardous materials.

## 5.0 Letters of Support

None proposed or required for the Phase I feasibility effort.