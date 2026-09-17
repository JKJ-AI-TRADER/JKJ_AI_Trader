"""
JKJ AI Trader
V15.5 Target Progression Controller Test

Tests:
    1. Below Target 1 → WAITING
    2. Target 1 reached → TARGET 1
    3. Target 2 reached → TARGET 2
    4. Target 3 reached → TARGET 3
    5. All targets completed → COMPLETE
    6. Target progression cannot be skipped
    7. Invalid input → REJECTED

Wisdom Before Wealth.
"""

from modules.nifty_option_target_progression import (
    evaluate_target_progression,
)


def make_target_data():

    return {
        "Status": "TARGETS_VALIDATED",

        "Trading Symbol": "NIFTY26SEP25000CE",
        "Underlying": "NIFTY",
        "Expiry": "2026-09-24",
        "Strike": 25000,
        "Option Type": "CE",

        "Entry Price": 103.0,
        "Stop Price": 100.0,

        "Target 1": 106.0,
        "Target 2": 109.0,
        "Target 3": 112.0,
    }


def test_waiting_for_target_1():

    result = evaluate_target_progression(
        make_target_data(),
        current_price=105.0,
    )

    assert result["Status"] == "WAITING"
    assert result["Next Target"] == "TARGET 1"
    assert result["Next Target Price"] == 106.0
    assert result["Targets Reached"] == []

    print("Waiting for Target 1: PASS")


def test_target_1_reached():

    result = evaluate_target_progression(
        make_target_data(),
        current_price=106.0,
    )

    assert result["Status"] == "TARGET_REACHED"
    assert result["Target Event"] == "TARGET 1"
    assert result["Target Price"] == 106.0
    assert result["Targets Reached"] == ["TARGET 1"]
    assert result["Final Target"] is False

    print("Target 1 Reached: PASS")


def test_target_2_reached():

    result = evaluate_target_progression(
        make_target_data(),
        current_price=109.0,
        targets_reached=["TARGET 1"],
    )

    assert result["Status"] == "TARGET_REACHED"
    assert result["Target Event"] == "TARGET 2"
    assert result["Target Price"] == 109.0
    assert result["Targets Reached"] == [
        "TARGET 1",
        "TARGET 2",
    ]
    assert result["Final Target"] is False

    print("Target 2 Reached: PASS")


def test_target_3_reached():

    result = evaluate_target_progression(
        make_target_data(),
        current_price=112.0,
        targets_reached=[
            "TARGET 1",
            "TARGET 2",
        ],
    )

    assert result["Status"] == "TARGET_REACHED"
    assert result["Target Event"] == "TARGET 3"
    assert result["Target Price"] == 112.0
    assert result["Targets Reached"] == [
        "TARGET 1",
        "TARGET 2",
        "TARGET 3",
    ]
    assert result["Final Target"] is True

    print("Target 3 Reached: PASS")


def test_all_targets_complete():

    result = evaluate_target_progression(
        make_target_data(),
        current_price=115.0,
        targets_reached=[
            "TARGET 1",
            "TARGET 2",
            "TARGET 3",
        ],
    )

    assert result["Status"] == "COMPLETE"
    assert result["Targets Reached"] == [
        "TARGET 1",
        "TARGET 2",
        "TARGET 3",
    ]

    print("All Targets Complete: PASS")


def test_target_progression_cannot_skip():

    result = evaluate_target_progression(
        make_target_data(),
        current_price=109.0,
        targets_reached=[],
    )

    assert result["Status"] == "TARGET_REACHED"
    assert result["Target Event"] == "TARGET 1"
    assert result["Targets Reached"] == ["TARGET 1"]

    print("Sequential Target Protection: PASS")


def test_invalid_input():

    result = evaluate_target_progression(
        None,
        current_price=106.0,
    )

    assert result["Status"] == "REJECTED"

    print("Invalid Input: PASS")


def test_invalid_price():

    result = evaluate_target_progression(
        make_target_data(),
        current_price=0,
    )

    assert result["Status"] == "REJECTED"

    print("Invalid Price: PASS")


if __name__ == "__main__":

    test_waiting_for_target_1()
    test_target_1_reached()
    test_target_2_reached()
    test_target_3_reached()
    test_all_targets_complete()
    test_target_progression_cannot_skip()
    test_invalid_input()
    test_invalid_price()

    # ---------------------------------------------------------
    # Test 9 — Non-sequential target history rejected
    # ---------------------------------------------------------

    result = evaluate_target_progression(
        target_data=make_target_data(),
        current_price=106.0,
        targets_reached=["TARGET 2"],
    )

    assert result["Status"] == "REJECTED"

    print()
    print(
        "V15.5 Target Progression: ALL TESTS PASSED"
    )