# Synthetic Scenarios

Generated scenario JSONL files are gitignored by default. Recreate them with:

```powershell
python -m scripts.create_synthetic_data --all
```

Built-in cross-domain scenarios:

- `scenario_01_maritime_shadowing.jsonl`
- `scenario_02_littoral_hazard.jsonl`
- `scenario_03_degraded_comms_decoy.jsonl`
- `scenario_04_cross_domain_ambiguity.jsonl`
- `scenario_05_unknown_unknown_injection.jsonl`

Each generated scenario remains synthetic, repeatable, and unclassified. Anomaly evidence rotates across Sea, Space, Air, Land, and Cyber style domains so the mission-level aggregate alignment layer is exercised by default. Scenario 05 injects a synthetic novelty disturbance into the state-space stream and then emits weak cross-domain echoes for unknown-unknown evaluation.
