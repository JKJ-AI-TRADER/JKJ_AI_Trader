from intraday_report_card import (
    create_daily_report,
    create_monthly_report,
    create_overall_report,
    calculate_trade_statistics,
    calculate_exit_statistics,
    calculate_slicing_statistics,
    calculate_profit_capture,
    calculate_max_drawdown,
)


print("\n=========================================")
print("JKJ REPORT CARD ENGINE V1 TEST")
print("=========================================")


# ---------------------------------------------------------
# TEST DATA
# ---------------------------------------------------------
#
# We deliberately use several trades so that the report
# can demonstrate:
#
# - winners
# - losers
# - breakeven
# - different exit reasons
# - single and multiple exits
# - costs
# - slippage
# - peak profit
# - drawdown
#
# ---------------------------------------------------------


trade_1 = {
    "Trade ID": "PAPER-001",
    "Status": "CLOSED",
    "Symbol": "NIFTY25000CE",
    "Instrument Type": "options",

    "Entry Time": "2026-09-11 10:15:00",
    "Entry Price": 100.0,
    "Original Quantity": 300,
    "Current Quantity": 0,

    "Peak Price": 118.0,
    "Peak Profit %": 18.0,

    "Gross P&L": 4010.0,
    "Trading Costs": 210.0,
    "Slippage": 30.0,
    "Net P&L": 3770.0,

    "Exit Time": "2026-09-11 10:40:00",
    "Exit Reason": "EXIT — MOMENTUM REVERSAL",

    "Exit Events": [
        {
            "Action": "SELL",
            "Quantity": 99,
            "Price": 108.0,
            "Reason": "PROFIT PROTECTION",
        },
        {
            "Action": "SELL",
            "Quantity": 100,
            "Price": 114.0,
            "Reason": "PROFIT PROTECTION",
        },
        {
            "Action": "SELL",
            "Quantity": 101,
            "Price": 118.0,
            "Reason": "MOMENTUM REVERSAL",
        },
    ],
}


trade_2 = {
    "Trade ID": "PAPER-002",
    "Status": "CLOSED",
    "Symbol": "NIFTY25000PE",
    "Instrument Type": "options",

    "Entry Time": "2026-09-11 11:00:00",
    "Entry Price": 100.0,
    "Original Quantity": 100,
    "Current Quantity": 0,

    "Peak Price": 106.0,
    "Peak Profit %": 6.0,

    "Gross P&L": -300.0,
    "Trading Costs": 60.0,
    "Slippage": 10.0,
    "Net P&L": -370.0,

    "Exit Time": "2026-09-11 11:15:00",
    "Exit Reason": "EXIT — STOP LOSS",

    "Exit Events": [
        {
            "Action": "SELL",
            "Quantity": 100,
            "Price": 97.0,
            "Reason": "STOP LOSS",
        },
    ],
}


trade_3 = {
    "Trade ID": "PAPER-003",
    "Status": "CLOSED",
    "Symbol": "RELIANCE",
    "Instrument Type": "equity_intraday",

    "Entry Time": "2026-09-11 12:00:00",
    "Entry Price": 100.0,
    "Original Quantity": 100,
    "Current Quantity": 0,

    "Peak Price": 101.0,
    "Peak Profit %": 1.0,

    "Gross P&L": 100.0,
    "Trading Costs": 50.0,
    "Slippage": 50.0,
    "Net P&L": 0.0,

    "Exit Time": "2026-09-11 12:20:00",
    "Exit Reason": "EXIT — TARGET REACHED",

    "Exit Events": [
        {
            "Action": "SELL",
            "Quantity": 100,
            "Price": 101.0,
            "Reason": "TARGET REACHED",
        },
    ],
}


trade_4 = {
    "Trade ID": "PAPER-004",
    "Status": "CLOSED",
    "Symbol": "NIFTY25100CE",
    "Instrument Type": "options",

    "Entry Time": "2026-09-12 10:10:00",
    "Entry Price": 100.0,
    "Original Quantity": 100,
    "Current Quantity": 0,

    "Peak Price": 105.0,
    "Peak Profit %": 5.0,

    "Gross P&L": 500.0,
    "Trading Costs": 60.0,
    "Slippage": 10.0,
    "Net P&L": 430.0,

    "Exit Time": "2026-09-12 10:30:00",
    "Exit Reason": "EXIT — PROFIT PROTECTION",

    "Exit Events": [
        {
            "Action": "SELL",
            "Quantity": 50,
            "Price": 103.0,
            "Reason": "PROFIT PROTECTION",
        },
        {
            "Action": "SELL",
            "Quantity": 50,
            "Price": 107.0,
            "Reason": "PROFIT PROTECTION",
        },
    ],
}


# ---------------------------------------------------------
# TEST 1 — Trade statistics
# ---------------------------------------------------------

trades = [
    trade_1,
    trade_2,
    trade_3,
    trade_4,
]

statistics = calculate_trade_statistics(
    trades
)

print("\nTEST 1 — TRADE STATISTICS")
print("-----------------------------------------")

for key, value in statistics.items():
    print(f"{key}: {value}")

if (
    statistics["Total Trades"] == 4
    and statistics["Winning Trades"] == 2
    and statistics["Losing Trades"] == 1
    and statistics["Breakeven Trades"] == 1
):
    print("PASS")
