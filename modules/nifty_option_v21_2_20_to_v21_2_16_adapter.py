"""
JKJ AI Trader
V21.2.20 → V21.2.16 Observation Adapter

Purpose:
    Convert the existing V21.2.19 persistent observation store,
    restricted to V21.2.20 qualified candidates, into the
    V21.2.15-compatible UNIFIED_OBSERVATION_COMPLETE structure.

Important:
    - Does NOT capture market data.
    - Does NOT create observations.
    - Does NOT rank candidates.
    - Does NOT place orders.
    - Does NOT paper trade.
    - Preserves the original observation history.

Architecture:

    V21.2.19 Observation Store
              +
    V21.2.20 Qualified Candidates
              ↓
       This Adapter
              ↓
    UNIFIED_OBSERVATION_COMPLETE
              ↓
         V21.2.16
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict


LIVE_ORDER = False
PAPER_TRADE = False


def _identity_from_observations(
    observations,
):
    """Build the V21.2.15 identity from actual observation data."""

    if not isinstance(observations, list) or not observations:
        return None

    first = observations[0]

    if not isinstance(first, dict):
        return None

    required_fields = (
        "Trading Symbol",
        "Underlying",
        "Expiry",
        "Strike",
        "Option Type",
    )

    if any(
        first.get(field) is None
        for field in required_fields
    ):
        return None

    return (
        first.get("Trading Symbol"),
        first.get("Underlying"),
        first.get("Expiry"),
        first.get("Strike"),
        first.get("Option Type"),
    )


def build_unified_observation_from_qualified_candidates(
    observation_store: Dict[str, list],
    qualification_result: Dict[str, Any],
):
    """
    Build a V21.2.15-compatible unified observation result.

    Only V21.2.20 qualified candidates are included.

    The original observation dictionaries are preserved.
    """

    if not isinstance(observation_store, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Observation Store must be a dictionary.",
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

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

    qualified_candidates = qualification_result.get(
        "Qualified Candidates"
    )

    if not isinstance(qualified_candidates, list):
        return {
            "Status": "REJECTED",
            "Reason": (
                "Qualified Candidates must be a list."
            ),
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    observations_by_contract = {}
    latest_observations = {}

    rejected_candidates = []

    for candidate in qualified_candidates:

        if not isinstance(candidate, dict):
            continue

        symbol = candidate.get("Trading Symbol")

        if not symbol:
            rejected_candidates.append({
                "Trading Symbol": symbol,
                "Reason": "Qualified candidate has no Trading Symbol.",
            })
            continue

        observations = observation_store.get(symbol)

        if not isinstance(observations, list) or not observations:
            rejected_candidates.append({
                "Trading Symbol": symbol,
                "Reason": (
                    "No observation history found in "
                    "V21.2.19 Observation Store."
                ),
            })
            continue

        identity = _identity_from_observations(
            observations
        )

        if identity is None:
            rejected_candidates.append({
                "Trading Symbol": symbol,
                "Reason": (
                    "Unable to construct V21.2.15 "
                    "contract identity from observations."
                ),
            })
            continue

        observations_by_contract[identity] = list(
            observations
        )

        latest_observations[identity] = observations[-1]

    if not observations_by_contract:
        return {
            "Status": "REJECTED",
            "Reason": (
                "No qualified candidates contained "
                "usable observation history."
            ),
            "Qualified Candidate Count": len(
                qualified_candidates
            ),
            "Rejected Candidate Count": len(
                rejected_candidates
            ),
            "Rejected Candidates": rejected_candidates,
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    observation_counts = {
        len(history)
        for history in observations_by_contract.values()
    }

    if len(observation_counts) != 1:
        return {
            "Status": "REJECTED",
            "Reason": (
                "Qualified candidates do not have "
                "a consistent observation count."
            ),
            "Observation Counts": sorted(
                observation_counts
            ),
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    observation_count = next(
        iter(observation_counts)
    )

    if observation_count < 4:
        return {
            "Status": "REJECTED",
            "Reason": (
                "At least 4 observations are required "
                "for V21.2.16/V12.6 processing."
            ),
            "Observation Count": observation_count,
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    return {
        "Status": "UNIFIED_OBSERVATION_COMPLETE",

        "Observation Count": observation_count,
        "Movement Intervals": observation_count - 1,

        "Interval Seconds": None,

        "Contract Count": len(
            observations_by_contract
        ),

        "Observation Cycles": [],

        "Observations By Contract": (
            observations_by_contract
        ),

        "Latest Observations": (
            latest_observations
        ),

        "Session Timestamp": (
            datetime.now().astimezone().isoformat(
                timespec="seconds"
            )
        ),

        "Qualified Candidate Count": len(
            qualified_candidates
        ),

        "Rejected Candidate Count": len(
            rejected_candidates
        ),

        "Rejected Candidates": rejected_candidates,

        "Source": (
            "V21.2.19 Persistent Observation Store "
            "+ V21.2.20 Candidate Qualification"
        ),

        "New Market Observations": False,

        "Live Order": LIVE_ORDER,
        "Paper Trade": PAPER_TRADE,
    }
