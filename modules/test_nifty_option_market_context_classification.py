"""
JKJ AI Trader
Test — NIFTY Option Market Context Classification — V12.7 Stage 2
"""

from modules.nifty_option_market_context_classification import (
    classify_market_context,
    evaluate_market_context_classification,
)


def build_evidence(relationship):

    return {
        "Status": "EVALUATED",
        "Trading Symbol": "NIFTYTESTCE",
        "Underlying": "NIFTY",
        "Expiry": "2026-09-22",
        "Strike": 23300,
        "Option Type": "CE",
        "Option Direction": "UP",
        "NIFTY Movement Evidence": True,
        "Price Movement Evidence": True,
        "Volume Evidence": True,
        "Open Interest Evidence": False,
        "Movement Relationship": relationship,
        "Momentum Confirmation": "CONFIRMED",
    }


def test_moving_together():

    assert (
        classify_market_context("MOVING_TOGETHER")
        == "MOVING_TOGETHER"
    )


def test_diverging():

    assert (
        classify_market_context("DIVERGING")
        == "DIVERGING"
    )


def test_option_moving_nifty_flat():

    assert (
        classify_market_context(
            "OPTION_MOVING_NIFTY_FLAT"
        )
        == "OPTION_MOVING_NIFTY_FLAT"
    )


def test_option_flat_nifty_moving():

    assert (
        classify_market_context(
            "OPTION_FLAT_NIFTY_MOVING"
        )
        == "OPTION_FLAT_NIFTY_MOVING"
    )


def test_both_flat():

    assert (
        classify_market_context("BOTH_FLAT")
        == "BOTH_FLAT"
    )


def test_invalid_relationship():

    assert (
        classify_market_context("UNKNOWN")
        == "INVALID"
    )


def test_valid_classification():

    result = evaluate_market_context_classification(
        build_evidence("MOVING_TOGETHER")
    )

    assert result["Status"] == "CLASSIFIED"
    assert result["Market Context"] == "MOVING_TOGETHER"


def test_diverging_classification():

    result = evaluate_market_context_classification(
        build_evidence("DIVERGING")
    )

    assert result["Status"] == "CLASSIFIED"
    assert result["Market Context"] == "DIVERGING"


def test_invalid_status():

    evidence = build_evidence("MOVING_TOGETHER")
    evidence["Status"] = "INVALID"

    result = evaluate_market_context_classification(
        evidence
    )

    assert result["Status"] == "REJECTED"


def test_missing_relationship():

    evidence = build_evidence("MOVING_TOGETHER")
    del evidence["Movement Relationship"]

    result = evaluate_market_context_classification(
        evidence
    )

    assert result["Status"] == "REJECTED"


def test_invalid_input():

    result = evaluate_market_context_classification(None)

    assert result["Status"] == "REJECTED"


if __name__ == "__main__":
    test_moving_together()
    test_diverging()
    test_option_moving_nifty_flat()
    test_option_flat_nifty_moving()
    test_both_flat()
    test_invalid_relationship()
    test_valid_classification()
    test_diverging_classification()
    test_invalid_status()
    test_missing_relationship()
    test_invalid_input()

    print(
        "V12.7 Stage 2 Market Context Classification: PASS"
    )