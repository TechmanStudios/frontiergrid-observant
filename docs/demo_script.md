# Demo Script

## One-Command Demo

```powershell
python -m scripts.export_demo_artifacts
python -m frontiergrid_observant.eval.compare_substrates --seed 149 --ticks 30
python -m frontiergrid_observant.eval.ablation_study --seed 149 --ticks 30
python -m frontiergrid_observant.eval.stress_study --seed 149 --runs 3 --ticks 30
python -m frontiergrid_observant.demo.dashboard
python -m frontiergrid_observant.demo.run_demo --scenario scenario_01 --substrate fallback --seed 149 --ticks 30 --export
python -m frontiergrid_observant.demo.run_demo --scenario scenario_01 --substrate frontier_os --seed 149 --ticks 30 --export
```

## Narrative

1. Start from a clean synthetic scenario.
2. Show the event stream begins as normal background activity.
3. Add an ambiguous anomaly pattern.
4. Show agent signals disagree or remain cautious early.
5. As evidence accumulates, the shared context strengthens the alert candidate.
6. The risk officer raises a review alert.
7. The skeptic lowers confidence when data quality or benign alternatives are present.
8. Alert cards export side-by-side watcher, integrator, risk officer, skeptic, and explainer evidence.
9. The explainer exports who, what, where, when, why, supporting evidence, and replay trace.
10. The comparison report shows fallback versus native Frontier_OS alert timing, metrics, status, and evidence completeness.
11. The ablation report compares rule-only, centralized sequential, fallback shared-context, and native manifold shared-context modes.
12. The randomized stress report repeats the four-mode comparison across multiple seeds.
13. The scenario evidence summary rolls repeated stress records into reviewer-facing scenario/mode tables, including the unknown-unknown check.
14. The static dashboard renders alert cards, fallback/native comparison, ablation evidence, and stress evidence for presentation.
15. The metrics runner compares results to scenario ground truth.

## Expected Exports

```text
artifacts/demo/scenario_01_alerts.json
artifacts/demo/scenario_01_context.json
artifacts/demo/scenario_01_replay.md
artifacts/demo/scenario_01_metrics.json
artifacts/demo/fallback_vs_frontier_os_metrics.json
artifacts/demo/fallback_vs_frontier_os_report.md
artifacts/demo/ablation_study_metrics.json
artifacts/demo/ablation_study_report.md
artifacts/demo/stress_study_metrics.json
artifacts/demo/stress_study_report.md
artifacts/demo/monte_carlo_progress.json
artifacts/demo/scenario_evidence_summary.json
artifacts/demo/scenario_evidence_summary.md
artifacts/demo/index.html
artifacts/demo/frontiergrid_observant_demo_report.md
```

## Static Demo App

`artifacts/demo/index.html` is self-contained and can be opened directly in a browser. For a private Render static site, publish `artifacts/demo` after running the export command in the build step and keep final release/data-rights review in the loop.

## Manifold Evaluation

```powershell
python -m frontiergrid_observant.eval.run_eval --all --substrate frontier_os
```

## Ablation Evaluation

```powershell
python -m frontiergrid_observant.eval.ablation_study --seed 149 --ticks 30
```

The current ablation artifact is proposal-support evidence, not an operational-performance claim. It shows the shared-context modes preserving five-role evidence and improving analytic-completeness scoring while holding false discovery at zero in the built-in synthetic runs; the rule-only baseline can alert earlier in some scenarios but produces partial evidence and false discovery.

## Randomized Stress Evaluation

```powershell
python -m frontiergrid_observant.eval.stress_study --seed 149 --runs 25 --ticks 30 --refresh-dashboard
python -m frontiergrid_observant.eval.evidence_summary
```

The current stress artifact repeats the four-mode ablation across multiple seeds and all five cross-domain scenarios. During long runs, `monte_carlo_progress.json` is updated at run boundaries and the static dashboard can be refreshed to show the latest completed run. `scenario_evidence_summary.md` is the proposal-facing rollup: it reports detection rate, alert timing, precision, sensitivity, miss rate, false discovery rate, analytic completeness, alignment, domain coverage, and role-evidence completeness by scenario and mode. Treat this as feasibility trend evidence only.
