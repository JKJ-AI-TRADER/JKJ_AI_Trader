"""
JKJ AI Trader
V17.3 Target Progression + Exit Plan Integration Test

Purpose:
    Validate the complete chain:

    V15.5 Target Progression
        ↓
    V17.1 Target Exit Plan
        ↓
    V17.2 Execution State
        ↓
    Actual execution result
        ↓
    Actual remaining quantity

No Zerodha.
No live orders.
No V11 modification.

Wisdom Before Wealth.
"""

from modules.nifty_option_v17_3_target_exit_integration import (
    create_target_exit_integration,
    record_target_exit_execution,
)


def target_event(
    stage,
    target_price,
    current_price,
    final_target=False,
):
    """Create a minimal valid V15.5 target event."""

    return {
        "Status": "TARGET_REACHED",
        "Target Event": stage,
        "Target Price": target_price,
        "Current Price": current_price,
        "Final Target": final_target,
        "Targets Reached": [stage],
    }


def test_target_1_partial_fill():
    progression = target_event(
        "TARGET 1",
        120.0,
        120.5,
    )

    result = create_target_exit_integration(
        progression,
        65,
    )

    assert result["Status"] == "PLANNED"
    assert result["Target Stage"] == "TARGET 1"
    assert result["Planned Exit Quantity"] == 22
    assert result["Execution"]["Execution Status"] == "PLANNED"
    assert result["Execution Confirmed"] is False

    updated = record_target_exit_execution(
        result,
        execution_status="PARTIAL",
        submitted_quantity=22,
        filled_quantity=15,
    )

    assert updated["Status"] == "EXECUTION_UPDATED"
    assert updated["Execution"]["Execution Status"] == "PARTIAL"
    assert updated["Execution"]["Filled Quantity"] == 15
    assert updated["Actual Remaining Quantity"] == 50

    print(
        "PASS | T1 | Planned 22 | Filled 15 | Remaining 50"
    )


def test_target_2_full_fill():
    progression = target_event(
        "TARGET 2",
        125.0,
        125.5,
    )

    result = create_target_exit_integration(
        progression,
        65,
    )

    assert result["Status"] == "PLANNED"
    assert result["Target Stage"] == "TARGET 2"
    assert result["Planned Exit Quantity"] == 22

    updated = record_target_exit_execution(
        result,
        execution_status="FILLED",
        submitted_quantity=22,
        filled_quantity=22,
    )

    assert updated["Status"] == "EXECUTION_UPDATED"
    assert updated["Execution"]["Execution Status"] == "FILLED"
    assert updated["Execution Confirmed"] is True
    assert updated["Actual Remaining Quantity"] == 43

    print(
        "PASS | T2 | Planned 22 | Filled 22 | Remaining 43"
    )


def test_target_3_full_fill():
    progression = target_event(
        "TARGET 3",
        130.0,
        130.5,
        final_target=True,
    )

    result = create_target_exit_integration(
        progression,
        65,
    )

    assert result["Status"] == "PLANNED"
    assert result["Target Stage"] == "TARGET 3"
    assert result["Planned Exit Quantity"] == 21
    assert result["Final Target"] is True

    updated = record_target_exit_execution(
        result,
        execution_status="FILLED",
        submitted_quantity=21,
        filled_quantity=21,
    )

    assert updated["Status"] == "EXECUTION_UPDATED"
    assert updated["Execution"]["Execution Status"] == "FILLED"
    assert updated["Execution Confirmed"] is True
    assert updated["Actual Remaining Quantity"] == 44

    print(
        "PASS | T3 | Planned 21 | Filled 21 | Remaining 44"
    )


def test_pending_execution():
    progression = target_event(
        "TARGET 1",
        120.0,
        120.5,
    )

    result = create_target_exit_integration(
        progression,
        65,
    )

    updated = record_target_exit_execution(
        result,
        execution_status="PENDING",
        submitted_quantity=22,
        filled_quantity=0,
    )

    assert updated["Status"] == "EXECUTION_UPDATED"
    assert updated["Execution"]["Execution Status"] == "PENDING"
    assert updated["Execution Confirmed"] is False
    assert updated["Actual Remaining Quantity"] == 65

    print(
        "PASS | PENDING | Filled 0 | Remaining 65"
    )


def test_rejected_execution():
    progression = target_event(
        "TARGET 2",
        125.0,
        125.5,
    )

    result = create_target_exit_integration(
        progression,
        65,
    )

    updated = record_target_exit_execution(
        result,
        execution_status="REJECTED",
        submitted_quantity=22,
        filled_quantity=0,
    )

    assert updated["Status"] == "EXECUTION_UPDATED"
    assert updated["Execution"]["Execution Status"] == "REJECTED"
    assert updated["Execution Confirmed"] is False
    assert updated["Actual Remaining Quantity"] == 65

    print(
        "PASS | REJECTED | Filled 0 | Remaining 65"
    )


def test_invalid_target_event():
    progression = target_event(
        "TARGET 4",
        135.0,
        135.5,
    )

    result = create_target_exit_integration(
        progression,
        65,
    )

    assert result["Status"] == "REJECTED"

    print(
        "PASS | Invalid target event rejected"
    )


def test_target_not_reached():
    progression = {
        "Status": "WAITING",
        "Target Event": None,
        "Target Price": 120.0,
        "Current Price": 119.0,
        "Final Target": False,
        "Targets Reached": [],
    }

    result = create_target_exit_integration(
        progression,
        65,
    )

    assert result["Status"] == "REJECTED"

    print(
        "PASS | Target not reached rejected"
    )


def main():

    print("\nJKJ AI Trader")
    print("V17.3 Target Progression + Exit Plan Integration Test")
    print("=" * 65)

    test_target_1_partial_fill()
    test_target_2_full_fill()
    test_target_3_full_fill()
    test_pending_execution()
    test_rejected_execution()
    test_invalid_target_event()
    test_target_not_reached()

    print("=" * 65)
    print("V17.3 TARGET EXIT INTEGRATION TEST: PASS")
    print("V15.5 → V17.1 → V17.2 chain validated.")
    print("Partial execution reconciliation validated.")
    print("Pending execution preserved.")
    print("Rejected execution preserved.")
    print("No live orders.")
    print("No Zerodha connection.")
    print("No V11 modification.")
    print("Wisdom Before Wealth.")
    print("=" * 65)


if __name__ == "__main__":
    main()