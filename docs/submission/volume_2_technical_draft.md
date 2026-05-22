# Volume 2 Technical Proposal Draft

Working draft for the DON Phase I Technical Proposal. This must be compressed into a compliant 10-page, single-column Volume 2 before submission. Bracketed items are placeholders to fill with company-specific facts.

## Suggested Page Budget

| Section | Target length |
| --- | ---: |
| 1. Problem / opportunity | 0.75 page |
| 2. Technical objectives | 0.75 page |
| 3. Phase I statement of work | 3.0 pages |
| 4. Related work and technical advancement | 1.25 pages |
| 5. Future R&D / Phase II relationship | 0.75 page |
| 6. Commercialization strategy | 0.75 page |
| 7-12. Personnel, facilities, support, data rights | 1.75 pages |
| Reserve for figure/table | 1.0 page |

## 1. Identification And Significance Of The Problem Or Opportunity

Naval ISRT operations increasingly depend on fragmented, time-sensitive observations from maritime tracks, air and space assets, cyber/network telemetry, logistics reports, weather context, operator notes, and autonomous systems. The operational challenge is not simply data volume. The difficult cases arise when evidence is incomplete, contradictory, delayed, degraded, or intentionally deceptive. In those conditions, conventional centralized risk analysis can become brittle: rules fire late, score-only outputs obscure uncertainty, and analysts may receive alerts without a traceable account of how the system fused cross-domain evidence.

DON26BZ01-NV023 calls for Observant-AI: risk-aware regenerative AI-based multimodal visual-tactical monitoring, understanding, alerting, and assistance. The topic envisions distributed mission-focused AI agents that self-organize, share insights through ad hoc networking, form mission-oriented collaborative teams, process multidomain anomalous events, and provide natural-language explanations and risk escalation controls. The topic also asks Phase I performers to determine feasibility using three compelling challenge problems, relevant datasets, end-to-end performance assessment, and metrics including sensitivity, specificity, precision, miss rate, false discovery rate, false omission rate, analytic completeness, uniqueness, validity, consistency, and accuracy under noisy data.

FrontierGrid-Observant treats that agent-team requirement as a substrate problem, not only a workflow problem. Rather than scripting a fixed chain of agents or routing every observation through one central scorer, the proposed testbed represents events, entities, sources, and candidate hypotheses inside a shared contextual state-space. Mission-focused agents then read and write role-specific evidence against that shared state. A watcher detects anomaly pressure, an integrator evaluates cross-domain coherence, a risk officer evaluates severity and escalation posture, a skeptic tests benign alternatives and data-quality limits, an explainer preserves provenance, and a coordinator consolidates the alert package. Team formation is therefore driven by measured contextual alignment, contradiction, uncertainty, and hotspot pressure rather than by static task routing alone.

Techman Studios proposes FrontierGrid-Observant, an unclassified Phase I feasibility testbed for multi-agent contextual fusion and risk-aware alerting under noisy cross-domain conditions. The effort adapts prior SOL, Frontier_OS, and Exciton-MoA research into a controlled Observant-AI prototype that uses synthetic and approved public-style data only during Phase I. The goal is not to deliver an operational command-and-control system in Phase I. The goal is to determine whether a shared contextual state-space and role-specialized agents can improve event fusion, uncertainty handling, alert prioritization, and replayable explanation where conventional risk pipelines tend to lose context.

## 2. Phase I Technical Objectives

The Phase I objectives are:

1. Define at least three Navy-relevant cross-domain challenge problems involving littoral operations, navigation risk, ambiguous shadowing, degraded communications, decoy behavior, coordinated ambiguity, sudden unknown-unknown injections, and conflicting data quality.
2. Build an unclassified common event schema for track, text, network, weather, logistics, sensor metadata, and contextual reports.
3. Implement a deterministic fallback reasoning substrate and an experimental Frontier_OS / Exciton-MoA native substrate behind the same adapter contract.
4. Implement mission-focused agent roles: watcher, integrator, risk officer, skeptic, explainer, and coordinator.
5. Generate alert cards that include severity, confidence, data quality, supporting event IDs, review status, role-specific evidence, and replayable traces.
6. Evaluate the prototype against rule-only, centralized sequential-agent, fallback shared-context, and native shared-context baselines using the topic's classification and explanation-quality metrics plus federated alignment metrics.
7. Produce an end-to-end initial prototype, T&E results, demonstration artifacts, Phase II plan, and final report material.

