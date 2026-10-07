"""
JKJ AI Trader
V21.2.23.3 Underlying Confirmation Gate

Purpose:
- Confirm that option movement is directionally supported
  by the NIFTY underlying.
- Apply the same standard to CE and PE.
- Distinguish supported movement from unsupported movement.

Rules:
    CE -> NIFTY rising + CE rising
    PE -> NIFTY falling + PE rising

This is NOT a BUY signal.

Safety:
- NO LIVE ORDERS
- NO PAPER TRADES
- NO POSITION SIZING
- NO STOP / TARGET
"""

from typing import Any, Dict, List


LIVE_ORDER = False
PAPER_TRADE = False

MIN_NIFTY_MOVE_PCT = 0.02
MIN_OPTION_MOVE_PCT = 0.0


def evaluate_underlying_confirmation(
    candidate: Dict[str, Any],
) -> Dict[str, Any]:

    if not isinstance(candidate, dict):
        return {
            "Status": "UNDERLYING_CONFIRMATION_REJECTED",
            "Reason": "Invalid candidate.",
            "Live Order": False,
            "Paper Trade": False,
        }

    option_type = candidate.get("Option Type")
    option_move = candidate.get(
        "Total Observation Movement %"
    )

    nifty_move = candidate.get(
        "NIFTY Session Movement %"
    )

    symbol = candidate.get(
        "Trading Symbol",
        "UNKNOWN",
    )

    if option_type not in ("CE", "PE"):
        return {
            "Status": "UNDERLYING_CONFIRMATION_REJECTED",
            "Trading Symbol": symbol,
            "Reason": "Invalid option type.",
            "Live Order": False,
            "Paper Trade": False,
        }

    if option_move is None or nifty_move is None:
        return {
            "Status": "UNDERLYING_CONFIRMATION_COMPLETE",
            "Trading Symbol": symbol,
            "Option Type": option_type,
            "Option Movement": option_move,
            "NIFTY Movement": nifty_move,
            "Confirmation": "INSUFFICIENT_DATA",
            "Entry Evaluation": "PENDING",
            "Live Order": False,
            "Paper Trade": False,
        }

    option_move = float(option_move)
    nifty_move = float(nifty_move)

    option_positive = (
        option_move > MIN_OPTION_MOVE_PCT
    )

    if option_type == "CE":
        underlying_supports = (
            nifty_move >= MIN_NIFTY_MOVE_PCT
        )
        expected_direction = "UP"

    else:
        underlying_supports = (
            nifty_move <= -MIN_NIFTY_MOVE_PCT
        )
        expected_direction = "DOWN"

    if option_positive and underlying_supports:
        confirmation = "CONFIRMED"
        entry_evaluation = "PENDING_EVIDENCE"

    elif option_positive:
        confirmation = "NOT_CONFIRMED"
        entry_evaluation = "REJECTED_UNDERLYING_CONFLICT"

    else:
        confirmation = "OPTION_MOVEMENT_NOT_POSITIVE"
        entry_evaluation = "REJECTED"

    return {
        "Status": "UNDERLYING_CONFIRMATION_COMPLETE",
        "Trading Symbol": symbol,
        "Option Type": option_type,
        "Expected NIFTY Direction": expected_direction,
        "Option Movement": option_move,
        "NIFTY Movement": nifty_move,
        "Confirmation": confirmation,
        "Entry Evaluation": entry_evaluation,
        "Live Order": False,
        "Paper Trade": False,
    }


