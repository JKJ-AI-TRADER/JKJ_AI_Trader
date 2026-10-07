"""
JKJ AI Trader
V21.2.22-B.1 → V21.2.16 Selected Candidate Adapter

Purpose:
    Restrict the existing V21.2.20 qualified-candidate result
    to the small set selected by V21.2.22-B.1.

Important:
    - Does NOT capture market data.
    - Does NOT create observations.
    - Does NOT rank candidates.
    - Does NOT make BUY/SELL decisions.
    - Does NOT place orders.
    - Does NOT paper trade.
    - Preserves the original V21.2.20 qualification records.
    - Preserves the existing V21.2.20 → V21.2.16 adapter contract.

Architecture:

    V21.2.20 Qualification
              +
    V21.2.22-B.1 Selection
              ↓
       This Adapter
              ↓
    Restricted Qualification Result
              ↓
    Existing V21.2.20 → V21.2.16 Adapter
"""

from __future__ import annotations

from typing import Any, Dict


LIVE_ORDER = False
PAPER_TRADE = False


def build_selected_qualification_result(
    qualification_result: Dict[str, Any],
    selection_result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Restrict V21.2.20 qualified candidates to the candidates
    selected by V21.2.22-B.1.

    The original qualification records are preserved.

    No trading decision is made here.
    """

    if not isinstance(qualification_result, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Qualification result must be a dictionary.",
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    if qualification_result.get("Status") != (
        "CANDIDATE_QUALIFICATION_COMPLETE"
    ):
        return {
            "Status": "REJECTED",
            "Reason": (
                "Qualification result must be "
                "CANDIDATE_QUALIFICATION_COMPLETE."
            ),
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    if not isinstance(selection_result, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Selection result must be a dictionary.",
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    if selection_result.get("Status") != (
        "CANDIDATE_SELECTION_COMPLETE"
    ):
        return {
            "Status": "REJECTED",
            "Reason": (
                "Selection result must be "
                "CANDIDATE_SELECTION_COMPLETE."
            ),
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    selected_candidates = selection_result.get(
        "Selected Candidates"
    )

    if not isinstance(selected_candidates, list):
        return {
            "Status": "REJECTED",
            "Reason": "Selected Candidates must be a list.",
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    qualified_candidates = qualification_result.get(
        "Qualified Candidates"
    )

    if not isinstance(qualified_candidates, list):
        return {
            "Status": "REJECTED",
            "Reason": "Qualified Candidates must be a list.",
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    selected_symbols = []

    for candidate in selected_candidates:
        if not isinstance(candidate, dict):
            continue

        symbol = candidate.get("Trading Symbol")

        if symbol and symbol not in selected_symbols:
            selected_symbols.append(symbol)

    qualified_by_symbol = {}

    for candidate in qualified_candidates:
        if not isinstance(candidate, dict):
            continue

        symbol = candidate.get("Trading Symbol")

        if symbol:
            qualified_by_symbol[symbol] = candidate

    restricted_candidates = []
    rejected_selections = []

    for symbol in selected_symbols:
        candidate = qualified_by_symbol.get(symbol)

        if candidate is None:
            rejected_selections.append({
                "Trading Symbol": symbol,
                "Reason": (
                    "Selected candidate is not present in "
                    "V21.2.20 Qualified Candidates."
                ),
            })
            continue

        restricted_candidates.append(candidate)

    return {
        "Status": "CANDIDATE_QUALIFICATION_COMPLETE",
        "Candidates": qualification_result.get("Candidates", {}),
        "Qualified Candidates": restricted_candidates,
        "Selection Applied": True,
        "Qualified Candidate Count": len(
            restricted_candidates
        ),
        "Original Qualified Candidate Count": len(
            qualified_candidates
        ),
        "Selected Candidate Count": len(selected_candidates),
        "Accepted Selected Candidate Count": len(
            restricted_candidates
        ),
        "Rejected Selected Candidate Count": len(
            rejected_selections
        ),
        "Rejected Selected Candidates": rejected_selections,
        "Selection Source": (
            "V21.2.22-B.1 Candidate Selection"
        ),
        "Original Qualification Source": (
            "V21.2.20 Candidate Qualification"
        ),
        "Live Order": LIVE_ORDER,
        "Paper Trade": PAPER_TRADE,
    }


def print_selected_qualification_summary(
    result: Dict[str, Any],
) -> None:
    """Print a compact handoff summary."""

    print("\n=== B.1 → V21.2.16 HANDOFF ===")
    print(f"Status: {result.get('Status')}")
    print(
        "Selected Candidates: "
        f"{result.get('Selected Candidate Count', 0)}"
    )
    print(
        "Accepted: "
        f"{result.get('Accepted Selected Candidate Count', 0)}"
    )
    print(
        "Rejected: "
        f"{result.get('Rejected Selected Candidate Count', 0)}"
    )

    for candidate in result.get("Qualified Candidates", []):
        print(
            f"  {candidate.get('Trading Symbol')} "
            f"{candidate.get('Qualification')}"
        )

    print(
        "Live Order: "
        f"{result.get('Live Order')}"
    )
    print(
        "Paper Trade: "
        f"{result.get('Paper Trade')}"
    )
