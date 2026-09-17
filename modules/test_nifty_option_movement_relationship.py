"""
JKJ AI Trader
Test — NIFTY Option Movement Relationship V12.5 Stage 3
"""

from modules.nifty_option_movement_relationship import (
    classify_movement_relationship,
    interpret_movement_relationship,
)


def test_moving_together():
    assert (
        classify_movement_relationship("UP", "UP")
        == "MOVING_TOGETHER"
    )

    assert (
        classify_movement_relationship("DOWN", "DOWN")
        == "MOVING_TOGETHER"
    )


def test_diverging():
    assert (
        classify_movement_relationship("UP", "DOWN")
        == "DIVERGING"
    )

    assert (
        classify_movement_relationship("DOWN", "UP")
        == "DIVERGING"
    )


def test_option_moving_nifty_flat():
    assert (
        classify_movement_relationship("UP", "FLAT")
        == "OPTION_MOVING_NIFTY_FLAT"
    )

    assert (
        classify_movement_relationship("DOWN", "FLAT")
        == "OPTION_MOVING_NIFTY_FLAT"
    )


def test_option_flat_nifty_moving():
    assert (
        classify_movement_relationship("FLAT", "UP")
        == "OPTION_FLAT_NIFTY_MOVING"
    )

    assert (
        classify_movement_relationship("FLAT", "DOWN")
        == "OPTION_FLAT_NIFTY_MOVING"
    )


def test_both_flat():
    assert (
        classify_movement_relationship("FLAT", "FLAT")
        == "BOTH_FLAT"
    )


def test_invalid_direction():
    assert (
        classify_movement_relationship("INVALID", "UP")
        == "INVALID"
    )


def test_valid_relationship_interpretation():
    direction_result = {
        "Status": "INTERPRETED",
        "Trading Symbol": "NIFTY2692223300CE",
        "Underlying": "NIFTY",
        "Expiry": "2026-09-22",
        "Strike": 23300.0,
        "Option Type": "CE",
        "Option Direction": "DOWN",
        "NIFTY Direction": "UP",
    }

    result = interpret_movement_relationship(direction_result)

    assert result["Status"] == "INTERPRETED"
    assert result["Movement Relationship"] == "DIVERGING"


def test_invalid_status():
    direction_result = {
        "Status": "REJECTED",
        "Option Direction": "UP",
        "NIFTY Direction": "UP",
    }

    result = interpret_movement_relationship(direction_result)

    assert result["Status"] == "REJECTED"


def test_missing_field():
    direction_result = {
        "Status": "INTERPRETED",
        "Option Direction": "UP",
    }

    result = interpret_movement_relationship(direction_result)

    assert result["Status"] == "REJECTED"


if __name__ == "__main__":
    test_moving_together()
    test_diverging()
    test_option_moving_nifty_flat()
    test_option_flat_nifty_moving()
    test_both_flat()
    test_invalid_direction()
    test_valid_relationship_interpretation()
    test_invalid_status()
    test_missing_field()

    print("V12.5 Stage 3 Movement Relationship: PASS")