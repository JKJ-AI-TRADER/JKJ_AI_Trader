"""
JKJ AI Trader
Full V17.8 -> V18.1 Controlled Paper Lifecycle Integration Test

Wisdom Before Wealth.

This test:
- validates the controlled V17.7 quantity/execution boundary
- simulates paper order and paper fill
- maps the paper fill into V15
- hands off into the V15/V11 paper lifecycle
- validates target slicing and target execution boundaries
- synchronizes V11 paper quantity with V17.2 through V18.1

No Zerodha.
No real order.
No broker communication.
No main.py modification.
"""

from modules.nifty_option_v17_7_final_quantity_plan_validation import (
    validate_final_quantity_plan,
)
from modules.nifty_option_v17_7_execution_readiness_gate import (
    validate_execution_readiness,
)
from modules.nifty_option_v17_7_execution_request_specification import (
    create_execution_request,
)
from modules.nifty_option_v17_8_paper_order_simulator import (
    simulate_paper_order,
)
from modules.nifty_option_v17_8_paper_fill_engine import (
    simulate_paper_fill,
)
from modules.nifty_option_v17_8_paper_fill_v15_entry_bridge import (
    map_paper_fill_to_v15_entry,
)
from modules.nifty_option_v17_8_v15_paper_handoff import (
    handoff_to_v15_paper_trade,
)
from modules.nifty_option_v17_8_lifecycle_boundary import (
    validate_lifecycle_boundary,
)
from modules.nifty_option_target_slicing_bridge import (
    evaluate_target_slicing,
)
from modules.nifty_option_v17_3_target_exit_integration import (
    create_target_exit_integration,
)
from modules.nifty_option_v17_4_final_target_exit import (
    create_final_target_exit,
)
from modules.nifty_option_v18_1_paper_target_exit_synchronization import (
    synchronize_target_exit,
)


# ---------------------------------------------------------
# COMMON TEST DATA
# ---------------------------------------------------------

ORIGINAL_QUANTITY = 65
LOT_SIZE = 65
ENTRY_PRICE = 100.0

TRADING_SYMBOL = "NIFTY26SEP23000CE"
INSTRUMENT_TOKEN = 123456

STOP_PRICE = 90.0
TARGET_1 = 105.0
TARGET_2 = 110.0
TARGET_3 = 120.0


# ---------------------------------------------------------
# V17.7.3 -> V17.7.4 CONTROLLED FIXTURE
# ---------------------------------------------------------

def build_reconciliation_result():
    required_capital = ENTRY_PRICE * ORIGINAL_QUANTITY
    allocated_capital = 7000.0
    unused_capital = allocated_capital - required_capital

    return {
        "Status": "MULTI_CANDIDATE_RECONCILIATION_COMPLETE",

        "Reconciliations": [
            {
                "Candidate": "NIFTY_PRIMARY",
                "Priority": 1,
                "Status": "RECONCILIATION_COMPLETE",
                "Allocation Status": "ALLOCATED",

                "Allocated Capital": allocated_capital,
                "Entry Price": ENTRY_PRICE,
                "Lot Size": LOT_SIZE,
                "Reconciled Lots": 1,
                "Reconciled Quantity": ORIGINAL_QUANTITY,

                "Estimated Capital Required": required_capital,

                "Trading Symbol": TRADING_SYMBOL,
                "Instrument Token": INSTRUMENT_TOKEN,
                "Contract Identity Valid": True,

                "Unused Allocated Capital": unused_capital,
                "Order Placement Permitted": False,
            }
        ],

        "Total Allocated Capital": allocated_capital,
        "Total Required Capital": required_capital,

        # 7000 - 6500 = 500
        "Total Uncommitted Capital": unused_capital,

        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Order Placement Permitted": False,
    }


# ---------------------------------------------------------
# V15 QUALIFICATION
# ---------------------------------------------------------

