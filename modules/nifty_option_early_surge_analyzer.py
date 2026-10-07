"""
JKJ AI Trader
V21.2.18.1 — Early Surge Analyzer

Purpose:
Analyze an existing sequence of real-market option observations.

This module:
- calculates movement between observations
- calculates velocity
- calculates acceleration
- detects persistence
- detects deceleration
- detects weakening
- detects reversal
- tracks peak price and drawdown

This module does NOT:
- place orders
- create paper trades
- make BUY/SELL decisions
- modify V1–V12
- modify main.py
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

MIN_PERSISTENCE_OBSERVATIONS = 3
ACCELERATION_TOLERANCE = 0.001
MAX_CONTINUITY_GAP_SECONDS = 60


# ------------------------------------------------------------
# Basic calculations
# ------------------------------------------------------------

def _percentage_change(
    previous_price: float,
    current_price: float,
) -> float:
    """Return percentage price change."""

    if previous_price is None:
        return 0.0

    if current_price is None:
        return 0.0

    if previous_price <= 0:
        return 0.0

    return (
        (current_price - previous_price)
        / previous_price
    ) * 100.0


def _elapsed_seconds(
    previous_timestamp: Any,
    current_timestamp: Any,
) -> Optional[float]:
    """
    Return elapsed seconds between two timestamps.

    Supports datetime-like objects and ISO timestamp strings.
    """

    if previous_timestamp is None:
        return None

    if current_timestamp is None:
        return None

    try:
        delta = (
            current_timestamp - previous_timestamp
        )

        seconds = delta.total_seconds()

        if seconds > 0:
            return float(seconds)

    except Exception:
        pass

    try:
        from datetime import datetime

        previous_dt = datetime.fromisoformat(
            str(previous_timestamp)
        )

        current_dt = datetime.fromisoformat(
            str(current_timestamp)
        )

        seconds = (
            current_dt - previous_dt
        ).total_seconds()

        if seconds > 0:
            return float(seconds)

    except Exception:
        pass

    return None


def _calculate_velocity(
    movement_pct: float,
    elapsed_seconds: Optional[float],
) -> Optional[float]:
    """Return percentage movement per second."""

    if elapsed_seconds is None:
        return None

    if elapsed_seconds <= 0:
        return None

    return movement_pct / elapsed_seconds


def _calculate_acceleration(
    current_velocity: Optional[float],
    previous_velocity: Optional[float],
) -> Optional[float]:
    """Return change in velocity."""

    if current_velocity is None:
        return None

    if previous_velocity is None:
        return None

    return current_velocity - previous_velocity


# ------------------------------------------------------------
# State classification
# ------------------------------------------------------------

def classify_movement_state(
    velocity: Optional[float],
    acceleration: Optional[float],
    previous_velocity: Optional[float] = None,
) -> str:
    """
    Classify the current movement state.

    This is descriptive only.
    It is NOT an entry or exit signal.
    """

    if velocity is None:
        return "INSUFFICIENT_DATA"

    if acceleration is None:
        if velocity > 0:
            return "EARLY_MOVEMENT"

        if velocity < 0:
            return "FALLING"

        return "STABLE"

    # Upward movement with increasing velocity.
    if (
    velocity > 0
    and acceleration > ACCELERATION_TOLERANCE
):
        return "ACCELERATING"

    if (
        velocity > 0
        and acceleration < -ACCELERATION_TOLERANCE
    ):
        return "DECELERATING"

    if (
        velocity > 0
        and abs(acceleration)
        <= ACCELERATION_TOLERANCE
    ):
        return "STEADY_UP"

    # Downward movement.
    if velocity < 0:
        if previous_velocity is not None:
            if previous_velocity >= 0:
                return "REVERSING"

        return "FALLING"

    return "STABLE"


# ------------------------------------------------------------
# Observation validation
# ------------------------------------------------------------

def _extract_price(
    observation: Dict[str, Any],
) -> Optional[float]:

    value = observation.get("Current Price")

    if value is None:
        value = observation.get("Latest Price")

    try:
        price = float(value)

        if price > 0:
            return price

    except (TypeError, ValueError):
        pass

    return None


def _extract_timestamp(
    observation: Dict[str, Any],
) -> Any:

    timestamp = observation.get(
        "Observation Timestamp"
    )

    if timestamp is None:
        timestamp = observation.get(
            "Timestamp"
        )

    return timestamp


# ------------------------------------------------------------
# Main analyzer
# ------------------------------------------------------------

def analyze_observation_history(
    observations: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Analyze the chronological observation history
    of one option contract.

    The input observations must be ordered chronologically.

    Observation gaps greater than MAX_CONTINUITY_GAP_SECONDS
    start a new observation segment.

    Persistence is evaluated within the current continuous
    observation segment only.

    This module is descriptive only.
    It does NOT make BUY/SELL decisions.
    """

    if not isinstance(observations, list):
        return {
            "Status": "REJECTED",
            "Reason": "Observations must be a list.",
        }

    if not observations:
        return {
            "Status": "REJECTED",
            "Reason": "Observation history is empty.",
        }

    if any(
        not isinstance(item, dict)
        for item in observations
    ):
        return {
            "Status": "REJECTED",
            "Reason": "Every observation must be a dictionary.",
        }

    analysis = []

    previous_price = None
    previous_timestamp = None
    previous_velocity = None

    segment_id = 1
    segment_observation_count = 0
    segment_accelerating_count = 0
    segment_decelerating_count = 0

    peak_price = None
    peak_observation_number = None

    positive_movement_count = 0
    accelerating_count = 0
    decelerating_count = 0

    for index, observation in enumerate(
        observations,
        start=1,
    ):

        price = _extract_price(observation)
        timestamp = _extract_timestamp(observation)

        if price is None:
            return {
                "Status": "REJECTED",
                "Reason": (
                    "Observation "
                    f"{index} has no valid price."
                ),
            }

        if peak_price is None or price > peak_price:
            peak_price = price
            peak_observation_number = index

        # ----------------------------------------------------
        # First observation
        # ----------------------------------------------------

        if previous_price is None:
            movement_pct = None
            elapsed_seconds = None
            velocity = None
            acceleration = None
            state = "INITIAL"

        else:
            movement_pct = _percentage_change(
                previous_price,
                price,
            )

            elapsed_seconds = _elapsed_seconds(
                previous_timestamp,
                timestamp,
            )

            # ------------------------------------------------
            # Continuity protection
            # ------------------------------------------------
            # A large observation gap means JKJ did not
            # continuously observe the market.
            #
            # Price movement is retained, but velocity and
            # acceleration are reset for the new segment.
            # ------------------------------------------------

            if (
                elapsed_seconds is None
                or elapsed_seconds > MAX_CONTINUITY_GAP_SECONDS
            ):
                segment_id += 1
                segment_observation_count = 0
                segment_accelerating_count = 0
                segment_decelerating_count = 0

                velocity = None
                acceleration = None
                previous_velocity = None

                state = "NEW_SEGMENT"

            else:
                velocity = _calculate_velocity(
                    movement_pct,
                    elapsed_seconds,
                )

                acceleration = _calculate_acceleration(
                    velocity,
                    previous_velocity,
                )

                state = classify_movement_state(
                    velocity,
                    acceleration,
                    previous_velocity,
                )

            # -----------------------------------------------
            # Movement statistics
            # -----------------------------------------------

            if movement_pct > 0:
                positive_movement_count += 1

            # Count observations belonging to this segment.
            segment_observation_count += 1

            # -----------------------------------------------
            # Acceleration statistics
            # -----------------------------------------------

            if (
                acceleration is not None
                and acceleration > 0
                and velocity is not None
                and velocity > 0
            ):
                accelerating_count += 1
                segment_accelerating_count += 1

            if (
                acceleration is not None
                and acceleration < 0
                and velocity is not None
                and velocity > 0
            ):
                decelerating_count += 1
                segment_decelerating_count += 1

        # ----------------------------------------------------
        # Drawdown from overall observed peak
        # ----------------------------------------------------

        if peak_price and peak_price > 0:
            drawdown_from_peak_pct = _percentage_change(
                peak_price,
                price,
            )
        else:
            drawdown_from_peak_pct = 0.0

        # ----------------------------------------------------
        # Store observation
        # ----------------------------------------------------

        analysis.append(
            {
                "Observation Number": index,
                "Segment ID": segment_id,
                "Timestamp": timestamp,
                "Price": round(price, 4),
                "Movement %": (
                    round(movement_pct, 4)
                    if movement_pct is not None
                    else None
                ),
                "Elapsed Seconds": (
                    round(elapsed_seconds, 4)
                    if elapsed_seconds is not None
                    else None
                ),
                "Velocity %/sec": (
                    round(velocity, 6)
                    if velocity is not None
                    else None
                ),
                "Acceleration %/sec²": (
                    round(acceleration, 6)
                    if acceleration is not None
                    else None
                ),
                "Peak Price": round(
                    peak_price,
                    4,
                ),
                "Drawdown From Peak %": round(
                    drawdown_from_peak_pct,
                    4,
                ),
                "State": state,
            }
        )

        # ----------------------------------------------------
        # Prepare for next observation
        # ----------------------------------------------------

        previous_price = price
        previous_timestamp = timestamp
        previous_velocity = velocity

    observation_count = len(analysis)

    # --------------------------------------------------------
    # Current segment persistence
    # --------------------------------------------------------
    # Persistence must come from the current continuous
    # observation segment, not from unrelated observations
    # earlier in the history.
    # --------------------------------------------------------

    persistent_acceleration = (
        segment_observation_count >= MIN_PERSISTENCE_OBSERVATIONS
        and segment_accelerating_count >= 2
    )

    # --------------------------------------------------------
    # Current state
    # --------------------------------------------------------

    latest = analysis[-1]

    latest_state = latest.get(
        "State",
        "UNKNOWN",
    )

    latest_drawdown = latest.get(
        "Drawdown From Peak %",
        0.0,
    )

    if latest_state == "REVERSING":
        overall_state = "REVERSING"

    elif latest_state == "FALLING":
        if latest_drawdown < 0:
            overall_state = "WEAKENING"
        else:
            overall_state = "FALLING"

    elif latest_state == "DECELERATING":
        overall_state = "DECELERATING"

    elif persistent_acceleration:
        overall_state = "PERSISTENT_ACCELERATION"

    else:
        overall_state = latest_state

    return {
        "Status": "ANALYSIS_COMPLETE",
        "Observation Count": observation_count,
        "Minimum Persistence Observations": (
            MIN_PERSISTENCE_OBSERVATIONS
        ),
        "Current Segment ID": segment_id,
        "Current Segment Observation Count": (
            segment_observation_count
        ),
        "Current Segment Accelerating Count": (
            segment_accelerating_count
        ),
        "Current Segment Decelerating Count": (
            segment_decelerating_count
        ),
        "Observations": analysis,
        "Peak Price": (
            round(peak_price, 4)
            if peak_price is not None
            else None
        ),
        "Peak Observation Number": (
            peak_observation_number
        ),
        "Positive Movement Count": (
            positive_movement_count
        ),
        "Accelerating Observation Count": (
            accelerating_count
        ),
        "Decelerating Observation Count": (
            decelerating_count
        ),
        "Persistent Acceleration": (
            persistent_acceleration
        ),
        "Latest State": latest_state,
        "Overall State": overall_state,
        "Live Order": False,
        "Paper Trade": False,
    }