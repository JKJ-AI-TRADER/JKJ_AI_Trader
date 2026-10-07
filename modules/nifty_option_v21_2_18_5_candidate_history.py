"""
JKJ AI Trader
V21.2.18.5.1 - Intraday Candidate History Store

Purpose:
    Preserve the development history of NIFTY option candidates
    across repeated intraday scans.

Safety:
    - Observation only
    - No live orders
    - No paper trades
    - No entry decisions
    - No exit decisions
"""

from datetime import datetime
from typing import Any, Dict, List


LIVE_ORDER = False
PAPER_TRADE = False


def create_candidate_history() -> Dict[str, List[Dict[str, Any]]]:
    """
    Create an empty intraday candidate history.
    """
    return {}


def record_scan(
    history: Dict[str, List[Dict[str, Any]]],
    scan_result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Record one completed scanner result.

    Each candidate is stored under its Trading Symbol.
    Existing scanner fields are preserved.
    """

    if not isinstance(history, dict):
        raise TypeError("history must be a dictionary")

    if not isinstance(scan_result, dict):
        raise TypeError("scan_result must be a dictionary")

    timestamp = datetime.now().isoformat()

    candidates = scan_result.get(
        "Candidates",
        [],
    )

    recorded = 0

    for candidate in candidates:

        if not isinstance(candidate, dict):
            continue

        symbol = candidate.get(
            "Trading Symbol"
        )

        if not symbol:
            continue

        observation = dict(candidate)

        observation["History Timestamp"] = timestamp

        history.setdefault(
            symbol,
            [],
        ).append(
            observation
        )

        recorded += 1

    return {
        "Status": "HISTORY_RECORDED",
        "Timestamp": timestamp,
        "Candidates Received": len(candidates),
        "Candidates Recorded": recorded,
        "Tracked Symbols": len(history),
        "Live Order": LIVE_ORDER,
        "Paper Trade": PAPER_TRADE,
    }


def get_candidate_history(
    history: Dict[str, List[Dict[str, Any]]],
    trading_symbol: str,
) -> List[Dict[str, Any]]:
    """
    Return the recorded history for one option.
    """

    if not isinstance(history, dict):
        return []

    return list(
        history.get(
            trading_symbol,
            [],
        )
    )


def get_latest_candidates(
    history: Dict[str, List[Dict[str, Any]]],
) -> List[Dict[str, Any]]:
    """
    Return the latest recorded observation for
    every tracked candidate.
    """

    latest = []

    for observations in history.values():

        if not observations:
            continue

        latest.append(
            observations[-1]
        )

    return latest


def get_history_summary(
    history: Dict[str, List[Dict[str, Any]]],
) -> Dict[str, Any]:
    """
    Provide a simple summary of the observation store.
    """

    observation_count = sum(
        len(items)
        for items in history.values()
    )

    return {
        "Status": "HISTORY_SUMMARY",
        "Tracked Symbols": len(history),
        "Total Observations": observation_count,
        "Symbols": sorted(history.keys()),
        "Live Order": LIVE_ORDER,
        "Paper Trade": PAPER_TRADE,
    }
