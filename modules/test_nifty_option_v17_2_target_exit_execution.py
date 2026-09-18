"""
JKJ AI Trader
V17.2 Target Exit Execution State Test

Purpose:
    Validate separation between planned target exits
    and actual execution results.

Tests:
    - PLANNED
    - FILLED
    - PARTIAL
    - PENDING
    - REJECTED
    - invalid filled quantity
    - quantity reconciliation

Wisdom Before Wealth.
"""

from modules.nifty_option_target_exit_execution import (
    create_target_exit_execution,
    update_target_exit_execution,
)


def assert_common_result(result, target_stage, original_quantity):
    assert result["Target Stage"] == target_stage
    assert result["Original Quantity"] == original_quantity


def test_planned():
    result = create_target_exit_execution(
        target_stage="TARGET 1",
        original_quantity=65,
        planned_quantity=22,
    )

    assert result["Status"] == "PLANNED"
    assert result["Execution Status"] == "PLANNED"
    assert result["Execution Confirmed"] is False
    assert result["Planned Quantity"] == 22
    assert result["Filled Quantity"] == 0
    assert result["Actual Remaining Quantity"] == 65

    print("PASS | PLANNED | 65 quantity | T1 planned 22")


def test_filled():
    record = create_target_exit_execution(
        target_stage="TARGET 1",
        original_quantity=65,
        planned_quantity=22,
    )

    result = update_target_exit_execution(
        execution_record=record,
        execution_status="FILLED",
        submitted_quantity=22,
        filled_quantity=22,
    )

    assert result["Status"] == "UPDATED"
    assert result["Execution Status"] == "FILLED"
    assert result["Execution Confirmed"] is True
    assert result["Submitted Quantity"] == 22
    assert result["Filled Quantity"] == 22
    assert result["Actual Remaining Quantity"] == 43

    print("PASS | FILLED | Planned 22 | Filled 22 | Remaining 43")


def test_partial():
    record = create_target_exit_execution(
        target_stage="TARGET 1",
        original_quantity=65,
        planned_quantity=22,
    )

    result = update_target_exit_execution(
        execution_record=record,
        execution_status="PARTIAL",
        submitted_quantity=22,
        filled_quantity=15,
    )

    assert result["Status"] == "UPDATED"
    assert result["Execution Status"] == "PARTIAL"
    assert result["Execution Confirmed"] is True
    assert result["Submitted Quantity"] == 22
    assert result["Filled Quantity"] == 15
    assert result["Actual Remaining Quantity"] == 50

    print("PASS | PARTIAL | Planned 22 | Filled 15 | Remaining 50")


def test_pending():
    record = create_target_exit_execution(
        target_stage="TARGET 2",
        original_quantity=65,
        planned_quantity=22,
    )

    result = update_target_exit_execution(
        execution_record=record,
        execution_status="PENDING",
        submitted_quantity=22,
        filled_quantity=0,
    )

    assert result["Status"] == "UPDATED"
    assert result["Execution Status"] == "PENDING"
    assert result["Execution Confirmed"] is False
    assert result["Filled Quantity"] == 0
    assert result["Actual Remaining Quantity"] == 65

    print("PASS | PENDING | Filled 0 | Remaining 65")


def test_rejected():
    record = create_target_exit_execution(
        target_stage="TARGET 2",
        original_quantity=65,
        planned_quantity=22,
    )

    result = update_target_exit_execution(
        execution_record=record,
        execution_status="REJECTED",
        submitted_quantity=22,
        filled_quantity=0,
    )

    assert result["Status"] == "UPDATED"
    assert result["Execution Status"] == "REJECTED"
    assert result["Execution Confirmed"] is False
    assert result["Filled Quantity"] == 0
    assert result["Actual Remaining Quantity"] == 65

    print("PASS | REJECTED | Filled 0 | Remaining 65")


def test_invalid_filled_quantity():
    record = create_target_exit_execution(
        target_stage="TARGET 1",
        original_quantity=65,
        planned_quantity=22,
    )

    result = update_target_exit_execution(
        execution_record=record,
        execution_status="FILLED",
        submitted_quantity=22,
        filled_quantity=15,
    )

    assert result["Status"] == "REJECTED"

    print("PASS | Invalid FILLED quantity rejected")


def test_filled_exceeds_submitted():
    record = create_target_exit_execution(
        target_stage="TARGET 1",
        original_quantity=65,
        planned_quantity=22,
    )

    result = update_target_exit_execution(
        execution_record=record,
        execution_status="PARTIAL",
        submitted_quantity=15,
        filled_quantity=20,
    )

    assert result["Status"] == "REJECTED"

    print("PASS | Filled quantity exceeding submitted quantity rejected")


def test_invalid_planned_quantity():
    result = create_target_exit_execution(
        target_stage="TARGET 1",
        original_quantity=65,
        planned_quantity=70,
    )

    assert result["Status"] == "REJECTED"

    print("PASS | Planned quantity exceeding original quantity rejected")


def main():

    print("\nJKJ AI Trader")
    print("V17.2 Target Exit Execution State Test")
    print("=" * 60)

    test_planned()
    test_filled()
    test_partial()
    test_pending()
    test_rejected()
    test_invalid_filled_quantity()
    test_filled_exceeds_submitted()
    test_invalid_planned_quantity()

    print("=" * 60)
    print("V17.2 TARGET EXIT EXECUTION STATE TEST: PASS")
    print("Execution states validated.")
    print("Actual remaining quantity reconciliation validated.")
    print("No live orders.")
    print("No Zerodha connection.")
    print("No V11 modification.")
    print("Wisdom Before Wealth.")
    print("=" * 60)


if __name__ == "__main__":
    main()