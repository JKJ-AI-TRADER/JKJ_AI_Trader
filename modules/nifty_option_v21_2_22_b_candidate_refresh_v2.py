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



def _states_by_observation(
    record: Dict[str, Any],
) -> List[str]:
    """Reconstruct state for each observation from V21.2.19 transitions."""

    observations = record.get("Observations", [])
    transitions = record.get("State History", [])

    if not isinstance(observations, list):
        return []

    if not isinstance(transitions, list):
        transitions = []

    valid = []

    for transition in transitions:
        if not isinstance(transition, dict):
            continue

        try:
            observation_number = int(
                transition.get("Observation Count")
            )
        except (TypeError, ValueError):
            continue

        valid.append(
            (
                observation_number,
                transition.get("To", "NEW"),
            )
        )

    valid.sort(key=lambda item: item[0])

    states = []
    current_state = "NEW"
    transition_index = 0

    for observation_number in range(
        1,
        len(observations) + 1,
    ):
        while (
            transition_index < len(valid)
            and valid[transition_index][0] <= observation_number
        ):
            current_state = valid[transition_index][1]
            transition_index += 1

        states.append(current_state)

    return states

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


# ---------------------------------------------------------------------------
# V21.2.22-B v2 classification
# ---------------------------------------------------------------------------

DEVELOPING_STATES = {
    "PERSISTING",
    "STRENGTHENING",
}

RECENT_DEVELOPING_WINDOW = 2


def _number(value: Any) -> float:
    try:
        return float(value or 0.0)
    except (TypeError, ValueError):
        return 0.0


def _positive_developing_evidence(
    snapshot: Dict[str, Any],
) -> bool:
    movement = _number(
        snapshot.get("Recent Movement %")
    )
    velocity = _number(
        snapshot.get("Latest Velocity %/sec")
    )
    acceleration = _number(
        snapshot.get("Latest Acceleration %/sec2")
    )

    return (
        movement > 0
        and velocity > 0
        and acceleration > 0
    )


