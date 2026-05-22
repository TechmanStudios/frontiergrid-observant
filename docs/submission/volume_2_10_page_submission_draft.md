# Volume 2 Technical Proposal: FrontierGrid-Observant

Topic: DON26BZ01-NV023 Observant-AI  
Offeror: Techman Studios  
Status: 10-page-ready working source; verify all final formatting, page limits, markings, and placeholders in DSIP before submission.

## 1. Identification And Significance Of The Problem Or Opportunity

Naval ISRT operations increasingly depend on fragmented, time-sensitive observations from maritime tracks, air and space assets, cyber and network telemetry, logistics reports, weather context, operator notes, and autonomous systems. The difficult cases are not merely high-volume data problems. They occur when evidence is incomplete, contradictory, delayed, degraded, or intentionally deceptive. In those conditions, conventional centralized risk analysis can become brittle: rules fire late or on partial evidence, score-only outputs obscure uncertainty, and analysts may receive alerts without a traceable account of how cross-domain evidence was fused.

DON26BZ01-NV023 calls for Observant-AI: risk-aware regenerative AI-based multimodal visual-tactical monitoring, understanding, alerting, and assistance. The topic envisions distributed mission-focused AI agents that self-organize, share insights through ad hoc networking, form mission-oriented collaborative teams, process multidomain anomalous events, and provide natural-language explanations and risk escalation controls. It also asks Phase I performers to determine feasibility using compelling challenge problems, relevant datasets, end-to-end performance assessment, and metrics including sensitivity, specificity, precision, miss rate, false discovery rate, false omission rate, analytic completeness, uniqueness, validity, consistency, and accuracy under noisy data.

Techman Studios proposes FrontierGrid-Observant, an unclassified Phase I feasibility testbed for multi-agent contextual fusion and risk-aware alerting under noisy cross-domain conditions. The effort adapts prior SOL, Frontier_OS, and Exciton-MoA research into a controlled Observant-AI prototype that uses synthetic and approved public-style data only during Phase I. The Phase I objective is not to deliver an operational command-and-control system. The objective is to determine whether a shared contextual state-space and role-specialized agents can improve event fusion, uncertainty handling, alert prioritization, and replayable explanation where conventional risk pipelines tend to lose context.

## 2. Technical Objectives

FrontierGrid-Observant treats the Observant-AI team requirement as a substrate problem, not only a workflow problem. Rather than scripting a fixed chain of agents or routing every observation through one central scorer, the prototype represents events, entities, sources, and candidate hypotheses inside a shared contextual state-space. Mission-focused agents then read and write role-specific evidence against that shared state. A watcher detects anomaly pressure, an integrator evaluates cross-domain coherence, a risk officer evaluates severity and escalation posture, a skeptic tests benign alternatives and data-quality limits, an explainer preserves provenance, and a coordinator consolidates the alert package.

The Phase I technical objectives are to:

1. Define at least three Navy-relevant cross-domain challenge problems involving ambiguous shadowing, degraded communications, decoy behavior, coordinated ambiguity, sudden unknown-unknown injections, and conflicting data quality.
2. Build an unclassified common event schema for track, text, network, weather, logistics, sensor metadata, and contextual reports.
3. Implement deterministic fallback and experimental Frontier_OS / Exciton-MoA native reasoning substrates behind the same adapter contract.
4. Implement mission-focused agent roles for anomaly detection, integration, risk review, skepticism, explanation, and coordination.
5. Generate alert cards with severity, confidence, data quality, supporting event IDs, review status, role-specific evidence, and replay traces.
6. Evaluate rule-only, centralized sequential-agent, fallback shared-context, and native shared-context behavior using the topic metrics plus context-geodesic alignment, active-domain coverage, contribution balance, candidate-team completeness, and uncertainty pressure.
7. Produce an end-to-end initial prototype, T&E results, demonstration artifacts, Phase II plan, and final report material.

A key technical concept is context-geodesic ordering and alignment: candidate evidence chains are ranked by coherent paths through mission context, time, entity relationships, source reliability, and cross-domain support, while incoherent or weakly aligned paths increase skeptic pressure and may route the alert to human review. In software, this is implemented as federated domain-local summaries for Sea, Space, Air, Land, and Cyber-style inputs feeding a mission-level aggregate alignment score exported on alert cards and role traces.

