"""
JKJ AI Trader
V21.2.18.5.3 - Intraday Observation Store

Stores repeated observations for the full scanner universe.

This is separate from Candidate History:
- Full universe is observed here.
- Only developing candidates may later be promoted.
- No live orders.
- No paper trades.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List


LIVE_ORDER = False
PAPER_TRADE = False


def create_intraday_observation_store() -> Dict[str, List[Dict[str, Any]]]:
    """Create an empty full-universe observation store."""
    return {}


def record_scan_observations(
    store: Dict[str, List[Dict[str, Any]]],
    scan_result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Record every contract from scan_result['Results'].

    Each scan receives one common observation timestamp.
    Existing scanner fields are preserved.
    """

    if not isinstance(store, dict):
        raise TypeError("store must be a dictionary")

    if not isinstance(scan_result, dict):
        raise TypeError("scan_result must be a dictionary")

    results = scan_result.get("Results", [])

    if not isinstance(results, list):
        results = []

    timestamp = datetime.now().isoformat()

    recorded = 0

    for result in results:

        if not isinstance(result, dict):
            continue

        symbol = result.get("Trading Symbol")

        if not symbol:
            continue

        observation = dict(result)

        observation["Observation Timestamp"] = timestamp

        store.setdefault(symbol, []).append(observation)

        recorded += 1

    return {
        "Status": "INTRADAY_OBSERVATIONS_RECORDED",
        "Timestamp": timestamp,
        "Results Received": len(results),
        "Observations Recorded": recorded,
        "Tracked Symbols": len(store),
        "Live Order": LIVE_ORDER,
        "Paper Trade": PAPER_TRADE,
    }


def get_intraday_observations(
    store: Dict[str, List[Dict[str, Any]]],
    trading_symbol: str,
) -> List[Dict[str, Any]]:
    """Return all observations for one contract."""

    if not isinstance(store, dict):
        return []

    return list(store.get(trading_symbol, []))


def get_latest_intraday_observations(
    store: Dict[str, List[Dict[str, Any]]],
) -> List[Dict[str, Any]]:
    """Return the latest observation for every tracked contract."""

    latest = []

    for observations in store.values():

        if observations:
            latest.append(observations[-1])

    return latest


def get_intraday_store_summary(
    store: Dict[str, List[Dict[str, Any]]],
) -> Dict[str, Any]:
    """Return a simple store summary."""

    total_observations = sum(
        len(observations)
        for observations in store.values()
    )

    return {
        "Status": "INTRADAY_STORE_SUMMARY",
        "Tracked Symbols": len(store),
        "Total Observations": total_observations,
        "Symbols": sorted(store.keys()),
        "Live Order": LIVE_ORDER,
        "Paper Trade": PAPER_TRADE,
    }
