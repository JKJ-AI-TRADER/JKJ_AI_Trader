"""
JKJ AI TRADER
V21.2.19-C - Candidate Lifecycle + Peak Tracking

Purpose:
    Track the observational lifecycle of NIFTY option contracts
    across repeated intraday observations.

States:
    NEW
    WATCHING
    PERSISTING
    STRENGTHENING
    PEAK
    RETREAT
    MOMENTUM_SHIFT_UP
    MOMENTUM_SHIFT_DOWN
    WEAKENING
    DROPPED

Safety:
    - Observation only
    - No entry decisions
    - No live orders
    - No paper trades
    - No position sizing
"""

from __future__ import annotations

from typing import Any, Dict, List


LIVE_ORDER = False
PAPER_TRADE = False

MIN_OBSERVATIONS_FOR_LIFECYCLE = 3
MOVEMENT_THRESHOLD = 0.50
MIN_GIVEBACK_FROM_PEAK = 1.00


def _latest(history: List[Dict[str, Any]]) -> Dict[str, Any]:
    return history[-1] if history else {}


def _get_recent_movement(item: Dict[str, Any]) -> float:
    value = item.get("Recent Movement %")
    return float(value) if value is not None else 0.0


def _get_velocity(item: Dict[str, Any]) -> float:
    value = item.get("Latest Velocity %/sec")
    return float(value) if value is not None else 0.0


def _get_acceleration(item: Dict[str, Any]) -> float:
    value = item.get("Latest Acceleration %/sec2")
    return float(value) if value is not None else 0.0


def _classify_lifecycle(
    previous_state: str,
    history: List[Dict[str, Any]],
) -> str:

    if not history:
        return "NEW"

    latest = _latest(history)

    observation_count = latest.get("Observation Count") or len(history)

    recent_movement = _get_recent_movement(latest)
    velocity = _get_velocity(latest)
    acceleration = _get_acceleration(latest)

    peak_movement = float(
        latest.get("Peak Movement %", recent_movement) or 0.0
    )

    giveback = float(
        latest.get("Giveback From Peak %", 0.0) or 0.0
    )

    if observation_count < MIN_OBSERVATIONS_FOR_LIFECYCLE:
        return "NEW"

    # A meaningful peak has already been established and
    # the candidate is now giving back part of that move.
    if (
        peak_movement >= MOVEMENT_THRESHOLD
        and giveback >= MIN_GIVEBACK_FROM_PEAK
        and velocity < 0
    ):
        return "RETREAT"

    # Candidate is reaching a possible peak, but has not
    # yet given enough movement back to call it a retreat.
    if (
        previous_state in {
            "PERSISTING",
            "STRENGTHENING",
        }
        and recent_movement >= peak_movement
        and peak_movement >= MOVEMENT_THRESHOLD
        and velocity <= 0
    ):
        return "PEAK"

    if abs(recent_movement) < MOVEMENT_THRESHOLD:
        return "WATCHING"

    # Negative movement is becoming positive momentum.
    if (
        recent_movement < -MOVEMENT_THRESHOLD
        and velocity > 0
        and acceleration > 0
    ):
        return "MOMENTUM_SHIFT_UP"

    # Positive movement is turning into negative momentum.
    if (
        recent_movement > MOVEMENT_THRESHOLD
        and velocity < 0
        and acceleration < 0
    ):
        return "MOMENTUM_SHIFT_DOWN"

    if velocity > 0 and acceleration > 0:
        if previous_state in {
            "PERSISTING",
            "STRENGTHENING",
        }:
            return "STRENGTHENING"

        return "PERSISTING"

    if velocity < 0 and acceleration < 0:
        if previous_state in {
            "PERSISTING",
            "STRENGTHENING",
            "PEAK",
            "RETREAT",
            "MOMENTUM_SHIFT_UP",
            "MOMENTUM_SHIFT_DOWN",
        }:
            return "WEAKENING"

        return "WATCHING"

    if previous_state in {
        "PERSISTING",
        "STRENGTHENING",
        "PEAK",
        "RETREAT",
        "MOMENTUM_SHIFT_UP",
        "MOMENTUM_SHIFT_DOWN",
    }:
        return "WEAKENING"

    return "WATCHING"


