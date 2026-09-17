from modules.nifty_option_risk_classification import (
    classify_risk_context,
    evaluate_risk_classification,
)


def build_risk_evidence(
    momentum_context,
    confirmation,
    opportunity_strength,
    opportunity_classification,
):
    return {
        "Status": "EVALUATED",
        "Trading Symbol": "NIFTY2692223300CE",
        "Underlying": "NIFTY",
        "Expiry": "2026-09-22",
        "Strike": 23300,
        "Option Type": "CE",
        "Option Direction": "UP",
        "Momentum Confirmation": confirmation,
        "Market Context": "MOVING_TOGETHER",
        "Movement Relationship": "MOVING_TOGETHER",
        "Momentum Context": momentum_context,
        "Opportunity Classification": opportunity_classification,
        "Opportunity Strength": opportunity_strength,
    }


def test_lower_risk_context():
    result = evaluate_risk_classification(
        build_risk_evidence(
            "SUPPORTED",
            "CONFIRMED",
            "STRONG",
            "SUPPORTED_OPPORTUNITY",
        )
    )

    assert result["Status"] == "CLASSIFIED"
    assert result["Risk Classification"] == "LOWER_RISK_CONTEXT"


def test_moderate_risk_context():
    result = evaluate_risk_classification(
        build_risk_evidence(
            "SUPPORTED",
            "PARTIALLY_CONFIRMED",
            "DEVELOPING",
            "SUPPORTED_OPPORTUNITY",
        )
    )

    assert result["Status"] == "CLASSIFIED"
    assert result["Risk Classification"] == "MODERATE_RISK_CONTEXT"


def test_higher_risk_context():
    result = evaluate_risk_classification(
        build_risk_evidence(
            "CONTEXT_CONFLICT",
            "CONFIRMED",
            "WEAK",
            "CONTEXT_CONFLICT",
        )
    )

    assert result["Status"] == "CLASSIFIED"
    assert result["Risk Classification"] == "HIGHER_RISK_CONTEXT"


def test_mixed_opportunity():
    result = evaluate_risk_classification(
        build_risk_evidence(
            "MIXED_CONTEXT",
            "PARTIALLY_CONFIRMED",
            "DEVELOPING",
            "MIXED_OPPORTUNITY",
        )
    )

    assert result["Status"] == "CLASSIFIED"
    assert result["Risk Classification"] == "MODERATE_RISK_CONTEXT"


def test_no_clear_opportunity():
    result = evaluate_risk_classification(
        build_risk_evidence(
            "MIXED_CONTEXT",
            "NOT_CONFIRMED",
            "WEAK",
            "NO_CLEAR_OPPORTUNITY",
        )
    )

    assert result["Status"] == "CLASSIFIED"
    assert result["Risk Classification"] == "HIGHER_RISK_CONTEXT"


def test_invalid_input():
    result = evaluate_risk_classification(None)

    assert result["Status"] == "REJECTED"


def test_invalid_evidence():
    result = evaluate_risk_classification({
        "Status": "INVALID",
    })

    assert result["Status"] == "REJECTED"


def test_undefined_combination():
    result = classify_risk_context(
        "SUPPORTED",
        "CONFIRMED",
        "WEAK",
        "SUPPORTED_OPPORTUNITY",
    )

    assert result == "UNDEFINED_RISK"


if __name__ == "__main__":
    test_lower_risk_context()
    test_moderate_risk_context()
    test_higher_risk_context()
    test_mixed_opportunity()
    test_no_clear_opportunity()
    test_invalid_input()
    test_invalid_evidence()
    test_undefined_combination()

    print("V12.9 Stage 2 Risk Classification: PASS")