The central technical question is whether Sol-derived manifold dynamics can provide a better substrate for adaptive self-organizing interpretation than a single centralized scoring pipeline. In this proposal, the internal term "manifold dynamics" is treated as a distributed contextual state-space: events are projected into shared contextual coordinates, local coherence and hotspot pressure are measured, and specialized agents use those signals to form risk, uncertainty, and explanation evidence. A key Phase I concept is context-geodesic ordering and alignment: candidate evidence chains are ranked by the most coherent path through mission context, time, entity relationships, source reliability, and cross-domain support, while incoherent or weakly aligned paths increase skeptic pressure and may route the alert to human review.

## 3. Phase I Statement Of Work

### Base Period: Six Months

**Task 1: Requirements and challenge scenario definition.** Techman Studios will refine at least three unclassified Phase I challenge problems: cross-domain maritime shadowing with ambiguous intent, cross-domain littoral hazard escalation, cross-domain degraded communications with decoy behavior, an optional coordinated ambiguity case where no single domain is decisive alone, and an optional unknown-unknown injection case that introduces a novel weak-signal disturbance into the continuous state-space stream. Each scenario will define entities, event streams, expected anomaly intervals, data-quality conditions, and ground-truth labels for evaluation. The task will produce a CONOPS-style scenario brief and evaluation assumptions.

**Task 2: Architecture and interface design.** Techman Studios will define the FrontierGrid-Observant architecture, including event normalization, context graph, provenance store, reasoning substrate adapter, agent roles, risk engine, explanation generator, metrics harness, and demo artifacts. The adapter will keep deterministic fallback behavior available while allowing controlled experiments with Frontier_OS / Exciton-MoA local manifold components. The task will produce a system architecture document and adapter contract.

**Task 3: Synthetic data and event schema.** Techman Studios will build synthetic, unclassified event streams and JSON schemas for the cross-domain challenge problems. Data types will include track-style movement, maritime/littoral context, space/overhead-style metadata, air/weather/ISR context, network/degraded communications indicators, logistics/context notes, and text-report events. The schema will include source reliability, data quality, location/time, entity IDs, event type, attributes, and provenance fields. The task will produce synthetic datasets, schema documentation, and validation tests.

**Task 4: Prototype multi-agent contextual fusion harness.** Techman Studios will implement the initial prototype harness. The fallback substrate will provide deterministic event fusion and risk evaluation. The native experimental substrate will broadcast event embeddings through a local Frontier_OS / Exciton-MoA manifold runtime, collect contextual coherence and hotspot telemetry, and expose those metrics through the same Observant-AI adapter boundary. Lightweight roles will evaluate events from different mission-relevant perspectives: watcher for anomaly pressure, integrator for cross-source coherence, risk officer for severity and escalation, skeptic for benign alternatives and data-quality pressure, explainer for source-grounded narrative, and coordinator for final status handling. The harness will maintain federated domain-manifold summaries for Sea, Space, Air, Land, and Cyber style inputs, then test whether mission-level context-geodesic ordering improves agent teaming by prioritizing the evidence paths and agent roles most aligned with the emerging mission context.

**Task 5: Risk scoring and explanation replay.** Techman Studios will implement alert cards and replay traces. Each alert will include risk type, severity, confidence, data quality, source-grounded supporting events, status, and role-separated evidence. The skeptic and data-quality controls will route moderate-risk cases to human review when confidence, source reliability, or data quality is insufficient. The task will produce alert-card artifacts, replay traces, and escalation-control logic.

**Task 6: Testing and evaluation.** Techman Studios will run repeatable evaluations across the cross-domain challenge problems. Metrics will include sensitivity, specificity, precision, miss rate, false discovery rate, false omission rate, analytic completeness, uniqueness, validity, consistency, and accuracy under noisy data. The evaluation will also track context-geodesic alignment, active-domain coverage, domain contribution balance, candidate-team completeness, and uncertainty pressure. The evaluation will compare rule-only, centralized sequential-agent, fallback shared-context, and native shared-context behavior where feasible. The task will produce a T&E report with metric tables, scenario assumptions, limitations, and recommended Phase II improvements.

