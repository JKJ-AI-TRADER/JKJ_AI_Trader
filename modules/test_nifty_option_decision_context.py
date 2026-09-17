from modules.nifty_option_decision_context import (
    evaluate_decision_context,
)


def build_trade_quality():
    return {
        "Status": "CLASSIFIED",
        "Trading Symbol": "NIFTY2692223300CE",
        "Underlying": "NIFTY",
        "Expiry": "2026-09-22",
        "Strike": 23300,
        "Option Type": "CE",

        "Option Direction": "UP",
        "Momentum Confirmation": "CONFIRMED",
        "Market Context": "MOVING_TOGETHER",
        "Movement Relationship": "MOVING_TOGETHER",
        "Momentum Context": "SUPPORTED",

        "Opportunity Classification": "SUPPORTED_OPPORTUNITY",
        "Opportunity Strength": "STRONG",

        "Risk Classification": "LOWER_RISK_CONTEXT",
        "Trade Quality": "HIGH_QUALITY_CONTEXT",
    }


def test_decision_context():
    result = evaluate_decision_context(
        build_trade_quality()
    )

    assert result["Status"] == "EVALUATED"
    assert result["Option Direction"] == "UP"
    assert result["Momentum Confirmation"] == "CONFIRMED"
    assert result["Opportunity Classification"] == (
        "SUPPORTED_OPPORTUNITY"
    )
    assert result["Opportunity Strength"] == "STRONG"
    assert result["Risk Classification"] == (
        "LOWER_RISK_CONTEXT"
    )
    assert result["Trade Quality"] == "HIGH_QUALITY_CONTEXT"


def test_invalid_input():
    result = evaluate_decision_context(None)

    assert result["Status"] == "REJECTED"


def test_invalid_trade_quality():
    result = evaluate_decision_context({
        "Status": "INVALID",
    })

    assert result["Status"] == "REJECTED"


def test_missing_field():
    trade_quality = build_trade_quality()
    del trade_quality["Trade Quality"]

    result = evaluate_decision_context(trade_quality)

    assert result["Status"] == "REJECTED"


if __name__ == "__main__":
    test_decision_context()
    test_invalid_input()
    test_invalid_trade_quality()
    test_missing_field()

    print("V13.1 Decision Context: PASS")