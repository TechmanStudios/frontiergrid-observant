"""Evaluation metric schemas and formulas."""

from __future__ import annotations

from pydantic import BaseModel, Field


def _safe_div(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


class ConfusionMatrix(BaseModel):
    true_positive: int = Field(default=0, ge=0)
    false_positive: int = Field(default=0, ge=0)
    true_negative: int = Field(default=0, ge=0)
    false_negative: int = Field(default=0, ge=0)

    def rates(self) -> dict[str, float]:
        tp = self.true_positive
        fp = self.false_positive
        tn = self.true_negative
        fn = self.false_negative
        return {
            "sensitivity": _safe_div(tp, tp + fn),
            "specificity": _safe_div(tn, tn + fp),
            "precision": _safe_div(tp, tp + fp),
            "miss_rate": _safe_div(fn, tp + fn),
            "false_discovery_rate": _safe_div(fp, tp + fp),
            "false_omission_rate": _safe_div(fn, tn + fn),
        }


class MetricReport(BaseModel):
    scenario_id: str
    substrate: str = "fallback"
    confusion: ConfusionMatrix
    analytic_completeness: float = Field(default=0.0, ge=0, le=1)
    uniqueness: float = Field(default=0.0, ge=0, le=1)
    validity: float = Field(default=0.0, ge=0, le=1)
    consistency: float = Field(default=0.0, ge=0, le=1)
    accuracy_under_noise: float = Field(default=0.0, ge=0, le=1)
    context_geodesic_alignment: float = Field(default=0.0, ge=0, le=1)
    active_domain_coverage: float = Field(default=0.0, ge=0, le=1)
    domain_contribution_balance: float = Field(default=0.0, ge=0, le=1)
    candidate_team_completeness: float = Field(default=0.0, ge=0, le=1)
    uncertainty_pressure: float = Field(default=0.0, ge=0, le=1)

    def summary(self) -> dict[str, float | str]:
        return {
            "scenario_id": self.scenario_id,
            "substrate": self.substrate,
            **self.confusion.rates(),
            "analytic_completeness": self.analytic_completeness,
            "uniqueness": self.uniqueness,
            "validity": self.validity,
            "consistency": self.consistency,
            "accuracy_under_noise": self.accuracy_under_noise,
            "context_geodesic_alignment": self.context_geodesic_alignment,
            "active_domain_coverage": self.active_domain_coverage,
            "domain_contribution_balance": self.domain_contribution_balance,
            "candidate_team_completeness": self.candidate_team_completeness,
            "uncertainty_pressure": self.uncertainty_pressure,
        }
