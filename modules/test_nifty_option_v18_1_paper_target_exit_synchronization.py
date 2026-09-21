"""
JKJ AI Trader
V18.1 Paper Target Exit Synchronization Test

Wisdom Before Wealth.
"""

from modules.nifty_option_target_exit_execution import (
    create_target_exit_execution,
)

from modules.nifty_option_v18_1_paper_target_exit_synchronization import (
    synchronize_target_exit,
)


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
# TEST 1 — TARGET 1 partial synchronization
# ---------------------------------------------------------

original_quantity = 65

t1_execution = create_target_exit_execution(
    target_stage="TARGET 1",
    original_quantity=65,
    planned_quantity=22,
)

v11_t1 = make_v11_exit_result(
    exit_quantity=15,
    remaining_quantity=50,
)

result_t1 = synchronize_target_exit(
    v11_exit_result=v11_t1,
    execution_record=t1_execution,
    global_original_quantity=65,
    previous_cumulative_filled=0,
)

assert result_t1["Status"] == "SYNCHRONIZED"
assert result_t1["Target Stage"] == "TARGET 1"
assert result_t1["V11 Event Exit Quantity"] == 15
assert result_t1["Cumulative Filled Quantity"] == 15
assert result_t1["V11 Remaining Quantity"] == 50
assert result_t1["Expected Remaining Quantity"] == 50
assert result_t1["V17.2 Execution Status"] == "PARTIAL"
assert result_t1["V17.2 Execution Confirmed"] is True


# ---------------------------------------------------------
# TEST 2 — TARGET 2 full synchronization
# ---------------------------------------------------------

t2_execution = create_target_exit_execution(
    target_stage="TARGET 2",
    original_quantity=65,
    planned_quantity=22,
)

v11_t2 = make_v11_exit_result(
    exit_quantity=22,
    remaining_quantity=28,
)

result_t2 = synchronize_target_exit(
    v11_exit_result=v11_t2,
    execution_record=t2_execution,
    global_original_quantity=65,
    previous_cumulative_filled=15,
)

assert result_t2["Status"] == "SYNCHRONIZED"
assert result_t2["Target Stage"] == "TARGET 2"
assert result_t2["V11 Event Exit Quantity"] == 22
assert result_t2["Cumulative Filled Quantity"] == 37
assert result_t2["V11 Remaining Quantity"] == 28
assert result_t2["Expected Remaining Quantity"] == 28
assert result_t2["V17.2 Execution Status"] == "FILLED"
assert result_t2["V17.2 Execution Confirmed"] is True


# ---------------------------------------------------------
# TEST 3 — TARGET 3 final synchronization
# ---------------------------------------------------------

# V17.4 creates the T3 execution using the
# actual remaining quantity: 28.

t3_execution = create_target_exit_execution(
    target_stage="TARGET 3",
    original_quantity=28,
    planned_quantity=28,
)

v11_t3 = make_v11_exit_result(
    exit_quantity=28,
    remaining_quantity=0,
    trade_status="CLOSED",
)

result_t3 = synchronize_target_exit(
    v11_exit_result=v11_t3,
    execution_record=t3_execution,
    global_original_quantity=65,
    previous_cumulative_filled=37,
)

assert result_t3["Status"] == "SYNCHRONIZED"
assert result_t3["Target Stage"] == "TARGET 3"
assert result_t3["V11 Event Exit Quantity"] == 28
assert result_t3["Cumulative Filled Quantity"] == 65
assert result_t3["V11 Remaining Quantity"] == 0
assert result_t3["Expected Remaining Quantity"] == 0
assert result_t3["V17.2 Execution Status"] == "FILLED"
assert result_t3["V17.2 Execution Confirmed"] is True


# ---------------------------------------------------------
# TEST 4 — Complete sequential lifecycle
# ---------------------------------------------------------

assert result_t1["Cumulative Filled Quantity"] == 15
assert result_t2["Cumulative Filled Quantity"] == 37
assert result_t3["Cumulative Filled Quantity"] == 65

assert result_t1["V11 Remaining Quantity"] == 50
assert result_t2["V11 Remaining Quantity"] == 28
assert result_t3["V11 Remaining Quantity"] == 0

assert (
    result_t3["Cumulative Filled Quantity"]
    == original_quantity
)


# ---------------------------------------------------------
# TEST 5 — V11/V18 mismatch must be blocked
# ---------------------------------------------------------

t2_mismatch_execution = create_target_exit_execution(
    target_stage="TARGET 2",
    original_quantity=65,
    planned_quantity=22,
)

v11_mismatch = make_v11_exit_result(
    exit_quantity=22,
    remaining_quantity=30,
)

result_mismatch = synchronize_target_exit(
    v11_exit_result=v11_mismatch,
    execution_record=t2_mismatch_execution,
    global_original_quantity=65,
    previous_cumulative_filled=15,
)

assert result_mismatch["Status"] == "SYNCHRONIZATION_BLOCKED"
assert result_mismatch["Synchronization Confirmed"] is False


# ---------------------------------------------------------
# TEST 6 — Zero exit must be blocked
# ---------------------------------------------------------

t1_zero_execution = create_target_exit_execution(
    target_stage="TARGET 1",
    original_quantity=65,
    planned_quantity=22,
)

v11_zero = make_v11_exit_result(
    exit_quantity=0,
    remaining_quantity=65,
)

result_zero = synchronize_target_exit(
    v11_exit_result=v11_zero,
    execution_record=t1_zero_execution,
    global_original_quantity=65,
    previous_cumulative_filled=0,
)

assert result_zero["Status"] == "SYNCHRONIZATION_BLOCKED"


# ---------------------------------------------------------
# TEST 7 — Over-execution must be blocked
# ---------------------------------------------------------

t3_over_execution = create_target_exit_execution(
    target_stage="TARGET 3",
    original_quantity=65,
    planned_quantity=28,
)

v11_over_execution = make_v11_exit_result(
    exit_quantity=30,
    remaining_quantity=0,
    trade_status="CLOSED",
)

result_over = synchronize_target_exit(
    v11_exit_result=v11_over_execution,
    execution_record=t3_over_execution,
    global_original_quantity=65,
    previous_cumulative_filled=37,
)

assert result_over["Status"] == "SYNCHRONIZATION_BLOCKED"


# ---------------------------------------------------------
# TEST 8 — Target-stage ownership remains independent
# ---------------------------------------------------------

assert result_t1["Target Stage"] == "TARGET 1"
assert result_t2["Target Stage"] == "TARGET 2"
assert result_t3["Target Stage"] == "TARGET 3"

assert (
    result_t1["V17.2 Execution State"]["Target Stage"]
    == "TARGET 1"
)

assert (
    result_t2["V17.2 Execution State"]["Target Stage"]
    == "TARGET 2"
)

assert (
    result_t3["V17.2 Execution State"]["Target Stage"]
    == "TARGET 3"
)


print(
    "V18.1 Paper Target Exit Synchronization: ALL TESTS PASSED"
)

print(
    "T1: 65 -> 15 -> 50"
)

print(
    "T2: 50 -> 22 -> 28"
)

print(
    "T3: 28 -> 28 -> 0"
)

print(
    "V11 actual quantity reconciled with V17.2 target-stage state."
)

print(
    "Mismatch and over-execution safeguards validated."
)

print("No V11 modification.")
print("No V17.2 modification.")
print("No Zerodha order.")