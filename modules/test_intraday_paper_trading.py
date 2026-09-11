from intraday_paper_trading import (
    open_paper_trade,
    update_paper_price,
    process_paper_exit,
    get_paper_position,
)


print("\n=========================================")
print("JKJ PAPER TRADING ENGINE V1 TEST")
print("=========================================")


# ---------------------------------------------------------
# TEST 1 — Open paper trade
# ---------------------------------------------------------

trade = open_paper_trade(
    trade_id="PAPER-001",
    symbol="NIFTY25000CE",
    instrument_type="options",
    entry_price=100,
    quantity=300,
    stop_loss=95,
    target=120,
    momentum_score=86,
    entry_status="STRONG ENTRY",
    entry_reason="Momentum + volume + underlying confirmation",
    expiry="2026-09-17",
    strike=25000,
    option_type="CE",
    underlying="NIFTY",
    entry_time="2026-09-11 10:15:00",
)

print("\nTEST 1 — OPEN PAPER TRADE")
print("-----------------------------------------")
print("Trade ID:", trade.get("Trade ID"))
print("Status:", trade.get("Status"))
print("Quantity:", trade.get("Current Quantity"))
print("Entry Price:", trade.get("Entry Price"))

if (
    trade.get("Status") == "OPEN"
    and trade.get("Current Quantity") == 300
):
    print("PASS")
else:
    print("FAIL")


# ---------------------------------------------------------
# TEST 2 — Price rises and peak is updated
# ---------------------------------------------------------

result = update_paper_price(
    trade,
    110,
)

print("\nTEST 2 — UPDATE PRICE / PEAK")
print("-----------------------------------------")
print(result)

if (
    trade.get("Current Price") == 110
    and trade.get("Peak Price") == 110
    and trade.get("Peak Profit %") == 10
):
    print("PASS")
else:
    print("FAIL")


# ---------------------------------------------------------
# TEST 3 — First partial exit
# ---------------------------------------------------------

result = process_paper_exit(
    trade=trade,
    current_price=108,
    exit_signal="WATCH — DETERIORATION WATCH",
    momentum_status="WEAK",
    volume_status="DECREASING",
    underlying_status="SUPPORTIVE",
    structure_status="STABLE",
    costs=65,
    slippage=10,
    timestamp="2026-09-11 10:25:00",
)

print("\nTEST 3 — FIRST PARTIAL EXIT")
print("-----------------------------------------")
print("Status:", result.get("Status"))
print("Exit Quantity:", result.get("Exit Quantity"))
print("Remaining Quantity:", result.get("Remaining Quantity"))
print("Trade Status:", result.get("Trade Status"))

if (
    result.get("Status") == "RECORDED"
    and result.get("Exit Quantity") > 0
    and result.get("Remaining Quantity") < 300
    and result.get("Trade Status") == "OPEN"
):
    print("PASS")
else:
    print("FAIL")


# ---------------------------------------------------------
# TEST 4 — Second partial exit
# ---------------------------------------------------------

result = process_paper_exit(
    trade=trade,
    current_price=114,
    exit_signal="EXIT — PROFIT PROTECTION",
    momentum_status="DETERIORATING",
    volume_status="DECREASING",
    underlying_status="WEAK",
    structure_status="DETERIORATING",
    costs=70,
    slippage=10,
    timestamp="2026-09-11 10:32:00",
)

print("\nTEST 4 — SECOND PARTIAL EXIT")
print("-----------------------------------------")
print("Status:", result.get("Status"))
print("Exit Quantity:", result.get("Exit Quantity"))
print("Remaining Quantity:", result.get("Remaining Quantity"))
print("Trade Status:", result.get("Trade Status"))

if (
    result.get("Status") == "RECORDED"
    and result.get("Exit Quantity") > 0
    and result.get("Remaining Quantity") >= 0
    and result.get("Trade Status") in ["OPEN", "CLOSED"]
):
    print("PASS")
else:
    print("FAIL")


# ---------------------------------------------------------
# TEST 5 — Final exit
# ---------------------------------------------------------

remaining = trade.get("Current Quantity", 0)

result = process_paper_exit(
    trade=trade,
    current_price=118,
    exit_signal="EXIT — MOMENTUM REVERSAL",
    momentum_status="REVERSING",
    volume_status="DECREASING",
    underlying_status="DETERIORATING",
    structure_status="DETERIORATING",
    costs=75,
    slippage=10,
    timestamp="2026-09-11 10:40:00",
)

print("\nTEST 5 — FINAL EXIT")
print("-----------------------------------------")
print("Status:", result.get("Status"))
print("Exit Quantity:", result.get("Exit Quantity"))
print("Remaining Quantity:", result.get("Remaining Quantity"))
print("Trade Status:", result.get("Trade Status"))

if (
    result.get("Status") == "RECORDED"
    and trade.get("Current Quantity") == 0
    and trade.get("Status") == "CLOSED"
):
    print("PASS")
else:
    print("FAIL")


# ---------------------------------------------------------
# TEST 6 — Check final paper position
# ---------------------------------------------------------

position = get_paper_position(trade)

print("\nTEST 6 — FINAL POSITION")
print("-----------------------------------------")

for key, value in position.items():
    print(f"{key}: {value}")

if (
    position.get("Status") == "CLOSED"
    and position.get("Current Quantity") == 0
):
    print("PASS")
else:
    print("FAIL")


# ---------------------------------------------------------
# TEST 7 — Verify three exit events
# ---------------------------------------------------------

exit_events = trade.get("Exit Events", [])

print("\nTEST 7 — EXIT EVENT HISTORY")
print("-----------------------------------------")
print("Number of exit events:", len(exit_events))

for event_number, event in enumerate(
    exit_events,
    start=1,
):
    print(f"\nExit Event {event_number}")
    print(event)

if len(exit_events) == 3:
    print("\nPASS")
else:
    print("\nFAIL")


# ---------------------------------------------------------
# TEST 8 — Verify cumulative P&L
# ---------------------------------------------------------

print("\nTEST 8 — CUMULATIVE P&L")
print("-----------------------------------------")
print("Gross P&L:", trade.get("Gross P&L"))
print("Trading Costs:", trade.get("Trading Costs"))
print("Slippage:", trade.get("Slippage"))
print("Net P&L:", trade.get("Net P&L"))

if (
    trade.get("Gross P&L", 0) > 0
    and trade.get("Trading Costs", 0) == 210
    and trade.get("Slippage", 0) == 30
):
    print("PASS")
else:
    print("FAIL")


print("\n=========================================")
print("PAPER TRADING ENGINE V1 TEST COMPLETE")
print("=========================================")