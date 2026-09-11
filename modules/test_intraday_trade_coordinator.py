from intraday_trade_coordinator import (
    analyse_intraday_trade
)


print()
print("=" * 50)
print("JKJ AI COMPLETE INTRADAY TRADE TEST")
print("=" * 50)


result = analyse_intraday_trade(

    # -----------------------------------------
    # MARKET DATA
    # -----------------------------------------

    market_price=25000,

    market_ma20=24800,

    market_ma50=24600,

    market_rsi=60,


    # -----------------------------------------
    # STOCK DATA
    # -----------------------------------------

    stock_price=1000,
    stock_ma20=990,
    stock_rsi=60,
    short_term_trend="IMPROVING",
    volume_trend="STRONG",


    # -----------------------------------------
    # TRADE PLAN
    # -----------------------------------------

    entry_price=1000,

    stop_loss=950,

    target_price=1020
    )


# =========================================
# EXTRACT RESULTS
# =========================================

market = result.get(
    "Market Analysis",
    {}
)

setup = result.get(
    "Setup Analysis",
    {}
)

risk = result.get(
    "Risk Analysis",
    {}
)

decision = result.get(
    "Final Decision",
    {}
)


# =========================================
# MARKET RESULT
# =========================================

print()
print("MARKET ANALYSIS")

print(
    "Status:",
    market.get(
        "Intraday Market Status"
    )
)

print(
    "Trading Allowed:",
    market.get(
        "Trading Allowed"
    )
)


# =========================================
# SETUP RESULT
# =========================================

print()
print("STOCK SETUP")

print(
    "Status:",
    setup.get(
        "Intraday Setup Status"
    )
)

print(
    "Setup Score:",
    setup.get(
        "Setup Score"
    )
)


# =========================================
# RISK RESULT
# =========================================

print()
print("RISK ANALYSIS")

print(
    "Trade Allowed:",
    risk.get(
        "Trade Allowed"
    )
)

print(
    "Risk Level:",
    risk.get(
        "Risk Level"
    )
)

print(
    "Risk / Reward:",
    risk.get(
        "Risk Reward Ratio"
    )
)


# =========================================
# FINAL DECISION
# =========================================

print()
print("=" * 50)
print("FINAL JKJ INTRADAY DECISION")
print("=" * 50)

print()

print(
    "Decision:",
    decision.get(
        "Final Decision"
    )
)

print(
    "Confidence:",
    decision.get(
        "Confidence"
    ),
    "%"
)


print()
print("REASONS:")

for reason in decision.get(
    "Reasons",
    []
):

    print("•", reason)


print()
print("WARNINGS:")

warnings = decision.get(
    "Warnings",
    []
)

if warnings:

    for warning in warnings:

        print("•", warning)

else:

    print("None")


print()
print("=" * 50)