def update_candidate_lifecycle(
    lifecycle_store: Dict[str, Dict[str, Any]],
    analysis: Dict[str, Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    """
    Update lifecycle state for each observed contract.

    This function does not make trading decisions.

    Recovery tracking records:
        - Lowest Movement %
        - Lowest Price
        - Lowest Observation
        - Recovery Start Observation
        - Recovery Start Movement %
        - Current Recovery %
        - Maximum Recovery %
        - Recovery Duration (observations)
    """

    for symbol, movement in analysis.items():

        history = movement.get("History", [])

        if symbol not in lifecycle_store:
            lifecycle_store[symbol] = {
                "Trading Symbol": symbol,
                "State": "NEW",
                "Observations": [],
                "State History": [],
                "Live Order": False,
                "Paper Trade": False,

                # Peak tracking
                "Peak Movement %": None,
                "Peak Price": None,
                "Peak Observation": None,
                "Giveback From Peak %": 0.0,

                # Recovery tracking
                "Lowest Movement %": None,
                "Lowest Price": None,
                "Lowest Observation": None,
                "Recovery Start Observation": None,
                "Recovery Start Movement %": None,
                "Current Recovery %": 0.0,
                "Maximum Recovery %": 0.0,
                "Recovery Duration Observations": 0,
            }

        record = lifecycle_store[symbol]

        recent_movement = movement.get("Recent Movement %")
        latest_price = movement.get("Latest Price")

        try:
            recent_movement_value = (
                float(recent_movement)
                if recent_movement is not None
                else 0.0
            )
        except (TypeError, ValueError):
            recent_movement_value = 0.0

        observation_number = len(record["Observations"]) + 1

        # ---------------------------------------------------------
        # PEAK TRACKING
        # ---------------------------------------------------------

        previous_peak = record.get("Peak Movement %")

        if previous_peak is None:
            peak_movement = recent_movement_value
        else:
            peak_movement = max(
                float(previous_peak),
                recent_movement_value,
            )

        is_new_peak = (
            previous_peak is None
            or recent_movement_value > float(previous_peak)
        )

        if is_new_peak:
            peak_price = latest_price
            peak_observation = observation_number
        else:
            peak_price = record.get("Peak Price")
            peak_observation = record.get("Peak Observation")

        giveback_from_peak = max(
            0.0,
            peak_movement - recent_movement_value,
        )

        # ---------------------------------------------------------
        # RECOVERY TRACKING
        # ---------------------------------------------------------

        previous_low = record.get("Lowest Movement %")

        if previous_low is None:
            lowest_movement = recent_movement_value
            lowest_price = latest_price
            lowest_observation = observation_number
        elif recent_movement_value < float(previous_low):
            lowest_movement = recent_movement_value
            lowest_price = latest_price
            lowest_observation = observation_number
        else:
            lowest_movement = float(previous_low)
            lowest_price = record.get("Lowest Price")
            lowest_observation = record.get("Lowest Observation")

        # Recovery is measured from the lowest observed movement.
        current_recovery = max(
            0.0,
            recent_movement_value - lowest_movement,
        )

        previous_max_recovery = float(
            record.get("Maximum Recovery %", 0.0) or 0.0
        )

        maximum_recovery = max(
            previous_max_recovery,
            current_recovery,
        )

        # A recovery is considered to have started when the
        # current movement improves from the established low.
        recovery_start_observation = record.get(
            "Recovery Start Observation"
        )
        recovery_start_movement = record.get(
            "Recovery Start Movement %"
        )

        if (
            lowest_observation is not None
            and observation_number > lowest_observation
            and current_recovery > 0
        ):
            if recovery_start_observation is None:
                recovery_start_observation = observation_number
                recovery_start_movement = recent_movement_value

        if recovery_start_observation is not None:
            recovery_duration = (
                observation_number - recovery_start_observation
            )
        else:
            recovery_duration = 0

        snapshot = {
            "Recent Movement %": movement.get("Recent Movement %"),
            "Latest Velocity %/sec": movement.get(
                "Latest Velocity %/sec"
            ),
            "Latest Acceleration %/sec2": movement.get(
                "Latest Acceleration %/sec2"
            ),
            "Movement State": movement.get("Movement State"),
            "Latest Price": latest_price,
            "Observation Count": movement.get("Observation Count"),

            # Peak tracking
            "Peak Movement %": peak_movement,
            "Peak Price": peak_price,
            "Peak Observation": peak_observation,
            "Giveback From Peak %": giveback_from_peak,

            # Recovery tracking
            "Lowest Movement %": lowest_movement,
            "Lowest Price": lowest_price,
            "Lowest Observation": lowest_observation,
            "Recovery Start Observation": recovery_start_observation,
            "Recovery Start Movement %": recovery_start_movement,
            "Current Recovery %": current_recovery,
            "Maximum Recovery %": maximum_recovery,
            "Recovery Duration Observations": recovery_duration,
        }

        record["Observations"].append(snapshot)

        previous_state = record["State"]

        new_state = _classify_lifecycle(
            previous_state,
            record["Observations"],
        )

        if previous_state != new_state:
            record["State History"].append({
                "From": previous_state,
                "To": new_state,
                "Observation Count": observation_number,
                "Peak Movement %": peak_movement,
                "Giveback From Peak %": giveback_from_peak,
                "Lowest Movement %": lowest_movement,
                "Current Recovery %": current_recovery,
                "Maximum Recovery %": maximum_recovery,
            })

        record["State"] = new_state

        # Peak tracking
        record["Peak Movement %"] = peak_movement
        record["Peak Price"] = peak_price
        record["Peak Observation"] = peak_observation
        record["Giveback From Peak %"] = giveback_from_peak

        # Recovery tracking
        record["Lowest Movement %"] = lowest_movement
        record["Lowest Price"] = lowest_price
        record["Lowest Observation"] = lowest_observation
        record["Recovery Start Observation"] = recovery_start_observation
        record["Recovery Start Movement %"] = recovery_start_movement
        record["Current Recovery %"] = current_recovery
        record["Maximum Recovery %"] = maximum_recovery
        record["Recovery Duration Observations"] = recovery_duration

        record["Latest"] = snapshot

    return lifecycle_store


def get_lifecycle_summary(
    lifecycle_store: Dict[str, Dict[str, Any]]
) -> Dict[str, int]:

    summary = {
        "NEW": 0,
        "WATCHING": 0,
        "PERSISTING": 0,
        "STRENGTHENING": 0,
        "PEAK": 0,
        "RETREAT": 0,
        "MOMENTUM_SHIFT_UP": 0,
        "MOMENTUM_SHIFT_DOWN": 0,
        "WEAKENING": 0,
        "DROPPED": 0,
    }

    for record in lifecycle_store.values():
        state = record.get("State", "NEW")

        if state not in summary:
            state = "NEW"

        summary[state] += 1

    return summary


def get_active_lifecycle_candidates(
    lifecycle_store: Dict[str, Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Return contracts currently showing meaningful observational
    movement.

    This is NOT a trading candidate list.
    """

    active_states = {
        "WATCHING",
        "PERSISTING",
        "STRENGTHENING",
        "PEAK",
        "RETREAT",
        "MOMENTUM_SHIFT_UP",
        "MOMENTUM_SHIFT_DOWN",
        "WEAKENING",
    }

    results = []

    for record in lifecycle_store.values():
        if record.get("State") in active_states:
            results.append(record)

    return results


def print_lifecycle_summary(
    lifecycle_store: Dict[str, Dict[str, Any]]
) -> None:

    summary = get_lifecycle_summary(lifecycle_store)

    print()
    print("CANDIDATE LIFECYCLE")
    print("-" * 90)

    for state, count in summary.items():
        print(f"{state:<22} {count}")

    print()
    print("Safety: OBSERVATION ONLY")
    print("Live Order:", LIVE_ORDER)
    print("Paper Trade:", PAPER_TRADE)
