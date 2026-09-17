"""
JKJ AI Trader
V15 Complete Paper Trade Lifecycle Test

Purpose:
    Validate the complete V15.1 → V15.6 paper-trading flow.

Wisdom Before Wealth.
"""

from modules.nifty_option_paper_trade_coordinator import (
    create_qualified_paper_trade,
)
from modules.nifty_option_paper_position_lifecycle import (
    update_paper_position,
    process_paper_position_exit,
)
from modules.nifty_option_target_progression import (
    evaluate_target_progression,
)
from modules.nifty_option_target_slicing_bridge import (
    evaluate_target_slicing,
)


def make_exit_qualification():
    return {
        "Status": "EVALUATED",
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
        "Risk Reward 1": 1.0,
        "Risk Reward 2": 2.0,
        "Risk Reward 3": 3.0,
        "Entry Qualification": "ENTRY_QUALIFIED",
        "Entry Risk Context": "CONTROLLED_RISK_CONTEXT",
        "Stop-Loss Context": "STOP_SUPPORTED",
        "Exit Structure": "EXIT_STRUCTURE_SUPPORTED",
    }


def make_target_data():
    return {
        **make_exit_qualification(),
        "Status": "TARGETS_VALIDATED",
    }


# ---------------------------------------------------------
# 1. Qualified paper trade entry
# ---------------------------------------------------------

result = create_qualified_paper_trade(
    exit_qualification=make_exit_qualification(),
    quantity=75,
    trade_id="JKJ-V15-E2E-001",
    entry_time="2026-09-17 15:15:00",
)

assert result["Status"] == "PAPER_TRADE_OPENED"

trade = result["Trade"]

assert trade["Status"] == "OPEN"
assert trade["Current Quantity"] == 75
assert trade["Entry Price"] == 103.0

print("V15 Paper Entry: PASS")


# ---------------------------------------------------------
# 2. Price update
# ---------------------------------------------------------

result = update_paper_position(
    trade,
    105.0,
)

assert trade["Status"] == "OPEN"
assert trade["Current Price"] == 105.0
assert trade["Peak Price"] == 105.0

print("V15 Price Update: PASS")


# ---------------------------------------------------------
# 3. Target 1 progression
# ---------------------------------------------------------

target_data = make_target_data()

target_result = evaluate_target_progression(
    target_data=target_data,
    current_price=106.0,
    targets_reached=[],
)

assert target_result["Status"] == "TARGET_REACHED"
assert target_result["Target Event"] == "TARGET 1"

print("V15 Target 1: PASS")


# ---------------------------------------------------------
# 4. Target 1 → V11 slicing
# ---------------------------------------------------------

slice_result = evaluate_target_slicing(
    target_progression=target_result,
    total_quantity=75,
    current_quantity=75,
    entry_price=103.0,
    current_price=106.0,
    peak_price=106.0,
    momentum_status="WEAK",
    volume_status="WEAK",
    underlying_status="SUPPORTIVE",
    structure_status="STRONG",
)

assert slice_result["Status"] == "EVALUATED"

slice_plan = slice_result["V11 Slice Plan"]

assert slice_plan["Exit Quantity"] >= 0
assert slice_plan["Exit Quantity"] <= 75

print("V15 Target 1 → V11 Slicing: PASS")


# ---------------------------------------------------------
# 5. Target 2 progression
# ---------------------------------------------------------

target_result = evaluate_target_progression(
    target_data=target_data,
    current_price=109.0,
    targets_reached=["TARGET 1"],
)

assert target_result["Status"] == "TARGET_REACHED"
assert target_result["Target Event"] == "TARGET 2"

print("V15 Target 2: PASS")


# ---------------------------------------------------------
# 6. Target 3 progression
# ---------------------------------------------------------

target_result = evaluate_target_progression(
    target_data=target_data,
    current_price=112.0,
    targets_reached=["TARGET 1", "TARGET 2"],
)

assert target_result["Status"] == "TARGET_REACHED"
assert target_result["Target Event"] == "TARGET 3"
assert target_result["Final Target"] is True

print("V15 Target 3: PASS")


# ---------------------------------------------------------
# 7. Final paper position exit
# ---------------------------------------------------------

result = process_paper_position_exit(
    trade=trade,
    current_price=112.0,
    exit_signal="MOMENTUM REVERSAL",
    momentum_status="REVERSING",
    volume_status="DECREASING",
    underlying_status="WEAK",
    structure_status="WEAK",
)

assert trade["Status"] == "CLOSED"
assert trade["Current Quantity"] == 0
assert len(trade["Exit Events"]) >= 1

print("V15 Final Paper Exit: PASS")
print("V15 Complete Exit History: PASS")

print()
print("V15.1-V15.6 Complete Lifecycle: ALL TESTS PASSED")
