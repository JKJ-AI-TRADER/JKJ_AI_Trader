"""
JKJ AI TRADER
V21.2.22-C - Evidence Reconciliation Layer

Purpose:
    Reconcile V21.2.20 candidate qualification,
    B.2 detailed market evidence, and V12.6
    classical momentum results.

Safety:
    - Reconciliation only
    - NO live orders
    - NO paper trades
    - NO BUY decisions
    - NO SELL decisions
    - NO position sizing
    - NO stop/target calculation

This module does NOT modify:
    - V21.2.19 lifecycle logic
    - V21.2.20 qualification logic
    - V12.6 momentum logic
"""

from __future__ import annotations

from typing import Any, Dict, List


LIVE_ORDER = False
PAPER_TRADE = False

MIN_OBSERVATIONS = 4

DEVELOPING_QUALIFICATIONS = {
    "DEVELOPING_CANDIDATE",
    "STRONG_DEVELOPING_CANDIDATE",
}

POSITIVE_LIFECYCLE_STATES = {
    "PERSISTING",
    "STRENGTHENING",
}

CAUTION_LIFECYCLE_STATES = {
    "WATCHING",
    "MOMENTUM_SHIFT_UP",
    "PEAK",
    "RETREAT",
    "WEAKENING",
    "MOMENTUM_SHIFT_DOWN",
    "NEW",
    "DROPPED",
}


def _safe_float(value: Any) -> float | None:
    """Convert a value to float without raising an exception."""

    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _get_observation_list(
    detailed_evidence: Dict[str, Any],
    symbol: str,
) -> List[Dict[str, Any]]:
    """
    Retrieve the detailed observation history for one symbol.
    """

    observations = detailed_evidence.get(
        "Observations",
        {},
    )

    if not isinstance(observations, dict):
        return []

    history = observations.get(symbol, [])

    if not isinstance(history, list):
        return []

    return [
        item
        for item in history
        if isinstance(item, dict)
    ]


