"""
JKJ AI Trader
V12.3 — Option Paper Monitor Bridge Test

Purpose:
Verify that a validated market observation can be passed
safely into the existing V10 option paper position monitor.

This test does NOT:
- connect to Zerodha
- place live orders
- execute paper exits
- make BUY decisions
- modify V10
- modify V11
- modify main.py
"""


from modules.intraday_option_paper_monitor_bridge import (
    monitor_real_market_paper_position,
)

from modules.intraday_paper_trading import (
    open_paper_trade,
)


def make_valid_observation():
    return {
        "Status": "RECORDED",
        "Data Status": "VALID",
        "Trading Symbol": "NIFTY2691525000PE",
        "Instrument Token": 12125186,
        "Underlying": "NIFTY",
        "Current Price": 1652.00,
        "Observation Timestamp": "2026-09-15T06:15:29",
    }


def make_paper_trade():
    return open_paper_trade(
        trade_id="V12-3-MONITOR-TEST",
        symbol="NIFTY2691525000PE",
        instrument_type="OPTION",
        entry_price=1600.00,
        quantity=65,
        stop_loss=1550.00,
        target=1700.00,
        underlying="NIFTY",
        strike=25000,
        option_type="PE",
    )


def test_valid_monitor_bridge():
    result = monitor_real_market_paper_position(
        observation_record=make_valid_observation(),
        paper_trade=make_paper_trade(),
    )

    assert result["Status"] == "MONITORED"
    assert result["Market Data Status"] == "VALID"
    assert result["Trading Symbol"] == "NIFTY2691525000PE"
    assert result["Current Price"] == 1652.00

    assert isinstance(result["V10 Result"], dict)

    print(
        "PASS: Valid real-market observation reached V10."
    )


def test_invalid_observation_status():
    observation = make_valid_observation()
    observation["Status"] = "STALE"

    result = monitor_real_market_paper_position(
        observation_record=observation,
        paper_trade=make_paper_trade(),
    )

    assert result["Status"] == "REJECTED"
    assert result["Decision"] == "NO TRADE"

    print(
        "PASS: Non-recorded observation is rejected."
    )


def test_invalid_data_status():
    observation = make_valid_observation()
    observation["Data Status"] = "INVALID"

    result = monitor_real_market_paper_position(
        observation_record=observation,
        paper_trade=make_paper_trade(),
    )

    assert result["Status"] == "REJECTED"
    assert result["Decision"] == "NO TRADE"

    print(
        "PASS: Invalid market data is rejected."
    )


def test_invalid_price():
    observation = make_valid_observation()
    observation["Current Price"] = 0

    result = monitor_real_market_paper_position(
        observation_record=observation,
        paper_trade=make_paper_trade(),
    )

    assert result["Status"] == "REJECTED"
    assert result["Decision"] == "NO TRADE"

    print(
        "PASS: Invalid market price is rejected."
    )


def test_invalid_trade():
    result = monitor_real_market_paper_position(
        observation_record=make_valid_observation(),
        paper_trade=None,
    )

    assert result["Status"] == "REJECTED"
    assert result["Decision"] == "NO TRADE"

    print(
        "PASS: Invalid paper trade is rejected."
    )


def run_all_tests():
    print("\nJKJ AI Trader — V12.3 Monitor Bridge Tests")
    print("=" * 55)

    test_valid_monitor_bridge()
    test_invalid_observation_status()
    test_invalid_data_status()
    test_invalid_price()
    test_invalid_trade()

    print("\n" + "=" * 55)
    print("V12.3 OPTION PAPER MONITOR BRIDGE TESTS: PASS")
    print("=" * 55)


if __name__ == "__main__":
    run_all_tests()