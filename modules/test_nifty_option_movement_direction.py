"""
JKJ AI Trader
Test — NIFTY Option Movement Direction V12.5 Stage 1
"""

from modules.nifty_option_movement_direction import (
    classify_direction,
    interpret_movement_direction,
)


def test_classify_direction():
    assert classify_direction(10) == "UP"
    assert classify_direction(-10) == "DOWN"
    assert classify_direction(0) == "FLAT"


def test_invalid_direction():
    assert classify_direction("10") == "INVALID"


def test_valid_movement():
    movement = {
        "Status": "ANALYZED",
        "Trading Symbol": "NIFTY2692223300CE",
        "Underlying": "NIFTY",
        "Expiry": "2026-09-22",
        "Strike": 23300.0,
        "Option Type": "CE",
        "Option Price Change": -1.10,
        "NIFTY Spot Change": 0.35,
    }

    result = interpret_movement_direction(movement)

    assert result["Status"] == "INTERPRETED"
    assert result["Option Direction"] == "DOWN"
    assert result["NIFTY Direction"] == "UP"


def test_flat_movement():
    movement = {
        "Status": "ANALYZED",
        "Option Price Change": 0,
        "NIFTY Spot Change": 0,
    }

    result = interpret_movement_direction(movement)

    assert result["Status"] == "INTERPRETED"
    assert result["Option Direction"] == "FLAT"
    assert result["NIFTY Direction"] == "FLAT"


def test_invalid_status():
    movement = {
        "Status": "REJECTED",
        "Option Price Change": 10,
        "NIFTY Spot Change": 5,
    }

    result = interpret_movement_direction(movement)

    assert result["Status"] == "REJECTED"


def test_missing_field():
    movement = {
        "Status": "ANALYZED",
        "Option Price Change": 10,
    }

    result = interpret_movement_direction(movement)

    assert result["Status"] == "REJECTED"


def test_invalid_numeric_value():
    movement = {
        "Status": "ANALYZED",
        "Option Price Change": "DOWN",
        "NIFTY Spot Change": 5,
    }

    result = interpret_movement_direction(movement)

    assert result["Status"] == "REJECTED"


if __name__ == "__main__":
    test_classify_direction()
    test_invalid_direction()
    test_valid_movement()
    test_flat_movement()
    test_invalid_status()
    test_missing_field()
    test_invalid_numeric_value()

    print("V12.5 Stage 1 Movement Direction: PASS")