**Task 7: Final report and Phase II plan.** Techman Studios will document the prototype, tests, findings, limitations, and transition path. The final report material will include architecture, scenario definitions, T&E results, demo artifacts, data-rights assertions, and a Phase II plan for hardened prototype development, expanded approved datasets, interface requirements, and transition engagement.

### Option Period: Six Months

**Task 8: Expanded scenarios and data-quality stress testing.** If the Phase I Option is exercised, Techman Studios will expand the synthetic scenario set and run additional Monte Carlo-style variations involving delayed reports, conflicting sources, deceptive signatures, sparse observations, and sudden unknown-unknown event injections. The task will produce an expanded robustness report and updated metric tables.

**Task 9: Frontier_OS / Exciton-MoA adapter experiment.** Techman Studios will mature the native substrate experiment behind the established adapter boundary. Work will focus on calibrating event embeddings, improving early anomaly sensitivity, preserving low false-discovery behavior, refining context-geodesic alignment signals, and exporting richer manifold telemetry for the watcher, integrator, risk officer, skeptic, and explainer roles. The task will produce comparison artifacts and an assessment of whether native shared-context dynamics justify Phase II hardening.

**Task 10: Transition and interface planning.** Techman Studios will define Phase II interface requirements, data-governance assumptions, cybersecurity/export-control considerations, and transition-risk-reduction steps for future integration with approved ISR processing, maritime tactical command-and-control, or human-AI teaming evaluation environments. The task will produce an interface requirements package and Phase II transition plan.

## 4. Related Work And Technical Advancement

FrontierGrid-Observant builds on three Techman Studios research directions. SOL contributes a semantic/contextual design layer for meaning-centric graphs, support and contradiction relations, memory, and agent role patterns. Frontier_OS contributes the system boundary for agentic computation and adapter-first runtime integration. Exciton-MoA contributes experimental manifold components: a blank manifold core, statistical transduction, contextual operators, telemetry scanning, hotspot detection, and replay concepts. In this proposal these concepts are translated into defense-facing engineering language: distributed contextual state-space, specialized contextual inference operators, contextual coherence signals, alert consolidation, and replayable audit traces.

The key technical differentiator is manifold-native agentic computation for distributed collaboration. Conventional ISRT exploitation architectures commonly serialize observations through rule stacks, centralized fusion services, or sequential prompt chains. Those approaches can work when the operating picture is clean, but they can become fragile when evidence arrives out of order, when communications degrade, when a decoy partially matches a threat pattern, or when multiple domains provide conflicting signals. FrontierGrid-Observant instead investigates whether a shared contextual state-space can act as the coordination surface for an Observant-AI team. Each agent maintains a mission role, but the shared substrate supplies the ordering signal: what evidence is near or far in context, what evidence coheres across domains, what evidence contradicts the dominant hypothesis, and what gaps should lower confidence.

This is where context-geodesic ordering and alignment become valuable to the Volume 2 technical argument. In reviewer-facing terms, the system attempts to order candidate interpretations by the shortest coherent path through the current mission context rather than by a single threshold, keyword match, or isolated model confidence. A vessel-track deviation, a degraded communications burst, a weather shift, a logistics note, and an operator text report may be weak or ambiguous in isolation; on the shared state-space, they can either align into an emerging hotspot or remain separated by contradiction, poor source quality, or temporal mismatch. The resulting alignment signal can activate the appropriate collaborative team, preserve dissenting role evidence, and make alert consolidation more transparent. The current software design implements this as federated domain-local summaries feeding a mission-level aggregate alignment score that is exported on alert cards and replayable role traces.

The same architecture supports future ad hoc networking. A Phase II distributed implementation could allow edge nodes or platform-local agents to exchange compact contextual traces, role evidence, and alignment scores rather than continuously moving all raw data to a central processor. During degraded connectivity, each node could continue local contextual interpretation, then merge replayable traces and alignment evidence when links recover. Phase I will not claim operational network integration; it will test the core feasibility question in software: whether shared contextual ordering improves fusion, uncertainty control, and explanation quality under noisy cross-domain synthetic scenarios.

The proposed advancement is not a claim that the current prototype is already operational or more accurate across every metric. The defensible Phase I claim is that Sol-derived manifold dynamics may provide a better substrate for Observant-AI-style self-organizing interpretation than brittle centralized risk scoring. Instead of treating multimodal events as a single queue, FrontierGrid-Observant projects events into shared contextual state, lets specialized agents evaluate coherence, anomaly pressure, risk severity, benign alternatives, explanation provenance, and contextual alignment, and exports a reviewable alert package.

