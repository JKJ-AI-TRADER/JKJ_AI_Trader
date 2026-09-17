from modules.nifty_option_trade_quality import (
    classify_trade_quality,
    evaluate_trade_quality,
)


def build_risk_classification(
    momentum_context,
    confirmation,
    opportunity_strength,
    opportunity_classification,
    risk_classification,
):
    return {
        "Status": "CLASSIFIED",
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
        "Risk Classification": risk_classification,
    }


def test_high_quality_context():
    result = evaluate_trade_quality(
        build_risk_classification(
            "SUPPORTED",
            "CONFIRMED",
            "STRONG",
            "SUPPORTED_OPPORTUNITY",
            "LOWER_RISK_CONTEXT",
        )
    )

    assert result["Status"] == "CLASSIFIED"
    assert result["Trade Quality"] == "HIGH_QUALITY_CONTEXT"


def test_developing_quality_context():
    result = evaluate_trade_quality(
        build_risk_classification(
            "SUPPORTED",
            "PARTIALLY_CONFIRMED",
            "DEVELOPING",
            "SUPPORTED_OPPORTUNITY",
            "MODERATE_RISK_CONTEXT",
        )
    )

    assert result["Status"] == "CLASSIFIED"
    assert result["Trade Quality"] == "DEVELOPING_QUALITY_CONTEXT"


def test_mixed_opportunity():
    result = evaluate_trade_quality(
        build_risk_classification(
            "MIXED_CONTEXT",
            "PARTIALLY_CONFIRMED",
            "DEVELOPING",
            "MIXED_OPPORTUNITY",
            "MODERATE_RISK_CONTEXT",
        )
    )

    assert result["Status"] == "CLASSIFIED"
    assert result["Trade Quality"] == "DEVELOPING_QUALITY_CONTEXT"


def test_higher_risk_context():
    result = evaluate_trade_quality(
        build_risk_classification(
            "CONTEXT_CONFLICT",
            "CONFIRMED",
            "WEAK",
            "CONTEXT_CONFLICT",
            "HIGHER_RISK_CONTEXT",
        )
    )

    assert result["Status"] == "CLASSIFIED"
    assert result["Trade Quality"] == "LOW_QUALITY_CONTEXT"


def test_no_clear_opportunity():
    result = evaluate_trade_quality(
        build_risk_classification(
            "MIXED_CONTEXT",
            "NOT_CONFIRMED",
            "WEAK",
            "NO_CLEAR_OPPORTUNITY",
            "HIGHER_RISK_CONTEXT",
        )
    )

    assert result["Status"] == "CLASSIFIED"
    assert result["Trade Quality"] == "LOW_QUALITY_CONTEXT"


def test_invalid_input():
    result = evaluate_trade_quality(None)

    assert result["Status"] == "REJECTED"


def test_invalid_classification():
    result = evaluate_trade_quality({
        "Status": "INVALID",
    })

    assert result["Status"] == "REJECTED"


def test_undefined_combination():
    result = classify_trade_quality(
        "SUPPORTED",
        "CONFIRMED",
        "WEAK",
        "SUPPORTED_OPPORTUNITY",
        "LOWER_RISK_CONTEXT",
    )

    assert result == "UNDEFINED_QUALITY"


if __name__ == "__main__":
    test_high_quality_context()
    test_developing_quality_context()
    test_mixed_opportunity()
    test_higher_risk_context()
    test_no_clear_opportunity()
    test_invalid_input()
    test_invalid_classification()
    test_undefined_combination()

    print("V12.9 Stage 3 Trade Quality: PASS")