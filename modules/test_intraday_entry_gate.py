"""
JKJ AI Trader — Intraday Entry Gate Test

Wisdom Before Wealth.

No live market data.
No broker connection.
No real trading.
"""


from intraday_entry_gate import evaluate_intraday_entry


def test_strong_entry():

    momentum_result = {
        "Momentum Score": 90,
        "Momentum Status": "STRONG MOMENTUM",
        "Trade Candidate": True,
        "Exhaustion Penalty": 0
    }

    cost_result = {
        "Trade Viable": True,
        "Net P&L": 300.00
    }

    result = evaluate_intraday_entry(
        momentum_result=momentum_result,
        cost_result=cost_result,
        risk_reward_ratio=2.5,
        current_price=105
    )

    print("\nTEST 1 — STRONG ENTRY")
    print("-----------------------------------------")
    print("Entry Status:", result["Entry Status"])
    print("Entry Allowed:", result["Entry Allowed"])
    print("Confidence:", result["Confidence"])

    assert result["Entry Allowed"] is True
    assert result["Entry Status"] == "STRONG ENTRY"
    assert result["Confidence"] == 90

    print("PASS")


def test_severe_exhaustion():

    momentum_result = {
        "Momentum Score": 90,
        "Momentum Status": "STRONG MOMENTUM",
        "Trade Candidate": True,
        "Exhaustion Penalty": -13
    }

    cost_result = {
        "Trade Viable": True,
        "Net P&L": 300.00
    }

    result = evaluate_intraday_entry(
        momentum_result=momentum_result,
        cost_result=cost_result,
        risk_reward_ratio=2.5,
        current_price=105
    )

    print("\nTEST 2 — SEVERE EXHAUSTION")
    print("-----------------------------------------")
    print("Entry Status:", result["Entry Status"])
    print("Entry Allowed:", result["Entry Allowed"])

    assert result["Entry Allowed"] is False
    assert result["Entry Status"] == "NO TRADE"

    print("PASS")


def test_costs_make_trade_unviable():

    momentum_result = {
        "Momentum Score": 90,
        "Momentum Status": "STRONG MOMENTUM",
        "Trade Candidate": True,
        "Exhaustion Penalty": 0
    }

    cost_result = {
        "Trade Viable": False,
        "Net P&L": -50.00
    }

    result = evaluate_intraday_entry(
        momentum_result=momentum_result,
        cost_result=cost_result,
        risk_reward_ratio=2.5,
        current_price=100.20
    )

    print("\nTEST 3 — COSTS MAKE TRADE UNVIABLE")
    print("-----------------------------------------")
    print("Entry Status:", result["Entry Status"])
    print("Entry Allowed:", result["Entry Allowed"])
    print("Net P&L:", result["Net P&L"])

    assert result["Entry Allowed"] is False
    assert result["Entry Status"] == "NO TRADE"
    assert result["Net P&L"] < 0

    print("PASS")


def test_weak_momentum():

    momentum_result = {
        "Momentum Score": 65,
        "Momentum Status": "DEVELOPING",
        "Trade Candidate": False,
        "Exhaustion Penalty": 0
    }

    cost_result = {
        "Trade Viable": True,
        "Net P&L": 100.00
    }

    result = evaluate_intraday_entry(
        momentum_result=momentum_result,
        cost_result=cost_result,
        risk_reward_ratio=2.0,
        current_price=102
    )

    print("\nTEST 4 — WEAK MOMENTUM")
    print("-----------------------------------------")
    print("Entry Status:", result["Entry Status"])
    print("Entry Allowed:", result["Entry Allowed"])

    assert result["Entry Allowed"] is False
    assert result["Entry Status"] == "NO TRADE"

    print("PASS")


if __name__ == "__main__":

    test_strong_entry()
    test_severe_exhaustion()
    test_costs_make_trade_unviable()
    test_weak_momentum()

    print("\n=========================================")
    print("ALL ENTRY GATE TESTS PASSED")
    print("=========================================")