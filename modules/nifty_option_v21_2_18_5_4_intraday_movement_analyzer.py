"""
JKJ AI Trader
V21.2.18.5.4 - Intraday Movement Analyzer

Purpose:
    Analyze genuine intraday price movement from the full observation
    history of each NIFTY option contract.

Movement concepts are deliberately separated:

1. Movement Since 9:15 %
       Genuine 09:15 baseline price -> latest price

2. Recent Movement %
       First observed price -> latest observed price

3. Velocity
       Recent percentage price movement per second

4. Acceleration
       Change in velocity per second

5. Persistence
       Whether positive movement/acceleration is sustained

This is an observation/analysis layer only.

Safety:
    - No live orders
    - No paper trades
    - No entry qualification
    - No position sizing
    - No trading decisions
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


LIVE_ORDER = False
PAPER_TRADE = False

MIN_OBSERVATIONS = 3

# These are deliberately modest analysis thresholds.
# They are NOT trade-entry thresholds.
MIN_MOVEMENT_PCT = 0.50
MIN_VELOCITY_PCT_PER_SEC = 0.001
MIN_ACCELERATION_PCT_PER_SEC2 = 0.00001


def _get_price(observation: Dict[str, Any]) -> Optional[float]:
    """
    Get the observed latest price.

    Prefer the scanner's Latest Price field.
    Fall back to Current Price / Price for compatibility.
    """

    value = observation.get("Latest Price")

    if value is None:
        value = observation.get("Current Price")

    if value is None:
        value = observation.get("Price")

    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _get_baseline_price(
    observation: Dict[str, Any],
) -> Optional[float]:
    """
    Get the genuine 09:15 baseline price.

    The scanner stores this as '9:15 Price'.
    """

    value = observation.get("9:15 Price")

    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _get_timestamp(
    observation: Dict[str, Any],
) -> Optional[datetime]:
    """Read the observation timestamp."""

    value = observation.get(
        "Observation Timestamp",
        observation.get("Timestamp"),
    )

    if isinstance(value, datetime):
        return value

    if not value:
        return None

    try:
        return datetime.fromisoformat(str(value))
    except (ValueError, TypeError):
        return None


def _movement_pct(
    first_price: Optional[float],
    latest_price: Optional[float],
) -> Optional[float]:
    """Calculate percentage movement."""

    if first_price in (None, 0) or latest_price is None:
        return None

    return (
        (latest_price - first_price)
        / first_price
    ) * 100.0


def _rate_pct_per_sec(
    price1: Optional[float],
    price2: Optional[float],
    seconds: float,
) -> Optional[float]:
    """Calculate percentage movement per second."""

    if (
        price1 in (None, 0)
        or price2 is None
        or seconds <= 0
    ):
        return None

    movement = (
        (price2 - price1)
        / price1
    ) * 100.0

    return movement / seconds


def _calculate_velocities(
    valid: List[Tuple[datetime, float, Dict[str, Any]]],
) -> List[float]:
    """Calculate sequential percentage velocities."""

    velocities: List[float] = []

    for index in range(1, len(valid)):

        previous_timestamp, previous_price, _ = valid[index - 1]
        current_timestamp, current_price, _ = valid[index]

        seconds = (
            current_timestamp - previous_timestamp
        ).total_seconds()

        velocity = _rate_pct_per_sec(
            previous_price,
            current_price,
            seconds,
        )

        if velocity is not None:
            velocities.append(velocity)

    return velocities


def _calculate_accelerations(
    velocities: List[float],
    valid: List[Tuple[datetime, float, Dict[str, Any]]],
) -> List[float]:
    """
    Calculate acceleration as change in velocity per second.

    Each acceleration compares two consecutive velocity
    observations.
    """

    accelerations: List[float] = []

    if len(velocities) < 2:
        return accelerations

    for index in range(1, len(velocities)):

        # The time interval corresponding to the later
        # velocity observation.
        if index + 1 >= len(valid):
            break

        previous_timestamp = valid[index].__getitem__(0)
        current_timestamp = valid[index + 1].__getitem__(0)

        seconds = (
            current_timestamp - previous_timestamp
        ).total_seconds()

        if seconds <= 0:
            continue

        acceleration = (
            velocities[index] - velocities[index - 1]
        ) / seconds

        accelerations.append(acceleration)

    return accelerations


def analyze_intraday_movement(
    observations: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Analyze one contract's observation history.

    Returns both:
        - genuine 09:15 movement
        - recent movement
        - velocity
        - acceleration
        - persistence
    """

    valid: List[
        Tuple[datetime, float, Dict[str, Any]]
    ] = []

    for observation in observations or []:

        if not isinstance(observation, dict):
            continue

        price = _get_price(observation)
        timestamp = _get_timestamp(observation)

        if price is None or timestamp is None:
            continue

        valid.append(
            (
                timestamp,
                price,
                observation,
            )
        )

    valid.sort(key=lambda item: item[0])

    result: Dict[str, Any] = {
        "Status": "MOVEMENT_ANALYSIS",
        "Observation Count": len(valid),

        "9:15 Price": None,
        "Latest Price": None,
        "Movement Since 9:15 %": None,

        "First Observed Price": None,
        "Recent Movement %": None,

        "Latest Velocity %/sec": None,
        "Latest Acceleration %/sec2": None,

        "Positive Velocity Observations": 0,
        "Positive Acceleration Observations": 0,

        "Persistent Acceleration": False,
        "Movement State": "INSUFFICIENT_DATA",

        "Live Order": LIVE_ORDER,
        "Paper Trade": PAPER_TRADE,
    }

    if len(valid) < MIN_OBSERVATIONS:
        return result

    first_timestamp, first_price, first_observation = valid[0]
    latest_timestamp, latest_price, latest_observation = valid[-1]

    # ---------------------------------------------------------
    # Genuine 09:15 baseline
    # ---------------------------------------------------------

    baseline_price = None

    # Prefer the latest observation that contains a valid
    # genuine 09:15 baseline.
    for _, _, observation in reversed(valid):
        candidate_baseline = _get_baseline_price(observation)

        if candidate_baseline not in (None, 0):
            baseline_price = candidate_baseline
            break

    movement_since_915 = _movement_pct(
        baseline_price,
        latest_price,
    )

    # ---------------------------------------------------------
    # Recent movement
    # ---------------------------------------------------------

    recent_movement = _movement_pct(
        first_price,
        latest_price,
    )

    # ---------------------------------------------------------
    # Velocity / acceleration
    # ---------------------------------------------------------

    velocities = _calculate_velocities(valid)

    accelerations = _calculate_accelerations(
        velocities,
        valid,
    )

    latest_velocity = (
        velocities[-1]
        if velocities
        else None
    )

    latest_acceleration = (
        accelerations[-1]
        if accelerations
        else None
    )

    positive_velocity_count = sum(
        1
        for value in velocities
        if value > 0
    )

    positive_acceleration_count = sum(
        1
        for value in accelerations
        if value > 0
    )

    # ---------------------------------------------------------
    # Persistence
    # ---------------------------------------------------------

    persistent_acceleration = (
        len(accelerations) >= 2
        and accelerations[-1] > 0
        and accelerations[-2] > 0
    )

    # ---------------------------------------------------------
    # Movement state
    # ---------------------------------------------------------

    movement_ok = (
        movement_since_915 is not None
        and movement_since_915 >= MIN_MOVEMENT_PCT
    )

    velocity_positive = (
        latest_velocity is not None
        and latest_velocity >= MIN_VELOCITY_PCT_PER_SEC
    )

    acceleration_positive = (
        latest_acceleration is not None
        and latest_acceleration >= MIN_ACCELERATION_PCT_PER_SEC2
    )

    if (
        movement_ok
        and velocity_positive
        and acceleration_positive
        and persistent_acceleration
    ):
        movement_state = "ACCELERATING"

    elif movement_ok and velocity_positive:
        movement_state = "DEVELOPING"

    elif movement_ok:
        movement_state = "MOVING"

    else:
        movement_state = "STABLE"

    result.update(
        {
            "9:15 Price": baseline_price,
            "Latest Price": latest_price,
            "Movement Since 9:15 %": (
                round(movement_since_915, 4)
                if movement_since_915 is not None
                else None
            ),
            "First Observed Price": first_price,
            "Recent Movement %": (
                round(recent_movement, 4)
                if recent_movement is not None
                else None
            ),
            "Latest Velocity %/sec": (
                round(latest_velocity, 8)
                if latest_velocity is not None
                else None
            ),
            "Latest Acceleration %/sec2": (
                round(latest_acceleration, 10)
                if latest_acceleration is not None
                else None
            ),
            "Positive Velocity Observations": (
                positive_velocity_count
            ),
            "Positive Acceleration Observations": (
                positive_acceleration_count
            ),
            "Persistent Acceleration": (
                persistent_acceleration
            ),
            "Movement State": movement_state,
        }
    )

    return result


