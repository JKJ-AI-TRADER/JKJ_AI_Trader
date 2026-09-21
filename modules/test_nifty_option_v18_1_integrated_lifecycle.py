"""
JKJ AI Trader
V18.1 Integrated Paper Target Exit Lifecycle Test

Lifecycle:

V15.6
    ↓
V17.3
    ↓
V11 actual paper-exit event
    ↓
V18.1 synchronization
    ↓
V17.4 final target
    ↓
V11 final paper-exit event
    ↓
V18.1 final synchronization

Wisdom Before Wealth.
"""

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
# Helper — simulated actual V11 paper-exit result
# ---------------------------------------------------------

def make_v11_exit_result(
    exit_quantity,
    remaining_quantity,
    trade_status="OPEN",
):
    return {
        "Status": "SELL_RECORDED",
        "Exit Quantity": exit_quantity,
        "Remaining Quantity": remaining_quantity,
        "Trade Status": trade_status,
    }


# ---------------------------------------------------------
# GLOBAL PAPER POSITION
# ---------------------------------------------------------

GLOBAL_ORIGINAL_QUANTITY = 65


# ---------------------------------------------------------
# TEST 1 — V15.6 TARGET 1
# ---------------------------------------------------------

target_1 = {
    "Status": "TARGET_REACHED",
    "Target Event": "TARGET 1",
    "Target Price": 110,
    "Current Price": 110,
    "Final Target": False,
    "Targets Reached": ["TARGET 1"],
}

v15_t1 = evaluate_target_slicing(
    target_progression=target_1,
    total_quantity=65,
    current_quantity=65,
    entry_price=100,
    current_price=110,
    peak_price=112,
)

assert v15_t1["Status"] == "EVALUATED"
assert v15_t1["Target Stage"] == "TARGET 1"


# ---------------------------------------------------------
# TEST 2 — V17.3 TARGET 1 EXECUTION STATE
# ---------------------------------------------------------

v17_t1 = create_target_exit_integration(
    target_progression=target_1,
    total_quantity=65,
)

assert v17_t1["Status"] == "PLANNED"
assert v17_t1["Target Stage"] == "TARGET 1"

t1_execution = v17_t1["Execution"]

assert t1_execution["Status"] == "PLANNED"
assert t1_execution["Original Quantity"] == 65


# ---------------------------------------------------------
# TEST 3 — ACTUAL V11 TARGET 1 EXIT
# ---------------------------------------------------------

v11_t1 = make_v11_exit_result(
    exit_quantity=15,
    remaining_quantity=50,
)

# ---------------------------------------------------------
# TEST 4 — V18.1 TARGET 1 SYNCHRONIZATION
# ---------------------------------------------------------

sync_t1 = synchronize_target_exit(
    v11_exit_result=v11_t1,
    execution_record=t1_execution,
    global_original_quantity=65,
    previous_cumulative_filled=0,
)

assert sync_t1["Status"] == "SYNCHRONIZED"
assert sync_t1["Target Stage"] == "TARGET 1"
assert sync_t1["V11 Event Exit Quantity"] == 15
assert sync_t1["Cumulative Filled Quantity"] == 15
assert sync_t1["V11 Remaining Quantity"] == 50
assert sync_t1["Expected Remaining Quantity"] == 50


# ---------------------------------------------------------
# TEST 5 — V15.6 TARGET 2
# ---------------------------------------------------------

target_2 = {
    "Status": "TARGET_REACHED",
    "Target Event": "TARGET 2",
    "Target Price": 120,
    "Current Price": 120,
    "Final Target": False,
    "Targets Reached": [
        "TARGET 1",
        "TARGET 2",
    ],
}

v15_t2 = evaluate_target_slicing(
    target_progression=target_2,
    total_quantity=65,
    current_quantity=50,
    entry_price=100,
    current_price=120,
    peak_price=122,
)

assert v15_t2["Status"] == "EVALUATED"
assert v15_t2["Target Stage"] == "TARGET 2"


# ---------------------------------------------------------
# TEST 6 — V17.3 TARGET 2 EXECUTION STATE
# ---------------------------------------------------------

v17_t2 = create_target_exit_integration(
    target_progression=target_2,
    total_quantity=65,
)

assert v17_t2["Status"] == "PLANNED"
assert v17_t2["Target Stage"] == "TARGET 2"

t2_execution = v17_t2["Execution"]

assert t2_execution["Status"] == "PLANNED"
assert t2_execution["Original Quantity"] == 65


# ---------------------------------------------------------
# TEST 7 — ACTUAL V11 TARGET 2 EXIT
# ---------------------------------------------------------

v11_t2 = make_v11_exit_result(
    exit_quantity=22,
    remaining_quantity=28,
)

# ---------------------------------------------------------
# TEST 8 — V18.1 TARGET 2 SYNCHRONIZATION
# ---------------------------------------------------------

