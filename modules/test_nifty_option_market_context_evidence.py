"""
JKJ AI Trader
Test — NIFTY Option Market Context Evidence — V12.7 Stage 1
"""

from modules.nifty_option_market_context_evidence import (
    evaluate_market_context_evidence,
)


def build_confirmation():
    return {
        "Status": "EVALUATED",
        "Trading Symbol": "NIFTYTESTCE",
        "Underlying": "NIFTY",
        "Expiry": "2026-09-22",
        "Strike": 23300,
        "Option Type": "CE",
        "Option Direction": "UP",
        "Persistence Status": "PERSISTENT",
        "Price Movement Evidence": True,
        "NIFTY Movement Evidence": True,
        "Volume Evidence": True,
        "Open Interest Evidence": False,
        "Movement Relationship": "MOVING_TOGETHER",
        "Momentum Confirmation": "CONFIRMED",
    }


def test_valid_context():

    result = evaluate_market_context_evidence(
        build_confirmation()
    )

    assert result["Status"] == "EVALUATED"
    assert result["Option Direction"] == "UP"
    assert result["NIFTY Movement Evidence"] is True
    assert result["Price Movement Evidence"] is True
    assert result["Volume Evidence"] is True
    assert result["Open Interest Evidence"] is False
    assert result["Movement Relationship"] == "MOVING_TOGETHER"
    assert result["Momentum Confirmation"] == "CONFIRMED"


def test_invalid_status():

    confirmation = build_confirmation()
    confirmation["Status"] = "INVALID"

    result = evaluate_market_context_evidence(
        confirmation
    )

    assert result["Status"] == "REJECTED"


def test_missing_field():

    confirmation = build_confirmation()
    del confirmation["Movement Relationship"]

    result = evaluate_market_context_evidence(
        confirmation
    )

    assert result["Status"] == "REJECTED"


def test_invalid_input():

    result = evaluate_market_context_evidence(None)

    assert result["Status"] == "REJECTED"


if __name__ == "__main__":
    test_valid_context()
    test_invalid_status()
    test_missing_field()
    test_invalid_input()

    print(
        "V12.7 Stage 1 Market Context Evidence: PASS"
    )