def _classify_candidate(
    record: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Classify one lifecycle record.

    CURRENT_DEVELOPING:
        Current lifecycle state is PERSISTING/STRENGTHENING
        and current evidence remains positive.

    RECENT_DEVELOPING:
        A recent observation was PERSISTING/STRENGTHENING
        with positive movement, velocity and acceleration,
        but the current observation is no longer developing.

    RECOVERY:
        Current recovery is positive with positive velocity
        and acceleration.

    No trading decision is made here.
    """

    history = record.get("Observations", [])

    if not isinstance(history, list) or not history:
        return {
            "Category": "REJECTED",
            "Evidence Observation": None,
        }

    states = _states_by_observation(record)

    if len(states) != len(history):
        return {
            "Category": "REJECTED",
            "Evidence Observation": None,
        }

    current_state = record.get("State", "NEW")
    latest = history[-1]

    # ---------------------------------------------------------
    # CURRENT DEVELOPING
    # ---------------------------------------------------------

    if (
        current_state in DEVELOPING_STATES
        and _positive_developing_evidence(latest)
    ):
        return {
            "Category": "CURRENT_DEVELOPING",
            "Evidence Observation": len(history),
        }

    # ---------------------------------------------------------
    # RECENT DEVELOPING
    # ---------------------------------------------------------

    first_recent = max(
        0,
        len(history) - 1 - RECENT_DEVELOPING_WINDOW,
    )

    for index in range(
        len(history) - 2,
        first_recent - 1,
        -1,
    ):
        if (
            states[index] in DEVELOPING_STATES
            and _positive_developing_evidence(history[index])
        ):
            return {
                "Category": "RECENT_DEVELOPING",
                "Evidence Observation": index + 1,
                "Observations Since Evidence":
                    len(history) - index - 1,
            }

    # ---------------------------------------------------------
    # RECOVERY
    # ---------------------------------------------------------

    current_recovery = _number(
        latest.get("Current Recovery %")
    )

    velocity = _number(
        latest.get("Latest Velocity %/sec")
    )

    acceleration = _number(
        latest.get("Latest Acceleration %/sec2")
    )

    if (
        current_recovery > 0
        and velocity > 0
        and acceleration > 0
    ):
        return {
            "Category": "RECOVERY",
            "Evidence Observation": len(history),
        }

    return {
        "Category": "REJECTED",
        "Evidence Observation": None,
    }


# ---------------------------------------------------------------------------
# V21.2.22-B v2 ranking
# ---------------------------------------------------------------------------

CATEGORY_PRIORITY = {
    "CURRENT_DEVELOPING": 0,
    "RECENT_DEVELOPING": 1,
    "RECOVERY": 2,
}


def _ranking_score(
    movement: float,
    velocity: float,
    acceleration: float,
) -> float:
    """
    Transparent observational strength score.

    This is NOT a BUY score and is NOT a probability.
    """

    return movement + velocity + acceleration


def rank_candidate_records(
    candidate_records: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Rank already-classified observational candidates.

    Priority:
        CURRENT_DEVELOPING
        RECENT_DEVELOPING
        RECOVERY

    Within the same category, stronger observational evidence
    ranks higher.

    No trading decision is made.
    """

    ranked = []

    for candidate in candidate_records:

        if not isinstance(candidate, dict):
            continue

        category = candidate.get("Category")

        if category not in CATEGORY_PRIORITY:
            continue

        movement = _number(
            candidate.get("Recent Movement %")
        )

        velocity = _number(
            candidate.get("Velocity %/sec")
        )

        acceleration = _number(
            candidate.get("Acceleration %/sec2")
        )

        score = _ranking_score(
            movement,
            velocity,
            acceleration,
        )

        item = dict(candidate)

        item["Ranking Score"] = score

        ranked.append(item)

    ranked.sort(
        key=lambda item: (
            CATEGORY_PRIORITY[item["Category"]],
            -item["Ranking Score"],
            item.get("Trading Symbol", ""),
        )
    )

    for rank, item in enumerate(ranked, start=1):
        item["Rank"] = rank

    return ranked


# ---------------------------------------------------------------------------
# V21.2.22-B v2 complete refresh
# ---------------------------------------------------------------------------

def refresh_developing_candidates_v2(
    lifecycle_store: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Complete V21.2.22-B v2 candidate refresh.

    Flow:
        V21.2.19 lifecycle
            ->
        historical state reconstruction
            ->
        candidate classification
            ->
        transparent ranking
            ->
        strongest observational candidates

    Observation only.
    No BUY/SELL decisions.
    No live orders.
    No paper trades.
    """

    if not isinstance(lifecycle_store, dict):
        return {
            "Status": "INVALID_LIFECYCLE_STORE",
            "Candidates": [],
            "Candidate Count": 0,
            "Category Counts": {},
            "Live Order": False,
            "Paper Trade": False,
        }

    classified_candidates = []

    for symbol, record in lifecycle_store.items():

        if not isinstance(record, dict):
            continue

        classification = _classify_candidate(record)

        category = classification.get("Category")

        if category == "REJECTED":
            continue

        history = record.get("Observations", [])

        if not isinstance(history, list) or not history:
            continue

        evidence_observation = classification.get(
            "Evidence Observation"
        )

        if not evidence_observation:
            continue

        try:
            evidence_index = int(evidence_observation) - 1
        except (TypeError, ValueError):
            continue

        if (
            evidence_index < 0
            or evidence_index >= len(history)
        ):
            continue

        evidence = history[evidence_index]

        if not isinstance(evidence, dict):
            continue

        movement = _number(
            evidence.get("Recent Movement %")
        )

        velocity = _number(
            evidence.get("Latest Velocity %/sec")
        )

        acceleration = _number(
            evidence.get("Latest Acceleration %/sec2")
        )

        ranking_score = _ranking_score(
            movement,
            velocity,
            acceleration,
        )

        latest = history[-1]

        classified_candidates.append({
            "Trading Symbol": symbol,
            "Category": category,
            "Lifecycle State": record.get(
                "State",
                "NEW",
            ),
            "Evidence Observation": evidence_observation,
            "Observations Since Evidence": classification.get(
                "Observations Since Evidence",
                0,
            ),
            "Recent Movement %": movement,
            "Velocity %/sec": velocity,
            "Acceleration %/sec2": acceleration,
            "Ranking Score": ranking_score,
            "Current Movement %": _number(
                latest.get("Recent Movement %")
            ),
            "Current Velocity %/sec": _number(
                latest.get("Latest Velocity %/sec")
            ),
            "Current Acceleration %/sec2": _number(
                latest.get("Latest Acceleration %/sec2")
            ),
            "Current Recovery %": _number(
                latest.get("Current Recovery %")
            ),
            "Live Order": False,
            "Paper Trade": False,
        })

    ranked_candidates = rank_candidate_records(
        classified_candidates
    )

    category_counts = {
        "CURRENT_DEVELOPING": 0,
        "RECENT_DEVELOPING": 0,
        "RECOVERY": 0,
    }

    for candidate in ranked_candidates:
        category = candidate.get("Category")

        if category in category_counts:
            category_counts[category] += 1

    return {
        "Status": "DEVELOPING_CANDIDATE_REFRESH_V2_COMPLETE",
        "Candidates": ranked_candidates,
        "Candidate Count": len(ranked_candidates),
        "Category Counts": category_counts,
        "Developing States": sorted(
            DEVELOPING_STATES
        ),
        "Recent Developing Window": (
            RECENT_DEVELOPING_WINDOW
        ),
        "Live Order": LIVE_ORDER,
        "Paper Trade": PAPER_TRADE,
    }


def print_developing_candidates_v2(
    result: Dict[str, Any],
) -> None:

    print()
    print("=" * 120)
    print("V21.2.22-B v2 DEVELOPING CANDIDATE REFRESH")
    print("=" * 120)

    print("Status:", result.get("Status"))
    print(
        "Candidate Count:",
        result.get("Candidate Count", 0),
    )

    print(
        "Category Counts:",
        result.get("Category Counts", {}),
    )

    print(
        "Safety:",
        "LIVE_ORDER=False | PAPER_TRADE=False",
    )

    candidates = result.get("Candidates", [])

    if not candidates:
        print()
        print("No observational candidates detected.")
        return

    print()
    print(
        "RANK | SYMBOL"
        " | CATEGORY"
        " | CURRENT STATE"
        " | EVIDENCE OBS"
        " | AGE"
        " | MOVEMENT %"
        " | VELOCITY"
        " | ACCELERATION"
        " | SCORE"
    )

    print("-" * 120)

    for candidate in candidates:

        print(
            f"{candidate['Rank']:>4} | "
            f"{candidate['Trading Symbol']:<22} | "
            f"{candidate['Category']:<20} | "
            f"{candidate['Lifecycle State']:<18} | "
            f"{candidate['Evidence Observation']:>11} | "
            f"{candidate['Observations Since Evidence']:>3} | "
            f"{candidate['Recent Movement %']:>9.2f} | "
            f"{candidate['Velocity %/sec']:>9.4f} | "
            f"{candidate['Acceleration %/sec2']:>11.4f} | "
            f"{candidate['Ranking Score']:>8.4f}"
        )
