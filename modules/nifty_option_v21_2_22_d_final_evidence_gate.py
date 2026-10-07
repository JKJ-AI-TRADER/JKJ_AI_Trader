"""
JKJ AI Trader
V21.2.22-D — Final Evidence Gate

Purpose:
    Final observational gate after V21.2.22-C reconciliation.

Safety:
    - No live orders
    - No paper trades
    - No BUY/SELL decisions
    - No position sizing
    - No stop/target calculation

A candidate passes only when current detailed evidence agrees
with the developing lifecycle and V12.6 momentum evidence.
"""

from typing import Any, Dict


LIVE_ORDER = False
PAPER_TRADE = False

ACCEPTED_LIFECYCLE_STATES = {
    "PERSISTING",
    "STRENGTHENING",
}

ACCEPTED_QUALIFICATIONS = {
    "DEVELOPING_CANDIDATE",
    "STRONG_DEVELOPING_CANDIDATE",
}

ACCEPTED_CONFIRMATIONS = {
    "CONFIRMED",
    "PARTIALLY_CONFIRMED",
}


def _number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def evaluate_final_evidence(candidate: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate one reconciled candidate.

    This is an evidence gate only.
    """

    symbol = candidate.get("Trading Symbol")

    lifecycle = candidate.get("Lifecycle")
    qualification = candidate.get("Qualification")

    persistence = candidate.get("V12.6 Persistence")
    direction = candidate.get("V12.6 Direction")
    confirmation = candidate.get("V12.6 Confirmation")

    overall_movement = _number(candidate.get("Overall Movement %"))
    latest_movement = _number(candidate.get("Latest Movement %"))

    checks = {
        "Lifecycle": lifecycle in ACCEPTED_LIFECYCLE_STATES,
        "Qualification": qualification in ACCEPTED_QUALIFICATIONS,
        "Positive Overall Movement": (
            overall_movement is not None and overall_movement > 0
        ),
        "Positive Latest Movement": (
            latest_movement is not None and latest_movement > 0
        ),
        "V12.6 Direction UP": direction == "UP",
        "V12.6 Persistence": persistence == "PERSISTENT",
        "V12.6 Confirmation": confirmation in ACCEPTED_CONFIRMATIONS,
    }

    failed_checks = [
        name for name, passed in checks.items()
        if not passed
    ]

    if not failed_checks:
        status = "FINAL_EVIDENCE_ACCEPTED"
        reason = (
            "Current lifecycle, detailed price movement, "
            "and V12.6 momentum evidence are aligned."
        )
    else:
        status = "FINAL_EVIDENCE_REJECTED"
        reason = (
            "One or more required evidence conditions failed."
        )

    return {
        "Trading Symbol": symbol,
        "Status": status,
        "Lifecycle": lifecycle,
        "Qualification": qualification,
        "V12.6 Persistence": persistence,
        "V12.6 Direction": direction,
        "V12.6 Confirmation": confirmation,
        "Overall Movement %": overall_movement,
        "Latest Movement %": latest_movement,
        "Evidence Checks": checks,
        "Failed Checks": failed_checks,
        "Reason": reason,
        "Live Order": False,
        "Paper Trade": False,
    }


def evaluate_final_evidence_gate(
    reconciliation_result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Evaluate all reconciled candidates.
    """

    if reconciliation_result.get("Status") != (
        "EVIDENCE_RECONCILIATION_COMPLETE"
    ):
        return {
            "Status": "FINAL_EVIDENCE_GATE_REJECTED",
            "Reason": "Invalid reconciliation result.",
            "Accepted Candidates": [],
            "Rejected Candidates": [],
            "Live Order": False,
            "Paper Trade": False,
        }

    candidates = reconciliation_result.get(
        "Candidates",
        reconciliation_result.get("Reconciled Candidates", {}),
    )

    accepted = []
    rejected = []

    if isinstance(candidates, dict):
        iterable = candidates.values()
    else:
        iterable = candidates

    for candidate in iterable:
        result = evaluate_final_evidence(candidate)

        if result["Status"] == "FINAL_EVIDENCE_ACCEPTED":
            accepted.append(result)
        else:
            rejected.append(result)

    return {
        "Status": "FINAL_EVIDENCE_GATE_COMPLETE",
        "Candidate Count": len(accepted) + len(rejected),
        "Accepted Candidate Count": len(accepted),
        "Rejected Candidate Count": len(rejected),
        "Accepted Candidates": accepted,
        "Rejected Candidates": rejected,
        "Live Order": False,
        "Paper Trade": False,
    }


if __name__ == "__main__":
    print("V21.2.22-D Final Evidence Gate")
    print("Observation/evidence gate only")
    print("Live Order: False")
    print("Paper Trade: False")
