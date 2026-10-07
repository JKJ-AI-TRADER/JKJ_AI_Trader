"""
JKJ AI Trader
V21.2.22-B.1 - Candidate Selection

Purpose:
    Select a small number of the strongest observational candidates
    from the validated V21.2.22-B v2 candidate output.

Safety:
    - Observation only
    - No BUY/SELL decisions
    - No live orders
    - No paper trades
    - No position sizing

Candidate != Trade.
"""

from __future__ import annotations

from typing import Any, Dict, List


LIVE_ORDER = False
PAPER_TRADE = False

MAX_SELECTED_CANDIDATES = 3
MAX_RECENT_DEVELOPING_AGE = 2

CATEGORY_PRIORITY = {
    "CURRENT_DEVELOPING": 0,
    "RECENT_DEVELOPING": 1,
    "RECOVERY": 2,
}


def _number(value: Any) -> float:
    try:
        return float(value or 0.0)
    except (TypeError, ValueError):
        return 0.0


def select_candidates(
    b2_result: Dict[str, Any],
    max_candidates: int = MAX_SELECTED_CANDIDATES,
) -> Dict[str, Any]:
    """
    Select a small observational shortlist from B v2.

    This function does not make a trading decision.
    """

    if not isinstance(b2_result, dict):
        return {
            "Status": "INVALID_B2_RESULT",
            "Selected Candidates": [],
            "Selected Count": 0,
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    if b2_result.get("Status") != (
        "DEVELOPING_CANDIDATE_REFRESH_V2_COMPLETE"
    ):
        return {
            "Status": "INVALID_B2_STATUS",
            "Selected Candidates": [],
            "Selected Count": 0,
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    candidates = b2_result.get("Candidates", [])

    if not isinstance(candidates, list):
        candidates = []

    try:
        limit = int(max_candidates)
    except (TypeError, ValueError):
        limit = MAX_SELECTED_CANDIDATES

    if limit <= 0:
        limit = MAX_SELECTED_CANDIDATES

    eligible: List[Dict[str, Any]] = []

    for candidate in candidates:

        if not isinstance(candidate, dict):
            continue

        category = candidate.get("Category")

        if category not in CATEGORY_PRIORITY:
            continue

        age = _number(
            candidate.get(
                "Observations Since Evidence",
                0,
            )
        )

        if (
            category == "RECENT_DEVELOPING"
            and age > MAX_RECENT_DEVELOPING_AGE
        ):
            continue

        item = dict(candidate)

        item["Selection Priority"] = CATEGORY_PRIORITY[
            category
        ]

        item["Selection Age"] = age

        eligible.append(item)

    eligible.sort(
        key=lambda item: (
            item["Selection Priority"],
            item["Selection Age"],
            -_number(
                item.get("Ranking Score", 0.0)
            ),
            item.get("Trading Symbol", ""),
        )
    )

    selected = eligible[:limit]

    for rank, candidate in enumerate(
        selected,
        start=1,
    ):
        candidate["Selection Rank"] = rank

    return {
        "Status": "CANDIDATE_SELECTION_COMPLETE",
        "Selected Candidates": selected,
        "Selected Count": len(selected),
        "Eligible Candidate Count": len(eligible),
        "Maximum Selected Candidates": limit,
        "Maximum Recent Developing Age":
            MAX_RECENT_DEVELOPING_AGE,
        "Live Order": LIVE_ORDER,
        "Paper Trade": PAPER_TRADE,
    }


def print_selected_candidates(
    result: Dict[str, Any],
) -> None:

    print()
    print("=" * 110)
    print("V21.2.22-B.1 CANDIDATE SELECTION")
    print("=" * 110)

    print("Status:", result.get("Status"))
    print(
        "Selected Candidates:",
        result.get("Selected Count", 0),
    )
    print(
        "Eligible Candidates:",
        result.get("Eligible Candidate Count", 0),
    )

    print(
        "Safety:",
        "LIVE_ORDER=False | PAPER_TRADE=False",
    )

    candidates = result.get(
        "Selected Candidates",
        [],
    )

    if not candidates:
        print()
        print("No candidates selected.")
        return

    print()
    print(
        "RANK | SYMBOL"
        " | CATEGORY"
        " | CURRENT STATE"
        " | AGE"
        " | MOVEMENT %"
        " | VELOCITY"
        " | ACCELERATION"
        " | SCORE"
    )

    print("-" * 110)

    for candidate in candidates:

        print(
            f"{candidate['Selection Rank']:>4} | "
            f"{candidate['Trading Symbol']:<22} | "
            f"{candidate['Category']:<20} | "
            f"{candidate['Lifecycle State']:<18} | "
            f"{candidate['Selection Age']:>3.0f} | "
            f"{candidate['Recent Movement %']:>9.2f} | "
            f"{candidate['Velocity %/sec']:>9.4f} | "
            f"{candidate['Acceleration %/sec2']:>11.4f} | "
            f"{candidate['Ranking Score']:>8.4f}"
        )
