"""
JKJ AI Trader
V12.2 — Real Market to Paper Position Bridge Test

Purpose:
Verify that a validated V12.1 observation can safely update
an existing V11 paper position.

This test does NOT:
- place live orders
- connect to Zerodha
- create live positions
- make BUY/SELL decisions
- modify V1–V11
- modify main.py
"""


from modules.intraday_option_real_to_paper_bridge import (
    bridge_real_market_to_paper,
)


def make_valid_observation():
    return {
        "Status": "RECORDED",
        "Data Status": "VALID",
        "Trading Symbol": "NIFTY2691525000PE",
        "Instrument Token": 12125186,
        "Underlying": "NIFTY",
        "Current Price": 1646.35,
        "Observation Timestamp": "2026-09-15T05:35:33",
    }


def make_valid_paper_trade():
    return {
        "Status": "OPEN",
        "Trade ID": "TEST-V12-2",
        "Symbol": "NIFTY2691525000PE",
        "Instrument Type": "OPTION",
        "Entry Price": 1600.00,
        "Current Price": 1600.00,
        "Original Quantity": 65,
        "Current Quantity": 65,
    }


def test_valid_bridge():
    result = bridge_real_market_to_paper(
        make_valid_observation(),
        make_valid_paper_trade(),
    )

    assert result["Status"] == "BRIDGED"
    assert result["Market Data Status"] == "VALID"
    assert result["Current Price"] == 1646.35

    updated_trade = result["Paper Trade"]

    assert updated_trade["Status"] == "OPEN"
    assert updated_trade["Entry Price"] == 1600.00
    assert updated_trade["Current Price"] == 1646.35
    assert updated_trade["Current Quantity"] == 65

    print("PASS: Valid real-market observation bridged to paper trade.")


def test_invalid_observation():
    observation = make_valid_observation()
    observation["Status"] = "STALE"

    result = bridge_real_market_to_paper(
        observation,
        make_valid_paper_trade(),
    )

    assert result["Status"] == "REJECTED"

    print("PASS: Non-recorded observation is rejected.")


def test_invalid_data_status():
    observation = make_valid_observation()
    observation["Data Status"] = "INVALID"

    result = bridge_real_market_to_paper(
        observation,
        make_valid_paper_trade(),
    )

    assert result["Status"] == "REJECTED"

    print("PASS: Invalid market data is rejected.")


def test_invalid_paper_trade():
    result = bridge_real_market_to_paper(
        make_valid_observation(),
        None,
    )

    assert result["Status"] == "REJECTED"

    print("PASS: Invalid paper trade is rejected.")


def test_invalid_price():
    observation = make_valid_observation()
    observation["Current Price"] = 0

    result = bridge_real_market_to_paper(
        observation,
        make_valid_paper_trade(),
    )

    assert result["Status"] == "REJECTED"

    print("PASS: Invalid market price is rejected.")


def run_all_tests():
    print("\nJKJ AI Trader — V12.2 Bridge Tests")
    print("=" * 55)

    test_valid_bridge()
    test_invalid_observation()
    test_invalid_data_status()
    test_invalid_paper_trade()
    test_invalid_price()

    print("\n" + "=" * 55)
    print("V12.2 REAL MARKET → PAPER BRIDGE TESTS: PASS")
    print("=" * 55)


if __name__ == "__main__":
    run_all_tests()