"""
JKJ AI Trader
V20.1 -> V18.1 Integration Test

Wisdom Before Wealth.
"""

from nifty_option_v20_1_v18_1_integration import (
    integrate_v20_1_to_v18_1,
)

from modules.nifty_option_target_exit_execution import (
    create_target_exit_execution,
)


SYMBOL = "NIFTY26SEP25000CE"


def valid_v20_1_v17_8_8_result():
    trade = {
        "Trade ID": "JKJ-TRADE-001",
        "Status": "OPEN",
        "Symbol": SYMBOL,
        "Instrument Type": "OPTION",
        "Entry Price": 100.0,
        "Original Quantity": 65,
        "Current Quantity": 65,
        "Stop Loss": 90.0,
        "Target": 120.0,
    }

    qualification = {
        "Status": "QUALIFIED",
        "Trading Symbol": SYMBOL,
        "Paper Trade Permission": "PERMITTED",
    }

    v17_8_7_result = {
        "Status": "V17_8_7_PAPER_HANDOFF_COMPLETE",
        "Trade": trade,
        "Paper Trade Qualification": qualification,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Wisdom Before Wealth": True,
    }

    v17_8_8_result = {
        "Status": "V17_8_8_LIFECYCLE_BOUNDARY_VALIDATED",
        "Lifecycle Ready": True,
        "Lifecycle Owner": "V15.4 / V11",
        "Trade ID": "JKJ-TRADE-001",
        "Symbol": SYMBOL,
        "Instrument Type": "OPTION",
        "Entry Price": 100.0,
        "Original Quantity": 65,
        "Current Quantity": 65,
        "Stop Loss": 90.0,
        "Target": 120.0,
        "Paper Trade Qualification": qualification,
        "Trade": trade,
        "V15.4 Lifecycle Action Permitted": True,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Automatic Ranking": False,
        "Capital Reassignment": False,
        "Wisdom Before Wealth": True,
    }

    return {
        "Status": "V20_1_V17_8_8_INTEGRATION_COMPLETE",
        "V17.8.7 Result": v17_8_7_result,
        "V17.8.8 Result": v17_8_8_result,
        "Lifecycle Ready": True,
        "Lifecycle Owner": "V15.4 / V11",
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Automatic Ranking": False,
        "Capital Reassignment": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Wisdom Before Wealth": True,
    }


def make_v11_exit(exit_quantity, remaining_quantity):
    return {
        "Status": "SELL_RECORDED",
        "Exit Quantity": exit_quantity,
        "Remaining Quantity": remaining_quantity,
        "Trade Status": "OPEN",
    }


def test_successful_v18_1_synchronization():
    v17_2_execution = create_target_exit_execution(
        target_stage="TARGET 1",
        original_quantity=65,
        planned_quantity=22,
    )

    v11_exit = make_v11_exit(
        exit_quantity=15,
        remaining_quantity=50,
    )

    result = integrate_v20_1_to_v18_1(
        v20_1_v17_8_8_result=valid_v20_1_v17_8_8_result(),
        v11_exit_result=v11_exit,
        execution_record=v17_2_execution,
        global_original_quantity=65,
        previous_cumulative_filled=0,
    )

    assert (
        result["Status"]
        == "V20_1_V18_1_INTEGRATION_COMPLETE"
    )
    assert result["Synchronization Confirmed"] is True
    assert result["Target Stage"] == "TARGET 1"
    assert result["V11 Event Exit Quantity"] == 15
    assert result["Cumulative Filled Quantity"] == 15
    assert result["V11 Remaining Quantity"] == 50
    assert result["V17.2 Execution Status"] == "PARTIAL"
    assert result["V11 Quantity Authority"] is True
    assert result["V17.2 Target Stage Authority"] is True

    print(
        "Successful V20.1 -> V18.1 synchronization: PASS"
    )