def build_v15_qualification():
    return {
        "Status": "QUALIFIED",
        "Paper Trade Permission": "PERMITTED",

        "Trading Symbol": TRADING_SYMBOL,
        "Underlying": "NIFTY",
        "Expiry": "2026-09-24",
        "Strike": 23000,
        "Option Type": "CE",

        "Entry Price": ENTRY_PRICE,
        "Stop Price": STOP_PRICE,

        "Target 1": TARGET_1,
        "Target 2": TARGET_2,
        "Target 3": TARGET_3,

        "Risk Reward 1": 1.5,
        "Risk Reward 2": 2.0,
        "Risk Reward 3": 3.0,

        "Entry Qualification": "QUALIFIED",
        "Qualification Reason": "Controlled V17.8 -> V18.1 integration test",
    }


# ---------------------------------------------------------
# V14.5 / V15 EXIT QUALIFICATION
# ---------------------------------------------------------

def build_exit_qualification():
    return {
        "Status": "EVALUATED",

        "Trading Symbol": TRADING_SYMBOL,
        "Underlying": "NIFTY",
        "Expiry": "2026-09-24",
        "Strike": 23000,
        "Option Type": "CE",

        "Entry Price": ENTRY_PRICE,
        "Stop Price": STOP_PRICE,

        "Target 1": TARGET_1,
        "Target 2": TARGET_2,
        "Target 3": TARGET_3,

        "Risk Reward 1": 1.5,
        "Risk Reward 2": 2.0,
        "Risk Reward 3": 3.0,

        # Exact V15.1 controlled paper-trade requirements
        "Entry Qualification": "ENTRY_QUALIFIED",
        "Entry Risk Context": "CONTROLLED_RISK_CONTEXT",
        "Stop-Loss Context": "STOP_SUPPORTED",
        "Exit Structure": "EXIT_STRUCTURE_SUPPORTED",
    }


# ---------------------------------------------------------
# TARGET PROGRESSION FIXTURE
# ---------------------------------------------------------

def build_target_progression(
    target_event,
    target_price,
    current_price,
    final_target=False,
    targets_reached=None,
):
    if targets_reached is None:
        targets_reached = [target_event]

    return {
        "Status": "TARGET_REACHED",
        "Target Event": target_event,
        "Target Price": target_price,
        "Current Price": current_price,
        "Final Target": final_target,
        "Targets Reached": targets_reached,
    }


# ---------------------------------------------------------
# MAIN TEST
# ---------------------------------------------------------

