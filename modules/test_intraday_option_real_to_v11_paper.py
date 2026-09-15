"""
JKJ AI Trader
V12.2 — Real Market to V11 Paper Trading Integration Test

Purpose:
Verify that V12.2 can safely update a genuine V11 paper
trade created by open_paper_trade().

This test does NOT:
- connect to Zerodha
- place live orders
- create live positions
- make BUY/SELL decisions
- modify V1–V11
- modify main.py
"""


from modules.intraday_paper_trading import (
    open_paper_trade,
)

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


def test_real_market_to_v11_paper():
    paper_trade = open_paper_trade(
        trade_id="V12-2-REAL-TO-PAPER",
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

    assert isinstance(paper_trade, dict)
    assert paper_trade.get("Status") == "OPEN"
    assert paper_trade.get("Entry Price") == 1600.00
    
    assert paper_trade.get("Current Quantity") == 65

    result = bridge_real_market_to_paper(
        make_valid_observation(),
        paper_trade,
    )

    assert result["Status"] == "BRIDGED"
    assert result["Market Data Status"] == "VALID"
    assert result["Trading Symbol"] == "NIFTY2691525000PE"
    assert result["Current Price"] == 1646.35

    updated_trade = result["Paper Trade"]

    assert updated_trade.get("Status") == "OPEN"
    assert updated_trade.get("Entry Price") == 1600.00
    assert updated_trade.get("Current Price") == 1646.35
    assert updated_trade.get("Current Quantity") == 65
    assert updated_trade.get("Original Quantity") == 65

    print(
        "PASS: Real-market observation updated a genuine V11 paper trade."
    )


def test_entry_price_is_not_changed():
    paper_trade = open_paper_trade(
        trade_id="V12-2-ENTRY-PROTECTION",
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

    result = bridge_real_market_to_paper(
        make_valid_observation(),
        paper_trade,
    )

    updated_trade = result["Paper Trade"]

    assert updated_trade.get("Entry Price") == 1600.00
    assert updated_trade.get("Current Price") == 1646.35

    print("PASS: Entry price remains protected.")


def test_position_quantity_is_not_changed():
    paper_trade = open_paper_trade(
        trade_id="V12-2-QUANTITY-PROTECTION",
        symbol="NIFTY2691525000PE",
        instrument_type="OPTION",
        entry_price=1600.00,
        quantity=65,
        underlying="NIFTY",
        strike=25000,
        option_type="PE",
    )

    result = bridge_real_market_to_paper(
        make_valid_observation(),
        paper_trade,
    )

    updated_trade = result["Paper Trade"]

    assert updated_trade.get("Original Quantity") == 65
    assert updated_trade.get("Current Quantity") == 65

    print("PASS: Paper position quantity remains unchanged.")


def run_all_tests():
    print("\nJKJ AI Trader — V12.2 → V11 Integration Test")
    print("=" * 55)

    test_real_market_to_v11_paper()
    test_entry_price_is_not_changed()
    test_position_quantity_is_not_changed()

    print("\n" + "=" * 55)
    print("V12.2 → V11 PAPER INTEGRATION TESTS: PASS")
    print("=" * 55)


if __name__ == "__main__":
    run_all_tests()