## 3. Phase I Statement Of Work

### Base Period: Six Months

Task 1: Requirements and challenge scenario definition. Techman Studios will refine at least three unclassified Phase I challenge problems, with current candidates including cross-domain maritime shadowing, littoral hazard escalation, degraded communications with decoy behavior, coordinated ambiguity where no single domain is decisive alone, and an unknown-unknown injection that introduces a novel weak-signal disturbance into the continuous state-space stream. Output: CONOPS-style scenario brief and evaluation assumptions.

Task 2: Architecture and interface design. Techman Studios will define the event normalization, context graph, provenance store, reasoning substrate adapter, agent roles, risk engine, explanation generator, metrics harness, and demo artifacts. The adapter will keep deterministic fallback behavior available while allowing controlled experiments with Frontier_OS / Exciton-MoA local manifold components. Output: system architecture document and adapter contract.

Task 3: Synthetic data and event schema. Techman Studios will build synthetic, unclassified event streams and JSON schemas for the challenge problems. Data types will include track-style movement, maritime and littoral context, space and overhead-style metadata, air/weather/ISR context, network/degraded communications indicators, logistics/context notes, and text-report events. Output: synthetic datasets, schema documentation, and validation tests.

Task 4: Prototype multi-agent contextual fusion harness. Techman Studios will implement the initial prototype harness. Lightweight roles will evaluate events from different mission perspectives: watcher for anomaly pressure, integrator for cross-source coherence, risk officer for severity and escalation, skeptic for benign alternatives and data-quality pressure, explainer for source-grounded narrative, and coordinator for final status handling. The harness will maintain federated domain-manifold summaries and test whether mission-level context-geodesic ordering improves agent teaming by prioritizing evidence paths and agent roles aligned with the emerging mission context. Output: initial deterministic and adapter-backed prototype.

Task 5: Risk scoring and explanation replay. Techman Studios will implement alert cards and replay traces. Each alert will include risk type, severity, confidence, data quality, source-grounded supporting events, status, role-separated evidence, and uncertainty controls. The skeptic and data-quality controls will route moderate-risk cases to human review when confidence, source reliability, or data quality is insufficient. Output: alert-card artifacts, replay traces, and escalation-control logic.

Task 6: Testing and evaluation. Techman Studios will run repeatable evaluations across the challenge problems. Metrics will include sensitivity, specificity, precision, miss rate, false discovery rate, false omission rate, analytic completeness, uniqueness, validity, consistency, and accuracy under noisy data. The evaluation will also track context-geodesic alignment, active-domain coverage, contribution balance, candidate-team completeness, and uncertainty pressure. Output: T&E report comparing rule-only, centralized sequential, fallback shared-context, and native shared-context behavior.

Task 7: Final report and Phase II plan. Techman Studios will document the prototype, tests, findings, limitations, and transition path. Output: final report material, demo artifacts, data-rights assertions, and Phase II roadmap.

### Option Period: Six Months

Task 8: Expanded scenarios and data-quality stress testing. If the Phase I Option is exercised, Techman Studios will expand the synthetic scenario set and run additional Monte Carlo-style variations involving delayed reports, conflicting sources, deceptive signatures, sparse observations, and sudden unknown-unknown injections. Output: expanded robustness report and updated metric tables.

Task 9: Frontier_OS / Exciton-MoA adapter experiment. Techman Studios will mature the native substrate experiment behind the established adapter boundary, focusing on event-embedding calibration, early anomaly sensitivity, false-discovery control, context-geodesic alignment signals, and richer manifold telemetry for the agent roles. Output: safe-mode adapter prototype and comparison artifacts.

Task 10: Transition and interface planning. Techman Studios will define Phase II interface requirements, data-governance assumptions, cybersecurity/export-control considerations, and transition-risk-reduction steps for future integration with approved ISR processing, maritime tactical command-and-control, or human-AI teaming evaluation environments. Output: interface requirements and Phase II transition package.

## 4. Related Work And Technical Advancement

