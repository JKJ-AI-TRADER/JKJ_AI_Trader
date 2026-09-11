from intraday_position_slicing import calculate_slice_plan


def print_result(title, result):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

    for key, value in result.items():
        print(f"{key}: {value}")


# ---------------------------------------------------------
# TEST 1 — Healthy profitable trade
# Expected: HOLD
# ---------------------------------------------------------

result = calculate_slice_plan(
    total_quantity=300,
    current_quantity=300,
    entry_price=100,
    current_price=104,
    peak_price=105,
    exit_signal="NO EXIT CONDITION",
    momentum_status="STRONG",
    volume_status="STRONG",
    underlying_status="SUPPORTIVE",
    structure_status="STRONG",
)

print_result("TEST 1 — Healthy Trade", result)


# ---------------------------------------------------------
# TEST 2 — Profit protection
# Expected: PARTIAL EXIT
# ---------------------------------------------------------

result = calculate_slice_plan(
    total_quantity=300,
    current_quantity=300,
    entry_price=100,
    current_price=108,
    peak_price=110,
    exit_signal="WATCH — DETERIORATION WATCH",
    momentum_status="WEAK",
    volume_status="DECREASING",
    underlying_status="SUPPORTIVE",
    structure_status="STABLE",
)

print_result("TEST 2 — Profit Protection", result)


# ---------------------------------------------------------
# TEST 3 — Strong deterioration
# Expected: Larger PARTIAL EXIT
# ---------------------------------------------------------

result = calculate_slice_plan(
    total_quantity=300,
    current_quantity=225,
    entry_price=100,
    current_price=115,
    peak_price=120,
    exit_signal="EXIT — PROFIT PROTECTION",
    momentum_status="DETERIORATING",
    volume_status="DECREASING",
    underlying_status="DETERIORATING",
    structure_status="DETERIORATING",
)

print_result("TEST 3 — Strong Deterioration", result)


# ---------------------------------------------------------
# TEST 4 — Stop loss
# Expected: FULL EXIT
# ---------------------------------------------------------

result = calculate_slice_plan(
    total_quantity=300,
    current_quantity=300,
    entry_price=100,
    current_price=97,
    peak_price=101,
    exit_signal="EXIT — STOP LOSS",
    momentum_status="WEAK",
    volume_status="DECREASING",
    underlying_status="WEAK",
    structure_status="DETERIORATING",
)

print_result("TEST 4 — Stop Loss", result)


# ---------------------------------------------------------
# TEST 5 — Target reached
# Expected: FULL EXIT
# ---------------------------------------------------------

result = calculate_slice_plan(
    total_quantity=300,
    current_quantity=150,
    entry_price=100,
    current_price=120,
    peak_price=121,
    exit_signal="EXIT — TARGET REACHED",
    momentum_status="STRONG",
    volume_status="STRONG",
    underlying_status="SUPPORTIVE",
    structure_status="STRONG",
)

print_result("TEST 5 — Target Reached", result)


# ---------------------------------------------------------
# TEST 6 — No position remaining
# Expected: NO ACTION
# ---------------------------------------------------------

result = calculate_slice_plan(
    total_quantity=300,
    current_quantity=0,
    entry_price=100,
    current_price=110,
    peak_price=112,
    exit_signal="NO EXIT CONDITION",
)

print_result("TEST 6 — No Position", result)


# ---------------------------------------------------------
# TEST 7 — Invalid quantity
# Expected: NO ACTION
# ---------------------------------------------------------

result = calculate_slice_plan(
    total_quantity=300,
    current_quantity=400,
    entry_price=100,
    current_price=110,
    peak_price=112,
    exit_signal="NO EXIT CONDITION",
)

print_result("TEST 7 — Invalid Quantity", result)