from modules.nifty_option_risk_evidence import (
    evaluate_risk_evidence,
)


def build_opportunity_strength():
    return {
        "Status": "EVALUATED",
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
    }


def test_valid_risk_evidence():
    result = evaluate_risk_evidence(
        build_opportunity_strength()
    )

    assert result["Status"] == "EVALUATED"
    assert result["Option Direction"] == "UP"
    assert result["Momentum Confirmation"] == "CONFIRMED"
    assert result["Market Context"] == "MOVING_TOGETHER"
    assert result["Momentum Context"] == "SUPPORTED"
    assert result["Opportunity Classification"] == (
        "SUPPORTED_OPPORTUNITY"
    )
    assert result["Opportunity Strength"] == "STRONG"
    assert result["Momentum Risk Evidence"] == "CONFIRMED"
    assert result["Market Context Risk Evidence"] == (
        "MOVING_TOGETHER"
    )
    assert result["Opportunity Strength Risk Evidence"] == "STRONG"


def test_invalid_input():
    result = evaluate_risk_evidence(None)

    assert result["Status"] == "REJECTED"


def test_invalid_status():
    result = evaluate_risk_evidence({
        "Status": "INVALID",
    })

    assert result["Status"] == "REJECTED"


def test_missing_field():
    data = build_opportunity_strength()
    del data["Opportunity Strength"]

    result = evaluate_risk_evidence(data)

    assert result["Status"] == "REJECTED"


if __name__ == "__main__":
    test_valid_risk_evidence()
    test_invalid_input()
    test_invalid_status()
    test_missing_field()

    print("V12.9 Stage 1 Risk Evidence: PASS")