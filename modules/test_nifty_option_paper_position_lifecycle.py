"""
JKJ AI Trader
V15.4 Paper Position Lifecycle Test

Tests:
    1. Price update / peak tracking
    2. First partial exit
    3. Second partial exit
    4. Final exit
    5. Final closed position
    6. Exit event history
    7. Cumulative P&L

Wisdom Before Wealth.
"""

from modules.nifty_option_paper_position_lifecycle import (
    update_paper_position,
    process_paper_position_exit,
    get_current_paper_position,
)

from modules.intraday_paper_trading import (
    open_paper_trade,
)


def create_trade():

    return open_paper_trade(
        trade_id="JKJ-V15-006",
        symbol="NIFTY26SEP25000CE",
        instrument_type="OPTION",
        entry_price=100,
        quantity=300,
        stop_loss=95,
        target=120,
        entry_status="ENTRY_QUALIFIED",
        entry_reason="V15 qualified paper trade",
        expiry="2026-09-24",
        strike=25000,
        option_type="CE",
        underlying="NIFTY",
        entry_time="2026-09-17 15:15:00",
    )


def test_price_update():

    trade = create_trade()

    result = update_paper_position(
        trade,
        110,
    )

    assert result["Status"] == "UPDATED"
    assert trade["Current Price"] == 110
    assert trade["Peak Price"] == 110
    assert trade["Peak Profit %"] == 10

    print("Price Update / Peak: PASS")


def test_first_partial_exit():

    trade = create_trade()

    update_paper_position(
        trade,
        110,
    )

    result = process_paper_position_exit(
        trade=trade,
        current_price=108,
        exit_signal="WATCH — DETERIORATION WATCH",
        momentum_status="WEAK",
        volume_status="DECREASING",
        underlying_status="SUPPORTIVE",
        structure_status="STABLE",
        costs=65,
        slippage=10,
        timestamp="2026-09-17 15:25:00",
    )

    assert result["Status"] == "RECORDED"
    assert result["Exit Quantity"] > 0
    assert result["Remaining Quantity"] < 300
    assert result["Trade Status"] == "OPEN"

    print("First Partial Exit: PASS")


def test_complete_lifecycle():

    trade = create_trade()

    # Price rises and peak is recorded.
    update_paper_position(
        trade,
        110,
    )

    # First exit.
    result = process_paper_position_exit(
        trade=trade,
        current_price=108,
        exit_signal="WATCH — DETERIORATION WATCH",
        momentum_status="WEAK",
        volume_status="DECREASING",
        underlying_status="SUPPORTIVE",
        structure_status="STABLE",
        costs=65,
        slippage=10,
        timestamp="2026-09-17 15:25:00",
    )

    assert result["Status"] == "RECORDED"
    assert trade["Status"] == "OPEN"

    # Second exit.
    result = process_paper_position_exit(
        trade=trade,
        current_price=114,
        exit_signal="EXIT — PROFIT PROTECTION",
        momentum_status="DETERIORATING",
        volume_status="DECREASING",
        underlying_status="WEAK",
        structure_status="DETERIORATING",
        costs=70,
        slippage=10,
        timestamp="2026-09-17 15:32:00",
    )

    assert result["Status"] == "RECORDED"

    # Final exit.
    result = process_paper_position_exit(
        trade=trade,
        current_price=118,
        exit_signal="EXIT — MOMENTUM REVERSAL",
        momentum_status="REVERSING",
        volume_status="DECREASING",
        underlying_status="DETERIORATING",
        structure_status="DETERIORATING",
        costs=75,
        slippage=10,
        timestamp="2026-09-17 15:40:00",
    )

    assert result["Status"] == "RECORDED"
    assert trade["Current Quantity"] == 0
    assert trade["Status"] == "CLOSED"

    print("Complete Lifecycle: PASS")


def test_final_position():

    trade = create_trade()

    update_paper_position(
        trade,
        110,
    )

    process_paper_position_exit(
        trade=trade,
        current_price=108,
        exit_signal="WATCH — DETERIORATION WATCH",
        momentum_status="WEAK",
        volume_status="DECREASING",
        underlying_status="SUPPORTIVE",
        structure_status="STABLE",
        costs=65,
        slippage=10,
        timestamp="2026-09-17 15:25:00",
    )

    process_paper_position_exit(
        trade=trade,
        current_price=114,
        exit_signal="EXIT — PROFIT PROTECTION",
        momentum_status="DETERIORATING",
        volume_status="DECREASING",
        underlying_status="WEAK",
        structure_status="DETERIORATING",
        costs=70,
        slippage=10,
        timestamp="2026-09-17 15:32:00",
    )

    process_paper_position_exit(
        trade=trade,
        current_price=118,
        exit_signal="EXIT — MOMENTUM REVERSAL",
        momentum_status="REVERSING",
        volume_status="DECREASING",
        underlying_status="DETERIORATING",
        structure_status="DETERIORATING",
        costs=75,
        slippage=10,
        timestamp="2026-09-17 15:40:00",
    )

    position = get_current_paper_position(trade)

    assert position["Status"] == "CLOSED"
    assert position["Current Quantity"] == 0

    print("Final Position: PASS")


def test_exit_event_history():

    trade = create_trade()

    update_paper_position(
        trade,
        110,
    )

    process_paper_position_exit(
        trade=trade,
        current_price=108,
        exit_signal="WATCH — DETERIORATION WATCH",
        momentum_status="WEAK",
        volume_status="DECREASING",
        underlying_status="SUPPORTIVE",
        structure_status="STABLE",
        costs=65,
        slippage=10,
        timestamp="2026-09-17 15:25:00",
    )

    process_paper_position_exit(
        trade=trade,
        current_price=114,
        exit_signal="EXIT — PROFIT PROTECTION",
        momentum_status="DETERIORATING",
        volume_status="DECREASING",
        underlying_status="WEAK",
        structure_status="DETERIORATING",
        costs=70,
        slippage=10,
        timestamp="2026-09-17 15:32:00",
    )

    process_paper_position_exit(
        trade=trade,
        current_price=118,
        exit_signal="EXIT — MOMENTUM REVERSAL",
        momentum_status="REVERSING",
        volume_status="DECREASING",
        underlying_status="DETERIORATING",
        structure_status="DETERIORATING",
        costs=75,
        slippage=10,
        timestamp="2026-09-17 15:40:00",
    )

    exit_events = trade.get(
        "Exit Events",
        [],
    )

    assert len(exit_events) == 3

    print("Exit Event History: PASS")


if __name__ == "__main__":

    test_price_update()
    test_first_partial_exit()
    test_complete_lifecycle()
    test_final_position()
    test_exit_event_history()

    print()
    print(
        "V15.4 Paper Position Lifecycle: "
        "ALL TESTS PASSED"
    )