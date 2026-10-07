"""
JKJ AI Trader
V21.2.6 — Pre-Market Ready Controller

Purpose:
Assemble the tested V21.2 pre-market preparation stages
into one controlled readiness result.

Flow:
09:00-09:15
    ↓
Session validation
    ↓
NFO preparation
    ↓
NIFTY spot
    ↓
Expiry
    ↓
CE/PE candidates
    ↓
Identity validation
    ↓
PRE_MARKET_READY

This module does NOT:
- place live orders
- create paper trades
- make BUY/SELL decisions
- calculate opportunity scores
- modify V12.1-V21.1 modules
- modify main.py
"""

from datetime import datetime

from modules.nifty_option_v21_2_market_session import (
    get_market_session_state,
)

from modules.nifty_option_v21_2_candidate_preparation import (
    prepare_nifty_candidates,
)


def evaluate_pre_market_controller(
    current_time=None,
    contracts_per_side=2,
):
    """
    Assemble the V21.2 pre-market readiness chain.

    The current_time argument is intentionally injectable so
    the controller can be tested at different session boundaries
    without waiting for the actual clock.
    """

    # --------------------------------------------------
    # STEP 1 — SESSION STATE
    # --------------------------------------------------

    session_result = get_market_session_state(
        current_time
    )

    if session_result.get("Status") != "EVALUATED":
        return {
            "Status": "REJECTED",
            "Reason": "Unable to evaluate market session.",
            "Live Order": False,
            "Paper Trade": False,
        }

    session_state = session_result.get(
        "Session State"
    )

    if session_state != "PRE_MARKET":
        return {
            "Status": "NOT_READY",
            "Reason": (
                "Pre-market controller can only prepare "
                "during PRE_MARKET."
            ),
            "Session State": session_state,
            "Current Time": session_result.get(
                "Current Time"
            ),
            "Live Order": False,
            "Paper Trade": False,
        }

    # --------------------------------------------------
    # STEP 2 — NIFTY CANDIDATE PREPARATION
    # --------------------------------------------------

    candidate_result = prepare_nifty_candidates(
        contracts_per_side=contracts_per_side
    )

    if candidate_result.get("Status") != "CANDIDATES_READY":
        return {
            "Status": "NOT_READY",
            "Reason": candidate_result.get(
                "Reason",
                "NIFTY candidate preparation failed.",
            ),
            "Session State": session_state,
            "Current Time": session_result.get(
                "Current Time"
            ),
            "Candidate Preparation Status":
                candidate_result.get("Status"),
            "Live Order": False,
            "Paper Trade": False,
        }

    # --------------------------------------------------
    # STEP 3 — FINAL READINESS VALIDATION
    # --------------------------------------------------

    if candidate_result.get(
        "Contract Identity"
    ) != "VALIDATED":
        return {
            "Status": "NOT_READY",
            "Reason": "Contract identity validation failed.",
            "Session State": session_state,
            "Live Order": False,
            "Paper Trade": False,
        }

    if candidate_result.get(
        "Observation Universe"
    ) != "READY":
        return {
            "Status": "NOT_READY",
            "Reason": "Observation universe is not ready.",
            "Session State": session_state,
            "Live Order": False,
            "Paper Trade": False,
        }

    # --------------------------------------------------
    # STEP 4 — PRE-MARKET READY
    # --------------------------------------------------

    return {
        "Status": "PRE_MARKET_READY",
        "Session State": session_state,
        "Current Time": session_result.get(
            "Current Time"
        ),
        "Preparation Window": "09:00-09:15",
        "Session Status": candidate_result.get(
            "Session Status"
        ),
        "NFO Instruments": candidate_result.get(
            "NFO Instruments"
        ),
        "NIFTY Spot": candidate_result.get(
            "NIFTY Spot"
        ),
        "Expiry": candidate_result.get(
            "Expiry"
        ),
        "CE Candidates": candidate_result.get(
            "CE Candidates"
        ),
        "PE Candidates": candidate_result.get(
            "PE Candidates"
        ),
        "Contract Identity": candidate_result.get(
            "Contract Identity"
        ),
        "Observation Universe": candidate_result.get(
            "Observation Universe"
        ),
        "Live Order": False,
        "Paper Trade": False,
    }


if __name__ == "__main__":

    print("=" * 70)
    print(
        "JKJ AI TRADER — "
        "V21.2.6 PRE-MARKET READY CONTROLLER TEST"
    )
    print("=" * 70)

    test_time = datetime.strptime(
        "2026-09-24 09:05:00",
        "%Y-%m-%d %H:%M:%S",
    )

    result = evaluate_pre_market_controller(
        current_time=test_time,
        contracts_per_side=2,
    )

    for key, value in result.items():

        if key in (
            "CE Candidates",
            "PE Candidates",
        ):
            print(
                f"{key}: "
                f"{len(value) if isinstance(value, list) else value}"
            )

            if isinstance(value, list):
                for contract in value:
                    print(
                        "  ",
                        contract.get("tradingsymbol"),
                        "|",
                        contract.get("instrument_type"),
                        "| Strike:",
                        contract.get("strike"),
                        "| Token:",
                        contract.get("instrument_token"),
                    )

        else:
            print(f"{key}: {value}")

    print("=" * 70)
