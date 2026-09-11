"""
JKJ AI Trader
Test — Intraday Option Momentum Scanner V5
"""

import pandas as pd

from intraday_option_momentum_scanner import (
    scan_option_momentum
)


print("=" * 50)
print("JKJ OPTION MOMENTUM SCANNER V5 TEST")
print("=" * 50)


# ---------------------------------------------------------
# HELPER — CREATE OPTION HISTORY
# ---------------------------------------------------------

def create_history(
    start_price,
    price_step,
    volume_start,
    volume_step
):
    rows = []

    for i in range(30):

        open_price = (
            start_price
            + (i * price_step)
        )

        close_price = (
            open_price
            + price_step
        )

        high_price = close_price + 1
        low_price = open_price - 1

        volume = (
            volume_start
            + (i * volume_step)
        )

        rows.append(
            {
                "Open": open_price,
                "High": high_price,
                "Low": low_price,
                "Close": close_price,
                "Volume": volume,
            }
        )

    return pd.DataFrame(rows)


# ---------------------------------------------------------
# TEST DATA
# ---------------------------------------------------------

option_histories = {

    "NIFTY15SEP2623300CE":
        create_history(
            100,
            2.0,
            100000,
            10000
        ),

    "NIFTY15SEP2623300PE":
        create_history(
            100,
            1.0,
            100000,
            3000
        ),

    "NIFTY15SEP2623400CE":
        create_history(
            100,
            0.2,
            100000,
            500
        ),

    "NIFTY15SEP2623200PE":
        create_history(
            100,
            -0.2,
            100000,
            -500
        ),
}


option_context = {

    "NIFTY15SEP2623300CE": {
        "Underlying": "NIFTY",
        "Expiry": "2026-09-15",
        "Strike": 23300,
        "Option Type": "CE",
    },

    "NIFTY15SEP2623300PE": {
        "Underlying": "NIFTY",
        "Expiry": "2026-09-15",
        "Strike": 23300,
        "Option Type": "PE",
    },

    "NIFTY15SEP2623400CE": {
        "Underlying": "NIFTY",
        "Expiry": "2026-09-15",
        "Strike": 23400,
        "Option Type": "CE",
    },

    "NIFTY15SEP2623200PE": {
        "Underlying": "NIFTY",
        "Expiry": "2026-09-15",
        "Strike": 23200,
        "Option Type": "PE",
    },
}


# ---------------------------------------------------------
# TEST 1 — SCAN OPTIONS
# ---------------------------------------------------------

print()
print("TEST 1 — OPTION MOMENTUM SCAN")
print("-" * 50)

result = scan_option_momentum(
    option_histories,
    option_context
)

print("Status:", result["Status"])
print("Scanned Count:", result["Scanned Count"])
print("Result Count:", result["Result Count"])

assert result["Status"] == "READY"
assert result["Scanned Count"] == 4
assert result["Result Count"] == 4

print("PASS")


# ---------------------------------------------------------
# TEST 2 — RANKING
# ---------------------------------------------------------

print()
print("TEST 2 — MOMENTUM RANKING")
print("-" * 50)

for item in result["Ranked Opportunities"]:
    print(
        "Rank:",
        item["Rank"],
        "|",
        item["Trading Symbol"],
        "| Score:",
        item["Momentum Score"],
        "| Status:",
        item["Momentum Status"]
    )

scores = [
    item["Momentum Score"]
    for item in result["Ranked Opportunities"]
]

assert scores == sorted(
    scores,
    reverse=True
)

assert (
    result["Ranked Opportunities"][0]
    ["Trading Symbol"]
    == "NIFTY15SEP2623300CE"
)

print("PASS")


# ---------------------------------------------------------
# TEST 3 — RESULT STRUCTURE
# ---------------------------------------------------------

print()
print("TEST 3 — RESULT STRUCTURE")
print("-" * 50)

top_result = result["Ranked Opportunities"][0]

print(top_result)

assert "Trading Symbol" in top_result
assert "Underlying" in top_result
assert "Expiry" in top_result
assert "Strike" in top_result
assert "Option Type" in top_result
assert "Momentum Score" in top_result
assert "Momentum Status" in top_result
assert "Trade Candidate" in top_result
assert "Exhaustion Score" in top_result
assert "Rank" in top_result

assert top_result["Underlying"] == "NIFTY"
assert top_result["Strike"] == 23300
assert top_result["Option Type"] == "CE"

print("PASS")


# ---------------------------------------------------------
# TEST 4 — EMPTY INPUT
# ---------------------------------------------------------

print()
print("TEST 4 — EMPTY INPUT")
print("-" * 50)

result = scan_option_momentum(
    {}
)

print("Status:", result["Status"])
print("Reasons:", result["Reasons"])

assert result["Status"] == "INVALID"

print("PASS")


# ---------------------------------------------------------
# TEST 5 — INVALID INPUT
# ---------------------------------------------------------

print()
print("TEST 5 — INVALID INPUT")
print("-" * 50)

result = scan_option_momentum(
    "INVALID"
)

print("Status:", result["Status"])
print("Reasons:", result["Reasons"])

assert result["Status"] == "INVALID"

print("PASS")


# ---------------------------------------------------------
# TEST 6 — INVALID CONTEXT
# ---------------------------------------------------------

print()
print("TEST 6 — INVALID CONTEXT")
print("-" * 50)

result = scan_option_momentum(
    option_histories,
    option_context="INVALID"
)

print("Status:", result["Status"])
print("Reasons:", result["Reasons"])

assert result["Status"] == "INVALID"

print("PASS")


print()
print("=" * 50)
print("JKJ OPTION MOMENTUM SCANNER V5 TEST COMPLETE")
print("=" * 50)