sync_t2 = synchronize_target_exit(
    v11_exit_result=v11_t2,
    execution_record=t2_execution,
    global_original_quantity=65,
    previous_cumulative_filled=15,
)

assert sync_t2["Status"] == "SYNCHRONIZED"
assert sync_t2["Target Stage"] == "TARGET 2"
assert sync_t2["V11 Event Exit Quantity"] == 22
assert sync_t2["Cumulative Filled Quantity"] == 37
assert sync_t2["V11 Remaining Quantity"] == 28
assert sync_t2["Expected Remaining Quantity"] == 28


# ---------------------------------------------------------
# TEST 9 — V15.6 TARGET 3
# ---------------------------------------------------------

target_3 = {
    "Status": "TARGET_REACHED",
    "Target Event": "TARGET 3",
    "Target Price": 130,
    "Current Price": 130,
    "Final Target": True,
    "Targets Reached": [
        "TARGET 1",
        "TARGET 2",
        "TARGET 3",
    ],
}

v15_t3 = evaluate_target_slicing(
    target_progression=target_3,
    total_quantity=65,
    current_quantity=28,
    entry_price=100,
    current_price=130,
    peak_price=132,
)

assert v15_t3["Status"] == "EVALUATED"
assert v15_t3["Target Stage"] == "TARGET 3"
assert v15_t3["Final Target"] is True


# ---------------------------------------------------------
# TEST 10 — V17.4 FINAL TARGET USING ACTUAL REMAINING
# ---------------------------------------------------------

v17_t3 = create_final_target_exit(
    target_progression=target_3,
    actual_remaining_quantity=28,
)

assert v17_t3["Status"] == "VALIDATED"
assert v17_t3["Target Stage"] == "TARGET 3"
assert v17_t3["Final Target"] is True
assert v17_t3["Actual Remaining Quantity"] == 28
assert v17_t3["Planned Final Exit Quantity"] == 28


# ---------------------------------------------------------
# TEST 11 — ACTUAL V11 FINAL EXIT
# ---------------------------------------------------------

v11_t3 = make_v11_exit_result(
    exit_quantity=28,
    remaining_quantity=0,
    trade_status="CLOSED",
)


# ---------------------------------------------------------
# TEST 12 — V18.1 FINAL SYNCHRONIZATION
# ---------------------------------------------------------

#
# Important:
#
# V17.4 operates on the actual remaining quantity of 28.
#
# V18.1 reconciles this event against the original
# global position quantity of 65.
#

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

sync_t3 = synchronize_target_exit(
    v11_exit_result=v11_t3,
    execution_record=t3_execution,
    global_original_quantity=65,
    previous_cumulative_filled=37,
)

assert sync_t3["Status"] == "SYNCHRONIZED"
assert sync_t3["Target Stage"] == "TARGET 3"
assert sync_t3["V11 Event Exit Quantity"] == 28
assert sync_t3["Previous Cumulative Filled"] == 37
assert sync_t3["Cumulative Filled Quantity"] == 65
assert sync_t3["V11 Remaining Quantity"] == 0
assert sync_t3["Expected Remaining Quantity"] == 0
assert sync_t3["V17.2 Execution Status"] == "FILLED"
assert sync_t3["V17.2 Execution Confirmed"] is True


# ---------------------------------------------------------
# TEST 13 — COMPLETE GLOBAL LIFECYCLE
# ---------------------------------------------------------

assert sync_t1["Cumulative Filled Quantity"] == 15
assert sync_t2["Cumulative Filled Quantity"] == 37
assert sync_t3["Cumulative Filled Quantity"] == 65

assert sync_t1["V11 Remaining Quantity"] == 50
assert sync_t2["V11 Remaining Quantity"] == 28
assert sync_t3["V11 Remaining Quantity"] == 0

assert (
    sync_t3["Cumulative Filled Quantity"]
    == GLOBAL_ORIGINAL_QUANTITY
)


# ---------------------------------------------------------
# FINAL VALIDATION
# ---------------------------------------------------------

print(
    "V18.1 Integrated Paper Target Exit Lifecycle: "
    "ALL TESTS PASSED"
)

print(
    "V15.6 Target 1 -> V17.3 -> V11 -> V18.1: PASS"
)

print(
    "V15.6 Target 2 -> V17.3 -> V11 -> V18.1: PASS"
)

print(
    "V15.6 Target 3 -> V17.4 -> V11 -> V18.1: PASS"
)

print(
    "Global position: 65 -> 15 -> 50 -> 22 -> 28 -> 28 -> 0"
)

print(
    "V17.4 T3 actual remaining quantity: 28"
)

print(
    "V18.1 global cumulative filled quantity: 65"
)

print(
    "Final position quantity: 0"
)

print("No V11 modification.")
print("No V17.2 modification.")
print("No V17.3 modification.")
print("No V17.4 modification.")
print("No Zerodha order.")
print("No main.py modification.")
print("Wisdom Before Wealth.")