def analyze_intraday_store(
    store: Dict[str, List[Dict[str, Any]]],
) -> Dict[str, Dict[str, Any]]:
    """Analyze every contract in the observation store."""

    if not isinstance(store, dict):
        return {}

    analysis: Dict[str, Dict[str, Any]] = {}

    for trading_symbol, observations in store.items():

        result = analyze_intraday_movement(
            observations
        )

        result["Trading Symbol"] = trading_symbol

        if observations:

            latest = observations[-1]

            result["Option Type"] = latest.get(
                "Option Type"
            )
            result["Strike"] = latest.get(
                "Strike"
            )
            result["Expiry"] = latest.get(
                "Expiry"
            )

        analysis[trading_symbol] = result

    return analysis


if __name__ == "__main__":

    # Simple deterministic unit test.
    test_observations = [
        {
            "Trading Symbol": "TESTCE",
            "9:15 Price": 100.0,
            "Latest Price": 100.0,
            "Observation Timestamp": (
                "2026-09-29T09:15:00"
            ),
        },
        {
            "Trading Symbol": "TESTCE",
            "9:15 Price": 100.0,
            "Latest Price": 101.0,
            "Observation Timestamp": (
                "2026-09-29T09:15:10"
            ),
        },
        {
            "Trading Symbol": "TESTCE",
            "9:15 Price": 100.0,
            "Latest Price": 103.0,
            "Observation Timestamp": (
                "2026-09-29T09:15:20"
            ),
        },
        {
            "Trading Symbol": "TESTCE",
            "9:15 Price": 100.0,
            "Latest Price": 106.0,
            "Observation Timestamp": (
                "2026-09-29T09:15:30"
            ),
        },
    ]

    test_result = analyze_intraday_movement(
        test_observations
    )

    print("Status:", test_result["Status"])
    print(
        "Observation Count:",
        test_result["Observation Count"],
    )
    print(
        "9:15 Price:",
        test_result["9:15 Price"],
    )
    print(
        "Latest Price:",
        test_result["Latest Price"],
    )
    print(
        "Movement Since 9:15 %:",
        test_result["Movement Since 9:15 %"],
    )
    print(
        "Recent Movement %:",
        test_result["Recent Movement %"],
    )
    print(
        "Latest Velocity %/sec:",
        test_result["Latest Velocity %/sec"],
    )
    print(
        "Latest Acceleration %/sec2:",
        test_result["Latest Acceleration %/sec2"],
    )
    print(
        "Positive Velocity Observations:",
        test_result["Positive Velocity Observations"],
    )
    print(
        "Positive Acceleration Observations:",
        test_result["Positive Acceleration Observations"],
    )
    print(
        "Persistent Acceleration:",
        test_result["Persistent Acceleration"],
    )
    print(
        "Movement State:",
        test_result["Movement State"],
    )
    print("Live Order:", test_result["Live Order"])
    print("Paper Trade:", test_result["Paper Trade"])
