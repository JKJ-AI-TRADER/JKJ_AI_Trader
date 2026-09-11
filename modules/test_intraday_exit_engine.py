"""
JKJ AI Trader — Intraday Exit Engine Test

Wisdom Before Wealth.

No live market data.
No broker connection.
No real trading.
"""

from intraday_exit_engine import evaluate_intraday_exit


def test_stop_loss():

    result = evaluate_intraday_exit(
        entry_price=100,
        current_price=97,
        stop_loss_price=98,
        momentum_status="WEAK",
        volume_status="DECREASING",
        underlying_status="DETERIORATING",
        structure_status="DETERIORATING"
    )

    print("\nTEST 1 — STOP LOSS")
    print("-----------------------------------------")
    print("Exit Status:", result["Exit Status"])
    print("Exit Required:", result["Exit Required"])
    print("Exit Reason:", result["Exit Reason"])

    assert result["Exit Status"] == "EXIT"
    assert result["Exit Required"] is True
    assert result["Exit Reason"] == "STOP LOSS"

    print("PASS")


def test_profit_protection_exit():

    protection_result = {
        "Status": "EXIT — PROFIT PROTECTION",
        "Exit Decision": "EXIT"
    }

    result = evaluate_intraday_exit(
        entry_price=100,
        current_price=117,
        stop_loss_price=95,
        profit_protection_result=protection_result,
        momentum_status="WEAK",
        volume_status="DECREASING",
        underlying_status="DETERIORATING",
        structure_status="DETERIORATING"
    )

    print("\nTEST 2 — PROFIT PROTECTION EXIT")
    print("-----------------------------------------")
    print("Exit Status:", result["Exit Status"])
    print("Exit Required:", result["Exit Required"])
    print("Exit Reason:", result["Exit Reason"])

    assert result["Exit Status"] == "EXIT"
    assert result["Exit Required"] is True
    assert result["Exit Reason"] == "PROFIT PROTECTION"

    print("PASS")


def test_target_reached():

    result = evaluate_intraday_exit(
        entry_price=100,
        current_price=105,
        stop_loss_price=98,
        target_price=105,
        momentum_status="STRONG",
        volume_status="STRONG",
        underlying_status="SUPPORTIVE",
        structure_status="STRONG"
    )

    print("\nTEST 3 — TARGET REACHED")
    print("-----------------------------------------")
    print("Exit Status:", result["Exit Status"])
    print("Exit Required:", result["Exit Required"])
    print("Exit Reason:", result["Exit Reason"])

    assert result["Exit Status"] == "EXIT"
    assert result["Exit Required"] is True
    assert result["Exit Reason"] == "TARGET REACHED"

    print("PASS")


def test_momentum_reversal():

    result = evaluate_intraday_exit(
        entry_price=100,
        current_price=103,
        stop_loss_price=97,
        momentum_status="REVERSING",
        volume_status="DECREASING",
        underlying_status="DETERIORATING",
        structure_status="REVERSING"
    )

    print("\nTEST 4 — MOMENTUM REVERSAL")
    print("-----------------------------------------")
    print("Exit Status:", result["Exit Status"])
    print("Exit Required:", result["Exit Required"])
    print("Exit Reason:", result["Exit Reason"])

    assert result["Exit Status"] == "EXIT"
    assert result["Exit Required"] is True
    assert result["Exit Reason"] == "MOMENTUM REVERSAL"

    print("PASS")


def test_multiple_signal_deterioration():

    result = evaluate_intraday_exit(
        entry_price=100,
        current_price=106,
        stop_loss_price=97,
        momentum_status="DETERIORATING",
        volume_status="DECREASING",
        underlying_status="DETERIORATING",
        structure_status="STRONG"
    )

    print("\nTEST 5 — MULTIPLE SIGNAL DETERIORATION")
    print("-----------------------------------------")
    print("Exit Status:", result["Exit Status"])
    print("Exit Required:", result["Exit Required"])
    print("Exit Reason:", result["Exit Reason"])

    assert result["Exit Status"] == "EXIT"
    assert result["Exit Required"] is True
    assert result["Exit Reason"] == "SIGNAL DETERIORATION"

    print("PASS")


def test_losing_trade_weakening():

    result = evaluate_intraday_exit(
        entry_price=100,
        current_price=98,
        stop_loss_price=95,
        momentum_status="WEAK",
        volume_status="DECREASING",
        underlying_status="DETERIORATING",
        structure_status="STRONG"
    )

    print("\nTEST 6 — LOSING TRADE WITH WEAKENING")
    print("-----------------------------------------")
    print("Exit Status:", result["Exit Status"])
    print("Exit Required:", result["Exit Required"])
    print("Exit Reason:", result["Exit Reason"])

    assert result["Exit Status"] == "EXIT"
    assert result["Exit Required"] is True
    assert result["Exit Reason"] == "LOSING TRADE — WEAKENING"

    print("PASS")


def test_time_exit():

    result = evaluate_intraday_exit(
        entry_price=100,
        current_price=102,
        stop_loss_price=97,
        momentum_status="STRONG",
        volume_status="STRONG",
        underlying_status="SUPPORTIVE",
        structure_status="STRONG",
        holding_minutes=60,
        max_holding_minutes=60
    )

    print("\nTEST 7 — TIME EXIT")
    print("-----------------------------------------")
    print("Exit Status:", result["Exit Status"])
    print("Exit Required:", result["Exit Required"])
    print("Exit Reason:", result["Exit Reason"])

    assert result["Exit Status"] == "EXIT"
    assert result["Exit Required"] is True
    assert result["Exit Reason"] == "TIME EXIT"

    print("PASS")


def test_healthy_trade_hold():

    result = evaluate_intraday_exit(
        entry_price=100,
        current_price=103,
        stop_loss_price=97,
        momentum_status="STRONG",
        volume_status="STRONG",
        underlying_status="SUPPORTIVE",
        structure_status="STRONG",
        holding_minutes=20,
        max_holding_minutes=60
    )

    print("\nTEST 8 — HEALTHY TRADE")
    print("-----------------------------------------")
    print("Exit Status:", result["Exit Status"])
    print("Exit Required:", result["Exit Required"])
    print("Exit Reason:", result["Exit Reason"])

    assert result["Exit Status"] == "HOLD"
    assert result["Exit Required"] is False
    assert result["Exit Reason"] == "NO EXIT CONDITION"

    print("PASS")


if __name__ == "__main__":

    test_stop_loss()
    test_profit_protection_exit()
    test_target_reached()
    test_momentum_reversal()
    test_multiple_signal_deterioration()
    test_losing_trade_weakening()
    test_time_exit()
    test_healthy_trade_hold()

    print("\n=========================================")
    print("ALL EXIT ENGINE TESTS PASSED")
    print("=========================================")