Current local artifacts show the architecture is feasible enough to evaluate. The prototype runs five synthetic cross-domain scenarios end to end, compares fallback and native Frontier_OS substrates, exports role-separated evidence, runs four-mode ablation studies, runs randomized stress studies, exports a scenario evidence summary, and generates a static dashboard from repeatable artifacts. The current frozen baseline is a 25-run synthetic Monte Carlo-style sweep across five scenarios and four evaluation modes, for 500 total samples. In that sweep, shared-context modes achieved 100% synthetic-scenario detection, 1.000 precision, 1.000 sensitivity, 0.000 miss rate, 0.000 false discovery rate, 0.995 analytic completeness, and 100% role-evidence completeness. Rule-only and centralized sequential baselines remained useful comparison points but were less complete: rule-only detection was 60% with 0.414 miss rate, while centralized sequential detection was 88% with 0.175 miss rate and 0% complete role evidence. The strongest proof thread is the unknown-unknown injection scenario: rule-only missed the weak novelty stream, centralized sequential detected only 40% of runs and did so late, while both shared-context modes detected 100% of runs at average first tick 13.000 with complete role evidence. These results should be framed as synthetic Phase I feasibility and calibration evidence, not as operational performance claims. They support the thesis that a shared contextual state-space can preserve uncertainty, role evidence, and cross-domain alignment where brittle centralized risk scoring tends to lose context.

The Phase I tests will therefore emphasize controlled measurement rather than unsupported claims. The team will evaluate where the shared contextual substrate improves analytic completeness, validity, consistency, and noisy-data accuracy; where it fails to improve sensitivity or miss rate; and what calibration is required before Phase II prototype hardening.

## 5. Relationship With Future Research Or Research And Development

Phase I will produce an initial prototype and evidence base for a Phase II proof-of-concept. Phase II would harden the runtime, expand approved multimodal data feeds, improve scenario generation, perform larger Monte Carlo Red/Blue action-reaction studies, refine interface requirements, and test operationally relevant criteria such as prioritized sensor alerts, prioritized threat escalation, measured severity of events, and measured analytic completeness. Phase II work may require classified environment planning, export-control review, and facility/personnel security planning depending on Government direction.

The Phase I Base establishes feasibility. The Phase I Option bridges toward Phase II by expanding robustness testing, calibrating the native shared-context substrate, and defining interface requirements for future integration. The Phase II goal would be a proof-of-concept prototype with measured improvements over baselines, transition-ready design documentation, and a plan for Phase III integration into maritime tactical command-and-control, ISR processing, or human-AI teaming evaluation environments.

## 6. Commercialization Strategy

The defense commercialization path includes ISR processing support tools, maritime tactical command-and-control decision-support evaluation, human-AI teaming T&E harnesses, edge AI reasoning testbeds, and source-grounded alert-prioritization components. The near-term customer path is to use Phase I results to engage Navy stakeholders around T&E evidence, interface requirements, and Phase II prototype fit.

Dual-use commercial applications include maritime logistics anomaly detection, critical infrastructure monitoring, emergency response situational awareness, enterprise risk intelligence, and source-grounded operations dashboards. These markets face similar problems: distributed signals, uncertain sources, delayed reporting, incomplete event chains, and a need for explainable escalation rather than black-box scoring.

FrontierGrid-Observant differentiates from prompt-only multi-agent demos by keeping deterministic evaluation, provenance, data-quality scoring, and baseline comparison at the center of the architecture. Optional LLM or advanced model components can be added later, but the Phase I testbed is designed to remain measurable, replayable, and safe to run on synthetic unclassified data.

## 7. Key Personnel

Techman Studios proposes a highly qualified, single-investigator approach to execute the FrontierGrid-Observant project:

- **Bryan Tucker (Principal Investigator & Lead Systems Engineer)**: 100% effort (Base & Option). Mr. Tucker is the Founder and Lead AI Systems Engineer at Techman Studios. He is a US Army National Guard combat veteran (served in Operation Iraqi Freedom, awarded the Combat Infantryman Badge and Army Meritorious Service Medal). He has extensive experience in systems engineering, AI agent pipeline design, and knowledge engineering. At Techman Studios, he leads the architecting and deployment of multi-agent cognitive systems, specializing in vector database retrieval-augmented generation (RAG) pipelines, context grounding, and LLM integrations. His technical background includes systems engineering, IT support (Honda Manufacturing of Alabama), and technology studies at Jacksonville State University. As the sole key person and system architect, Mr. Tucker will dedicate 100% of his project labor to cover all technical, AI/simulation development, and security/compliance roles for both the Base and Option periods.

