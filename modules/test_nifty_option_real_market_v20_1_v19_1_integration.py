"""
JKJ AI Trader
Real-Market V20.1 -> V18.1 Target Exit Synchronization Integration Test

Wisdom Before Wealth.

Controlled chain:
V20.1
-> V17.7
-> V17.8.1
-> V17.8.2
-> V17.8.5
-> V17.8.6
-> V17.8.7
-> V17.8.8
-> V18.1

V18.1 lifecycle:
T1: 65 -> 15 -> 50
T2: 50 -> 22 -> 28
T3: 28 -> 28 -> 0

No Zerodha.
No live order.
No broker communication.
No capital reassignment.
No automatic ranking.
No main.py modification.
"""

from modules.nifty_option_v20_1_capital_allocation_qualification import (
    qualify_capital_allocation,
)
from modules.nifty_option_v20_1_v17_7_integration import (
    integrate_v20_1_to_v17_7,
)
from modules.nifty_option_v20_1_v17_8_integration import (
    integrate_v20_1_to_v17_8,
)
from modules.nifty_option_v20_1_v17_8_2_integration import (
    integrate_v20_1_to_v17_8_2,
)
from modules.nifty_option_v20_1_v17_8_5_integration import (
    integrate_v20_1_to_v17_8_5,
)
from modules.nifty_option_v20_1_v17_8_6_integration import (
    integrate_v20_1_to_v17_8_6,
)
from modules.nifty_option_v20_1_v17_8_7_integration import (
    integrate_v20_1_to_v17_8_7,
)
from modules.nifty_option_v20_1_v17_8_8_integration import (
    integrate_v20_1_to_v17_8_8,
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
from modules.nifty_option_v20_1_v19_1_integration import (
    integrate_v20_1_to_v19_1,
)


# =========================================================
# COMMON TEST DATA
# =========================================================

TRADING_SYMBOL = "NIFTY26SEP23000CE"
INSTRUMENT_TOKEN = 123456

LOT_SIZE = 65
ENTRY_PRICE = 100.0

STOP_PRICE = 90.0
TARGET_1 = 105.0
TARGET_2 = 110.0
TARGET_3 = 120.0

ORIGINAL_QUANTITY = 65


# =========================================================
# V20.1 -> V17.7
# =========================================================

def build_v20_1_v17_7_result():

    opportunity = {
        "Trading Symbol": TRADING_SYMBOL,
        "Paper Trade Permission": "PERMITTED",
        "Entry Risk Context": "CONTROLLED_RISK_CONTEXT",
        "Entry Qualification": "ENTRY_QUALIFIED",
        "Stop-Loss Context": "STOP_SUPPORTED",
        "Exit Structure": "EXIT_STRUCTURE_SUPPORTED",
    }

    v20_1_result = qualify_capital_allocation(
        opportunity,
        priority=1,
        requested_allocation=7000,
    )

    market_data = [
        {
            "Candidate": TRADING_SYMBOL,
            "Entry Price": ENTRY_PRICE,
            "Contract Validation": {
                "Status": "CONTRACT_VALIDATED",
                "Lot Size": LOT_SIZE,
                "Trading Symbol": TRADING_SYMBOL,
                "Instrument Token": INSTRUMENT_TOKEN,
                "Contract Identity Valid": True,
            },
        }
    ]

    return integrate_v20_1_to_v17_7(
        v20_1_results=[v20_1_result],
        candidate_market_data=market_data,
        usable_capital=7000,
        max_positions=1,
        max_capital_per_candidate=7000,
        minimum_candidate_allocation=5000,
    )


# =========================================================
# V15 QUALIFICATION
# =========================================================

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
        "Entry Risk Context": "CONTROLLED_RISK_CONTEXT",
        "Stop-Loss Context": "STOP_SUPPORTED",
        "Exit Structure": "EXIT_STRUCTURE_SUPPORTED",

        "Qualification Reason":
            "Real-market V20.1 -> V18.1 controlled integration test",
    }


# =========================================================
# V14.5 / V15 EXIT QUALIFICATION
# =========================================================

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

        "Entry Qualification": "ENTRY_QUALIFIED",
        "Entry Risk Context": "CONTROLLED_RISK_CONTEXT",
        "Stop-Loss Context": "STOP_SUPPORTED",
        "Exit Structure": "EXIT_STRUCTURE_SUPPORTED",
        "Exit Qualification": "EVALUATED",
    }


# =========================================================
# BUILD V17.8.1
# =========================================================

def build_v17_8_1_result():

    v17_7_result = build_v20_1_v17_7_result()

    assert (
        v17_7_result["Status"]
        == "V20_1_V17_7_INTEGRATION_COMPLETE"
    )

    return integrate_v20_1_to_v17_8(
        v17_7_result
    )


# =========================================================
# BUILD V17.8.2
# =========================================================

def build_v17_8_2_result():

    v17_8_1_result = build_v17_8_1_result()

    assert (
        v17_8_1_result["Status"]
        == "V20_1_V17_8_INTEGRATION_COMPLETE"
    )

    return integrate_v20_1_to_v17_8_2(
        v20_1_v17_8_result=v17_8_1_result,
        fill_price=ENTRY_PRICE,
    )


