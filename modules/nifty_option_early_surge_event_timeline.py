"""
JKJ AI Trader
V21.2.18.3 - Early Surge Event Timeline

Purpose
-------
Convert the existing V21.2.18.1 analyzer output into a
chronological event timeline.

This module does NOT:
- calculate a second version of velocity/acceleration
- place live orders
- create paper trades
- issue BUY/SELL decisions
- modify V1-V12
- modify main.py

The V21.2.18.1 analyzer remains the single source of truth
for movement, velocity, acceleration, persistence, weakening,
reversal and peak information.
"""

from typing import Any, Dict, List


# ----------------------------------------------------------------------
# Safety
# ----------------------------------------------------------------------

LIVE_ORDER = False
PAPER_TRADE = False


# ----------------------------------------------------------------------
# Event names
# ----------------------------------------------------------------------

EVENT_INITIAL = "INITIAL_EVENT"
EVENT_EARLY_MOVEMENT = "EARLY_MOVEMENT_EVENT"
EVENT_ACCELERATION = "ACCELERATION_EVENT"
EVENT_PERSISTENT_ACCELERATION = (
    "PERSISTENT_ACCELERATION_EVENT"
)
EVENT_DECELERATION = "DECELERATION_EVENT"
EVENT_WEAKENING = "WEAKENING_EVENT"
EVENT_REVERSAL = "REVERSAL_EVENT"
EVENT_NEW_SEGMENT = "NEW_SEGMENT_EVENT"
EVENT_PEAK = "PEAK_EVENT"
EVENT_FALLING = "FALLING_EVENT"
EVENT_STABLE = "STABLE_EVENT"


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def _safe_float(value: Any):
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _event(
    observation: Dict[str, Any],
    event_type: str,
    reason: str,
) -> Dict[str, Any]:

    return {
        "Event": event_type,
        "Observation Number": observation.get(
            "Observation Number"
        ),
        "Timestamp": observation.get(
            "Timestamp"
        ),
        "Price": observation.get(
            "Price"
        ),
        "Movement %": observation.get(
            "Movement %"
        ),
        "Velocity %/sec": observation.get(
            "Velocity %/sec"
        ),
        "Acceleration %/sec²": observation.get(
            "Acceleration %/sec²"
        ),
        "State": observation.get(
            "State"
        ),
        "Peak Price": observation.get(
            "Peak Price"
        ),
        "Drawdown From Peak %": observation.get(
            "Drawdown From Peak %"
        ),
        "Reason": reason,
        "Live Order": LIVE_ORDER,
        "Paper Trade": PAPER_TRADE,
    }


# ----------------------------------------------------------------------
# Event interpretation
# ----------------------------------------------------------------------

def _events_for_observation(
    observation: Dict[str, Any],
    previous_observation: Dict[str, Any] | None,
) -> List[Dict[str, Any]]:

    events = []

    state = str(
        observation.get("State", "")
    ).upper()

    previous_state = ""

    if previous_observation:
        previous_state = str(
            previous_observation.get(
                "State",
                "",
            )
        ).upper()

    # --------------------------------------------------------------
    # Initial observation
    # --------------------------------------------------------------

    if state == "INITIAL":
        events.append(
            _event(
                observation,
                EVENT_INITIAL,
                "First observation in the sequence.",
            )
        )

    # --------------------------------------------------------------
    # New segment
    # --------------------------------------------------------------

    if state == "NEW_SEGMENT":
        events.append(
            _event(
                observation,
                EVENT_NEW_SEGMENT,
                "A continuity gap caused the analyzer "
                "to start a new observation segment.",
            )
        )

    # --------------------------------------------------------------
    # Early movement
    # --------------------------------------------------------------

    if state == "EARLY_MOVEMENT":
        events.append(
            _event(
                observation,
                EVENT_EARLY_MOVEMENT,
                "Positive movement has appeared, but "
                "acceleration has not yet been established.",
            )
        )

    # --------------------------------------------------------------
    # Acceleration
    # --------------------------------------------------------------

    if state == "ACCELERATING":
        events.append(
            _event(
                observation,
                EVENT_ACCELERATION,
                "Velocity is increasing according to "
                "the existing V21.2.18.1 analyzer.",
            )
        )

    # --------------------------------------------------------------
    # Persistent acceleration
    #
    # The analyzer's top-level result determines whether
    # persistent acceleration exists. The observation itself
    # is still represented as an acceleration event.
    # The public function below adds the persistent event
    # when the overall analyzer confirms it.
    # --------------------------------------------------------------

    # --------------------------------------------------------------
    # Deceleration
    # --------------------------------------------------------------

    if state == "DECELERATING":
        events.append(
            _event(
                observation,
                EVENT_DECELERATION,
                "Price may still be rising, but velocity "
                "has weakened according to the analyzer.",
            )
        )

    # --------------------------------------------------------------
    # Weakening
    # --------------------------------------------------------------

    if state in {
        "REVERSING",
        "FALLING",
    }:
        events.append(
            _event(
                observation,
                EVENT_WEAKENING,
                "The observation sequence shows weakening "
                "after previous movement.",
            )
        )

    # --------------------------------------------------------------
    # Reversal
    # --------------------------------------------------------------

    if state == "REVERSING":
        events.append(
            _event(
                observation,
                EVENT_REVERSAL,
                "Direction has changed relative to the "
                "preceding movement.",
            )
        )

    # --------------------------------------------------------------
    # Falling
    # --------------------------------------------------------------

    if state == "FALLING":
        events.append(
            _event(
                observation,
                EVENT_FALLING,
                "Negative movement is continuing.",
            )
        )

    # --------------------------------------------------------------
    # Stable
    # --------------------------------------------------------------

    if state == "STABLE":
        events.append(
            _event(
                observation,
                EVENT_STABLE,
                "No meaningful movement is detected.",
            )
        )

    # --------------------------------------------------------------
    # Defensive fallback
    # --------------------------------------------------------------

    if (
        not events
        and previous_state
        and state != previous_state
    ):
        events.append(
            _event(
                observation,
                "STATE_CHANGE_EVENT",
                (
                    "Analyzer state changed from "
                    f"{previous_state} to {state}."
                ),
            )
        )

    return events