else:
    print("FAIL")


# ---------------------------------------------------------
# TEST 2 — Exit statistics
# ---------------------------------------------------------

exit_statistics = calculate_exit_statistics(
    trades
)

print("\nTEST 2 — EXIT STATISTICS")
print("-----------------------------------------")

print(
    "Exit Reason Counts:",
    exit_statistics["Exit Reason Counts"]
)

if (
    exit_statistics["Total Closed Trades"] == 4
):
    print("PASS")
else:
    print("FAIL")


# ---------------------------------------------------------
# TEST 3 — Slicing statistics
# ---------------------------------------------------------

slicing_statistics = calculate_slicing_statistics(
    trades
)

print("\nTEST 3 — SLICING STATISTICS")
print("-----------------------------------------")

for key, value in slicing_statistics.items():
    print(f"{key}: {value}")

if (
    slicing_statistics["Total Exit Events"] == 7
    and slicing_statistics["Trades With Multiple Exits"] == 2
    and slicing_statistics["Trades With Single Exit"] == 2
):
    print("PASS")
else:
    print("FAIL")


# ---------------------------------------------------------
# TEST 4 — Profit capture
# ---------------------------------------------------------

profit_capture = calculate_profit_capture(
    trades
)

print("\nTEST 4 — PROFIT CAPTURE")
print("-----------------------------------------")

for key, value in profit_capture.items():
    print(f"{key}: {value}")

if profit_capture["Trades Measured"] == 3:
    print("PASS")
else:
    print("FAIL")


# ---------------------------------------------------------
# TEST 5 — Maximum drawdown
# ---------------------------------------------------------

drawdown = calculate_max_drawdown(
    trades
)

print("\nTEST 5 — MAXIMUM DRAWDOWN")
print("-----------------------------------------")
print("Maximum Drawdown:", drawdown)

if drawdown >= 0:
    print("PASS")
else:
    print("FAIL")


# ---------------------------------------------------------
# TEST 6 — Daily report
# ---------------------------------------------------------

daily_trades = [
    trade_1,
    trade_2,
    trade_3,
]

daily_report = create_daily_report(
    daily_trades,
    report_date="2026-09-11",
)

print("\nTEST 6 — DAILY REPORT")
print("-----------------------------------------")

print(
    "Report Type:",
    daily_report["Report Type"]
)

print(
    "Report Date:",
    daily_report["Report Date"]
)

print(
    "Net P&L:",
    daily_report["Trade Statistics"]["Net P&L"]
)

print(
    "Win Rate:",
    daily_report["Trade Statistics"]["Win Rate %"]
)

print(
    "Maximum Drawdown:",
    daily_report["Maximum Drawdown"]
)

if (
    daily_report["Report Type"] == "DAILY"
    and daily_report["Report Date"] == "2026-09-11"
    and daily_report["Trade Statistics"]["Total Trades"] == 3
):
    print("PASS")
else:
    print("FAIL")


# ---------------------------------------------------------
# TEST 7 — Monthly report
# ---------------------------------------------------------

monthly_report = create_monthly_report(
    trades,
    year=2026,
    month=9,
)

print("\nTEST 7 — MONTHLY REPORT")
print("-----------------------------------------")

print(
    "Report Type:",
    monthly_report["Report Type"]
)

print(
    "Report Date:",
    monthly_report["Report Date"]
)

print(
    "Total Trades:",
    monthly_report["Trade Statistics"]["Total Trades"]
)

print(
    "Net P&L:",
    monthly_report["Trade Statistics"]["Net P&L"]
)

if (
    monthly_report["Report Type"] == "MONTHLY"
    and monthly_report["Trade Statistics"]["Total Trades"] == 4
):
    print("PASS")
else:
    print("FAIL")


# ---------------------------------------------------------
# TEST 8 — Overall report
# ---------------------------------------------------------

overall_report = create_overall_report(
    trades
)

print("\nTEST 8 — OVERALL REPORT")
print("-----------------------------------------")

print(
    "Report Type:",
    overall_report["Report Type"]
)

print(
    "Total Trades:",
    overall_report["Trade Statistics"]["Total Trades"]
)

print(
    "Net P&L:",
    overall_report["Trade Statistics"]["Net P&L"]
)

print(
    "Profit Factor:",
    overall_report["Trade Statistics"]["Profit Factor"]
)

if (
    overall_report["Report Type"] == "OVERALL"
    and overall_report["Trade Statistics"]["Total Trades"] == 4
):
    print("PASS")
else:
    print("FAIL")


# ---------------------------------------------------------
# TEST 9 — Verify net P&L
# ---------------------------------------------------------

expected_net_pnl = (
    trade_1["Net P&L"]
    + trade_2["Net P&L"]
    + trade_3["Net P&L"]
    + trade_4["Net P&L"]
)

actual_net_pnl = overall_report[
    "Trade Statistics"
]["Net P&L"]

print("\nTEST 9 — NET P&L VERIFICATION")
print("-----------------------------------------")

print("Expected Net P&L:", expected_net_pnl)
print("Actual Net P&L:", actual_net_pnl)

if actual_net_pnl == expected_net_pnl:
    print("PASS")
else:
    print("FAIL")


print("\n=========================================")
print("JKJ REPORT CARD ENGINE V1 TEST COMPLETE")
print("=========================================")