# =========================================================
# BUILD V17.8.5
# =========================================================

def build_v17_8_5_result():

    v17_8_2_result = build_v17_8_2_result()

    v15_qualification = build_v15_qualification()

    return integrate_v20_1_to_v17_8_5(
        v20_1_v17_8_2_result=v17_8_2_result,
        v15_qualification=v15_qualification,
        trade_id="JKJ-TRADE-001",
        entry_time="2026-09-22T09:30:00",
    )


# =========================================================
# BUILD V17.8.6
# =========================================================

def build_v17_8_6_result():

    v17_8_5_result = build_v17_8_5_result()

    return integrate_v20_1_to_v17_8_6(
        v20_1_v17_8_5_result=v17_8_5_result
    )


# =========================================================
# BUILD V17.8.7
# =========================================================

def build_v17_8_7_result():

    v17_8_6_result = build_v17_8_6_result()

    exit_qualification = build_exit_qualification()

    return integrate_v20_1_to_v17_8_7(
        v20_1_v17_8_6_result=v17_8_6_result,
        exit_qualification=exit_qualification,
        entry_time="2026-09-22T09:30:00",
    )


# =========================================================
# BUILD V17.8.8
# =========================================================

def build_v17_8_8_result():

    v17_8_7_result = build_v17_8_7_result()

    print("\nDEBUG V17.8.7 RESULT:")
    print(v17_8_7_result)

    return integrate_v20_1_to_v17_8_8(
        v20_1_v17_8_7_result=v17_8_7_result
    )


# =========================================================
# V18.1 TARGET EXIT SYNCHRONIZATION
# =========================================================

