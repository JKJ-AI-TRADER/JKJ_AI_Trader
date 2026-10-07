"""
JKJ AI Trader
V21.2.15 — Unified Real-Market Observation Session

Purpose:
    Capture ONE real-market observation session and preserve
    the observation history for downstream JKJ decision,
    momentum, risk and stop-loss processing.

Architecture:

    Zerodha
       ↓
    Observation Cycle 1
       ↓
    Observation Cycle 2
       ↓
    Observation Cycle 3
       ↓
    Observation Cycle 4
       ↓
    Unified Observation Session
       ↓
    Same history available to:
        V12.4 Movement
        V12.5 Interpretation
        V12.6 Momentum
        V12.7 Market Context
        V12.8 Opportunity
        V12.9 Risk / Trade Quality
        V13 Decision / Entry
        V14 Risk / Stop-Loss

Safety:
    NO LIVE ORDERS
    NO PAPER TRADE
"""

from datetime import datetime
from time import sleep

from modules.nifty_option_v21_2_observation_cycle import (
    capture_observation_cycle,
)


def _identity_key(observation):
    """
    Create a stable identity key for an option observation.
    """

    return (
        observation.get("Trading Symbol"),
        observation.get("Underlying"),
        observation.get("Expiry"),
        observation.get("Strike"),
        observation.get("Option Type"),
    )


def capture_unified_observation_session(
    kite,
    contracts,
    observation_count=4,
    interval_seconds=10,
):
    """
    Capture one unified real-market observation session.

    The same observations returned here must be used by
    downstream momentum, decision and risk processing.

    Requirements:
        observation_count >= 4
        interval_seconds >= 0
    """

    if observation_count < 4:
        return {
            "Status": "REJECTED",
            "Reason": (
                "At least 4 observations are required "
                "for V12.6 persistence"
            ),
            "Live Order": False,
            "Paper Trade": False,
        }

    if interval_seconds < 0:
        return {
            "Status": "REJECTED",
            "Reason": "Interval seconds cannot be negative",
            "Live Order": False,
            "Paper Trade": False,
        }

    if not isinstance(contracts, list) or not contracts:
        return {
            "Status": "REJECTED",
            "Reason": "Contracts must be a non-empty list",
            "Live Order": False,
            "Paper Trade": False,
        }

    observation_cycles = []

    # ---------------------------------------------------------
    # Capture ONE observation session
    # ---------------------------------------------------------

    for cycle_number in range(observation_count):

        cycle = capture_observation_cycle(
            kite,
            contracts,
        )

        if not isinstance(cycle, dict):
            return {
                "Status": "REJECTED",
                "Reason": (
                    "Observation cycle returned "
                    "an invalid result"
                ),
                "Live Order": False,
                "Paper Trade": False,
            }

        if cycle.get("Status") != "OBSERVATION_CYCLE_COMPLETE":
            return {
                "Status": "REJECTED",
                "Reason": (
                    "Observation cycle failed"
                ),
                "Failed Cycle": cycle_number + 1,
                "Cycle Result": cycle,
                "Live Order": False,
                "Paper Trade": False,
            }

        observation_cycles.append(cycle)

        if cycle_number < observation_count - 1:
            if interval_seconds > 0:
                sleep(interval_seconds)

    # ---------------------------------------------------------
    # Extract observations from every cycle
    # ---------------------------------------------------------

    all_observations = []

    for cycle in observation_cycles:

        observations = cycle.get("Observations")

        if not isinstance(observations, list):
            return {
                "Status": "REJECTED",
                "Reason": (
                    "Observation cycle does not contain "
                    "a valid Observations list"
                ),
                "Live Order": False,
                "Paper Trade": False,
            }

        for observation in observations:

            if not isinstance(observation, dict):
                return {
                    "Status": "REJECTED",
                    "Reason": (
                        "Observation history contains "
                        "an invalid item"
                    ),
                    "Live Order": False,
                    "Paper Trade": False,
                }

            if observation.get("Status") != "RECORDED":
                return {
                    "Status": "REJECTED",
                    "Reason": (
                        "All observations must have "
                        "Status RECORDED"
                    ),
                    "Live Order": False,
                    "Paper Trade": False,
                }

            all_observations.append(observation)

    # ---------------------------------------------------------
    # Group observations by contract identity
    # ---------------------------------------------------------

    observations_by_contract = {}

    for observation in all_observations:

        identity = _identity_key(observation)

        if identity not in observations_by_contract:
            observations_by_contract[identity] = []

        observations_by_contract[identity].append(
            observation
        )

    # ---------------------------------------------------------
    # Validate observation history
    # ---------------------------------------------------------

    for identity, history in observations_by_contract.items():

        if len(history) != observation_count:
            return {
                "Status": "REJECTED",
                "Reason": (
                    "Each contract must contain exactly "
                    "the requested observation count"
                ),
                "Identity": identity,
                "Observed Count": len(history),
                "Expected Count": observation_count,
                "Live Order": False,
                "Paper Trade": False,
            }

    # ---------------------------------------------------------
    # Latest observation for each contract
    # ---------------------------------------------------------

    latest_observations = {}

    for identity, history in observations_by_contract.items():
        latest_observations[identity] = history[-1]

    # ---------------------------------------------------------
    # Unified result
    # ---------------------------------------------------------

    return {
        "Status": "UNIFIED_OBSERVATION_COMPLETE",

        "Observation Count": observation_count,
        "Movement Intervals": observation_count - 1,
        "Interval Seconds": interval_seconds,

        "Contract Count": len(observations_by_contract),

        "Observation Cycles": observation_cycles,

        "Observations By Contract": (
            observations_by_contract
        ),

        "Latest Observations": latest_observations,

        "Session Timestamp": (
            datetime.now().isoformat()
        ),

        "Live Order": False,
        "Paper Trade": False,
    }