"""
JKJ AI Trader
V21.2.22-B - Developing Candidate Refresh & Ranking

Observation-only candidate ranking layer.

Consumes the existing V21.2.19 Candidate Lifecycle store.

This module:
- Does NOT modify V21.2.19.
- Does NOT make BUY/SELL decisions.
- Does NOT place live orders.
- Does NOT execute paper trades.
"""

from __future__ import annotations

from typing import Any, Dict, List


LIVE_ORDER = False
PAPER_TRADE = False

DEVELOPING_STATES = {
    "PERSISTING",
    "STRENGTHENING",
}


def _number(value: Any) -> float:
    try:
        return float(value or 0.0)
    except (TypeError, ValueError):
        return 0.0


def _candidate_strength_score(
    recent_movement: float,
    velocity: float,
    acceleration: float,
) -> float:
    """Transparent observational ranking score. Not a BUY score."""

    return (
        recent_movement
        + velocity
        + acceleration
    )


def refresh_developing_candidates(
    lifecycle_store: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:

    if not isinstance(lifecycle_store, dict):
        return {
            "Status": "INVALID_LIFECYCLE_STORE",
            "Candidates": [],
            "Candidate Count": 0,
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    candidates: List[Dict[str, Any]] = []

    for symbol, record in lifecycle_store.items():

        if not isinstance(record, dict):
            continue

        state = record.get("State")

        if state not in DEVELOPING_STATES:
            continue

        # V21.2.19 stores current movement metrics in Latest.
        latest = record.get("Latest", {})

        if not isinstance(latest, dict):
            continue

        recent_movement = _number(
            latest.get("Recent Movement %")
        )

        velocity = _number(
            latest.get("Latest Velocity %/sec")
        )

        acceleration = _number(
            latest.get("Latest Acceleration %/sec2")
        )

        if recent_movement <= 0:
            continue

        if velocity <= 0:
            continue

        if acceleration <= 0:
            continue

        score = _candidate_strength_score(
            recent_movement,
            velocity,
            acceleration,
        )

        candidates.append(
            {
                "Trading Symbol": symbol,
                "Lifecycle State": state,
                "Recent Movement %": recent_movement,
                "Velocity %/sec": velocity,
                "Acceleration %/sec2": acceleration,
                "Developing Strength Score": score,
                "Live Order": False,
                "Paper Trade": False,
            }
        )

    candidates.sort(
        key=lambda item: item["Developing Strength Score"],
        reverse=True,
    )

    for rank, candidate in enumerate(candidates, start=1):
        candidate["Rank"] = rank

    return {
        "Status": "DEVELOPING_CANDIDATE_REFRESH_COMPLETE",
        "Candidates": candidates,
        "Candidate Count": len(candidates),
        "Developing States": sorted(DEVELOPING_STATES),
        "Live Order": LIVE_ORDER,
        "Paper Trade": PAPER_TRADE,
    }


def print_developing_candidates(
    result: Dict[str, Any],
) -> None:

    print()
    print("=" * 100)
    print("V21.2.22-B DEVELOPING CANDIDATE REFRESH")
    print("=" * 100)

    print("Status:", result.get("Status"))
    print(
        "Developing Candidates:",
        result.get("Candidate Count", 0),
    )

    print(
        "Safety:",
        f"LIVE_ORDER={LIVE_ORDER} | PAPER_TRADE={PAPER_TRADE}",
    )

    candidates = result.get("Candidates", [])

    if not candidates:
        print()
        print("No developing candidates detected.")
        return

    print()
    print(
        "RANK | TRADING SYMBOL"
        " | STATE"
        " | MOVEMENT %"
        " | VELOCITY"
        " | ACCELERATION"
        " | STRENGTH"
    )
    print("-" * 115)

    for candidate in candidates:

        print(
            f"{candidate['Rank']:>4} | "
            f"{candidate['Trading Symbol']:<22} | "
            f"{candidate['Lifecycle State']:<13} | "
            f"{candidate['Recent Movement %']:>9.2f} | "
            f"{candidate['Velocity %/sec']:>9.4f} | "
            f"{candidate['Acceleration %/sec2']:>11.4f} | "
            f"{candidate['Developing Strength Score']:>9.4f}"
        )


if __name__ == "__main__":

    print(
        "V21.2.22-B requires a V21.2.19 Candidate Lifecycle store."
    )
    print(
        "Use refresh_developing_candidates(lifecycle_store)"
        " from the JKJ runtime."
    )
