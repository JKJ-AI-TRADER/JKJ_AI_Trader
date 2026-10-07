"""
JKJ AI Trader
V21.2.18.4 - Early Surge Paper Entry/Exit Replay

Purpose:
    Replay historical observation sequences without hindsight.

Important:
    - Observation/replay only
    - No live orders
    - No paper orders
    - No use of final historical classification as an entry trigger
    - Decisions use only information available up to the current observation
"""

from typing import Any, Dict, List


LIVE_ORDER = False
PAPER_TRADE = False

MIN_ENTRY_OBSERVATIONS = 3
MIN_ACCELERATION_COUNT = 1

ENTRY_NONE = "NO_ENTRY"
ENTRY_WATCH = "WATCH"
ENTRY_CANDIDATE = "ENTRY_CANDIDATE"

EXIT_NONE = "NO_EXIT"
EXIT_WEAKENING = "WEAKENING_EXIT"
EXIT_REVERSAL = "REVERSAL_EXIT"

STATE_WATCH = "WATCH"
STATE_ACCELERATING = "ACCELERATING"
STATE_WEAKENING = "WEAKENING"
STATE_REVERSING = "REVERSING"
STATE_STABLE = "STABLE"


def _valid_number(value):
    return isinstance(value, (int, float))


def _classify_entry(
    observations_seen: List[Dict[str, Any]]
) -> str:

    if len(observations_seen) < MIN_ENTRY_OBSERVATIONS:
        return ENTRY_WATCH

    latest = observations_seen[-1]

    velocity = latest.get("Velocity %/sec")
    acceleration = latest.get("Acceleration %/sec²")

    if not _valid_number(velocity):
        return ENTRY_WATCH

    if velocity <= 0:
        return ENTRY_WATCH

    if (
        _valid_number(acceleration)
        and acceleration > 0
    ):
        return ENTRY_CANDIDATE

    return ENTRY_WATCH


def _classify_exit(
    observations_seen: List[Dict[str, Any]]
) -> str:

    if len(observations_seen) < 2:
        return EXIT_NONE

    latest = observations_seen[-1]

    velocity = latest.get("Velocity %/sec")
    acceleration = latest.get("Acceleration %/sec²")

    state = latest.get("State")

    if (
        state == "REVERSING"
        or (
            _valid_number(velocity)
            and velocity < 0
        )
    ):
        return EXIT_REVERSAL

    if (
        _valid_number(acceleration)
        and acceleration < 0
        and _valid_number(velocity)
        and velocity >= 0
    ):
        return EXIT_WEAKENING

    return EXIT_NONE


def replay_observation_history(
    observations: List[Dict[str, Any]]
) -> Dict[str, Any]:

    if not isinstance(observations, list):
        return {
            "Status": "REJECTED",
            "Reason": "Observations must be a list.",
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    if not observations:
        return {
            "Status": "REJECTED",
            "Reason": "Observation history is empty.",
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    replay = []

    entry_observation = None
    exit_observation = None

    entry_price = None
    exit_price = None

    for index, observation in enumerate(
        observations,
        start=1,
    ):

        if not isinstance(observation, dict):
            return {
                "Status": "REJECTED",
                "Reason": (
                    f"Observation {index} is invalid."
                ),
                "Live Order": LIVE_ORDER,
                "Paper Trade": PAPER_TRADE,
            }

        current = dict(observation)

        current["Replay Observation Number"] = index

        observations_seen = replay + [current]

        entry_decision = ENTRY_NONE

        if entry_observation is None:
            entry_decision = _classify_entry(
                observations_seen
            )

            if entry_decision == ENTRY_CANDIDATE:
                entry_observation = index
                entry_price = current.get(
                    "Price",
                    current.get("Current Price"),
                )

        exit_decision = EXIT_NONE

        if entry_observation is not None:
            if index > entry_observation:
                exit_decision = _classify_exit(
                    observations_seen
                )

                if (
                    exit_observation is None
                    and exit_decision != EXIT_NONE
                ):
                    exit_observation = index
                    exit_price = current.get(
                        "Price",
                        current.get("Current Price"),
                    )

        current["Entry Decision"] = entry_decision
        current["Exit Decision"] = exit_decision

        replay.append(current)

    result = {
        "Status": "REPLAY_COMPLETE",
        "Observation Count": len(observations),
        "Entry Observation": entry_observation,
        "Entry Price": entry_price,
        "Exit Observation": exit_observation,
        "Exit Price": exit_price,
        "Replay": replay,
        "Hindsight Used For Entry": False,
        "Hindsight Used For Exit": False,
        "Live Order": LIVE_ORDER,
        "Paper Trade": PAPER_TRADE,
    }

    if (
        entry_observation is not None
        and exit_observation is not None
        and _valid_number(entry_price)
        and _valid_number(exit_price)
        and entry_price != 0
    ):
        result["Entry To Exit %"] = round(
            (
                (exit_price - entry_price)
                / entry_price
            ) * 100,
            2,
        )
    else:
        result["Entry To Exit %"] = None

    return result
