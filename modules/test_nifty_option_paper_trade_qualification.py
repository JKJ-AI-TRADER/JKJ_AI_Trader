"""
JKJ AI Trader
V15.1 Paper Trade Qualification Bridge Test

Tests:
    1. Controlled setup → PERMITTED
    2. Developing setup → NOT_PERMITTED
    3. Conflicting setup → NOT_PERMITTED
    4. Invalid input → REJECTED

Wisdom Before Wealth.
"""

from modules.nifty_option_paper_trade_qualification import (
    evaluate_paper_trade_qualification,
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


def test_controlled_setup():
    result = evaluate_paper_trade_qualification(
        make_exit_qualification()
    )

    assert result["Status"] == "QUALIFIED"
    assert result["Paper Trade Permission"] == "PERMITTED"

    print("Controlled Setup: PASS")


def test_developing_setup():
    result = evaluate_paper_trade_qualification(
        make_exit_qualification(
            entry_qualification="ENTRY_DEVELOPING",
            entry_risk_context="DEVELOPING_RISK_CONTEXT",
            stop_loss_context="STOP_DEVELOPING",
            exit_structure="EXIT_STRUCTURE_DEVELOPING",
        )
    )

    assert result["Status"] == "QUALIFIED"
    assert result["Paper Trade Permission"] == "NOT_PERMITTED"

    print("Developing Setup: PASS")


def test_conflicting_setup():
    result = evaluate_paper_trade_qualification(
        make_exit_qualification(
            entry_qualification="ENTRY_NOT_QUALIFIED",
            entry_risk_context="ELEVATED_RISK_CONTEXT",
            stop_loss_context="STOP_NOT_SUPPORTED",
            exit_structure="EXIT_STRUCTURE_NOT_SUPPORTED",
        )
    )

    assert result["Status"] == "QUALIFIED"
    assert result["Paper Trade Permission"] == "NOT_PERMITTED"

    print("Conflicting Setup: PASS")


def test_invalid_input():
    result = evaluate_paper_trade_qualification(None)

    assert result["Status"] == "REJECTED"

    print("Invalid Input: PASS")


def test_wrong_status():
    data = make_exit_qualification()
    data["Status"] = "INVALID"

    result = evaluate_paper_trade_qualification(data)

    assert result["Status"] == "REJECTED"

    print("Wrong Status: PASS")


if __name__ == "__main__":

    test_controlled_setup()
    test_developing_setup()
    test_conflicting_setup()
    test_invalid_input()
    test_wrong_status()

    print()
    print(
        "V15.1 Paper Trade Qualification: ALL TESTS PASSED"
    )