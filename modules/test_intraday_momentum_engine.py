"""
JKJ AI Intraday Momentum Engine Test

Wisdom Before Wealth.

Tests the Momentum Engine with controlled scenarios.

No live market data.
No broker connection.
No real trading.
"""

import pandas as pd

from intraday_momentum_engine import analyse_intraday_momentum


# -----------------------------------------
# TEST 1 — STRONG MOMENTUM
# -----------------------------------------

def test_strong_momentum():

    history = pd.DataFrame({
        "High": [
            100.0, 100.1, 100.2, 100.3, 100.4,
            100.5, 100.6, 100.7, 100.8, 100.9,
            101.0, 101.2, 101.4, 101.7, 102.0,
            102.4, 102.9, 103.5, 104.2, 105.0
        ],

        "Low": [
            99.0, 99.1, 99.2, 99.3, 99.4,
            99.5, 99.6, 99.7, 99.8, 99.9,
            100.0, 100.2, 100.4, 100.7, 101.0,
            101.4, 101.9, 102.5, 103.2, 104.0
        ],

        "Close": [
            99.5, 99.6, 99.7, 99.8, 99.9,
            100.0, 100.1, 100.2, 100.3, 100.4,
            100.5, 100.7, 100.9, 101.2, 101.5,
            101.9, 102.4, 103.0, 103.7, 104.5
        ],

        "Volume": [
            1000, 1000, 1000, 1000, 1000,
            1000, 1000, 1000, 1000, 1000,
            1000, 1000, 1000, 1000, 1000,
            1000, 1000, 1000, 1500, 2000
        ]
    })

    underlying = pd.DataFrame({
        "Close": [
            100, 100, 100, 100, 100,
            100, 100, 100, 100, 100,
            100, 100, 100, 100, 100,
            100, 100, 100.2, 100.4, 100.6
        ]
    })

    result = analyse_intraday_momentum(
        history=history,
        underlying_history=underlying,
        spread_percentage=0.10,
        remaining_profit_percentage=2.0,
        risk_reward_ratio=2.5
    )

    print("\nTEST 1 — STRONG MOMENTUM")
    print("-----------------------------------------")
    print("Momentum Score:", result["Momentum Score"])
    print("Momentum Status:", result["Momentum Status"])
    print("Trade Candidate:", result["Trade Candidate"])

    print("Reasons:")
    for reason in result["Reasons"]:
        print("-", reason)

    print("Warnings:")
    for warning in result["Warnings"]:
        print("-", warning)

    assert result["Momentum Status"] == "STRONG MOMENTUM"
    assert result["Trade Candidate"] is True
    assert result["Momentum Score"] >= 80

    print("PASS")


# -----------------------------------------
# TEST 2 — WEAK MOMENTUM
# -----------------------------------------

def test_weak_momentum():

    history = pd.DataFrame({
        "High": [100] * 20,
        "Low": [99] * 20,
        "Close": [99.5] * 20,
        "Volume": [1000] * 20
    })

    result = analyse_intraday_momentum(
        history=history,
        underlying_history=None,
        spread_percentage=1.20,
        remaining_profit_percentage=0.20,
        risk_reward_ratio=0.80
    )

    print("\nTEST 2 — WEAK MOMENTUM")
    print("-----------------------------------------")
    print("Momentum Score:", result["Momentum Score"])
    print("Momentum Status:", result["Momentum Status"])
    print("Trade Candidate:", result["Trade Candidate"])

    assert result["Momentum Status"] == "NO TRADE"
    assert result["Trade Candidate"] is False

    print("PASS")


# -----------------------------------------
# TEST 3 — INSUFFICIENT DATA
# -----------------------------------------

def test_insufficient_data():

    history = pd.DataFrame({
        "High": [100, 101, 102],
        "Low": [99, 100, 101],
        "Close": [99.5, 100.5, 101.5],
        "Volume": [1000, 1000, 1000]
    })

    result = analyse_intraday_momentum(
        history=history
    )

    print("\nTEST 3 — INSUFFICIENT DATA")
    print("-----------------------------------------")
    print("Momentum Score:", result["Momentum Score"])
    print("Momentum Status:", result["Momentum Status"])

    assert result["Momentum Score"] == 0
    assert result["Trade Candidate"] is False

    print("PASS")


# -----------------------------------------
# RUN ALL TESTS
# -----------------------------------------

if __name__ == "__main__":

    test_strong_momentum()
    test_weak_momentum()
    test_insufficient_data()

    print("\n=========================================")
    print("ALL MOMENTUM ENGINE TESTS PASSED")
    print("=========================================")