FrontierGrid-Observant builds on three Techman Studios research directions. SOL contributes a semantic/contextual design layer for meaning-centric graphs, support and contradiction relations, memory, and agent role patterns. Frontier_OS contributes the system boundary for agentic computation and adapter-first runtime integration. Exciton-MoA contributes experimental manifold components: blank manifold core, statistical transduction, contextual operators, telemetry scanning, hotspot detection, and replay concepts. In this proposal these concepts are translated into defense-facing engineering language: distributed contextual state-space, specialized contextual inference operators, contextual coherence signals, alert consolidation, and replayable audit traces.

The technical differentiator is manifold-native agentic computation for distributed collaboration. Conventional ISRT exploitation architectures commonly serialize observations through rule stacks, centralized fusion services, or sequential prompt chains. Those approaches can work when the operating picture is clean, but they can become fragile when evidence arrives out of order, communications degrade, a decoy partially matches a threat pattern, or multiple domains provide conflicting signals. FrontierGrid-Observant investigates whether a shared contextual state-space can act as the coordination surface for an Observant-AI team. Each agent maintains a mission role, but the shared substrate supplies the ordering signal: what evidence is near or far in context, what evidence coheres across domains, what evidence contradicts the dominant hypothesis, and what gaps should lower confidence.

Current local artifacts show the architecture is feasible enough to evaluate. The prototype runs five synthetic cross-domain scenarios end to end, compares fallback and native Frontier_OS substrates, exports role-separated evidence, runs four-mode ablation studies, runs randomized stress studies, exports a scenario evidence summary, and generates a static dashboard from repeatable artifacts. The current frozen baseline is a 25-run synthetic Monte Carlo-style sweep across five scenarios and four evaluation modes, for 500 total samples.

| Mode | Detection | Precision | Sensitivity | Miss rate | FDR | Analytic completeness | Evidence complete |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Rule-only | 60% | 0.570 | 0.586 | 0.414 | 0.030 | 0.203 | 0% |
| Centralized sequential | 88% | 0.880 | 0.825 | 0.175 | 0.000 | 0.798 | 0% |
| Fallback shared context | 100% | 1.000 | 1.000 | 0.000 | 0.000 | 0.995 | 100% |
| Native manifold shared context | 100% | 1.000 | 1.000 | 0.000 | 0.000 | 0.995 | 100% |

In the unknown-unknown injection scenario, rule-only missed the weak novelty stream, centralized sequential detected only 40% of runs at average first tick 21.400 and 0% complete role evidence, while both shared-context modes detected 100% of runs at average first tick 13.000 with complete role evidence. These results are synthetic feasibility and calibration evidence, not operational performance claims. They support the thesis that a shared contextual state-space can preserve uncertainty, role evidence, and cross-domain alignment where brittle centralized risk scoring tends to lose context.

The same architecture supports future ad hoc networking. A Phase II distributed implementation could allow edge nodes or platform-local agents to exchange compact contextual traces, role evidence, and alignment scores rather than continuously moving all raw data to a central processor. During degraded connectivity, each node could continue local contextual interpretation, then merge replayable traces and alignment evidence when links recover. Phase I will not claim operational network integration; it will test the core feasibility question in software.

## 5. Relationship With Future Research Or Research And Development

Phase I will produce an initial prototype and evidence base for a Phase II proof-of-concept. Phase II would harden the runtime, expand approved multimodal data feeds, improve scenario generation, perform larger Monte Carlo Red/Blue action-reaction studies, refine interface requirements, and test operationally relevant criteria such as prioritized sensor alerts, prioritized threat escalation, measured severity of events, and measured analytic completeness. Phase II work may require classified environment planning, export-control review, and facility/personnel security planning depending on Government direction.

The Phase I Base establishes feasibility. The Phase I Option bridges toward Phase II by expanding robustness testing, calibrating the native shared-context substrate, and defining interface requirements for future integration. The Phase II goal would be a proof-of-concept prototype with measured improvements over baselines, transition-ready design documentation, and a plan for Phase III integration into maritime tactical command-and-control, ISR processing, or human-AI teaming evaluation environments.

## 6. Commercialization Strategy

