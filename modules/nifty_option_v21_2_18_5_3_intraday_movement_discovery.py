"""
JKJ AI Trader
V21.2.18.5.3 - Intraday Movement Discovery

Purpose:
    Detect developing option movement from repeated intraday observations
    even when a genuine 9:15 baseline is unavailable.

Safety:
    Observation / discovery only.
    No live orders.
    No paper trades.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional


MIN_OBSERVATIONS = 3
MIN_PRICE = 0.0

# Initial discovery thresholds.
# These are deliberately modest because this module detects development,
# not final trade qualification.
MIN_INTRADAY_MOVE_PCT = 0.50
MIN_VELOCITY_PCT_PER_SEC = 0.001
MIN_ACCELERATION_PCT_PER_SEC2 = 0.00001


def _safe_float(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        result = float(value)
        return result
    except (TypeError, ValueError):
        return None


def _timestamp_seconds(value: Any) -> Optional[float]:
    if isinstance(value, datetime):
        return value.timestamp()

    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value).timestamp()
        except ValueError:
            return None

    return None


def _price(observation: Dict[str, Any]) -> Optional[float]:
    """
    Accept the real V21 observation field first.
    """
    value = observation.get("Current Price")

    if value is None:
        value = observation.get("Price")

    value = _safe_float(value)

    if value is None or value <= MIN_PRICE:
        return None

    return value


def _timestamp(observation: Dict[str, Any]) -> Optional[float]:
    return _timestamp_seconds(observation.get("Timestamp"))


def analyze_intraday_movement(
    observations: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Analyze repeated observations for developing intraday movement.

    This is NOT an entry decision.
    """

    if not isinstance(observations, list):
        return {
            "Status": "REJECTED",
            "Reason": "Observations must be a list",
            "Live Order": False,
            "Paper Trade": False,
        }

    if len(observations) < MIN_OBSERVATIONS:
        return {
            "Status": "INSUFFICIENT_OBSERVATIONS",
            "Observation Count": len(observations),
            "Minimum Observations": MIN_OBSERVATIONS,
            "Live Order": False,
            "Paper Trade": False,
        }

    first_price = _price(observations[0])

    if first_price is None:
        return {
            "Status": "REJECTED",
            "Reason": "First observation has no valid price",
            "Live Order": False,
            "Paper Trade": False,
        }

    calculated: List[Dict[str, Any]] = []

    previous_price: Optional[float] = None
    previous_velocity: Optional[float] = None

    for number, observation in enumerate(observations, start=1):

        current_price = _price(observation)

        if current_price is None:
            return {
                "Status": "REJECTED",
                "Reason": f"Observation {number} has no valid price",
                "Live Order": False,
                "Paper Trade": False,
            }

        current_time = _timestamp(observation)

        movement_pct = (
            ((current_price - first_price) / first_price) * 100.0
        )

        velocity = None
        acceleration = None
        elapsed_seconds = None

        if previous_price is not None and current_time is not None:
            previous_time = _timestamp(observations[number - 2])

            if previous_time is not None:
                elapsed_seconds = current_time - previous_time

                if elapsed_seconds > 0:
                    interval_move_pct = (
                        (current_price - previous_price)
                        / previous_price
                    ) * 100.0

                    velocity = interval_move_pct / elapsed_seconds

                    if (
                        previous_velocity is not None
                        and elapsed_seconds > 0
                    ):
                        acceleration = (
                            velocity - previous_velocity
                        ) / elapsed_seconds

        calculated.append(
            {
                "Observation Number": number,
                "Timestamp": observation.get("Timestamp"),
                "Price": current_price,
                "Movement %": round(movement_pct, 4),
                "Elapsed Seconds": elapsed_seconds,
                "Velocity %/sec": (
                    round(velocity, 6)
                    if velocity is not None
                    else None
                ),
                "Acceleration %/sec²": (
                    round(acceleration, 8)
                    if acceleration is not None
                    else None
                ),
            }
        )

        previous_price = current_price

        if velocity is not None:
            previous_velocity = velocity

    latest = calculated[-1]

    positive_movement = latest["Movement %"] >= MIN_INTRADAY_MOVE_PCT

    positive_velocity = (
        latest["Velocity %/sec"] is not None
        and latest["Velocity %/sec"] > MIN_VELOCITY_PCT_PER_SEC
    )

    positive_acceleration = (
        latest["Acceleration %/sec²"] is not None
        and latest["Acceleration %/sec²"]
        > MIN_ACCELERATION_PCT_PER_SEC2
    )

    if positive_acceleration and positive_velocity:
        state = "ACCELERATING"
    elif positive_velocity and positive_movement:
        state = "DEVELOPING"
    elif positive_movement:
        state = "MOVING"
    else:
        state = "STABLE"

    return {
        "Status": "INTRADAY_MOVEMENT_ANALYZED",
        "Observation Count": len(calculated),
        "Initial Price": first_price,
        "Latest Price": latest["Price"],
        "Intraday Movement %": latest["Movement %"],
        "Latest Velocity %/sec": latest["Velocity %/sec"],
        "Latest Acceleration %/sec²": latest["Acceleration %/sec²"],
        "Positive Movement": positive_movement,
        "Positive Velocity": positive_velocity,
        "Positive Acceleration": positive_acceleration,
        "State": state,
        "Observations": calculated,
        "Live Order": False,
        "Paper Trade": False,
    }


def discover_intraday_movement(
    history: Dict[str, List[Dict[str, Any]]],
) -> Dict[str, Any]:
    """
    Analyze observation histories for multiple option contracts.
    """

    if not isinstance(history, dict):
        return {
            "Status": "REJECTED",
            "Reason": "History must be a dictionary",
            "Live Order": False,
            "Paper Trade": False,
        }

    results: List[Dict[str, Any]] = []

    for symbol, observations in history.items():

        analysis = analyze_intraday_movement(observations)

        item = {
            "Trading Symbol": symbol,
            **analysis,
        }

        if analysis.get("State") in {
            "MOVING",
            "DEVELOPING",
            "ACCELERATING",
        }:
            results.append(item)

    return {
        "Status": "INTRADAY_DISCOVERY_COMPLETE",
        "Tracked Symbols": len(history),
        "Developing Candidates": results,
        "Candidate Count": len(results),
        "Live Order": False,
        "Paper Trade": False,
    }