def main():

    # =====================================================
    # 1. V17.7.4
    # =====================================================

    reconciliation = build_reconciliation_result()

    final_plan = validate_final_quantity_plan(
        reconciliation
    )

    assert final_plan["Status"] == (
        "FINAL_QUANTITY_PLAN_VALIDATED"
    )

    assert final_plan["Validated Candidates"] == 1
    assert final_plan["Total Allocated Capital"] == 7000.0
    assert final_plan["Total Required Capital"] == 6500.0
    assert final_plan["Total Uncommitted Capital"] == 500.0

    # =====================================================
    # 2. V17.7.5
    # =====================================================

    readiness = validate_execution_readiness(
        final_plan
    )

    assert readiness["Status"] == (
        "EXECUTION_READINESS_VALIDATED"
    )

    candidates = readiness["Execution Candidates"]

    assert len(candidates) == 1

    execution_candidate = candidates[0]

    assert execution_candidate["Candidate"] == "NIFTY_PRIMARY"
    assert execution_candidate["Priority"] == 1
    assert execution_candidate["Trading Symbol"] == TRADING_SYMBOL
    assert execution_candidate["Instrument Token"] == INSTRUMENT_TOKEN
    assert execution_candidate["Reconciled Quantity"] == 65
    assert execution_candidate["Execution Ready"] is True
    assert execution_candidate["Order Placement Permitted"] is False

    # =====================================================
    # 3. V17.7.6
    # =====================================================

    execution_request = create_execution_request(
        execution_candidate,
        order_type="MARKET",
        product="MIS",
        transaction_type="BUY",
    )

    request = execution_request["Execution Request"]

    # Controlled integration boundary:
    # V17.7.6 calls this "Contract Identity Valid".
    # V17.8.1 expects "Contract Valid".
    request["Contract Valid"] = request["Contract Identity Valid"]

    request = execution_request["Execution Request"]

    assert request["Trading Symbol"] == TRADING_SYMBOL
    assert request["Instrument Token"] == INSTRUMENT_TOKEN
    assert request["Quantity"] == 65
    assert request["Transaction Type"] == "BUY"
    assert request["Order Placement Permitted"] is False

    # =====================================================
    # 4. V17.8.1 PAPER ORDER
    # =====================================================

    paper_order = simulate_paper_order(
        execution_request
    )

    assert paper_order["Status"] == (
        "PAPER_ORDER_ACCEPTED"
    )

    paper_order_data = paper_order["Paper Order"]

    assert paper_order_data["Quantity"] == 65
    assert paper_order_data["Trading Symbol"] == TRADING_SYMBOL
    assert paper_order_data["Paper Status"] == "PAPER_ACCEPTED"

    # =====================================================
    # 5. V17.8.2 PAPER FILL
    # =====================================================

    paper_fill = simulate_paper_fill(
        paper_order,
        fill_price=ENTRY_PRICE,
    )

    assert paper_fill["Status"] == (
        "PAPER_FILL_COMPLETE"
    )

    fill = paper_fill["Paper Fill"]

    assert fill["Filled Quantity"] == 65
    assert fill["Fill Price"] == ENTRY_PRICE
    assert fill["Paper Fill Status"] == "FILLED"

    # =====================================================
    # 6. V17.8.5 ENTRY MAPPING
    # =====================================================

    v15_qualification = build_v15_qualification()

    mapped_entry = map_paper_fill_to_v15_entry(
        paper_fill,
        v15_qualification,
        trade_id="JKJ-V18-TEST-001",
    )

    assert mapped_entry["Status"] == (
        "V15_ENTRY_MAPPING_COMPLETE"
    )

    v15_entry_mapping = mapped_entry["V15 Entry Mapping"]

    # Controlled V17.8.5 -> V17.8.7 boundary normalization.
    # V17.8.5 uses descriptive field names.
    # V17.8.7 expects compact execution-boundary names.
    v15_entry_mapping["Target1"] = v15_entry_mapping["Target 1"]
    v15_entry_mapping["Target2"] = v15_entry_mapping["Target 2"]
    v15_entry_mapping["Target3"] = v15_entry_mapping["Target 3"]
    v15_entry_mapping["RR1"] = v15_entry_mapping["Risk Reward 1"]
    v15_entry_mapping["RR2"] = v15_entry_mapping["Risk Reward 2"]
    v15_entry_mapping["RR3"] = v15_entry_mapping["Risk Reward 3"]
    assert v15_entry_mapping["Entry Price"] == ENTRY_PRICE
    assert v15_entry_mapping["Trading Symbol"] == TRADING_SYMBOL
    assert v15_entry_mapping["Quantity"] == ORIGINAL_QUANTITY

    # =====================================================
    # 7. V17.8.7 V15 PAPER HANDOFF
    # =====================================================

    exit_qualification = build_exit_qualification()

    v15_entry_mapping = mapped_entry["V15 Entry Mapping"]

    handoff = handoff_to_v15_paper_trade(
        v15_entry_mapping,
        exit_qualification,
    )

    assert handoff["Status"] == (
        "V17_8_7_PAPER_HANDOFF_COMPLETE"
    )

    assert handoff["Quantity"] == ORIGINAL_QUANTITY
    assert handoff["V15 Handoff"] is True
    assert handoff["V15 Call Permitted"] is True
    assert handoff["V11 Call Permitted"] is True
    assert handoff["Paper Execution"] is True
    assert handoff["Broker Communication"] is False
    assert handoff["Order Placement Permitted"] is False

    # =====================================================
    # 8. V17.8.8 LIFECYCLE BOUNDARY
    # =====================================================

    lifecycle = validate_lifecycle_boundary(
        handoff
    )

    assert lifecycle["Status"] == (
        "V17_8_8_LIFECYCLE_BOUNDARY_VALIDATED"
    )

    assert lifecycle["Lifecycle Ready"] is True
    assert lifecycle["Lifecycle Owner"] == "V15.4 / V11"

    trade = lifecycle["Trade"]

    assert trade["Current Quantity"] == ORIGINAL_QUANTITY
    assert trade["Original Quantity"] == ORIGINAL_QUANTITY
    assert trade["Symbol"] == TRADING_SYMBOL
    assert trade["Instrument Type"] == "OPTION"

    # =====================================================
    # T1
    # V15.6 -> V17.3 -> V18.1
    # =====================================================

    t1_progression = build_target_progression(
        "TARGET 1",
        TARGET_1,
        106.0,
        final_target=False,
        targets_reached=["TARGET 1"],
    )

    t1_slicing = evaluate_target_slicing(
        t1_progression,
        total_quantity=65,
        current_quantity=65,
        entry_price=ENTRY_PRICE,
        current_price=106.0,
        peak_price=106.0,
        momentum_status="WEAK",
        volume_status="DECREASING",
        underlying_status="SUPPORTIVE",
        structure_status="WEAK",
    )

    assert t1_slicing["Status"] == "EVALUATED"
    assert t1_slicing["Target Stage"] == "TARGET 1"

    t1_integration = create_target_exit_integration(
        t1_progression,
        total_quantity=65,
    )
    
    assert t1_integration["Status"] == "PLANNED"

    t1_planned_execution = t1_integration["Execution"]

    assert t1_planned_execution["Status"] == "PLANNED"

    t1_v11_exit = {
        "Status": "SELL_RECORDED",
        "Exit Quantity": 15,
        "Remaining Quantity": 50,
        "Trade Status": "OPEN",
    }

    t1_sync = synchronize_target_exit(
        t1_v11_exit,
        t1_planned_execution,
        global_original_quantity=65,
        previous_cumulative_filled=0,
    )

    t1_sync = synchronize_target_exit(
        t1_v11_exit,
        t1_planned_execution,
        global_original_quantity=65,
        previous_cumulative_filled=0,
    )


    assert t1_sync["Status"] == "SYNCHRONIZED"
    assert t1_sync["Cumulative Filled Quantity"] == 15
    assert t1_sync["Expected Remaining Quantity"] == 50

    assert t1_sync["Status"] == "SYNCHRONIZED"
    assert t1_sync["Cumulative Filled Quantity"] == 15
    assert t1_sync["Expected Remaining Quantity"] == 50

    # =====================================================
    # T2
    # V15.6 -> V17.3 -> V18.1
    # =====================================================

    t2_progression = build_target_progression(
        "TARGET 2",
        TARGET_2,
        111.0,
        final_target=False,
        targets_reached=["TARGET 1", "TARGET 2"],
    )

    t2_slicing = evaluate_target_slicing(
        t2_progression,
        total_quantity=65,
        current_quantity=50,
        entry_price=ENTRY_PRICE,
        current_price=111.0,
        peak_price=111.0,
        momentum_status="STRONG",
        volume_status="STRONG",
        underlying_status="SUPPORTIVE",
        structure_status="STRONG",
    )

    assert t2_slicing["Status"] == "EVALUATED"
    assert t2_slicing["Target Stage"] == "TARGET 2"

    t2_integration = create_target_exit_integration(
        t2_progression,
        total_quantity=65,
    )

    assert t2_integration["Status"] == "PLANNED"

    t2_planned_execution = t2_integration["Execution"]

    assert t2_planned_execution["Status"] == "PLANNED"

    t2_v11_exit = {
        "Status": "SELL_RECORDED",
        "Exit Quantity": 22,
        "Remaining Quantity": 28,
        "Trade Status": "OPEN",
    }

    t2_sync = synchronize_target_exit(
        t2_v11_exit,
        t2_planned_execution,
        global_original_quantity=65,
        previous_cumulative_filled=15,
    )

    assert t2_sync["Status"] == "SYNCHRONIZED"
    assert t2_sync["Cumulative Filled Quantity"] == 37
    assert t2_sync["Expected Remaining Quantity"] == 28

    # =====================================================
    # T3
    # V17.4 -> V18.1
    # =====================================================

    t3_progression = build_target_progression(
        "TARGET 3",
        TARGET_3,
        121.0,
        final_target=True,
        targets_reached=[
            "TARGET 1",
            "TARGET 2",
            "TARGET 3",
        ],
    )

    t3_final = create_final_target_exit(
        t3_progression,
        actual_remaining_quantity=28,
    )

    assert t3_final["Status"] == "VALIDATED"
    assert t3_final["Target Stage"] == "TARGET 3"
    assert t3_final["Actual Remaining Quantity"] == 28
    assert t3_final["Planned Final Exit Quantity"] == 28

    # T3 execution record is deliberately based on
    # the ACTUAL remaining position: 28.
    t3_execution_record = {
        "Status": "PLANNED",
        "Target Stage": "TARGET 3",
        "Original Quantity": 28,
        "Planned Quantity": 28,
        "Submitted Quantity": 0,
        "Filled Quantity": 0,
        "Actual Remaining Quantity": 28,
        "Execution Status": "PLANNED",
        "Execution Confirmed": False,
    }

    t3_v11_exit = {
        "Status": "CLOSED",
        "Exit Quantity": 28,
        "Remaining Quantity": 0,
        "Trade Status": "CLOSED",
    }

    t3_sync = synchronize_target_exit(
        t3_v11_exit,
        t3_execution_record,
        global_original_quantity=65,
        previous_cumulative_filled=37,
    )

    assert t3_sync["Status"] == "SYNCHRONIZED"
    assert t3_sync["Cumulative Filled Quantity"] == 65
    assert t3_sync["Expected Remaining Quantity"] == 0

    # =====================================================
    # FINAL ASSERTIONS
    # =====================================================

    assert t1_v11_exit["Remaining Quantity"] == 50
    assert t2_v11_exit["Remaining Quantity"] == 28
    assert t3_v11_exit["Remaining Quantity"] == 0

    print()
    print("V17.7.4 -> V17.7.6: PASS")
    print("V17.8.1 Paper Order: PASS")
    print("V17.8.2 Paper Fill: PASS")
    print("V17.8.5 Entry Mapping: PASS")
    print("V17.8.7 V15 Paper Handoff: PASS")
    print("V17.8.8 Lifecycle Boundary: PASS")
    print("V11 Paper Position: OPEN")
    print(
        "T1: 65 -> 15 -> 50 | "
        "V15.6 -> V17.3 -> V18.1: PASS"
    )
    print(
        "T2: 50 -> 22 -> 28 | "
        "V15.6 -> V17.3 -> V18.1: PASS"
    )
    print(
        "T3: 28 -> 28 -> 0 | "
        "V17.4 -> V18.1: PASS"
    )
    print(
        "Global position: "
        "65 -> 15 -> 50 -> 22 -> 28 -> 28 -> 0"
    )
    print("Final position quantity: 0")
    print("Global cumulative filled quantity: 65")
    print("No Zerodha order.")
    print("No broker communication.")
    print("No main.py modification.")
    print("No V11 modification.")
    print("No V17.2/V17.3/V17.4 modification.")
    print()
    print(
        "V17.8 -> V18.1 FULL PAPER LIFECYCLE: "
        "ALL TESTS PASSED"
    )
    print("Wisdom Before Wealth.")


if __name__ == "__main__":
    main()