The defense commercialization path includes ISR processing support tools, maritime tactical command-and-control decision-support evaluation, human-AI teaming T&E harnesses, edge AI reasoning testbeds, and source-grounded alert-prioritization components. The near-term customer path is to use Phase I results to engage Navy stakeholders around T&E evidence, interface requirements, and Phase II prototype fit.

Dual-use commercial applications include maritime logistics anomaly detection, critical infrastructure monitoring, emergency response situational awareness, enterprise risk intelligence, and source-grounded operations dashboards. These markets face similar problems: distributed signals, uncertain sources, delayed reporting, incomplete event chains, and a need for explainable escalation rather than black-box scoring.

FrontierGrid-Observant differentiates from prompt-only multi-agent demos by keeping deterministic evaluation, provenance, data-quality scoring, and baseline comparison at the center of the architecture. Optional LLM or advanced model components can be added later, but the Phase I testbed is designed to remain measurable, replayable, and safe to run on synthetic unclassified data.

## 7. Key Personnel

[Insert Techman Studios key personnel, roles, relevant AI/software/systems/cybersecurity experience, and percentage of effort.]

Candidate role mapping: Principal Investigator for technical direction, Navy topic alignment, architecture, and final report; Lead Software Engineer for event schema, prototype runtime, metrics harness, and demo artifacts; AI/Simulation Lead for scenario generation, manifold calibration, evaluation design, and baseline comparison; Security/Compliance Lead for CMMC Level 2 (Self) planning, export-control handling, data-rights assertions, and unclassified data controls.

## 8. Foreign Citizens

[State whether any foreign citizens will perform work. If none, state that no foreign citizens are proposed for Phase I work. If any are proposed, list country of origin, visa/work authorization, tasks, and access limitations consistent with the solicitation.]

## 9. Facilities / Equipment

Techman Studios will perform Phase I work using company-controlled software development workstations and private repositories configured for unclassified synthetic-data research. Phase I will not require classified data, Government Furnished Equipment, live operational feeds, or hardware procurement beyond normal software development resources unless later directed by the Government. The prototype will use synthetic datasets and approved public-style data only after compliance review.

## 10. Subcontractors / Consultants

[State whether subcontractors or consultants are proposed. If none, state none. If any are proposed, identify organization, role, period of performance, and work share. Ensure the proposing small business performs at least two-thirds of the work in both the Base and Option.]

## 11. Prior, Current, Or Pending Support Of Similar Proposals Or Awards

[Insert required disclosure. Identify any prior, current, or pending support related to SOL, Frontier_OS, Exciton-MoA, FrontierGrid-Observant, Observant-AI, multimodal fusion, risk-aware AI, or similar work. If none, state none.]

## 12. Identification And Assertion Of Restrictions On Government Use, Release, Or Disclosure Of Technical Data Or Computer Software

Techman Studios anticipates asserting restrictions on pre-existing technical data and computer software related to SOL semantic/contextual architecture concepts, Frontier_OS / Exciton-MoA adapter design, manifold operator mapping, synthetic scenario generation methodology, risk scoring and escalation-control implementation, replay/provenance/explanation templates, and baseline comparison harnesses. SBIR-developed technical data and software will be marked according to the applicable solicitation and contract clauses.

Candidate assertion table for counsel review:

| Technical data or software | Basis for assertion | Asserted rights category | Responsible party |
| --- | --- | --- | --- |
| SOL-derived semantic/context graph concepts | Developed at private expense before award | [TBD] | Techman Studios |
| Frontier_OS / Exciton-MoA adapter mapping | Mixed pre-existing/private and proposed SBIR development | [TBD] | Techman Studios |
| Synthetic scenario generator methodology | Proposed SBIR development with pre-existing design ideas | [TBD] | Techman Studios |
| Risk scoring and escalation controls | Proposed SBIR development | [TBD] | Techman Studios |
| Replay/provenance/explanation templates | Proposed SBIR development | [TBD] | Techman Studios |

All final markings, legends, and assertions should be reviewed before submission. The proposal and all attachments should remain unclassified and should not include CUI, sensitive operational data, real mission data, credentials, or proprietary third-party material.