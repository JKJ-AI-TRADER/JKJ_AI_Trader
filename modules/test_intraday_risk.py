from intraday_risk_engine import (
    analyse_intraday_risk
)


print()
print("=" * 50)
print("JKJ AI INTRADAY RISK ENGINE TEST")
print("=" * 50)


result = analyse_intraday_risk(

    entry_price=1000,

    stop_loss=990,

    target_price=1020,

    setup_score=100,

    trading_allowed=True
)


print()

print(
    "Trade Allowed:",
    result.get("Trade Allowed")
)

print(
    "Risk Status:",
    result.get("Risk Status")
)

print(
    "Risk Level:",
    result.get("Risk Level")
)

print(
    "Entry Price:",
    result.get("Entry Price")
)

print(
    "Stop Loss:",
    result.get("Stop Loss")
)

print(
    "Target Price:",
    result.get("Target Price")
)

print(
    "Risk Percentage:",
    result.get("Risk Percentage"),
    "%"
)

print(
    "Reward Percentage:",
    result.get("Reward Percentage"),
    "%"
)

print(
    "Risk Reward Ratio:",
    result.get("Risk Reward Ratio")
)


print()
print("REASONS:")

for reason in result.get(
    "Reasons",
    []
):
    print("•", reason)


print()
print("WARNINGS:")

warnings = result.get(
    "Warnings",
    []
)

if warnings:

    for warning in warnings:
        print("•", warning)

else:

    print("None")