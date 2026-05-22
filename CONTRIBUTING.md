# Contributing

FrontierGrid-Observant is a private Phase I proposal prototype scaffold. Keep changes small, testable, and tied to a proposal requirement, demo artifact, or compliance need.

## Working Style

- Keep Phase I work unclassified and synthetic-data only.
- Prefer deterministic behavior before optional LLM, external API, or Frontier_OS integration.
- Preserve the adapter boundary around Frontier_OS / Exciton-MoA.
- Add or update tests for schema, metrics, risk scoring, and artifact export changes.
- Update `docs/observant_requirement_mapping.md` when implementing a feature that satisfies a topic requirement.

## Local Checks

```powershell
python -m pip install -e ".[dev]"
pytest
ruff check .
```

## Sensitive Information

Do not commit classified information, CUI, export-controlled technical data from third parties, credentials, real operational data, sensitive locations, or unsanitized OSINT datasets.
