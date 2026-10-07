"""
JKJ AI Trader

V21.2.22-D.1 → V21.2.22-B.1 Authorization Bridge

Purpose:
    Restrict the B.1 selected qualification result to ONLY those
    candidates explicitly accepted by the V21.2.22-D.1 evidence gate.

Architecture:

    V21.2.22-B.1 Selected Qualification
                    +
    V21.2.22-D.1 Accepted Candidates
                    ↓
          This Authorization Bridge
                    ↓
        D.1 Authorized B.1 Result
                    ↓
    Existing B.1 → V21.2.16 Adapter
                    ↓
              V21.2.16

Safety:
    - No market-data capture
    - No new observations
    - No ranking
    - No BUY/SELL decisions
    - No orders
    - No paper trades
    - No position sizing
    - No stop/target calculation
"""

from __future__ import annotations

from typing import Any, Dict


LIVE_ORDER = False
PAPER_TRADE = False


def build_d1_authorized_b1_result(
    selected_qualification_result: Dict[str, Any],
    d1_result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Restrict the existing B.1 selected qualification result to candidates
    explicitly accepted by V21.2.22-D.1.

    The original B.1 candidate records are preserved.

    D.1 is treated as the authorization boundary.
    """

    if not isinstance(selected_qualification_result, dict):
        return {
            "Status": "D1_AUTHORIZATION_REJECTED",
            "Reason": "Selected qualification result must be a dictionary.",
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    if selected_qualification_result.get("Status") != (
        "CANDIDATE_QUALIFICATION_COMPLETE"
    ):
        return {
            "Status": "D1_AUTHORIZATION_REJECTED",
            "Reason": (
                "Selected qualification result must be "
                "CANDIDATE_QUALIFICATION_COMPLETE."
            ),
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    if not isinstance(d1_result, dict):
        return {
            "Status": "D1_AUTHORIZATION_REJECTED",
            "Reason": "D.1 result must be a dictionary.",
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    if d1_result.get("Status") != (
        "EVIDENCE_GATED_ENTRY_BRIDGE_COMPLETE"
    ):
        return {
            "Status": "D1_AUTHORIZATION_REJECTED",
            "Reason": (
                "D.1 result must be "
                "EVIDENCE_GATED_ENTRY_BRIDGE_COMPLETE."
            ),
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    b1_candidates = selected_qualification_result.get(
        "Qualified Candidates"
    )

    if not isinstance(b1_candidates, list):
        return {
            "Status": "D1_AUTHORIZATION_REJECTED",
            "Reason": "B.1 Qualified Candidates must be a list.",
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    accepted_candidates = d1_result.get("Accepted Candidates")

    if not isinstance(accepted_candidates, list):
        return {
            "Status": "D1_AUTHORIZATION_REJECTED",
            "Reason": "D.1 Accepted Candidates must be a list.",
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    accepted_symbols = []

    for candidate in accepted_candidates:
        if not isinstance(candidate, dict):
            continue

        symbol = candidate.get("Trading Symbol")

        if symbol and symbol not in accepted_symbols:
            accepted_symbols.append(symbol)

    authorized_candidates = []
    rejected_candidates = []

    for candidate in b1_candidates:
        if not isinstance(candidate, dict):
            continue

        symbol = candidate.get("Trading Symbol")

        if not symbol:
            rejected_candidates.append({
                "Trading Symbol": symbol,
                "Reason": "B.1 candidate has no Trading Symbol.",
            })
            continue

        if symbol in accepted_symbols:
            authorized_candidates.append(candidate)
        else:
            rejected_candidates.append({
                "Trading Symbol": symbol,
                "Reason": (
                    "Candidate was selected by B.1 but was not "
                    "accepted by V21.2.22-D.1."
                ),
            })

    return {
        "Status": "D1_AUTHORIZED_B1_RESULT_COMPLETE",

        "Candidates": selected_qualification_result.get(
            "Candidates", {}
        ),

        "Qualified Candidates": authorized_candidates,

        "Selection Applied": True,

        "D1 Authorization Applied": True,

        "Original B1 Qualified Candidate Count": len(
            b1_candidates
        ),

        "D1 Accepted Candidate Count": len(
            accepted_symbols
        ),

        "Authorized Candidate Count": len(
            authorized_candidates
        ),

        "Rejected By D1 Count": len(
            rejected_candidates
        ),

        "Rejected By D1 Candidates": rejected_candidates,

        "Authorization Source": (
            "V21.2.22-D.1 Evidence-Gated Entry Bridge"
        ),

        "Selection Source": (
            selected_qualification_result.get(
                "Selection Source",
                "V21.2.22-B.1 Candidate Selection",
            )
        ),

        "Original Qualification Source": (
            selected_qualification_result.get(
                "Original Qualification Source",
                "V21.2.20 Candidate Qualification",
            )
        ),

        "Next Stage": (
            "Existing V21.2.20 → V21.2.16 Adapter"
        ),

        "Live Order": LIVE_ORDER,
        "Paper Trade": PAPER_TRADE,
    }


def print_d1_authorization_summary(
    result: Dict[str, Any],
) -> None:
    """Print a compact D.1 authorization summary."""

    print("\n=== D.1 → B.1 AUTHORIZATION ===")
    print(f"Status: {result.get('Status')}")
    print(
        "Original B.1 Candidates: "
        f"{result.get('Original B1 Qualified Candidate Count', 0)}"
    )
    print(
        "D.1 Accepted: "
        f"{result.get('D1 Accepted Candidate Count', 0)}"
    )
    print(
        "Authorized: "
        f"{result.get('Authorized Candidate Count', 0)}"
    )
    print(
        "Rejected By D.1: "
        f"{result.get('Rejected By D1 Count', 0)}"
    )

    for candidate in result.get(
        "Qualified Candidates", []
    ):
        print(
            f"  AUTHORIZED: "
            f"{candidate.get('Trading Symbol')}"
        )

    for candidate in result.get(
        "Rejected By D1 Candidates", []
    ):
        print(
            f"  BLOCKED: "
            f"{candidate.get('Trading Symbol')}"
        )

    print(
        "Next Stage: "
        f"{result.get('Next Stage')}"
    )
    print(
        "Live Order: "
        f"{result.get('Live Order')}"
    )
    print(
        "Paper Trade: "
        f"{result.get('Paper Trade')}"
    )
