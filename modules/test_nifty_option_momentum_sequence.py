"""
JKJ AI Trader
Test — NIFTY Option Momentum Sequence V12.6 Stage 2
"""

from modules.nifty_option_momentum_sequence import (
    MIN_OBSERVATIONS_FOR_PERSISTENCE,
    evaluate_momentum_sequence,
)


def build_direction(direction):
    return {
        "Status": "INTERPRETED",
        "Trading Symbol": "NIFTY2692223300CE",
        "Underlying": "NIFTY",
        "Expiry": "2026-09-22",
        "Strike": 23300.0,
        "Option Type": "CE",
        "Option Direction": direction,
        "NIFTY Direction": "UP",
    }


def test_persistent_down():

    results = [
        build_direction("DOWN"),
        build_direction("DOWN"),
        build_direction("DOWN"),
    ]

    result = evaluate_momentum_sequence(results)

    assert result["Status"] == "PERSISTENT"
    assert result["Direction"] == "DOWN"
    assert result["Persistence Status"] == "PERSISTENT"
    assert result["Observation Count"] == 3


def test_persistent_up():

    results = [
        build_direction("UP"),
        build_direction("UP"),
        build_direction("UP"),
        build_direction("UP"),
    ]

    result = evaluate_momentum_sequence(results)

    assert result["Status"] == "PERSISTENT"
    assert result["Direction"] == "UP"
    assert result["Observation Count"] == 4


def test_not_persistent():

    results = [
        build_direction("DOWN"),
        build_direction("UP"),
        build_direction("DOWN"),
    ]

    result = evaluate_momentum_sequence(results)

    assert result["Status"] == "NOT_PERSISTENT"
    assert result["Persistence Status"] == "NOT_PERSISTENT"


def test_flat_initial_direction():

    results = [
        build_direction("FLAT"),
        build_direction("UP"),
        build_direction("UP"),
    ]

    result = evaluate_momentum_sequence(results)

    assert result["Status"] == "NOT_PERSISTENT"
    assert result["Persistence Status"] == "NOT_PERSISTENT"


def test_insufficient_observations():

    results = [
        build_direction("DOWN"),
        build_direction("DOWN"),
    ]

    result = evaluate_momentum_sequence(results)

    assert result["Status"] == "INSUFFICIENT_OBSERVATIONS"
    assert result["Observation Count"] == 2
    assert (
        MIN_OBSERVATIONS_FOR_PERSISTENCE
        == 3
    )


def test_empty_sequence():

    result = evaluate_momentum_sequence([])

    assert result["Status"] == "INSUFFICIENT_OBSERVATIONS"
    assert result["Observation Count"] == 0


def test_invalid_input():

    result = evaluate_momentum_sequence("DOWN")

    assert result["Status"] == "REJECTED"


def test_invalid_direction_result():

    results = [
        build_direction("DOWN"),
        {
            "Status": "REJECTED",
            "Option Direction": "DOWN",
        },
        build_direction("DOWN"),
    ]

    result = evaluate_momentum_sequence(results)

    assert result["Status"] == "REJECTED"


def test_invalid_option_direction():

    results = [
        build_direction("DOWN"),
        build_direction("SIDEWAYS"),
        build_direction("DOWN"),
    ]

    result = evaluate_momentum_sequence(results)

    assert result["Status"] == "REJECTED"


if __name__ == "__main__":
    test_persistent_down()
    test_persistent_up()
    test_not_persistent()
    test_flat_initial_direction()
    test_insufficient_observations()
    test_empty_sequence()
    test_invalid_input()
    test_invalid_direction_result()
    test_invalid_option_direction()

    print("V12.6 Stage 2 Momentum Sequence: PASS")