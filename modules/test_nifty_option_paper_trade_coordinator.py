"""
JKJ AI Trader
V15.3 Paper Trade Coordinator Test

Tests:
    1. Qualified setup → PAPER_TRADE_OPENED
    2. Developing setup → NOT_PERMITTED
    3. Conflicting setup → NOT_PERMITTED

Wisdom Before Wealth.
"""

from modules.nifty_option_paper_trade_coordinator import (
    create_qualified_paper_trade,
)


def make_exit_qualification(
    entry_qualification="ENTRY_QUALIFIED",
    entry_risk_context="CONTROLLED_RISK_CONTEXT",
    stop_loss_context="STOP_SUPPORTED",
    exit_structure="EXIT_STRUCTURE_SUPPORTED",
):
    return {
        "Status": "EVALUATED",

        "Trading Symbol": "NIFTY26SEP25000CE",
        "Underlying": "NIFTY",
        "Expiry": "2026-09-24",
        "Strike": 25000,
        "Option Type": "CE",

        "Entry Price": 103.0,
        "Stop Price": 100.0,

        "Target 1": 106.0,
        "Target 2": 109.0,
        "Target 3": 112.0,

        "Risk Reward 1": 1.0,
        "Risk Reward 2": 2.0,
        "Risk Reward 3": 3.0,

        "Entry Qualification": entry_qualification,
        "Entry Risk Context": entry_risk_context,
        "Stop-Loss Context": stop_loss_context,
        "Exit Structure": exit_structure,
    }


def test_qualified_setup():

    result = create_qualified_paper_trade(
        exit_qualification=make_exit_qualification(),
        quantity=75,
        trade_id="JKJ-V15-003",
        entry_time="2026-09-17 15:15:00",
    )

    print("Qualified Result:", result)

    assert result["Status"] == "PAPER_TRADE_OPENED"
    assert result["Stage"] == "V11"

    trade = result["Trade"]

    assert trade["Status"] == "OPEN"
    assert trade["Trade ID"] == "JKJ-V15-003"
    assert trade["Symbol"] == "NIFTY26SEP25000CE"
    assert trade["Entry Price"] == 103.0
    assert trade["Original Quantity"] == 75
    assert trade["Current Quantity"] == 75

    print("Qualified Setup: PASS")


def test_developing_setup():

    result = create_qualified_paper_trade(
        exit_qualification=make_exit_qualification(
            entry_qualification="ENTRY_DEVELOPING",
            entry_risk_context="DEVELOPING_RISK_CONTEXT",
            stop_loss_context="STOP_DEVELOPING",
            exit_structure="EXIT_STRUCTURE_DEVELOPING",
        ),
        quantity=75,
        trade_id="JKJ-V15-004",
    )

    print("Developing Result:", result)

    assert result["Status"] == "NOT_PERMITTED"
    assert result["Stage"] == "V15.1"

    print("Developing Setup: PASS")


def test_conflicting_setup():

    result = create_qualified_paper_trade(
        exit_qualification=make_exit_qualification(
            entry_qualification="ENTRY_NOT_QUALIFIED",
            entry_risk_context="ELEVATED_RISK_CONTEXT",
            stop_loss_context="STOP_NOT_SUPPORTED",
            exit_structure="EXIT_STRUCTURE_NOT_SUPPORTED",
        ),
        quantity=75,
        trade_id="JKJ-V15-005",
    )

    print("Conflicting Result:", result)

    assert result["Status"] == "NOT_PERMITTED"
    assert result["Stage"] == "V15.1"

    print("Conflicting Setup: PASS")


if __name__ == "__main__":

    test_qualified_setup()
    test_developing_setup()
    test_conflicting_setup()

    print()
    print(
        "V15.3 Paper Trade Coordinator: ALL TESTS PASSED"
    )