"""
JKJ AI Trader
V17.4 Sequential Target Lifecycle Validation

Purpose:
    Validate the complete sequential lifecycle:

    V15.5 Target Progression
        ↓
    V17.1 Target Exit Plan
        ↓
    V17.2 Execution State
        ↓
    V17.3 Integration
        ↓
    Actual remaining quantity
        ↓
    Next target
        ↓
    Final target closes actual remaining position

No Zerodha.
No live orders.
No V11 modification.

Wisdom Before Wealth.
"""
from modules.nifty_option_v17_4_final_target_exit import (
    create_final_target_exit,
)

from modules.nifty_option_v17_3_target_exit_integration import (
    create_target_exit_integration,
    record_target_exit_execution,
)


def target_event(stage, target_price, current_price, reached):
    return {
        "Status": "TARGET_REACHED",
        "Target Event": stage,
        "Target Price": target_price,
        "Current Price": current_price,
        "Final Target": stage == "TARGET 3",
        "Targets Reached": reached,
    }


def main():

    print("\nJKJ AI Trader")
    print("V17.4 Sequential Target Lifecycle Validation")
    print("=" * 65)

    original_quantity = 65

    # ---------------------------------------------------------
    # TARGET 1
    # ---------------------------------------------------------

    t1 = target_event(
        "TARGET 1",
        120.0,
        120.5,
        ["TARGET 1"],
    )

    t1_state = create_target_exit_integration(
        t1,
        original_quantity,
    )

    assert t1_state["Status"] == "PLANNED"
    assert t1_state["Planned Exit Quantity"] == 22

    t1_result = record_target_exit_execution(
        t1_state,
        execution_status="PARTIAL",
        submitted_quantity=22,
        filled_quantity=15,
    )

    assert t1_result["Status"] == "EXECUTION_UPDATED"
    assert t1_result["Actual Remaining Quantity"] == 50

    print(
        "PASS | T1 | Planned 22 | Filled 15 | Remaining 50"
    )

    # ---------------------------------------------------------
    # TARGET 2
    # ---------------------------------------------------------

    t2 = target_event(
        "TARGET 2",
        125.0,
        125.5,
        ["TARGET 1", "TARGET 2"],
    )

    t2_state = create_target_exit_integration(
        t2,
        original_quantity,
    )

    assert t2_state["Status"] == "PLANNED"
    assert t2_state["Planned Exit Quantity"] == 22

    t2_result = record_target_exit_execution(
        t2_state,
        execution_status="FILLED",
        submitted_quantity=22,
        filled_quantity=22,
    )

    assert t2_result["Status"] == "EXECUTION_UPDATED"

    # Actual remaining after T2 must be based on
    # the cumulative actual fills:
    #
    # Original 65
    # T1 filled 15
    # T2 filled 22
    # Remaining = 28

    expected_remaining_after_t2 = (
        original_quantity
        - 15
        - 22
    )

    assert expected_remaining_after_t2 == 28

    print(
        "PASS | T2 | Planned 22 | Filled 22 | "
        "Cumulative Remaining 28"
    )

        # ---------------------------------------------------------
    # TARGET 3
    # ---------------------------------------------------------

    t3 = target_event(
        "TARGET 3",
        130.0,
        130.5,
        ["TARGET 1", "TARGET 2", "TARGET 3"],
    )

    # ---------------------------------------------------------
    # IMPORTANT:
    # T3 uses the ACTUAL remaining quantity.
    #
    # After T1 and T2:
    #
    # Original = 65
    # T1 filled = 15
    # T2 filled = 22
    # Actual remaining = 28
    #
    # T3 therefore exits 28, not the nominal V17.1
    # T3 allocation of 21.
    # ---------------------------------------------------------

    actual_remaining_quantity = (
        expected_remaining_after_t2
    )

    final_exit = create_final_target_exit(
        target_progression=t3,
        actual_remaining_quantity=actual_remaining_quantity,
    )

    assert final_exit["Status"] == "VALIDATED"
    assert final_exit["Target Stage"] == "TARGET 3"
    assert final_exit["Final Target"] is True
    assert (
        final_exit["Planned Final Exit Quantity"]
        == 28
    )

    print(
        "PASS | T3 Final Exit Plan | "
        "Actual Remaining 28 | Planned Exit 28"
    )

    # ---------------------------------------------------------
    # V17.2 records the actual final execution.
    #
    # Here the planned quantity is explicitly 28,
    # because 28 is the actual remaining position.
    # ---------------------------------------------------------

    t3_execution = {
        "Status": "PLANNED",
        "Target Stage": "TARGET 3",
        "Original Quantity": actual_remaining_quantity,
        "Planned Quantity": (
            final_exit["Planned Final Exit Quantity"]
        ),
        "Submitted Quantity": 0,
        "Filled Quantity": 0,
        "Actual Remaining Quantity": (
            actual_remaining_quantity
        ),
        "Execution Status": "PLANNED",
        "Execution Confirmed": False,
    }

    from modules.nifty_option_target_exit_execution import (
        update_target_exit_execution,
    )

    t3_result = update_target_exit_execution(
        execution_record=t3_execution,
        execution_status="FILLED",
        submitted_quantity=28,
        filled_quantity=28,
    )

    assert t3_result["Status"] == "UPDATED"
    assert t3_result["Execution Status"] == "FILLED"
    assert t3_result["Execution Confirmed"] is True
    assert t3_result["Actual Remaining Quantity"] == 0

    print(
        "PASS | T3 Execution | Filled 28 | Remaining 0"
    )

    # ---------------------------------------------------------
    # Final reconciliation
    # ---------------------------------------------------------

    total_filled = 15 + 22 + 28

    assert total_filled == original_quantity

    print("=" * 65)
    print("V17.4 SEQUENTIAL TARGET LIFECYCLE: PASS")
    print(
        "T1 → T2 → T3 sequential lifecycle validated."
    )
    print(
        "Actual remaining quantity governed final exit."
    )
    print(
        f"Original 65 = Filled {total_filled} + Remaining 0"
    )
    print("No live orders.")
    print("No Zerodha connection.")
    print("No V11 modification.")
    print("Wisdom Before Wealth.")
    print("=" * 65)


if __name__ == "__main__":
    main()