## 8. Foreign Citizens

No foreign citizens are proposed to perform work on this Phase I project. All proposed personnel are United States citizens.

## 9. Facilities / Equipment

Techman Studios will perform Phase I work using company-controlled software development workstations and private repositories configured for unclassified synthetic-data research. Phase I will not require classified data, Government Furnished Equipment, live operational feeds, or hardware procurement beyond normal software development resources unless later directed by the Government. The prototype will use synthetic datasets and approved public-style data only after compliance review.

## 10. Subcontractors / Consultants

No subcontractors or consultants are proposed for this effort. Techman Studios will perform 100% of the proposed effort in both the Base and Option periods, satisfying the SBIR requirement that the small business perform at least two-thirds of the work.

## 11. Prior, Current, Or Pending Support Of Similar Proposals Or Awards

Techman Studios has no prior, current, or pending support related to SOL, Frontier_OS, Exciton-MoA, FrontierGrid-Observant, or similar work.

## 12. Identification And Assertion Of Restrictions On Government Use, Release, Or Disclosure Of Technical Data Or Computer Software

Techman Studios asserts restrictions on the release, disclosure, or use of pre-existing technical data and computer software developed exclusively at private expense. In accordance with DFARS 252.227-7018, SBIR data rights are asserted for technical data and computer software developed under the SBIR contract.

Candidate assertion table for counsel review:

| Technical data or software | Basis for assertion | Asserted rights category | Responsible party |
| --- | --- | --- | --- |
| SOL-derived semantic/context graph concepts | Developed exclusively at private expense before award | Limited Rights (Technical Data) / Restricted Rights (Computer Software) | Techman Studios |
| Frontier_OS / Exciton-MoA adapter mapping | Developed exclusively at private expense before award | Limited Rights (Technical Data) / Restricted Rights (Computer Software) | Techman Studios |
| Synthetic scenario generator methodology | Proposed SBIR development incorporating pre-existing proprietary concepts | SBIR Data Rights | Techman Studios |
| Risk scoring and escalation controls | Proposed SBIR development | SBIR Data Rights | Techman Studios |
| Replay/provenance/explanation templates | Proposed SBIR development | SBIR Data Rights | Techman Studios |
| Metrics harness and baseline comparison | Proposed SBIR development | SBIR Data Rights | Techman Studios |

All final markings, legends, and assertions should be reviewed before submission. The proposal and all attachments should remain unclassified and should not include CUI, sensitive operational data, real mission data, credentials, or proprietary third-party material.

## Compact Figure Candidate

```text
Synthetic / approved event streams
        -> common event schema + provenance
        -> domain-local contextual summaries
        -> mission aggregate alignment
        -> watcher / integrator / risk officer / skeptic / explainer
        -> alert card + replay trace + metrics
        -> human review and Phase II transition evidence
```

## Current Evidence Table Candidate

| Evidence item | Current status | Proposal use |
| --- | --- | --- |
| Five cross-domain synthetic challenge scenarios | Implemented | Shows Phase I scope, repeatability, multidomain fusion pressure, and unknown-unknown stress behavior. |
| Fallback and native substrate adapters | Implemented | Supports baseline-versus-candidate evaluation. |
| Five-role alert evidence | Implemented | Supports self-organizing agent evidence claim. |
| Federated domain alignment | Implemented | Supports domain-local teaming and mission-level aggregate alignment claim. |
| Scenario evidence summary | Implemented from 25-run sweep | Provides concise reviewer-facing scenario/mode metrics and the unknown-unknown check. |
| Evidence run manifest and claims matrix | Implemented | Freezes the current synthetic baseline and maps claims to measured artifacts. |
| Static dashboard | Implemented | Internal demo support; not required submission artifact. |
| Comparison, ablation, and randomized stress metrics | 25-run synthetic baseline artifacts | Use cautiously; supports feasibility trends, not final superiority. |
| Data-quality and skeptic controls | Implemented | Supports AI-risk escalation-control claim. |