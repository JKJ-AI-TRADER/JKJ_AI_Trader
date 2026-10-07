"""
JKJ AI TRADER
V21.2.20 - Candidate Qualification Bridge

Purpose:
    Translate V21.2.19 candidate lifecycle states into
    qualification states for the next JKJ analytical layer.

Safety:
    - Qualification only
    - NO live orders
    - NO paper trades
    - NO BUY decisions
    - NO SELL decisions
    - NO position sizing
    - NO stop/target calculation

Input:
    V21.2.19 Candidate Lifecycle

Output:
    Candidate qualification records suitable for the
    V21.2.16 Decision + Entry Qualification layer.

This module does NOT modify or replace the V21.2.19
observation or lifecycle logic.
"""

from __future__ import annotations

from typing import Any, Dict


LIVE_ORDER = False
PAPER_TRADE = False


# ---------------------------------------------------------
# Lifecycle → Qualification mapping
# ---------------------------------------------------------

LIFECYCLE_QUALIFICATION = {
    "NEW": (
        "INSUFFICIENT_OBSERVATION",
        "Insufficient observations for candidate qualification.",
    ),

    "WATCHING": (
        "WATCH_ONLY",
        "Movement is being observed but is not yet persistent.",
    ),

    "PERSISTING": (
        "DEVELOPING_CANDIDATE",
        "Positive movement is persisting with positive momentum evidence.",
    ),

    "STRENGTHENING": (
        "STRONG_DEVELOPING_CANDIDATE",
        "Movement is strengthening with positive momentum evidence.",
    ),

    "MOMENTUM_SHIFT_UP": (
        "WATCH_ONLY",
        "Movement is shifting upward but persistence is not yet confirmed.",
    ),

    "PEAK": (
        "CAUTION_PEAK",
        "Candidate is near a possible movement peak.",
    ),

    "RETREAT": (
        "CAUTION_RETREAT",
        "Candidate is giving back movement after a peak.",
    ),

    "WEAKENING": (
        "NOT_QUALIFIED",
        "Movement and momentum evidence are weakening.",
    ),

    "MOMENTUM_SHIFT_DOWN": (
        "NOT_QUALIFIED",
        "Positive movement is shifting toward negative momentum.",
    ),

    "DROPPED": (
        "NOT_QUALIFIED",
        "Candidate has dropped from the active lifecycle.",
    ),
}


def _safe_float(value: Any) -> float | None:
    """Convert a value to float without raising an exception."""

    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def qualify_candidate(
    lifecycle_record: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Qualify one V21.2.19 lifecycle record.

    This function does not make a BUY/SELL decision.
    """

    if not isinstance(lifecycle_record, dict):
        return {
            "Status": "INVALID_INPUT",
            "Qualification": "NOT_QUALIFIED",
            "Reason": "Lifecycle record is not a dictionary.",
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    symbol = lifecycle_record.get("Trading Symbol")
    state = lifecycle_record.get("State", "NEW")

    latest = lifecycle_record.get("Latest", {})
    if not isinstance(latest, dict):
        latest = {}

    qualification, reason = LIFECYCLE_QUALIFICATION.get(
        state,
        (
            "NOT_QUALIFIED",
            f"Unknown lifecycle state: {state}.",
        ),
    )

    return {
        "Status": "CANDIDATE_QUALIFIED",
        "Trading Symbol": symbol,
        "Lifecycle State": state,
        "Qualification": qualification,
        "Reason": reason,

        # Evidence from V21.2.19
        "Recent Movement %": _safe_float(
            latest.get("Recent Movement %")
        ),
        "Latest Velocity %/sec": _safe_float(
            latest.get("Latest Velocity %/sec")
        ),
        "Latest Acceleration %/sec2": _safe_float(
            latest.get("Latest Acceleration %/sec2")
        ),
        "Movement State": latest.get(
            "Movement State"
        ),
        "Latest Price": _safe_float(
            latest.get("Latest Price")
        ),
        "Observation Count": latest.get(
            "Observation Count"
        ),

        # Lifecycle evidence
        "Peak Movement %": _safe_float(
            lifecycle_record.get("Peak Movement %")
        ),
        "Giveback From Peak %": _safe_float(
            lifecycle_record.get("Giveback From Peak %")
        ),
        "Current Recovery %": _safe_float(
            lifecycle_record.get("Current Recovery %")
        ),
        "Maximum Recovery %": _safe_float(
            lifecycle_record.get("Maximum Recovery %")
        ),

        # Safety boundary
        "Live Order": LIVE_ORDER,
        "Paper Trade": PAPER_TRADE,
    }


def qualify_candidates(
    lifecycle_store: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Qualify all contracts contained in a V21.2.19
    Candidate Lifecycle store.

    No ranking is performed.
    No trading decision is performed.
    """

    if not isinstance(lifecycle_store, dict):
        return {
            "Status": "INVALID_INPUT",
            "Candidates": {},
            "Qualified Candidates": [],
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    candidates: Dict[str, Dict[str, Any]] = {}

    for symbol, lifecycle_record in lifecycle_store.items():

        if not isinstance(lifecycle_record, dict):
            continue

        result = qualify_candidate(
            lifecycle_record
        )

        candidates[symbol] = result

    developing = [
        result
        for result in candidates.values()
        if result.get("Qualification") in {
            "DEVELOPING_CANDIDATE",
            "STRONG_DEVELOPING_CANDIDATE",
        }
    ]

    return {
        "Status": "CANDIDATE_QUALIFICATION_COMPLETE",
        "Candidates": candidates,
        "Qualified Candidates": developing,
        "Qualified Candidate Count": len(developing),
        "Observed Candidate Count": len(candidates),
        "Live Order": LIVE_ORDER,
        "Paper Trade": PAPER_TRADE,
    }


def print_qualification_summary(
    result: Dict[str, Any],
) -> None:
    """Print a human-readable qualification summary."""

    print()
    print("=" * 70)
    print("V21.2.20 CANDIDATE QUALIFICATION")
    print("=" * 70)

    if not isinstance(result, dict):
        print("Invalid qualification result.")
        return

    print(
        f"Observed Candidates: "
        f"{result.get('Observed Candidate Count', 0)}"
    )

    print(
        f"Qualified Candidates: "
        f"{result.get('Qualified Candidate Count', 0)}"
    )

    candidates = result.get(
        "Candidates",
        {},
    )

    for symbol, item in candidates.items():

        print()
        print(f"Trading Symbol: {symbol}")
        print(
            f"Lifecycle State: "
            f"{item.get('Lifecycle State')}"
        )
        print(
            f"Qualification: "
            f"{item.get('Qualification')}"
        )
        print(
            f"Recent Movement: "
            f"{item.get('Recent Movement %')}"
        )
        print(
            f"Velocity: "
            f"{item.get('Latest Velocity %/sec')}"
        )
        print(
            f"Acceleration: "
            f"{item.get('Latest Acceleration %/sec2')}"
        )
        print(
            f"Movement State: "
            f"{item.get('Movement State')}"
        )
        print(
            f"Reason: "
            f"{item.get('Reason')}"
        )

    print()
    print(
        f"Live Order: {result.get('Live Order')}"
    )
    print(
        f"Paper Trade: {result.get('Paper Trade')}"
    )


if __name__ == "__main__":

    print(
        "V21.2.20 Candidate Qualification"
    )
    print(
        "Qualification bridge only."
    )
    print(
        "No live orders."
    )
    print(
        "No paper trades."
    )