def test_incomplete_v17_8_8_blocked():
    result = valid_v20_1_v17_8_8_result()
    result["Status"] = (
        "V20_1_V17_8_8_INTEGRATION_BLOCKED"
    )

    execution = create_target_exit_execution(
        target_stage="TARGET 1",
        original_quantity=65,
        planned_quantity=22,
    )

    output = integrate_v20_1_to_v18_1(
        result,
        make_v11_exit(15, 50),
        execution,
        65,
        0,
    )

    assert (
        output["Status"]
        == "V20_1_V18_1_INTEGRATION_BLOCKED"
    )

    print(
        "Incomplete V17.8.8 safeguard: PASS"
    )


def test_broker_communication_blocked():
    result = valid_v20_1_v17_8_8_result()
    result["Broker Communication"] = True

    execution = create_target_exit_execution(
        target_stage="TARGET 1",
        original_quantity=65,
        planned_quantity=22,
    )

    output = integrate_v20_1_to_v18_1(
        result,
        make_v11_exit(15, 50),
        execution,
        65,
        0,
    )

    assert (
        output["Status"]
        == "V20_1_V18_1_INTEGRATION_BLOCKED"
    )

    print(
        "Broker communication safeguard: PASS"
    )


def test_live_order_blocked():
    result = valid_v20_1_v17_8_8_result()
    result["Order Placement Permitted"] = True

    execution = create_target_exit_execution(
        target_stage="TARGET 1",
        original_quantity=65,
        planned_quantity=22,
    )

    output = integrate_v20_1_to_v18_1(
        result,
        make_v11_exit(15, 50),
        execution,
        65,
        0,
    )

    assert (
        output["Status"]
        == "V20_1_V18_1_INTEGRATION_BLOCKED"
    )

    print(
        "Live order placement safeguard: PASS"
    )


def test_mismatch_blocked():
    execution = create_target_exit_execution(
        target_stage="TARGET 2",
        original_quantity=65,
        planned_quantity=22,
    )

    output = integrate_v20_1_to_v18_1(
        valid_v20_1_v17_8_8_result(),
        make_v11_exit(22, 30),
        execution,
        65,
        15,
    )

    assert (
        output["Status"]
        == "V20_1_V18_1_INTEGRATION_BLOCKED"
    )

    print(
        "V11/V17.2 quantity mismatch safeguard: PASS"
    )


def test_over_execution_blocked():
    execution = create_target_exit_execution(
        target_stage="TARGET 3",
        original_quantity=65,
        planned_quantity=28,
    )

    output = integrate_v20_1_to_v18_1(
        valid_v20_1_v17_8_8_result(),
        {
            "Status": "SELL_RECORDED",
            "Exit Quantity": 30,
            "Remaining Quantity": 0,
            "Trade Status": "CLOSED",
        },
        execution,
        65,
        37,
    )

    assert (
        output["Status"]
        == "V20_1_V18_1_INTEGRATION_BLOCKED"
    )

    print(
        "Over-execution safeguard: PASS"
    )


def test_no_exit_generation():
    execution = create_target_exit_execution(
        target_stage="TARGET 1",
        original_quantity=65,
        planned_quantity=22,
    )

    output = integrate_v20_1_to_v18_1(
        valid_v20_1_v17_8_8_result(),
        make_v11_exit(15, 50),
        execution,
        65,
        0,
    )

    assert output["V11 Event Exit Quantity"] == 15
    assert output["Planned Quantity"] == 22

    print(
        "No exit quantity generation: PASS"
    )


def run_test():
    test_successful_v18_1_synchronization()
    test_incomplete_v17_8_8_blocked()
    test_broker_communication_blocked()
    test_live_order_blocked()
    test_mismatch_blocked()
    test_over_execution_blocked()
    test_no_exit_generation()

    print()
    print(
        "V20.1 -> V18.1 INTEGRATION: ALL TESTS PASSED"
    )
    print(
        "V11 remains authoritative for actual quantity."
    )
    print(
        "V17.2 remains authoritative for target-stage state."
    )
    print(
        "V18.1 performs reconciliation only."
    )
    print("No exit quantity generation.")
    print("No V11 modification.")
    print("No V17.2 modification.")
    print("No live Zerodha order.")
    print("No broker communication.")
    print("No main.py modification.")
    print("Wisdom Before Wealth.")


if __name__ == "__main__":
    run_test()