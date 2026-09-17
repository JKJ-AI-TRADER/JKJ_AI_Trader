"""
JKJ AI Trader
Test — NIFTY Option Momentum Evidence V12.6 Stage 1
"""

from modules.nifty_option_momentum_evidence import (
    MIN_OBSERVATIONS_FOR_PERSISTENCE,
    evaluate_momentum_evidence,
)


def build_combined_interpretation():
    return {
        "Status": "INTERPRETED",
        "Trading Symbol": "NIFTY2692223300CE",
        "Underlying": "NIFTY",
        "Expiry": "2026-09-22",
        "Strike": 23300.0,
        "Option Type": "CE",
        "Option Direction": "DOWN",
        "NIFTY Direction": "UP",
        "Movement Relationship": "DIVERGING",
        "Volume Behaviour": "INCREASING",
        "Open Interest Behaviour": "UNCHANGED",
    }


def test_valid_evidence():

    result = evaluate_momentum_evidence(
        build_combined_interpretation()
    )

    assert result["Status"] == "EVALUATED"
    assert result["Price Movement Evidence"] is True
    assert result["NIFTY Movement Evidence"] is True
    assert result["Volume Evidence"] is True
    assert result["Open Interest Evidence"] is False
    assert result["Persistence Status"] == "NOT_YET_ESTABLISHED"


def test_persistence_requirement():

    assert MIN_OBSERVATIONS_FOR_PERSISTENCE == 3


def test_flat_option():

    data = build_combined_interpretation()
    data["Option Direction"] = "FLAT"

    result = evaluate_momentum_evidence(data)

    assert result["Status"] == "EVALUATED"
    assert result["Price Movement Evidence"] is False


def test_flat_nifty():

    data = build_combined_interpretation()
    data["NIFTY Direction"] = "FLAT"

    result = evaluate_momentum_evidence(data)

    assert result["Status"] == "EVALUATED"
    assert result["NIFTY Movement Evidence"] is False


def test_decreasing_volume():

    data = build_combined_interpretation()
    data["Volume Behaviour"] = "DECREASING"

    result = evaluate_momentum_evidence(data)

    assert result["Status"] == "EVALUATED"
    assert result["Volume Evidence"] is False


def test_oi_change():

    data = build_combined_interpretation()
    data["Open Interest Behaviour"] = "INCREASING"

    result = evaluate_momentum_evidence(data)

    assert result["Status"] == "EVALUATED"
    assert result["Open Interest Evidence"] is True


def test_invalid_status():

    data = build_combined_interpretation()
    data["Status"] = "REJECTED"

    result = evaluate_momentum_evidence(data)

    assert result["Status"] == "REJECTED"


def test_missing_field():

    data = build_combined_interpretation()
    del data["Volume Behaviour"]

    result = evaluate_momentum_evidence(data)

    assert result["Status"] == "REJECTED"


if __name__ == "__main__":
    test_valid_evidence()
    test_persistence_requirement()
    test_flat_option()
    test_flat_nifty()
    test_decreasing_volume()
    test_oi_change()
    test_invalid_status()
    test_missing_field()

    print("V12.6 Stage 1 Momentum Evidence: PASS")