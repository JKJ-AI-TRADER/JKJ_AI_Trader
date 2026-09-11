from intraday_decision_engine import (
    make_intraday_decision
)


print()
print("=" * 50)
print("JKJ AI INTRADAY DECISION ENGINE TEST")
print("=" * 50)


# -----------------------------------------
# TEST MARKET RESULT
# -----------------------------------------

market_result = {

    "Intraday Market Status":
        "FAVOURABLE",

    "Trading Environment":
        "STRONG",

    "Trading Allowed":
        True,

    "Confidence":
        80
}


# -----------------------------------------
# TEST SETUP RESULT
# -----------------------------------------

setup_result = {

    "Intraday Setup Status":
        "STRONG SETUP",

    "Setup Strength":
        "STRONG",

    "Trade Candidate":
        True,

    "Setup Score":
        100
}


# -----------------------------------------
# TEST RISK RESULT
# -----------------------------------------

risk_result = {

    "Trade Allowed":
        True,

    "Risk Status":
        "ACCEPTABLE",

    "Risk Level":
        "LOW",

    "Risk Percentage":
        1.0,

    "Reward Percentage":
        2.0,

    "Risk Reward Ratio":
        2.0
}


# -----------------------------------------
# MAKE FINAL DECISION
# -----------------------------------------

result = make_intraday_decision(

    market_result,

    setup_result,

    risk_result
)


print()

print(
    "FINAL DECISION:",
    result.get("Final Decision")
)

print(
    "CONFIDENCE:",
    result.get("Confidence"),
    "%"
)

print()

print(
    "Market Status:",
    result.get("Market Status")
)

print(
    "Setup Status:",
    result.get("Setup Status")
)

print(
    "Risk Status:",
    result.get("Risk Status")
)

print(
    "Risk Level:",
    result.get("Risk Level")
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