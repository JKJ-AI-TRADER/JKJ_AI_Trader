"""
JKJ AI Trader
V15.2 Paper Trade Entry Bridge Test

Tests:
    1. Permitted setup → PREPARED
    2. Developing setup → REJECTED
    3. Invalid quantity → REJECTED
    4. Missing trade ID → REJECTED

Wisdom Before Wealth.
"""

from modules.nifty_option_paper_trade_entry_bridge import (
    prepare_paper_trade_entry,
)


def make_qualification():
    return {
        "Status": "QUALIFIED",

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

        "Entry Qualification": "ENTRY_QUALIFIED",
        "Entry Risk Context": "CONTROLLED_RISK_CONTEXT",
        "Stop-Loss Context": "STOP_SUPPORTED",
        "Exit Structure": "EXIT_STRUCTURE_SUPPORTED",

        "Paper Trade Permission": "PERMITTED",

        "Qualification Reason": (
            "V14.5 setup satisfies all controlled "
            "paper-trade entry requirements"
        ),
    }


def test_permitted_setup():

    result = prepare_paper_trade_entry(
        paper_trade_qualification=make_qualification(),
        quantity=75,
        trade_id="JKJ-V15-001",
        entry_time="2026-09-17 15:15:00",
    )

    assert result["Status"] == "PREPARED"
    assert result["Paper Trade Permission"] == "PERMITTED"

    assert result["Trade ID"] == "JKJ-V15-001"
    assert result["Symbol"] == "NIFTY26SEP25000CE"
    assert result["Instrument Type"] == "OPTION"

    assert result["Entry Price"] == 103.0
    assert result["Stop Loss"] == 100.0
    assert result["Target"] == 106.0

    assert result["Target 1"] == 106.0
    assert result["Target 2"] == 109.0
    assert result["Target 3"] == 112.0

    assert result["Quantity"] == 75

    print("Permitted Setup: PASS")


def test_not_permitted_setup():

    data = make_qualification()
    data["Paper Trade Permission"] = "NOT_PERMITTED"

    result = prepare_paper_trade_entry(
        paper_trade_qualification=data,
        quantity=75,
        trade_id="JKJ-V15-002",
    )

    assert result["Status"] == "REJECTED"

    print("Not Permitted Setup: PASS")


def test_invalid_quantity():

    result = prepare_paper_trade_entry(
        paper_trade_qualification=make_qualification(),
        quantity=0,
        trade_id="JKJ-V15-003",
    )

    assert result["Status"] == "REJECTED"

    print("Invalid Quantity: PASS")


def test_missing_trade_id():

    result = prepare_paper_trade_entry(
        paper_trade_qualification=make_qualification(),
        quantity=75,
        trade_id="",
    )

    assert result["Status"] == "REJECTED"

    print("Missing Trade ID: PASS")


def test_invalid_qualification():

    result = prepare_paper_trade_entry(
        paper_trade_qualification=None,
        quantity=75,
        trade_id="JKJ-V15-005",
    )

    assert result["Status"] == "REJECTED"

    print("Invalid Qualification: PASS")


if __name__ == "__main__":

    test_permitted_setup()
    test_not_permitted_setup()
    test_invalid_quantity()
    test_missing_trade_id()
    test_invalid_qualification()

    print()
    print(
        "V15.2 Paper Trade Entry Bridge: ALL TESTS PASSED"
    )