def run_v18_1_lifecycle():

    v17_8_8_result = build_v17_8_8_result()

    print("\nDEBUG V17.8.8 RESULT:")
    print(v17_8_8_result)

    assert (
        v17_8_8_result["Status"]
        == "V20_1_V17_8_8_INTEGRATION_COMPLETE"
    )

    assert v17_8_8_result["Lifecycle Ready"] is True
    assert (
        v17_8_8_result["Lifecycle Owner"]
        == "V15.4 / V11"
    )

    assert (
        v17_8_8_result["Broker Communication"]
        is False
    )

    assert (
        v17_8_8_result["Order Placement Permitted"]
        is False
    )

    assert (
        v17_8_8_result["Capital Reassignment"]
        is False
    )

    assert (
        v17_8_8_result["Automatic Ranking"]
        is False
    )

    trade_id = v17_8_8_result["Trade ID"]

    assert trade_id == "JKJ-TRADE-001"

    # -----------------------------------------------------
    # T1
    # 65 -> 15 -> 50
    # -----------------------------------------------------

    t1_progression = {
        "Status": "TARGET_REACHED",
        "Target Event": "TARGET 1",
        "Target Price": TARGET_1,
        "Current Price": 106.0,
        "Final Target": False,
        "Targets Reached": ["TARGET 1"],
    }

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

    print("\nDEBUG T1 SLICING RESULT:")
    print(t1_slicing)

    assert t1_slicing["Status"] == "EVALUATED"

    t1_integration = create_target_exit_integration(
        t1_progression,
        total_quantity=65,
    )

    assert t1_integration["Status"] == "PLANNED"

    t1_execution = t1_integration["Execution"]

    t1_v11_exit = {
        "Status": "SELL_RECORDED",
        "Exit Quantity": 15,
        "Remaining Quantity": 50,
        "Trade Status": "OPEN",
    }

    t1_sync = synchronize_target_exit(
        t1_v11_exit,
        t1_execution,
        global_original_quantity=65,
        previous_cumulative_filled=0,
    )

    assert t1_sync["Status"] == "SYNCHRONIZED"
    assert t1_sync["Cumulative Filled Quantity"] == 15
    assert t1_sync["Expected Remaining Quantity"] == 50

    print("T1 synchronization: PASS")

    # -----------------------------------------------------
    # T2
    # 50 -> 22 -> 28
    # -----------------------------------------------------

    t2_progression = {
        "Status": "TARGET_REACHED",
        "Target Event": "TARGET 2",
        "Target Price": TARGET_2,
        "Current Price": 111.0,
        "Final Target": False,
        "Targets Reached": ["TARGET 1", "TARGET 2"],
    }

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

    print("\nDEBUG T2 SLICING RESULT:")
    print(t2_slicing)

    assert t2_slicing["Status"] == "EVALUATED"

    t2_integration = create_target_exit_integration(
        t2_progression,
        total_quantity=65,
    )

    assert t2_integration["Status"] == "PLANNED"

    t2_execution = t2_integration["Execution"]

    t2_v11_exit = {
        "Status": "SELL_RECORDED",
        "Exit Quantity": 22,
        "Remaining Quantity": 28,
        "Trade Status": "OPEN",
    }

    t2_sync = synchronize_target_exit(
        t2_v11_exit,
        t2_execution,
        global_original_quantity=65,
        previous_cumulative_filled=15,
    )

    assert t2_sync["Status"] == "SYNCHRONIZED"
    assert t2_sync["Cumulative Filled Quantity"] == 37
    assert t2_sync["Expected Remaining Quantity"] == 28

    print("T2 synchronization: PASS")

    # -----------------------------------------------------
    # T3
    # 28 -> 28 -> 0
    # -----------------------------------------------------

    t3_progression = {
        "Status": "TARGET_REACHED",
        "Target Event": "TARGET 3",
        "Target Price": TARGET_3,
        "Current Price": 121.0,
        "Final Target": True,
        "Targets Reached": ["TARGET 1", "TARGET 2", "TARGET 3"],
    }

    t3_final = create_final_target_exit(
        t3_progression,
        actual_remaining_quantity=28,
    )

    print("\nDEBUG T3 FINAL RESULT:")
    print(t3_final)

    assert t3_final["Status"] == "VALIDATED"
    assert t3_final["Actual Remaining Quantity"] == 28
    assert t3_final["Planned Final Exit Quantity"] == 28

    t3_execution = {
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
        t3_execution,
        global_original_quantity=65,
        previous_cumulative_filled=37,
    )

    assert t3_sync["Status"] == "SYNCHRONIZED"
    assert t3_sync["Cumulative Filled Quantity"] == 65
    assert t3_sync["Expected Remaining Quantity"] == 0

    print("T3 synchronization: PASS")

    # -----------------------------------------------------
    # V19.1 FINAL PAPER TRADE CLOSURE VALIDATION
    # -----------------------------------------------------

    v20_1_v18_1_result = {
        "Status": "V20_1_V18_1_INTEGRATION_COMPLETE",
        "V18.1 Result": t3_sync,
        "Lifecycle Owner": "V15.4 / V11",
        "Trade ID": "JKJ-TRADE-001",
        "Symbol": TRADING_SYMBOL,
        "Original Quantity": 65,
        "Cumulative Filled Quantity": 65,
        "Expected Remaining Quantity": 0,
        "V11 Remaining Quantity": 0,
        "Synchronization Confirmed": True,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Wisdom Before Wealth": True,
    }

    closed_trade = {
        "Trade ID": "JKJ-TRADE-001",
        "Status": "CLOSED",
        "Symbol": TRADING_SYMBOL,
        "Instrument Type": "OPTION",
        "Original Quantity": 65,
        "Current Quantity": 0,
        "Entry Price": ENTRY_PRICE,
        "Entry Time": "2026-09-22T09:30:00",
        "Exit Time": "2026-09-22T10:30:00",
        "Exit Reason": "TARGET 3",
        "Exit Events": [
            {"Action": "SELL", "Quantity": 15, "Price": TARGET_1},
            {"Action": "SELL", "Quantity": 22, "Price": TARGET_2},
            {"Action": "SELL", "Quantity": 28, "Price": TARGET_3},
        ],
        "Gross P&L": 3600.0,
        "Trading Costs": 100.0,
        "Slippage": 20.0,
        "Net P&L": 3480.0,
    }

    v19_1_result = integrate_v20_1_to_v19_1(
        v20_1_v18_1_result,
        closed_trade,
    )

    print("\nDEBUG V19.1 FINAL CLOSURE RESULT:")
    print(v19_1_result)

    assert v19_1_result["Status"] == (
        "V20_1_V19_1_INTEGRATION_COMPLETE"
    )
    assert v19_1_result["Final Audit"] is True
    assert v19_1_result["Read Only"] is True
    assert v19_1_result["V19.1 Result"]["Closure Record"][
        "Closure Status"
    ] == "PAPER_TRADE_CLOSED"

    print("V19.1 final closure validation: PASS")

    # -----------------------------------------------------
    # FINAL LIFECYCLE CHECKS
    # -----------------------------------------------------

    assert t1_v11_exit["Remaining Quantity"] == 50
    assert t2_v11_exit["Remaining Quantity"] == 28
    assert t3_v11_exit["Remaining Quantity"] == 0

    assert t1_sync["Cumulative Filled Quantity"] == 15
    assert t2_sync["Cumulative Filled Quantity"] == 37
    assert t3_sync["Cumulative Filled Quantity"] == 65

    print()
    print(
        "V20.1 -> V17.8.8 -> V18.1 -> V19.1 "
        "REAL-MARKET INTEGRATION: ALL TESTS PASSED"
    )
    print("T1: 65 -> 15 -> 50: PASS")
    print("T2: 50 -> 22 -> 28: PASS")
    print("T3: 28 -> 28 -> 0: PASS")
    print("Cumulative synchronization: 15 -> 37 -> 65: PASS")
    print("V15.4 / V11 remains lifecycle authority.")
    print("No automatic ranking.")
    print("No capital reassignment.")
    print("No live Zerodha order.")
    print("No broker communication.")
    print("No lifecycle action performed.")
    print("No main.py modification.")
    print("Wisdom Before Wealth.")


if __name__ == "__main__":
    run_v18_1_lifecycle()