def _price_movement(
    observations: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Calculate transparent price movement from B.2 observations.
    """

    if len(observations) < MIN_OBSERVATIONS:
        return {
            "Valid": False,
            "Reason": (
                "Insufficient detailed observations."
            ),
        }

    prices = [
        _safe_float(item.get("Current Price"))
        for item in observations
    ]

    if any(price is None or price <= 0 for price in prices):
        return {
            "Valid": False,
            "Reason": (
                "One or more observations have "
                "invalid option prices."
            ),
        }

    first_price = prices[0]
    latest_price = prices[-1]

    overall_change = latest_price - first_price
    overall_change_pct = (
        (overall_change / first_price) * 100
    )

    latest_change = (
        latest_price - prices[-2]
    )

    latest_change_pct = (
        (latest_change / prices[-2]) * 100
    )

    return {
        "Valid": True,
        "First Price": first_price,
        "Latest Price": latest_price,
        "Overall Movement %": overall_change_pct,
        "Latest Movement %": latest_change_pct,
        "Prices": prices,
    }


def _extract_v12_6(
    momentum_result: Dict[str, Any],
    symbol: str,
) -> Dict[str, Any]:
    """
    Extract the actual V12.6 result for one contract.

    V21.2.15 exposes contract results through the
    top-level ``Results`` list.

    This function does not reinterpret V12.6.
    """

    if not isinstance(momentum_result, dict):
        return {
            "Valid": False,
            "Reason": "V12.6 result is not a dictionary.",
        }

    results = momentum_result.get(
        "Results",
        [],
    )

    if not isinstance(results, list):
        return {
            "Valid": False,
            "Reason": "V12.6 Results is not a list.",
        }

    for result in results:

        if not isinstance(result, dict):
            continue

        if result.get("Trading Symbol") != symbol:
            continue

        momentum_sequence = result.get(
            "Momentum Sequence",
            {},
        )

        if not isinstance(
            momentum_sequence,
            dict,
        ):
            momentum_sequence = {}

        momentum_confirmation = result.get(
            "Momentum Confirmation",
            {},
        )

        if not isinstance(
            momentum_confirmation,
            dict,
        ):
            momentum_confirmation = {}

        return {
            "Valid": True,
            "Persistence": momentum_sequence.get(
                "Persistence Status"
            ),
            "Direction": momentum_sequence.get(
                "Direction"
            ),
            "Momentum Confirmation": (
                momentum_confirmation.get(
                    "Momentum Confirmation"
                )
            ),
            "Status": result.get("Status"),
        }

    return {
        "Valid": False,
        "Reason": (
            f"No V12.6 result found for {symbol}."
        ),
    }


def _reconcile(
    qualification: str,
    lifecycle_state: str,
    overall_movement_pct: float,
    latest_movement_pct: float,
    v12_persistence: Any,
    v12_confirmation: Any,
) -> tuple[str, str]:
    """
    Apply the V21.2.22-C reconciliation rules.

    This function produces an analytical classification only.
    """

    if qualification not in DEVELOPING_QUALIFICATIONS:
        return (
            "INSUFFICIENT_EVIDENCE",
            (
                "Candidate is not currently qualified as "
                "a developing candidate by V21.2.20."
            ),
        )

    if lifecycle_state not in POSITIVE_LIFECYCLE_STATES:
        return (
            "EVIDENCE_CONFLICT",
            (
                "Qualification indicates development, but "
                "the current lifecycle state is not "
                "PERSISTING or STRENGTHENING."
            ),
        )

    if overall_movement_pct <= 0:
        return (
            "EVIDENCE_CONFLICT",
            (
                "Detailed evidence does not show positive "
                "overall option-price development."
            ),
        )

    if latest_movement_pct < 0:
        return (
            "EVIDENCE_CONFLICT",
            (
                "Overall movement is positive, but the "
                "latest detailed observation is declining."
            ),
        )

    if (
        v12_persistence == "PERSISTENT"
        and v12_confirmation in {
            "CONFIRMED",
            "PARTIALLY_CONFIRMED",
        }
    ):
        return (
            "PERSISTENCE_SUPPORTED",
            (
                "Developing lifecycle evidence is supported "
                "by V12.6 classical persistence."
            ),
        )

    if v12_persistence == "NOT_PERSISTENT":
        return (
            "DEVELOPING_BUT_NOT_PERSISTENT",
            (
                "Detailed evidence and lifecycle indicate "
                "positive development, but V12.6 classical "
                "directional persistence is not established."
            ),
        )

    if v12_persistence is None:
        return (
            "INSUFFICIENT_EVIDENCE",
            (
                "V12.6 persistence result is unavailable."
            ),
        )

    return (
        "DEVELOPING_SUPPORTED",
        (
            "Lifecycle and detailed evidence support "
            "positive development."
        ),
    )


def reconcile_candidate(
    qualification_record: Dict[str, Any],
    detailed_evidence: Dict[str, Any],
    momentum_result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Reconcile one selected candidate.
    """

    if not isinstance(qualification_record, dict):
        return {
            "Status": "INVALID_INPUT",
            "Reconciliation": "INSUFFICIENT_EVIDENCE",
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    symbol = qualification_record.get(
        "Trading Symbol"
    )

    if not symbol:
        return {
            "Status": "INVALID_INPUT",
            "Reconciliation": "INSUFFICIENT_EVIDENCE",
            "Reason": "Trading Symbol is missing.",
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    observations = _get_observation_list(
        detailed_evidence,
        symbol,
    )

    if len(observations) < MIN_OBSERVATIONS:
        return {
            "Status": "INSUFFICIENT_EVIDENCE",
            "Trading Symbol": symbol,
            "Reconciliation": "INSUFFICIENT_EVIDENCE",
            "Reason": (
                f"At least {MIN_OBSERVATIONS} detailed "
                f"observations are required."
            ),
            "Observation Count": len(observations),
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    movement = _price_movement(observations)

    if not movement.get("Valid"):
        return {
            "Status": "INSUFFICIENT_EVIDENCE",
            "Trading Symbol": symbol,
            "Reconciliation": "INSUFFICIENT_EVIDENCE",
            "Reason": movement.get("Reason"),
            "Observation Count": len(observations),
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    v12_6 = _extract_v12_6(
        momentum_result,
        symbol,
    )

    if not v12_6.get("Valid"):
        return {
            "Status": "INSUFFICIENT_EVIDENCE",
            "Trading Symbol": symbol,
            "Reconciliation": "INSUFFICIENT_EVIDENCE",
            "Reason": v12_6.get("Reason"),
            "Observation Count": len(observations),
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    qualification = qualification_record.get(
        "Qualification"
    )

    lifecycle_state = qualification_record.get(
        "Lifecycle State"
    )

    latest_movement = qualification_record.get(
        "Recent Movement %"
    )

    velocity = qualification_record.get(
        "Latest Velocity %/sec"
    )

    acceleration = qualification_record.get(
        "Latest Acceleration %/sec2"
    )

    reconciliation, reason = _reconcile(
        qualification=qualification,
        lifecycle_state=lifecycle_state,
        overall_movement_pct=movement[
            "Overall Movement %"
        ],
        latest_movement_pct=movement[
            "Latest Movement %"
        ],
        v12_persistence=v12_6.get(
            "Persistence"
        ),
        v12_confirmation=v12_6.get(
            "Momentum Confirmation"
        ),
    )

    return {
        "Status": "EVIDENCE_RECONCILIATION_COMPLETE",
        "Trading Symbol": symbol,

        # Existing analytical layers
        "Lifecycle State": lifecycle_state,
        "Qualification": qualification,
        "V12.6 Persistence": v12_6.get(
            "Persistence"
        ),
        "V12.6 Direction": v12_6.get(
            "Direction"
        ),
        "V12.6 Confirmation": v12_6.get(
            "Momentum Confirmation"
        ),
        "V12.6 Status": v12_6.get(
            "Status"
        ),

        # B.2 detailed evidence
        "Observation Count": len(observations),
        "First Price": movement.get(
            "First Price"
        ),
        "Latest Price": movement.get(
            "Latest Price"
        ),
        "Overall Movement %": movement.get(
            "Overall Movement %"
        ),
        "Latest Movement %": movement.get(
            "Latest Movement %"
        ),

        # V21.2.20 lifecycle evidence
        "Recent Movement %": _safe_float(
            latest_movement
        ),
        "Latest Velocity %/sec": _safe_float(
            velocity
        ),
        "Latest Acceleration %/sec2": _safe_float(
            acceleration
        ),
        "Peak Movement %": qualification_record.get(
            "Peak Movement %"
        ),
        "Giveback From Peak %": qualification_record.get(
            "Giveback From Peak %"
        ),
        "Current Recovery %": qualification_record.get(
            "Current Recovery %"
        ),
        "Maximum Recovery %": qualification_record.get(
            "Maximum Recovery %"
        ),

        # Reconciliation
        "Reconciliation": reconciliation,
        "Reason": reason,

        # Safety boundary
        "Live Order": LIVE_ORDER,
        "Paper Trade": PAPER_TRADE,
    }


def reconcile_candidates(
    qualification_result: Dict[str, Any],
    detailed_evidence: Dict[str, Any],
    momentum_result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Reconcile all candidates contained in the
    V21.2.20 qualification result.

    No ranking is performed.
    No BUY/SELL decision is performed.
    """

    if not isinstance(qualification_result, dict):
        return {
            "Status": "INVALID_INPUT",
            "Candidates": [],
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    if qualification_result.get(
        "Status"
    ) != "CANDIDATE_QUALIFICATION_COMPLETE":
        return {
            "Status": "INVALID_INPUT",
            "Candidates": [],
            "Reason": (
                "Invalid V21.2.20 qualification status."
            ),
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    qualified_candidates = qualification_result.get(
        "Qualified Candidates",
        [],
    )

    if not isinstance(
        qualified_candidates,
        list,
    ):
        qualified_candidates = []

    results = []

    for qualification_record in qualified_candidates:

        result = reconcile_candidate(
            qualification_record,
            detailed_evidence,
            momentum_result,
        )

        results.append(result)

    return {
        "Status": "EVIDENCE_RECONCILIATION_COMPLETE",
        "Candidates": results,
        "Candidate Count": len(results),
        "Reconciliation Counts": _count_reconciliations(
            results
        ),
        "Live Order": LIVE_ORDER,
        "Paper Trade": PAPER_TRADE,
    }


def _count_reconciliations(
    results: List[Dict[str, Any]],
) -> Dict[str, int]:
    """Count reconciliation classifications."""

    counts: Dict[str, int] = {}

    for result in results:
        state = result.get(
            "Reconciliation",
            "UNKNOWN",
        )
        counts[state] = counts.get(
            state,
            0,
        ) + 1

    return counts


def print_reconciliation_summary(
    result: Dict[str, Any],
) -> None:
    """Print a human-readable reconciliation summary."""

    print()
    print("=" * 75)
    print("V21.2.22-C EVIDENCE RECONCILIATION")
    print("=" * 75)

    if not isinstance(result, dict):
        print("Invalid reconciliation result.")
        return

    print(
        f"Candidates: "
        f"{result.get('Candidate Count', 0)}"
    )

    counts = result.get(
        "Reconciliation Counts",
        {},
    )

    if isinstance(counts, dict):
        print(
            f"Reconciliation Counts: {counts}"
        )

    candidates = result.get(
        "Candidates",
        [],
    )

    for item in candidates:

        print()
        print(
            f"Trading Symbol: "
            f"{item.get('Trading Symbol')}"
        )
        print(
            f"Lifecycle State: "
            f"{item.get('Lifecycle State')}"
        )
        print(
            f"Qualification: "
            f"{item.get('Qualification')}"
        )
        print(
            f"V12.6 Persistence: "
            f"{item.get('V12.6 Persistence')}"
        )
        print(
            f"V12.6 Confirmation: "
            f"{item.get('V12.6 Confirmation')}"
        )
        print(
            f"First Price: "
            f"{item.get('First Price')}"
        )
        print(
            f"Latest Price: "
            f"{item.get('Latest Price')}"
        )
        print(
            f"Overall Movement: "
            f"{item.get('Overall Movement %')}"
        )
        print(
            f"Latest Movement: "
            f"{item.get('Latest Movement %')}"
        )
        print(
            f"Reconciliation: "
            f"{item.get('Reconciliation')}"
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
        "V21.2.22-C Evidence Reconciliation"
    )
    print(
        "Analytical reconciliation only."
    )
    print(
        "No live orders."
    )
    print(
        "No paper trades."
    )
