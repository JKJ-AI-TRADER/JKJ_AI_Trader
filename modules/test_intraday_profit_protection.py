"""
JKJ AI Trader — Intraday Profit Protection Test

Wisdom Before Wealth.

No live market data.
No broker connection.
No real trading.
"""

from intraday_profit_protection import evaluate_profit_protection


def test_early_profit():

    result = evaluate_profit_protection(
        entry_price=100,
        current_price=101,
        peak_price=101,
        momentum_status="STRONG",
        volume_status="STRONG",
        underlying_status="SUPPORTIVE",
        structure_status="STRONG"
    )

    print("\nTEST 1 — EARLY PROFIT")
    print("-----------------------------------------")
    print("Status:", result["Status"])
    print("Current Profit %:", result["Current Profit %"])
    print("Peak Profit %:", result["Peak Profit %"])
    print("Retracement %:", result["Retracement %"])

    assert result["Exit Decision"] == "HOLD"
    assert result["Profit Protected"] is False

    print("PASS")


def test_healthy_profit():

    result = evaluate_profit_protection(
        entry_price=100,
        current_price=104,
        peak_price=105,
        momentum_status="STRONG",
        volume_status="STRONG",
        underlying_status="SUPPORTIVE",
        structure_status="STRONG"
    )

    print("\nTEST 2 — HEALTHY PROFIT")
    print("-----------------------------------------")
    print("Status:", result["Status"])
    print("Current Profit %:", result["Current Profit %"])
    print("Peak Profit %:", result["Peak Profit %"])
    print("Retracement %:", result["Retracement %"])

    assert result["Exit Decision"] == "HOLD"
    assert result["Profit Protected"] is True

    print("PASS")


def test_profit_protection():

    result = evaluate_profit_protection(
        entry_price=100,
        current_price=108,
        peak_price=110,
        momentum_status="STRONG",
        volume_status="STRONG",
        underlying_status="SUPPORTIVE",
        structure_status="STRONG"
    )

    print("\nTEST 3 — PROFIT PROTECTION")
    print("-----------------------------------------")
    print("Status:", result["Status"])
    print("Current Profit %:", result["Current Profit %"])
    print("Peak Profit %:", result["Peak Profit %"])
    print("Retracement %:", result["Retracement %"])

    assert result["Profit Protected"] is True
    assert result["Exit Decision"] in {
        "HOLD",
        "WATCH"
    }

    print("PASS")


def test_peak_120_current_117():

    result = evaluate_profit_protection(
        entry_price=100,
        current_price=117,
        peak_price=120,
        momentum_status="WEAK",
        volume_status="DECREASING",
        underlying_status="DETERIORATING",
        structure_status="DETERIORATING"
    )

    print("\nTEST 4 — PEAK ₹120 → CURRENT ₹117")
    print("-----------------------------------------")
    print("Status:", result["Status"])
    print("Current Profit %:", result["Current Profit %"])
    print("Peak Profit %:", result["Peak Profit %"])
    print("Retracement %:", result["Retracement %"])

    assert result["Current Profit %"] == 17.0
    assert result["Peak Profit %"] == 20.0
    assert result["Retracement %"] == 15.0
    assert result["Exit Decision"] == "EXIT"

    print("PASS")


def test_exceptional_profit_with_weakening():

    result = evaluate_profit_protection(
        entry_price=100,
        current_price=130,
        peak_price=135,
        momentum_status="WEAK",
        volume_status="DECREASING",
        underlying_status="DETERIORATING",
        structure_status="DETERIORATING"
    )

    print("\nTEST 5 — EXCEPTIONAL PROFIT WITH WEAKENING")
    print("-----------------------------------------")
    print("Status:", result["Status"])
    print("Current Profit %:", result["Current Profit %"])
    print("Peak Profit %:", result["Peak Profit %"])
    print("Retracement %:", result["Retracement %"])

    assert result["Profit Protected"] is True
    assert result["Exit Decision"] == "EXIT"

    print("PASS")


def test_stop_loss():

    result = evaluate_profit_protection(
        entry_price=100,
        current_price=97,
        peak_price=101,
        momentum_status="WEAK",
        volume_status="DECREASING",
        underlying_status="DETERIORATING",
        structure_status="DETERIORATING",
        stop_loss_price=98
    )

    print("\nTEST 6 — STOP LOSS")
    print("-----------------------------------------")
    print("Status:", result["Status"])
    print("Exit Decision:", result["Exit Decision"])
    print("Current Profit %:", result["Current Profit %"])

    assert result["Status"] == "EXIT — STOP LOSS"
    assert result["Exit Decision"] == "EXIT"

    print("PASS")


if __name__ == "__main__":

    test_early_profit()
    test_healthy_profit()
    test_profit_protection()
    test_peak_120_current_117()
    test_exceptional_profit_with_weakening()
    test_stop_loss()

    print("\n=========================================")
    print("ALL PROFIT PROTECTION TESTS PASSED")
    print("=========================================")