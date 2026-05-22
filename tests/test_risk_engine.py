from frontiergrid_observant.risk.risk_engine import (
    ConfidenceInputs,
    RiskInputs,
    score_confidence,
    score_risk,
    status_for,
)


def test_risk_score_is_bounded() -> None:
    score = score_risk(
        RiskInputs(
            anomaly_score=0.8,
            evidence_alignment=0.7,
            persistence=0.6,
            proximity_or_route_relevance=0.5,
            source_reliability=0.9,
            cross_modal_support=0.4,
        )
    )

    assert 0 <= score <= 1


def test_confidence_uses_skeptic_discount() -> None:
    high = score_confidence(
        ConfidenceInputs(
            data_quality=0.8,
            source_reliability=0.8,
            agent_agreement=0.8,
            temporal_consistency=0.8,
            replay_completeness=0.8,
            benign_alternative_score=0.0,
        )
    )
    discounted = score_confidence(
        ConfidenceInputs(
            data_quality=0.8,
            source_reliability=0.8,
            agent_agreement=0.8,
            temporal_consistency=0.8,
            replay_completeness=0.8,
            benign_alternative_score=0.7,
        )
    )

    assert discounted < high


def test_status_for_human_review_threshold() -> None:
    assert status_for(0.8, 0.75) == "human_escalation_review"


def test_status_for_routes_degraded_data_to_human_review() -> None:
    assert (
        status_for(
            0.5,
            0.35,
            data_quality=0.48,
            source_reliability=0.58,
            benign_alternative_score=0.2,
        )
        == "human_escalation_review"
    )


def test_status_for_routes_strong_skeptic_pressure_to_human_review() -> None:
    assert (
        status_for(
            0.52,
            0.4,
            data_quality=0.8,
            source_reliability=0.8,
            benign_alternative_score=0.6,
        )
        == "human_escalation_review"
    )
