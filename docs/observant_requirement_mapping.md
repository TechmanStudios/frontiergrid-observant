# Observant-AI Requirement Mapping

| Solicitation need | FrontierGrid-Observant response | Initial artifact |
| --- | --- | --- |
| Distributed mission-focused AI agents | Deterministic role agents over shared context state | `frontiergrid_observant/agents/` |
| Self-organizing insight sharing | Context graph, substrate traces, federated domain summaries, and live manifold metrics | `frontiergrid_observant/runtime/federated_alignment.py`, `frontiergrid_observant/runtime/manifold_bridge.py` |
| Multimodal anomalous events | Common event schema for track, text, weather, logistics, network, and metadata events | `frontiergrid_observant/schemas/events.py` |
| Cross-domain contextual modeling | Entity timelines, event linkage, support and contradiction queries | `frontiergrid_observant/context/context_graph.py` |
| Mission-level aggregate alignment | Context-geodesic ordering across domain-local states | `frontiergrid_observant/runtime/federated_alignment.py` |
| Real-time visual-tactical understanding | Console demo with alert timeline and exported artifacts | `frontiergrid_observant/demo/run_demo.py` |
| Risk assessment and risk reduction | Severity, confidence, data quality, and review status | `frontiergrid_observant/risk/risk_engine.py` |
| AI-risk escalation control | Skeptic discount, data-quality warnings, and human-review statuses | `frontiergrid_observant/agents/skeptic.py` |
| Natural-language explanations | Source-grounded replay trace and explanation strings | `frontiergrid_observant/explain/` |
| Testing and evaluation | Classification and explanation metrics runnable against fallback or Frontier_OS substrates | `frontiergrid_observant/eval/run_eval.py` |
| Phase I deliverables | Prototype, T&E, demo, Phase II plan, final report support | `docs/submission/` |

## Topic Metrics To Track

- Sensitivity / true-positive rate.
- Specificity / true-negative rate.
- Precision / positive predictive value.
- Miss rate / false-negative rate.
- False discovery rate.
- False omission rate.
- Analytic completeness.
- Uniqueness.
- Validity.
- Consistency.
- Accuracy under noisy data.
