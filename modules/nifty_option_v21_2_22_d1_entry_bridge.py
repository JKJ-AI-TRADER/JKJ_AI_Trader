"""
JKJ AI Trader
V21.2.22-D.1 — Evidence-Gated Entry Bridge

Purpose:
    Pass only V21.2.22-D accepted candidates toward the
    existing entry-qualification layer.

Safety:
    Observation / qualification bridge only.
    No live orders.
    No paper trades.
    No BUY/SELL decisions.
    No position sizing.
    No stop/target calculation.
"""

from typing import Any, Dict


LIVE_ORDER = False
PAPER_TRADE = False


def build_entry_bridge(
    final_evidence_result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Accept only candidates that passed V21.2.22-D.
    """

    if final_evidence_result.get("Status") != (
        "FINAL_EVIDENCE_GATE_COMPLETE"
    ):
        return {
            "Status": "ENTRY_BRIDGE_REJECTED",
            "Reason": "Invalid V21.2.22-D result.",
            "Accepted Candidates": [],
            "Live Order": False,
            "Paper Trade": False,
        }

    accepted = final_evidence_result.get(
        "Accepted Candidates",
        [],
    )

    rejected = final_evidence_result.get(
        "Rejected Candidates",
        [],
    )

    bridge_candidates = []

    for candidate in accepted:
        bridge_candidates.append(
            {
                "Trading Symbol": candidate.get("Trading Symbol"),
                "Lifecycle": candidate.get("Lifecycle"),
                "Qualification": candidate.get("Qualification"),
                "V12.6 Persistence": candidate.get(
                    "V12.6 Persistence"
                ),
                "V12.6 Direction": candidate.get(
                    "V12.6 Direction"
                ),
                "V12.6 Confirmation": candidate.get(
                    "V12.6 Confirmation"
                ),
                "Overall Movement %": candidate.get(
                    "Overall Movement %"
                ),
                "Latest Movement %": candidate.get(
                    "Latest Movement %"
                ),
                "Evidence Gate": "PASSED",
                "Entry Evaluation": "PENDING",
                "Live Order": False,
                "Paper Trade": False,
            }
        )

    return {
        "Status": "EVIDENCE_GATED_ENTRY_BRIDGE_COMPLETE",
        "Accepted Candidate Count": len(bridge_candidates),
        "Rejected Candidate Count": len(rejected),
        "Accepted Candidates": bridge_candidates,
        "Rejected Candidates": rejected,
        "Next Stage": "EXISTING_ENTRY_QUALIFICATION",
        "Live Order": False,
        "Paper Trade": False,
    }


if __name__ == "__main__":
    print("V21.2.22-D.1 Evidence-Gated Entry Bridge")
    print("Bridge only — no trading execution")
    print("Live Order: False")
    print("Paper Trade: False")
