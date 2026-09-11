from intraday_trade_logger import (
    create_trade_record,
    update_peak_price,
    record_buy_event,
    record_sell_event,
    add_trade_note,
    close_trade,
    summarize_trade,
    create_daily_summary,
)


print("\n=========================================")
print("JKJ TRADE LOGGER V1 TEST")
print("=========================================")


# ---------------------------------------------------------
# TEST 1 — Create a new trade
# ---------------------------------------------------------

trade = create_trade_record(
    trade_id="JKJ-001",
    symbol="NIFTY25000CE",
    instrument_type="options",
    expiry="2026-09-17",
    strike=25000,
    option_type="CE",
    underlying="NIFTY",
    entry_time="2026-09-11 10:15:00",
    entry_price=100,
    quantity=300,
    stop_loss=95,
    target=120,
    momentum_score=86,
    entry_status="STRONG ENTRY",
    entry_reason="Momentum + volume + underlying confirmation",
)

print("\nTEST 1 — CREATE TRADE")
print("-----------------------------------------")
print(trade)
print("PASS" if trade.get("Status") == "OPEN" else "FAIL")


# ---------------------------------------------------------
# TEST 2 — Update peak price
# ---------------------------------------------------------

update_peak_price(trade, 110)

print("\nTEST 2 — UPDATE PEAK")
print("-----------------------------------------")
print("Peak Price:", trade["Peak Price"])
print("Peak Profit %:", trade["Peak Profit %"])

if trade["Peak Price"] == 110:
    print("PASS")
else:
    print("FAIL")


# ---------------------------------------------------------
# TEST 3 — Record first partial SELL
# ---------------------------------------------------------

result = record_sell_event(
    trade=trade,
    price=108,
    quantity=100,
    gross_pnl=800,
    costs=65,
    slippage=10,
    timestamp="2026-09-11 10:25:00",
    reason="PROFIT PROTECTION",
)

print("\nTEST 3 — FIRST PARTIAL SELL")
print("-----------------------------------------")
print(result)
print("Remaining Quantity:", trade["Current Quantity"])
print("Net P&L:", trade["Net P&L"])

if (
    result["Status"] == "RECORDED"
    and trade["Current Quantity"] == 200
):
    print("PASS")
else:
    print("FAIL")


# ---------------------------------------------------------
# TEST 4 — Record second partial SELL
# ---------------------------------------------------------

result = record_sell_event(
    trade=trade,
    price=114,
    quantity=100,
    gross_pnl=1400,
    costs=70,
    slippage=10,
    timestamp="2026-09-11 10:32:00",
    reason="PROFIT PROTECTION",
)

print("\nTEST 4 — SECOND PARTIAL SELL")
print("-----------------------------------------")
print(result)
print("Remaining Quantity:", trade["Current Quantity"])
print("Net P&L:", trade["Net P&L"])

if trade["Current Quantity"] == 100:
    print("PASS")
else:
    print("FAIL")


# ---------------------------------------------------------
# TEST 5 — Add trade note
# ---------------------------------------------------------

result = add_trade_note(
    trade,
    "Momentum weakened after the second profit-protection exit."
)

print("\nTEST 5 — ADD TRADE NOTE")
print("-----------------------------------------")
print(result)

if len(trade["Notes"]) == 1:
    print("PASS")
else:
    print("FAIL")


# ---------------------------------------------------------
# TEST 6 — Final SELL
# ---------------------------------------------------------

result = record_sell_event(
    trade=trade,
    price=118,
    quantity=100,
    gross_pnl=1800,
    costs=75,
    slippage=10,
    timestamp="2026-09-11 10:40:00",
    reason="MOMENTUM WEAKENING",
)

print("\nTEST 6 — FINAL SELL")
print("-----------------------------------------")
print(result)
print("Remaining Quantity:", trade["Current Quantity"])
print("Trade Status:", trade["Status"])
print("Gross P&L:", trade["Gross P&L"])
print("Trading Costs:", trade["Trading Costs"])
print("Slippage:", trade["Slippage"])
print("Net P&L:", trade["Net P&L"])

if (
    trade["Current Quantity"] == 0
    and trade["Status"] == "CLOSED"
):
    print("PASS")
else:
    print("FAIL")


# ---------------------------------------------------------
# TEST 7 — Summarize completed trade
# ---------------------------------------------------------

summary = summarize_trade(trade)

print("\nTEST 7 — TRADE SUMMARY")
print("-----------------------------------------")

for key, value in summary.items():
    print(f"{key}: {value}")

if summary["Status"] == "CLOSED":
    print("PASS")
else:
    print("FAIL")


# ---------------------------------------------------------
# TEST 8 — Daily report summary
# ---------------------------------------------------------

daily_summary = create_daily_summary([trade])

print("\nTEST 8 — DAILY SUMMARY")
print("-----------------------------------------")

for key, value in daily_summary.items():
    print(f"{key}: {value}")

if (
    daily_summary["Total Trades"] == 1
    and daily_summary["Winning Trades"] == 1
):
    print("PASS")
else:
    print("FAIL")


# ---------------------------------------------------------
# TEST 9 — Invalid SELL quantity
# ---------------------------------------------------------

invalid_result = record_sell_event(
    trade=trade,
    price=120,
    quantity=50,
    gross_pnl=1000,
    costs=50,
)

print("\nTEST 9 — SELL AFTER POSITION CLOSED")
print("-----------------------------------------")
print(invalid_result)

if invalid_result["Status"] == "ERROR":
    print("PASS")
else:
    print("FAIL")


print("\n=========================================")
print("TRADE LOGGER V1 TEST COMPLETE")
print("=========================================")