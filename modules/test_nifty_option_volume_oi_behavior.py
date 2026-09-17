"""
JKJ AI Trader
Test — NIFTY Option Volume & OI Behaviour V12.5 Stage 2
"""

from modules.nifty_option_volume_oi_behavior import (
    classify_volume_oi_change,
    interpret_volume_oi_behavior,
)


def test_classify_change():
    assert classify_volume_oi_change(100) == "INCREASING"
    assert classify_volume_oi_change(-100) == "DECREASING"
    assert classify_volume_oi_change(0) == "UNCHANGED"


def test_invalid_change():
    assert classify_volume_oi_change("100") == "INVALID"


def test_valid_behavior():
    movement = {
        "Status": "ANALYZED",
        "Trading Symbol": "NIFTY2692223300CE",
        "Underlying": "NIFTY",
        "Expiry": "2026-09-22",
        "Strike": 23300.0,
        "Option Type": "CE",
        "Volume Change": 102440,
        "Open Interest Change": 0,
    }

    result = interpret_volume_oi_behavior(movement)

    assert result["Status"] == "INTERPRETED"
    assert result["Volume Behaviour"] == "INCREASING"
    assert result["Open Interest Behaviour"] == "UNCHANGED"


def test_decreasing_behavior():
    movement = {
        "Status": "ANALYZED",
        "Volume Change": -5000,
        "Open Interest Change": -1000,
    }

    result = interpret_volume_oi_behavior(movement)

    assert result["Status"] == "INTERPRETED"
    assert result["Volume Behaviour"] == "DECREASING"
    assert result["Open Interest Behaviour"] == "DECREASING"


def test_invalid_status():
    movement = {
        "Status": "REJECTED",
        "Volume Change": 100,
        "Open Interest Change": 50,
    }

    result = interpret_volume_oi_behavior(movement)

    assert result["Status"] == "REJECTED"


def test_missing_field():
    movement = {
        "Status": "ANALYZED",
        "Volume Change": 100,
    }

    result = interpret_volume_oi_behavior(movement)

    assert result["Status"] == "REJECTED"


def test_invalid_numeric_value():
    movement = {
        "Status": "ANALYZED",
        "Volume Change": "INCREASING",
        "Open Interest Change": 100,
    }

    result = interpret_volume_oi_behavior(movement)

    assert result["Status"] == "REJECTED"


if __name__ == "__main__":
    test_classify_change()
    test_invalid_change()
    test_valid_behavior()
    test_decreasing_behavior()
    test_invalid_status()
    test_missing_field()
    test_invalid_numeric_value()

    print("V12.5 Stage 2 Volume & OI Behaviour: PASS")