"""
JKJ AI Trader — Intraday Cost Engine Test

Wisdom Before Wealth.

No live market data.
No broker connection.
No real trading.
"""


from intraday_cost_engine import calculate_intraday_cost


def test_profitable_option_trade():

    result = calculate_intraday_cost(
        instrument_type="options",
        buy_price=100,
        sell_price=105,
        quantity=75
    )

    print("\nTEST 1 — PROFITABLE OPTION TRADE")
    print("-----------------------------------------")
    print("Gross P&L:", result["Gross P&L"])
    print("Total Costs:", result["Total Costs"])
    print("Net P&L:", result["Net P&L"])
    print("Breakeven Price:", result["Breakeven Price"])
    print("Trade Viable:", result["Trade Viable"])

    assert result["Status"] == "PROFITABLE"
    assert result["Trade Viable"] is True
    assert result["Net P&L"] > 0
    assert result["Net P&L"] < result["Gross P&L"]

    print("PASS")


def test_small_profit_becomes_loss():

    result = calculate_intraday_cost(
        instrument_type="options",
        buy_price=100,
        sell_price=100.20,
        quantity=75
    )

    print("\nTEST 2 — SMALL GROSS PROFIT")
    print("-----------------------------------------")
    print("Gross P&L:", result["Gross P&L"])
    print("Total Costs:", result["Total Costs"])
    print("Net P&L:", result["Net P&L"])
    print("Breakeven Price:", result["Breakeven Price"])
    print("Trade Viable:", result["Trade Viable"])

    assert result["Gross P&L"] > 0
    assert result["Net P&L"] < 0
    assert result["Trade Viable"] is False

    print("PASS")


def test_invalid_input():

    result = calculate_intraday_cost(
        instrument_type="options",
        buy_price=0,
        sell_price=105,
        quantity=75
    )

    print("\nTEST 3 — INVALID INPUT")
    print("-----------------------------------------")
    print("Status:", result["Status"])
    print("Trade Viable:", result["Trade Viable"])

    assert result["Status"] == "INVALID"
    assert result["Trade Viable"] is False

    print("PASS")


if __name__ == "__main__":

    test_profitable_option_trade()
    test_small_profit_becomes_loss()
    test_invalid_input()

    print("\n=========================================")
    print("ALL COST ENGINE TESTS PASSED")
    print("=========================================")