def evaluate_underlying_confirmation_gate(
    early_entry_result: Dict[str, Any],
) -> Dict[str, Any]:

    if not isinstance(early_entry_result, dict):
        return {
            "Status": "UNDERLYING_CONFIRMATION_GATE_REJECTED",
            "Reason": "Invalid early-entry result.",
            "Confirmed Candidates": [],
            "Rejected Candidates": [],
            "Live Order": False,
            "Paper Trade": False,
        }

    if early_entry_result.get("Status") != (
        "EARLY_ENTRY_OBSERVATION_COMPLETE"
    ):
        return {
            "Status": "UNDERLYING_CONFIRMATION_GATE_REJECTED",
            "Reason": "Invalid V21.2.23.2 result.",
            "Confirmed Candidates": [],
            "Rejected Candidates": [],
            "Live Order": False,
            "Paper Trade": False,
        }

    candidates = early_entry_result.get(
        "Early Entry Candidates",
        [],
    )

    confirmed = []
    rejected = []

    for candidate in candidates:

        result = evaluate_underlying_confirmation(
            candidate
        )

        enriched = {
            **candidate,
            "Underlying Confirmation":
                result.get("Confirmation"),
            "Expected NIFTY Direction":
                result.get("Expected NIFTY Direction"),
            "Entry Evaluation":
                result.get("Entry Evaluation"),
            "Live Order": False,
            "Paper Trade": False,
        }

        if result.get("Confirmation") == "CONFIRMED":
            confirmed.append(enriched)
        else:
            rejected.append(enriched)

    print()
    print("=" * 70)
    print("V21.2.23.3 UNDERLYING CONFIRMATION GATE")
    print("=" * 70)

    print(
        f"Early Entry Candidates: {len(candidates)}"
    )

    print(
        f"Underlying Confirmed: {len(confirmed)}"
    )

    print(
        f"Underlying Rejected: {len(rejected)}"
    )

    if confirmed:
        print()
        print("CONFIRMED:")

        for item in confirmed:
            print(
                f"  {item['Trading Symbol']} | "
                f"{item['Option Type']} | "
                f"Option Move="
                f"{item.get('Total Observation Movement %', 0.0):.2f}% | "
                f"NIFTY Move="
                f"{item.get('NIFTY Session Movement %', 0.0):+.2f}%"
            )

    if rejected:
        print()
        print("REJECTED / NOT CONFIRMED:")

        for item in rejected:
            print(
                f"  {item['Trading Symbol']} | "
                f"{item['Option Type']} | "
                f"Option Move="
                f"{item.get('Total Observation Movement %', 0.0):.2f}% | "
                f"NIFTY Move="
                f"{item.get('NIFTY Session Movement %', 0.0):+.2f}%"
            )

    print()
    print("IMPORTANT:")
    print("Underlying confirmation is NOT a BUY signal.")
    print("Evidence gate still required.")
    print("Risk evaluation still required.")
    print("Live Order: False")
    print("Paper Trade: False")

    return {
        "Status": "UNDERLYING_CONFIRMATION_GATE_COMPLETE",
        "Confirmed Candidates": confirmed,
        "Rejected Candidates": rejected,
        "Confirmed Candidate Count": len(confirmed),
        "Rejected Candidate Count": len(rejected),
        "Source": (
            "V21.2.23.2 Early Entry Observation"
        ),
        "Next Stage": (
            "V21.2.22 Evidence Reconciliation"
        ),
        "Live Order": False,
        "Paper Trade": False,
    }


def _synthetic_test():

    ce = {
        "Trading Symbol": "TESTCE",
        "Option Type": "CE",
        "Total Observation Movement %": 3.0,
        "NIFTY Session Movement %": 0.10,
    }

    pe = {
        "Trading Symbol": "TESTPE",
        "Option Type": "PE",
        "Total Observation Movement %": 3.0,
        "NIFTY Session Movement %": -0.10,
    }

    conflict = {
        "Trading Symbol": "TESTCONFLICT",
        "Option Type": "PE",
        "Total Observation Movement %": 3.0,
        "NIFTY Session Movement %": 0.10,
    }

    assert (
        evaluate_underlying_confirmation(ce)[
            "Confirmation"
        ]
        == "CONFIRMED"
    )

    assert (
        evaluate_underlying_confirmation(pe)[
            "Confirmation"
        ]
        == "CONFIRMED"
    )

    assert (
        evaluate_underlying_confirmation(conflict)[
            "Confirmation"
        ]
        == "NOT_CONFIRMED"
    )

    early_entry = {
        "Status":
            "EARLY_ENTRY_OBSERVATION_COMPLETE",
        "Early Entry Candidates": [
            ce,
            pe,
            conflict,
        ],
    }

    result = evaluate_underlying_confirmation_gate(
        early_entry
    )

    assert result["Status"] == (
        "UNDERLYING_CONFIRMATION_GATE_COMPLETE"
    )

    assert result["Confirmed Candidate Count"] == 2
    assert result["Rejected Candidate Count"] == 1
    assert result["Live Order"] is False
    assert result["Paper Trade"] is False

    print()
    print(
        "V21.2.23.3 SYNTHETIC TEST: PASS"
    )


if __name__ == "__main__":
    _synthetic_test()
