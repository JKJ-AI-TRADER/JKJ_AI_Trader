"""
JKJ AI Trader — V21.2.24.2
Movement / Peak / Giveback Analyzer

Purpose:
    Analyze V21.2.24.1 one-hour observation history.

Research only:
    - No BUY
    - No SELL
    - No live orders
    - No paper trades
    - No position sizing
    - No stop-loss / target generation

Measures:
    - Discovery movement
    - Checkpoint movement
    - Peak movement
    - Time to peak
    - Maximum giveback
    - Final movement
    - Persistence / reversal characteristics

This module does NOT decide whether a candidate should be traded.
"""

from __future__ import annotations

import math

from typing import Any, Dict, List


LIVE_ORDER = False
PAPER_TRADE = False

CLASS_SUSTAINED = "SUSTAINED"
CLASS_EXTENDED = "EXTENDED"
CLASS_SPIKE_REVERSE = "SPIKE_THEN_REVERSE"
CLASS_WEAKENED = "WEAKENED"
CLASS_FAILED = "FAILED"
CLASS_INSUFFICIENT = "INSUFFICIENT_OBSERVATION"


def _safe_float(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        converted = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return converted if math.isfinite(converted) else None


def _classify_outcome(
    peak_movement: float,
    final_movement: float,
    maximum_giveback: float,
    observation_count: int,
) -> str:
    """
    Descriptive research classification only.

    Giveback is converted to a percentage of the peak movement
    so that classification remains scale-independent.

    These labels are NOT trading signals.
    """

    if observation_count < 2:
        return CLASS_INSUFFICIENT

    if peak_movement <= 0:
        return CLASS_FAILED

    giveback_from_peak_pct = (
        maximum_giveback / peak_movement
    ) * 100.0

    final_retention_pct = (
        final_movement / peak_movement
    ) * 100.0

    # A large move followed by loss of at least 50% of that
    # peak movement is classified as spike/reversal.
    if (
        peak_movement >= 5.0
        and giveback_from_peak_pct >= 50.0
        and final_retention_pct < 50.0
    ):
        return CLASS_SPIKE_REVERSE

    # Candidate retained most of its peak movement.
    if (
        final_retention_pct >= 75.0
        and giveback_from_peak_pct < 25.0
    ):
        return CLASS_SUSTAINED

    # Very large move that remained materially positive.
    if (
        peak_movement >= 10.0
        and final_movement > 0
        and final_retention_pct >= 50.0
    ):
        return CLASS_EXTENDED

    # Positive final result, but meaningful deterioration occurred.
    if final_movement > 0 and giveback_from_peak_pct >= 25.0:
        return CLASS_WEAKENED

    if final_movement <= 0:
        return CLASS_FAILED

    return CLASS_WEAKENED


def _analyze_candidate(
    symbol: str,
    observations: List[Dict[str, Any]],
    discovery_candidate: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    valid = []

    for observation in observations:
        movement = _safe_float(observation.get("Movement %"))
        if movement is None:
            movement = _safe_float(
                observation.get("Total Movement %")
            )

        if movement is None:
            continue

        elapsed = _safe_float(
            observation.get("Elapsed Minutes")
        )

        price = _safe_float(observation.get("Latest Price"))
        if price is None:
            price = _safe_float(observation.get("Current Price"))

        valid.append(
            {
                "Movement": movement,
                "Elapsed": elapsed,
                "Timestamp": observation.get("Timestamp"),
                "Price": price,
                "NIFTY Movement": _safe_float(
                    observation.get("NIFTY Movement %")
                ),
            }
        )

    if not valid:
        return {
            "Trading Symbol": symbol,
            "Status": CLASS_INSUFFICIENT,
            "Observation Count": 0,
            "Live Order": False,
            "Paper Trade": False,
        }

    peak_item = max(valid, key=lambda item: item["Movement"])
    peak_movement = peak_item["Movement"]

    final_item = valid[-1]
    final_movement = final_item["Movement"]

    # Maximum giveback is measured from the running peak.
    # Keep two distinct measures:
    #   1. percentage-point giveback
    #   2. percentage of the peak movement given back
    maximum_giveback = 0.0
    maximum_giveback_from_peak_pct = 0.0
    peak_seen = valid[0]["Movement"]

    for item in valid:
        peak_seen = max(peak_seen, item["Movement"])
        giveback = peak_seen - item["Movement"]
        maximum_giveback = max(maximum_giveback, giveback)

        if peak_seen > 0:
            giveback_from_peak_pct = (
                giveback / peak_seen
            ) * 100.0
            maximum_giveback_from_peak_pct = max(
                maximum_giveback_from_peak_pct,
                giveback_from_peak_pct,
            )

    final_retention_pct = None
    if peak_movement > 0:
        final_retention_pct = (
            final_movement / peak_movement
        ) * 100.0

    discovery_movement = None
    discovery_acceleration = None

    if discovery_candidate:
        discovery_movement = _safe_float(
            discovery_candidate.get("Movement")
        )
        discovery_acceleration = _safe_float(
            discovery_candidate.get("Acceleration")
        )

    outcome = _classify_outcome(
        peak_movement=peak_movement,
        final_movement=final_movement,
        maximum_giveback=maximum_giveback,
        observation_count=len(valid),
    )

    return {
        "Trading Symbol": symbol,
        "Option Type": (
            discovery_candidate.get("Option Type")
            if discovery_candidate
            else None
        ),
        "Expiry": (
            discovery_candidate.get("Expiry")
            if discovery_candidate
            else None
        ),
        "Strike": (
            discovery_candidate.get("Strike")
            if discovery_candidate
            else None
        ),
        "Discovery Movement %": discovery_movement,
        "Discovery Acceleration": discovery_acceleration,
        "Observation Count": len(valid),
        "Checkpoint Movements": [
            {
                "Elapsed Minutes": item["Elapsed"],
                "Movement %": item["Movement"],
                "Timestamp": item["Timestamp"],
            }
            for item in valid
        ],
        "Peak Movement %": round(peak_movement, 4),
        "Time To Peak Minutes": peak_item["Elapsed"],
        "Peak Timestamp": peak_item["Timestamp"],
        "Peak Price": peak_item["Price"],
        "Maximum Giveback Percentage Points": round(
            maximum_giveback,
            4,
        ),
        "Maximum Giveback From Peak %": round(
            maximum_giveback_from_peak_pct,
            4,
        ),
        "Final Peak Retention %": (
            round(final_retention_pct, 4)
            if final_retention_pct is not None
            else None
        ),
        "Final Movement %": round(final_movement, 4),
        "Final Price": final_item["Price"],
        "Final NIFTY Movement %": final_item["NIFTY Movement"],
        "Outcome Classification": outcome,
        "Research Only": True,
        "Live Order": False,
        "Paper Trade": False,
    }


def analyze_one_hour_observation(
    observation_result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Analyze the output of V21.2.24.1 observe_for_one_hour().
    """

    if not isinstance(observation_result, dict):
        return {
            "Status": "INVALID_OBSERVATION_RESULT",
            "Live Order": False,
            "Paper Trade": False,
        }

    if observation_result.get("Status") != (
        "ONE_HOUR_OBSERVATION_COMPLETE"
    ):
        return {
            "Status": "INVALID_OBSERVATION_STATUS",
            "Received Status": observation_result.get("Status"),
            "Live Order": False,
            "Paper Trade": False,
        }

    history = observation_result.get(
        "Observation History",
        [],
    )

    if not isinstance(history, list) or not history:
        return {
            "Status": "NO_OBSERVATION_HISTORY",
            "Live Order": False,
            "Paper Trade": False,
        }

    by_symbol: Dict[str, List[Dict[str, Any]]] = {}

    for cycle in history:
        if not isinstance(cycle, dict):
            continue

        candidates = cycle.get("Candidates", [])

        if not isinstance(candidates, list):
            continue

        for observation in candidates:
            if not isinstance(observation, dict):
                continue

            symbol = observation.get("Trading Symbol")
            if not symbol:
                continue

            by_symbol.setdefault(symbol, []).append(observation)

    selected_candidates = observation_result.get(
        "Selected Candidates",
        [],
    )

    discovery_map: Dict[str, Dict[str, Any]] = {}

    if isinstance(selected_candidates, list):
        for candidate in selected_candidates:
            if isinstance(candidate, dict):
                symbol = candidate.get("Trading Symbol")
                if symbol:
                    discovery_map[symbol] = candidate

    # Some V21.2.24.1 versions may not carry Selected Candidates
    # into the result. In that case, analysis still works from history.
    analyses = []

    for symbol, observations in by_symbol.items():
        analyses.append(
            _analyze_candidate(
                symbol=symbol,
                observations=observations,
                discovery_candidate=discovery_map.get(symbol),
            )
        )

    analyses.sort(
        key=lambda item: (
            item.get("Peak Movement %") or 0.0
        ),
        reverse=True,
    )

    counts: Dict[str, int] = {}

    for item in analyses:
        outcome = item.get(
            "Outcome Classification",
            CLASS_INSUFFICIENT,
        )
        counts[outcome] = counts.get(outcome, 0) + 1

    return {
        "Status": "MOVEMENT_PEAK_GIVEBACK_ANALYSIS_COMPLETE",
        "Observation Status": observation_result.get("Status"),
        "Duration Minutes": observation_result.get(
            "Duration Minutes"
        ),
        "Interval Seconds": observation_result.get(
            "Interval Seconds"
        ),
        "Candidate Count": len(analyses),
        "Candidates": analyses,
        "Outcome Counts": counts,
        "Research Purpose": (
            "Measure persistence, extension, peak, giveback "
            "and reversal characteristics."
        ),
        "Trading Decision": False,
        "Live Order": False,
        "Paper Trade": False,
        "BUY": False,
        "SELL": False,
    }


if __name__ == "__main__":
    print("=" * 70)
    print("V21.2.24.2 MOVEMENT / PEAK / GIVEBACK ANALYZER")
    print("=" * 70)
    print("Mode: RESEARCH ONLY")
    print("Live Order:", LIVE_ORDER)
    print("Paper Trade:", PAPER_TRADE)
    print("BUY: False")
    print("SELL: False")
