# Evidence Run Manifest: 25-Run Monte Carlo Baseline

Status: frozen reviewer-support baseline  
Created: 2026-05-21  
Repository: `frontiergrid-observant`  
Artifact root: `artifacts/demo`

This manifest records the current synthetic Monte Carlo evidence package for proposal drafting. Treat the artifacts below as the current baseline unless a later run is intentionally promoted with a new manifest. The evidence is unclassified synthetic Phase I feasibility evidence. It should be used for calibration, architecture justification, and reviewer-facing feasibility claims, not for operational performance claims.

## Run Settings

| Field | Value |
| --- | --- |
| Study | `observant_randomized_stress_study` |
| Seed | `149` |
| Runs | `25` |
| Seed stride | `100` |
| Final seed | `2549` |
| Ticks per scenario | `30` |
| Scenarios | `scenario_01` through `scenario_05` |
| Modes | `rule_only`, `centralized_sequential`, `fallback_shared_context`, `native_manifold_shared_context` |
| Samples | `500` total; `125` per mode |
| Native node count | `FRONTIER_OS_NODE_COUNT=128` |
| Progress artifact | `artifacts/demo/monte_carlo_progress.json` |
| Dashboard | `artifacts/demo/index.html` |

Command used for the completed run:

```powershell
$env:PYTHONPATH='G:\aiDoW\DON\DON26BZ01-NVO23\frontiergrid-observant'
$env:FRONTIERGRID_ARTIFACT_ROOT='G:\aiDoW\DON\DON26BZ01-NVO23\frontiergrid-observant\artifacts\demo'
$env:FRONTIER_OS_NODE_COUNT='128'
python -m frontiergrid_observant.eval.stress_study --seed 149 --runs 25 --ticks 30 --refresh-dashboard
python -m frontiergrid_observant.eval.evidence_summary
python -m frontiergrid_observant.demo.dashboard
```

## Frozen Evidence Summary

| Mode | Samples | Detection | Avg first tick | Precision | Sensitivity | Miss rate | FDR | Analytic completeness | Evidence complete |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Rule-only | 125 | 60% | 12.280 | 0.570 | 0.586 | 0.414 | 0.030 | 0.203 | 0% |
| Centralized sequential | 125 | 88% | 13.318 | 0.880 | 0.825 | 0.175 | 0.000 | 0.798 | 0% |
| Fallback shared context | 125 | 100% | 12.600 | 1.000 | 1.000 | 0.000 | 0.000 | 0.995 | 100% |
| Native manifold shared context | 125 | 100% | 12.600 | 1.000 | 1.000 | 0.000 | 0.000 | 0.995 | 100% |

## Unknown-Unknown Check

Scenario 05 is the strongest proof thread in this run. The event stream injects weak novelty cues into the continuous state-space engine. Those cues are below local rule thresholds but cohere across Sea, Space, Air, Land, and Cyber-style domains.

| Mode | Detection | Avg first tick | Evidence complete | Interpretation |
| --- | ---: | ---: | ---: | --- |
| Rule-only | 0% | n/a | 0% | Missed weak novelty stream. |
| Centralized sequential | 40% | 21.400 | 0% | Late partial detection without complete role evidence. |
| Fallback shared context | 100% | 13.000 | 100% | Detected through shared context. |
| Native manifold shared context | 100% | 13.000 | 100% | Detected through shared context. |

## Artifact Hashes

SHA256 hashes captured after the completed sweep and dashboard refresh:

| Artifact | SHA256 |
| --- | --- |
| `artifacts/demo/stress_study_metrics.json` | `4716DD9D32390AC02C30D8872B080773D290F0EE94D7E8F06D33068C0A1391E0` |
| `artifacts/demo/stress_study_report.md` | `4B099C8C0EE599939FC67E8057FFEB55D4E493D7036A23A3420B1E420483E56D` |
| `artifacts/demo/scenario_evidence_summary.json` | `49C23AA711F714A353CCEAF55960D5E0CBD1D253302F5B3DFFDC9F71C294AA85` |
| `artifacts/demo/scenario_evidence_summary.md` | `8964230D6E92D4FB127221CD7DDC6EBE983AA59787DCE655075A260FBC191CF7` |
| `artifacts/demo/monte_carlo_progress.json` | `3BA297A4E2FCEFAE6ABE084A91171C365EC430401D9D45BEB63F7FA733C7AD1F` |
| `artifacts/demo/index.html` | `75F541A3132770558C92DAB1E93AA5F6D0AF1B265E9567835E69D876643E83E2` |

Note: if any artifact is regenerated, recalculate hashes and either update this manifest deliberately or create a new dated manifest.

## Proposal Guardrail

Use language such as: "In a 25-run synthetic Monte Carlo-style stress sweep across five unclassified cross-domain scenarios, the shared-context modes achieved complete role evidence and 100% synthetic-scenario detection, while the rule-only and centralized sequential baselines exhibited misses or incomplete role evidence. These results support Phase I feasibility and calibration planning; they do not constitute operational performance claims."