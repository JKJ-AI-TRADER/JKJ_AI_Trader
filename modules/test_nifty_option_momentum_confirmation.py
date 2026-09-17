"""
JKJ AI Trader
Test — NIFTY Option Momentum Confirmation V12.6 Stage 3
"""

from modules.nifty_option_momentum_confirmation import (
    evaluate_momentum_confirmation,
)


def build_evidence(
    price=True,
    nifty=True,
    volume=True,
    oi=False,
):
    return {
        "Status": "EVALUATED",
        "Trading Symbol": "NIFTY2692223300CE",
        "Underlying": "NIFTY",
        "Expiry": "2026-09-22",
        "Strike": 23300.0,
        "Option Type": "CE",
        "Option Direction": "DOWN",
        "NIFTY Direction": "UP",
        "Movement Relationship": "DIVERGING",
        "Volume Behaviour": (
            "INCREASING"
            if volume
            else "DECREASING"
        ),
        "Open Interest Behaviour": (
            "INCREASING"
            if oi
            else "UNCHANGED"
        ),
        "Price Movement Evidence": price,
        "NIFTY Movement Evidence": nifty,
        "Volume Evidence": volume,
        "Open Interest Evidence": oi,
        "Persistence Status": "NOT_YET_ESTABLISHED",
    }


def build_sequence(status="PERSISTENT"):
    return {
        "Status": status,
        "Persistence Status": status,
        "Observation Count": 3,
        "Direction": "DOWN",
        "Direction Sequence": [
            "DOWN",
            "DOWN",
            "DOWN",
        ],
    }


def test_confirmed():

    result = evaluate_momentum_confirmation(
        build_evidence(
            price=True,
            nifty=True,
            volume=True,
            oi=False,
        ),
        build_sequence("PERSISTENT"),
    )

    assert result["Status"] == "EVALUATED"
    assert result["Momentum Confirmation"] == "CONFIRMED"
    assert result["Persistence Status"] == "PERSISTENT"
    assert result["Price Movement Evidence"] is True
    assert result["Volume Evidence"] is True


def test_partially_confirmed():

    result = evaluate_momentum_confirmation(
        build_evidence(
            price=True,
            nifty=True,
            volume=False,
            oi=False,
        ),
        build_sequence("PERSISTENT"),
    )

    assert result["Status"] == "EVALUATED"
    assert (
        result["Momentum Confirmation"]
        == "PARTIALLY_CONFIRMED"
    )


def test_not_confirmed_without_persistence():

    result = evaluate_momentum_confirmation(
        build_evidence(
            price=True,
            nifty=True,
            volume=True,
        ),
        build_sequence("NOT_PERSISTENT"),
    )

    assert result["Status"] == "EVALUATED"
    assert (
        result["Momentum Confirmation"]
        == "NOT_CONFIRMED"
    )


def test_not_confirmed_without_price():

    result = evaluate_momentum_confirmation(
        build_evidence(
            price=False,
            nifty=True,
            volume=True,
        ),
        build_sequence("PERSISTENT"),
    )

    assert result["Status"] == "EVALUATED"
    assert (
        result["Momentum Confirmation"]
        == "NOT_CONFIRMED"
    )


def test_oi_is_reported():

    result = evaluate_momentum_confirmation(
        build_evidence(
            price=True,
            nifty=True,
            volume=True,
            oi=True,
        ),
        build_sequence("PERSISTENT"),
    )

    assert result["Status"] == "EVALUATED"
    assert result["Open Interest Evidence"] is True
    assert result["Momentum Confirmation"] == "CONFIRMED"


def test_invalid_evidence_status():

    evidence = build_evidence()
    evidence["Status"] = "REJECTED"

    result = evaluate_momentum_confirmation(
        evidence,
        build_sequence("PERSISTENT"),
    )

    assert result["Status"] == "REJECTED"


def test_invalid_sequence_status():

    result = evaluate_momentum_confirmation(
        build_evidence(),
        {
            "Status": "INSUFFICIENT_OBSERVATIONS",
            "Persistence Status": "NOT_YET_ESTABLISHED",
        },
    )

    assert result["Status"] == "REJECTED"


def test_missing_evidence_field():

    evidence = build_evidence()
    del evidence["Volume Evidence"]

    result = evaluate_momentum_confirmation(
        evidence,
        build_sequence("PERSISTENT"),
    )

    assert result["Status"] == "REJECTED"


def test_missing_persistence_field():

    sequence = build_sequence("PERSISTENT")
    del sequence["Persistence Status"]

    result = evaluate_momentum_confirmation(
        build_evidence(),
        sequence,
    )

    assert result["Status"] == "REJECTED"


if __name__ == "__main__":
    test_confirmed()
    test_partially_confirmed()
    test_not_confirmed_without_persistence()
    test_not_confirmed_without_price()
    test_oi_is_reported()
    test_invalid_evidence_status()
    test_invalid_sequence_status()
    test_missing_evidence_field()
    test_missing_persistence_field()

    print("V12.6 Stage 3 Momentum Confirmation: PASS")