# FrontierGrid-Observant Agent Instructions

You are working on FrontierGrid-Observant, an unclassified Phase I feasibility testbed for DON26BZ01-NV023 Observant-AI.

Core constraints:

- Use only unclassified synthetic data, public mock data, or sanitized OSINT-style data approved for this repo.
- Do not ingest, generate, or ask for classified information, CUI, real operational data, sensitive military data, credentials, or restricted third-party datasets.
- Avoid operational targeting, weapon employment, or tactical maneuver recommendations. Use review-oriented terms: risk alert, confidence score, analyst review recommended, contextual explanation, possible anomaly cluster, and data-quality warning.
- Treat the topic as ITAR/EAR-sensitive for planning. Do not make public-release assumptions without review.
- Keep claims Phase I-feasibility oriented. Do not present the prototype as an operational defense system.

Technical direction:

- Preserve deterministic fallback capability. LLM calls and external APIs must remain optional.
- Keep Frontier_OS / Exciton-MoA interaction behind `frontiergrid_observant.runtime.frontier_os_adapter` and `frontiergrid_observant.runtime.manifold_bridge` where practical so the demo remains stable.
- The user owns the Techman Studios source repos and has authorized local, ephemeral integration of Frontier_OS, SOL, and Exciton-MoA for this build. Do not let internal license labels block prototype integration inside this workspace.
- Keep public release, proposal submission, and third-party distribution language conservative until Techman Studios chooses the final licensing/data-rights posture.
- Use defense-facing engineering language. Translate internal terms such as resonance, threshold burst, and hippocampal replay into contextual coherence, alert event, and replayable audit trail in proposal-facing docs.
- Update requirement mappings, compliance notes, and tests when changing behavior.

Useful local references:

- `../FrontierGrid-Observant_Planning_Build_Guide.md`
- `../topic_DON26BZ01-NV023_Risk-Aware Regenerative AI-based Multimodal Visual-Tactical (ISRT) (Observant-AI) – Monitor, Understand, Alert, and Assist.PDF`
- `../NAVY_26.BZ_PH I_R1_v4.pdf`
- `../DoW 2026 SBIR BAA Preface_04132026.pdf`
- `../Frontier_OS-main/Frontier_OS-main/`
- `../sol-main/sol-main/`