# ----------------------------------------------------------------------
# Public function
# ----------------------------------------------------------------------

def build_event_timeline(
    analysis: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build a chronological event timeline from the existing
    V21.2.18.1 analyzer output.
    """

    if not isinstance(analysis, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Analyzer result must be a dictionary.",
            "Events": [],
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    if analysis.get("Status") != "ANALYSIS_COMPLETE":
        return {
            "Status": "REJECTED",
            "Reason": (
                "Analyzer result is not ANALYSIS_COMPLETE."
            ),
            "Analyzer Status": analysis.get("Status"),
            "Events": [],
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    observations = analysis.get(
        "Observations",
        [],
    )

    if not isinstance(observations, list):
        return {
            "Status": "REJECTED",
            "Reason": "Analyzer Observations must be a list.",
            "Events": [],
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    events = []

    previous_observation = None

    for observation in observations:

        if not isinstance(observation, dict):
            continue

        observation_events = _events_for_observation(
            observation,
            previous_observation,
        )

        events.extend(observation_events)

        previous_observation = observation

    # --------------------------------------------------------------
    # Persistent acceleration event
    #
    # We attach this to the first accelerating observation
    # because the top-level analyzer confirms persistence for
    # the overall sequence. This is explicitly labelled as
    # analyzer-level evidence, not a new calculation.
    # --------------------------------------------------------------

    persistent = bool(
        analysis.get(
            "Persistent Acceleration",
            False,
        )
    )

    if persistent:

        first_accelerating = None

        for observation in observations:

            if (
                isinstance(observation, dict)
                and str(
                    observation.get("State", "")
                ).upper()
                == "ACCELERATING"
            ):
                first_accelerating = observation
                break

        if first_accelerating is not None:

            persistent_event = _event(
                first_accelerating,
                EVENT_PERSISTENT_ACCELERATION,
                (
                    "The existing V21.2.18.1 analyzer "
                    "confirms persistent acceleration "
                    "for this observation history."
                ),
            )

            # Put it immediately after the first acceleration
            # event for chronological readability.
            insert_at = 0

            for index, existing in enumerate(events):
                if (
                    existing.get("Observation Number")
                    == first_accelerating.get(
                        "Observation Number"
                    )
                ):
                    insert_at = index + 1
                    break

            events.insert(
                insert_at,
                persistent_event,
            )

    # --------------------------------------------------------------
    # Peak event
    # --------------------------------------------------------------

    peak_observation_number = analysis.get(
        "Peak Observation Number"
    )

    peak_price = _safe_float(
        analysis.get("Peak Price")
    )

    if peak_observation_number is not None:

        peak_observation = None

        for observation in observations:

            if (
                observation.get(
                    "Observation Number"
                )
                == peak_observation_number
            ):
                peak_observation = observation
                break

        if peak_observation is not None:

            events.append(
                _event(
                    peak_observation,
                    EVENT_PEAK,
                    (
                        "Analyzer identified this observation "
                        f"as the peak price {peak_price}."
                    ),
                )
            )

    # --------------------------------------------------------------
    # Sort chronologically by observation number.
    # Event ordering within one observation is preserved.
    # --------------------------------------------------------------

    events.sort(
        key=lambda item: (
            item.get("Observation Number")
            if item.get("Observation Number")
            is not None
            else 999999
        )
    )

    # --------------------------------------------------------------
    # Event summary
    # --------------------------------------------------------------

    event_counts = {}

    for item in events:

        event_name = item.get(
            "Event"
        )

        event_counts[event_name] = (
            event_counts.get(event_name, 0)
            + 1
        )

    return {
        "Status": "EVENT_TIMELINE_COMPLETE",

        "Observation Count": analysis.get(
            "Observation Count"
        ),

        "Overall State": analysis.get(
            "Overall State"
        ),

        "Latest State": analysis.get(
            "Latest State"
        ),

        "Peak Price": analysis.get(
            "Peak Price"
        ),

        "Peak Observation Number": analysis.get(
            "Peak Observation Number"
        ),

        "Persistent Acceleration": persistent,

        "Events": events,

        "Event Counts": event_counts,

        "Live Order": LIVE_ORDER,
        "Paper Trade": PAPER_TRADE,
    }


# ----------------------------------------------------------------------
# Convenience function
# ----------------------------------------------------------------------

def build_event_timeline_from_observations(
    observations: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Analyze observations using V21.2.18.1 and immediately
    construct the V21.2.18.3 event timeline.

    The analyzer remains the source of truth.
    """

    from modules.nifty_option_early_surge_analyzer import (
        analyze_observation_history,
    )

    analysis = analyze_observation_history(
        observations
    )

    if analysis.get("Status") != "ANALYSIS_COMPLETE":
        return {
            "Status": "REJECTED",
            "Reason": (
                "Underlying early-surge analysis failed."
            ),
            "Analysis": analysis,
            "Events": [],
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    timeline = build_event_timeline(
        analysis
    )

    timeline["Analysis"] = analysis

    return timeline
