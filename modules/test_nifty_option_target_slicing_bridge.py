"""
JKJ AI Trader
V15.6 Target-to-Slicing Bridge Test

Wisdom Before Wealth.
"""

from modules.nifty_option_target_slicing_bridge import (
    evaluate_target_slicing,
)


def make_target_progression(
    target_event,
    target_price,
    current_price,
    final_target=False,
    targets_reached=None,
):
    return {
        "Status": "TARGET_REACHED",
        "Target Event": target_event,
        "Target Price": target_price,
        "Current Price": current_price,
        "Final Target": final_target,
        "Targets Reached": targets_reached or [target_event],
    }


# ---------------------------------------------------------
# Test 1 — Target 1 reached, strong conditions
# V11 should evaluate the position without using
# the TARGET full-exit branch.
# ---------------------------------------------------------

result = evaluate_target_slicing(
    target_progression=make_target_progression(
        "TARGET 1",
        103.0,
        103.0,
    ),
    total_quantity=100,
    current_quantity=100,
    entry_price=100.0,
    current_price=103.0,
    peak_price=103.0,
    momentum_status="STRONG",
    volume_status="STRONG",
    underlying_status="SUPPORTIVE",
    structure_status="STRONG",
)

assert result["Status"] == "EVALUATED"
assert result["Target Stage"] == "TARGET 1"
assert result["V11 Slice Plan"]["Position Status"] == "HOLD"
assert result["V11 Slice Plan"]["Exit Quantity"] == 0


# ---------------------------------------------------------
# Test 2 — Target 1 reached with weakening conditions
# V11 should be allowed to create a partial slice.
# ---------------------------------------------------------

result = evaluate_target_slicing(
    target_progression=make_target_progression(
        "TARGET 1",
        105.0,
        105.0,
    ),
    total_quantity=100,
    current_quantity=100,
    entry_price=100.0,
    current_price=105.0,
    peak_price=110.0,
    momentum_status="WEAK",
    volume_status="WEAK",
    underlying_status="SUPPORTIVE",
    structure_status="STRONG",
)

assert result["Status"] == "EVALUATED"
assert result["Target Stage"] == "TARGET 1"
assert result["V11 Slice Plan"]["Position Status"] == "PARTIAL EXIT"
assert result["V11 Slice Plan"]["Exit Quantity"] > 0
assert result["V11 Slice Plan"]["Exit Quantity"] < 100


# ---------------------------------------------------------
# Test 3 — Target 2 reached
# V11 still owns quantity decision.
# ---------------------------------------------------------

result = evaluate_target_slicing(
    target_progression=make_target_progression(
        "TARGET 2",
        106.0,
        107.0,
        targets_reached=["TARGET 1", "TARGET 2"],
    ),
    total_quantity=100,
    current_quantity=75,
    entry_price=100.0,
    current_price=107.0,
    peak_price=110.0,
    momentum_status="WEAK",
    volume_status="WEAK",
    underlying_status="SUPPORTIVE",
    structure_status="STRONG",
)

assert result["Status"] == "EVALUATED"
assert result["Target Stage"] == "TARGET 2"
assert (
    result["V11 Slice Plan"]["Exit Quantity"]
    <= 75
)


# ---------------------------------------------------------
# Test 4 — Target 3 reached
# Final target is correctly preserved.
# ---------------------------------------------------------

result = evaluate_target_slicing(
    target_progression=make_target_progression(
        "TARGET 3",
        109.0,
        110.0,
        final_target=True,
        targets_reached=[
            "TARGET 1",
            "TARGET 2",
            "TARGET 3",
        ],
    ),
    total_quantity=100,
    current_quantity=50,
    entry_price=100.0,
    current_price=110.0,
    peak_price=112.0,
    momentum_status="STRONG",
    volume_status="STRONG",
    underlying_status="SUPPORTIVE",
    structure_status="STRONG",
)

assert result["Status"] == "EVALUATED"
assert result["Target Stage"] == "TARGET 3"
assert result["Final Target"] is True


# ---------------------------------------------------------
# Test 5 — Invalid progression rejected
# ---------------------------------------------------------

result = evaluate_target_slicing(
    target_progression={
        "Status": "WAITING",
    },
    total_quantity=100,
    current_quantity=100,
    entry_price=100.0,
    current_price=103.0,
    peak_price=103.0,
)

assert result["Status"] == "REJECTED"


# ---------------------------------------------------------
# Test 6 — V15.6 must not determine a slice percentage
# ---------------------------------------------------------

result = evaluate_target_slicing(
    target_progression=make_target_progression(
        "TARGET 1",
        105.0,
        105.0,
    ),
    total_quantity=100,
    current_quantity=100,
    entry_price=100.0,
    current_price=105.0,
    peak_price=110.0,
    momentum_status="WEAK",
    volume_status="WEAK",
    underlying_status="SUPPORTIVE",
    structure_status="STRONG",
)

assert "Slice Percentage" in result["V11 Slice Plan"]
assert "Exit Quantity" in result["V11 Slice Plan"]


print("V15.6 Target-to-Slicing Bridge: ALL TESTS PASSED")
