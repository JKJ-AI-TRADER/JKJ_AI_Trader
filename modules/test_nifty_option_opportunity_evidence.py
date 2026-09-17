from modules.nifty_option_opportunity_evidence import (
    evaluate_opportunity_evidence,
)


def test_valid_momentum_context():
    momentum_context = {
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
        "Volume Evidence": True,
        "OI Evidence": True,
        "NIFTY Movement Evidence": "UP",
    }

    result = evaluate_opportunity_evidence(momentum_context)

    assert result["Status"] == "EVALUATED"
    assert result["Option Direction"] == "UP"
    assert result["Momentum Confirmation"] == "CONFIRMED"
    assert result["Market Context"] == "MOVING_TOGETHER"
    assert result["Momentum Context"] == "SUPPORTED"
    assert result["Price Movement Evidence"] is True
    assert result["Volume Evidence"] is True
    assert result["Open Interest Evidence"] is True
    assert result["NIFTY Movement Evidence"] == "UP"


def test_invalid_input():
    result = evaluate_opportunity_evidence(None)

    assert result["Status"] == "REJECTED"


def test_invalid_status():
    momentum_context = {
        "Status": "INVALID",
    }

    result = evaluate_opportunity_evidence(momentum_context)

    assert result["Status"] == "REJECTED"


if __name__ == "__main__":
    test_valid_momentum_context()
    test_invalid_input()
    test_invalid_status()

    print("V12.8 Stage 1 Opportunity Evidence: PASS")