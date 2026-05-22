# Metrics Plan

The Phase I testbed should report both classification metrics and explanation-quality metrics. All metrics are scenario-local until external datasets are approved.

## Classification Metrics

For each evaluated tick or event cluster:

- True positive: anomaly exists and alert is raised.
- False positive: no anomaly exists but alert is raised.
- True negative: no anomaly exists and no alert is raised.
- False negative: anomaly exists and no alert is raised.

Formulas:

```text
sensitivity = TP / (TP + FN)
specificity = TN / (TN + FP)
precision = TP / (TP + FP)
miss_rate = FN / (TP + FN)
false_discovery_rate = FP / (TP + FP)
false_omission_rate = FN / (TN + FN)
```

## Explanation Metrics

- Analytic completeness: explanation synthesizes chain of events, not only the final alert.
- Uniqueness: who, what, why, where, and when are retrievable.
- Validity: major claims cite supporting event IDs.
- Consistency: repeated updates reinforce or correctly revise linkages.
- Accuracy: noisy data does not produce overconfident false conclusions.

## Baselines

Initial comparisons should include:

1. Rule-only threshold baseline.
2. Centralized sequential agent baseline.
3. FrontierGrid-Observant shared-context candidate.
