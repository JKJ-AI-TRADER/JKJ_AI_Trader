"""
JKJ AI Trader
V21.2.18.2 - Early Surge Candidate Discovery

Purpose
-------
Discover and classify developing NIFTY option candidates using:

1. Existing V21.2.18 scanner output
2. Existing V21.2.15 unified observation output
3. Existing V21.2.18.1 early-surge analyzer

This module is OBSERVATION / DISCOVERY ONLY.

It does NOT:
- place live orders
- create paper trades
- issue BUY/SELL decisions
- modify V1-V12
- modify main.py
- replace the V21.2.18 scanner
- replace the V21.2.18.1 analyzer

Important:
Daily movement, 9:15 movement, velocity and acceleration
remain separate concepts.
"""

from typing import Any, Dict, List, Optional, Tuple

from modules.nifty_option_early_surge_analyzer import (
    analyze_observation_history,
)


# ----------------------------------------------------------------------
# Safety
# ----------------------------------------------------------------------

LIVE_ORDER = False
PAPER_TRADE = False


# ----------------------------------------------------------------------
# Candidate states
# ----------------------------------------------------------------------

STATE_WATCH = "WATCH"
STATE_DEVELOPING = "DEVELOPING"
STATE_ACCELERATING = "ACCELERATING"
STATE_PERSISTENT = "PERSISTENT"
STATE_MULTI_STRIKE_CONFIRMED = "MULTI_STRIKE_CONFIRMED"
STATE_EXTENDED = "EXTENDED"
STATE_WEAKENING = "WEAKENING"
STATE_REJECTED = "REJECTED"


# ----------------------------------------------------------------------
# Discovery thresholds
# ----------------------------------------------------------------------

MIN_DISCOVERY_MOVEMENT = 2.0
MIN_MULTI_STRIKE_MOVEMENT = 2.0
MIN_MULTI_STRIKE_COUNT = 2

MIN_OBSERVATION_COUNT = 4

EXTENDED_MOVEMENT = 30.0


# ----------------------------------------------------------------------
# Basic helpers
# ----------------------------------------------------------------------

def _safe_float(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _option_type(candidate: Dict[str, Any]) -> str:
    return str(candidate.get("Option Type", "")).upper()


def _strike(candidate: Dict[str, Any]) -> Optional[float]:
    return _safe_float(candidate.get("Strike"))


def _symbol(candidate: Dict[str, Any]) -> str:
    return str(candidate.get("Trading Symbol", ""))


def _movement_since_915(candidate: Dict[str, Any]) -> Optional[float]:
    return _safe_float(candidate.get("Movement Since 9:15 %"))


def _daily_change(candidate: Dict[str, Any]) -> Optional[float]:
    return _safe_float(candidate.get("Daily Change %"))


def _is_candidate_candidate(candidate: Dict[str, Any]) -> bool:
    """
    Determine whether a scanner result deserves observation.

    This is deliberately conservative. The scanner's own
    'Candidates' list is respected, while a modest 9:15 movement
    can also qualify a result for discovery.
    """

    if not isinstance(candidate, dict):
        return False

    if not _symbol(candidate):
        return False

    movement = _movement_since_915(candidate)

    scanner_flag = bool(
        candidate.get("Early Surge Candidate", False)
    )

    if scanner_flag:
        return True

    if movement is not None:
        return movement >= MIN_DISCOVERY_MOVEMENT

    return False


# ----------------------------------------------------------------------
# Multi-strike confirmation
# ----------------------------------------------------------------------

def _find_supporting_strikes(
    candidate: Dict[str, Any],
    candidates: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Find nearby strikes moving in the same option direction.

    We deliberately do not rank candidates here.
    This function only establishes whether a move is appearing
    across nearby strikes.
    """

    candidate_type = _option_type(candidate)
    candidate_strike = _strike(candidate)

    if candidate_strike is None:
        return []

    supporting = []

    for item in candidates:

        if item is candidate:
            continue

        if _option_type(item) != candidate_type:
            continue

        strike = _strike(item)

        if strike is None:
            continue

        movement = _movement_since_915(item)

        if movement is None:
            continue

        if movement < MIN_MULTI_STRIKE_MOVEMENT:
            continue

        supporting.append(
            {
                "Trading Symbol": _symbol(item),
                "Strike": strike,
                "Movement Since 9:15 %": movement,
                "Distance From Candidate Strike": abs(
                    strike - candidate_strike
                ),
            }
        )

    supporting.sort(
        key=lambda item: (
            item["Distance From Candidate Strike"],
            item["Strike"],
        )
    )

    return supporting


# ----------------------------------------------------------------------
# Observation analysis
# ----------------------------------------------------------------------

def _get_observation_history(
    observations_by_contract: Dict[Any, Any],
    symbol: str,
) -> Optional[List[Dict[str, Any]]]:
    """
    Locate observation history by trading symbol.

    V21.2.15 uses an identity key, so the exact dictionary key is
    not assumed to be the trading symbol. We inspect each history
    and identify it from the observation's Trading Symbol field.
    """

    if not isinstance(observations_by_contract, dict):
        return None

    for _, history in observations_by_contract.items():

        if not isinstance(history, list):
            continue

        for observation in history:

            if not isinstance(observation, dict):
                continue

            if observation.get("Trading Symbol") == symbol:
                return history

    return None


def _analyze_candidate_history(
    candidate: Dict[str, Any],
    observations_by_contract: Dict[Any, Any],
) -> Dict[str, Any]:
    """
    Run the existing V21.2.18.1 analyzer against one contract.
    """

    symbol = _symbol(candidate)

    history = _get_observation_history(
        observations_by_contract,
        symbol,
    )

    if not history:
        return {
            "Status": "OBSERVATION_HISTORY_UNAVAILABLE",
            "Trading Symbol": symbol,
            "Analyzer": None,
        }

    if len(history) < MIN_OBSERVATION_COUNT:
        return {
            "Status": "INSUFFICIENT_OBSERVATIONS",
            "Trading Symbol": symbol,
            "Observation Count": len(history),
            "Analyzer": None,
        }

    analysis = analyze_observation_history(history)

    return {
        "Status": "ANALYSIS_COMPLETE",
        "Trading Symbol": symbol,
        "Observation Count": len(history),
        "Analyzer": analysis,
    }


# ----------------------------------------------------------------------
# Candidate state interpretation
# ----------------------------------------------------------------------

def _determine_state(
    candidate: Dict[str, Any],
    analysis: Optional[Dict[str, Any]],
    supporting_strikes: List[Dict[str, Any]],
) -> Tuple[str, str]:
    """
    Convert evidence into a descriptive discovery state.

    This is NOT a trade decision.
    """

    movement = _movement_since_915(candidate)

    if movement is None:
        movement = 0.0

    if analysis is None:
        if movement >= EXTENDED_MOVEMENT:
            return (
                STATE_EXTENDED,
                "Large 9:15 movement is present, but observation "
                "history is not available for acceleration analysis.",
            )

        if movement >= MIN_DISCOVERY_MOVEMENT:
            return (
                STATE_DEVELOPING,
                "Early movement is present; continued observation "
                "is required to establish velocity and acceleration.",
            )

        return (
            STATE_WATCH,
            "Candidate is on the observation watch list.",
        )

    overall_state = str(
        analysis.get("Overall State", "")
    ).upper()

    latest_state = str(
        analysis.get("Latest State", "")
    ).upper()

    persistent = bool(
        analysis.get("Persistent Acceleration", False)
    )

    if overall_state in {
        "WEAKENING",
        "REVERSING",
        "FALLING",
    }:
        return (
            STATE_WEAKENING,
            "Observation history shows weakening or reversal "
            "after the earlier movement.",
        )

    if movement >= EXTENDED_MOVEMENT and overall_state not in {
        "ACCELERATING",
        "STEADY_UP",
    }:
        return (
            STATE_EXTENDED,
            "Movement is already extended and current "
            "acceleration evidence is not strengthening.",
        )

    if len(supporting_strikes) + 1 >= MIN_MULTI_STRIKE_COUNT:
        if persistent:
            return (
                STATE_MULTI_STRIKE_CONFIRMED,
                "Persistent acceleration is accompanied by "
                "movement across nearby strikes.",
            )

        if overall_state == "ACCELERATING" or latest_state == "ACCELERATING":
            return (
                STATE_MULTI_STRIKE_CONFIRMED,
                "Acceleration is accompanied by movement "
                "across nearby strikes.",
            )

    if persistent:
        return (
            STATE_PERSISTENT,
            "The existing analyzer reports persistent acceleration.",
        )

    if overall_state == "ACCELERATING" or latest_state == "ACCELERATING":
        return (
            STATE_ACCELERATING,
            "Observation history shows increasing velocity.",
        )

    if overall_state in {
        "STEADY_UP",
        "EARLY_MOVEMENT",
        "DEVELOPING",
    }:
        return (
            STATE_DEVELOPING,
            "Movement is developing, but stronger acceleration "
            "evidence has not yet been established.",
        )

    return (
        STATE_WATCH,
        "Candidate remains under observation pending stronger "
        "movement evidence.",
    )


# ----------------------------------------------------------------------
# Public discovery function
# ----------------------------------------------------------------------

def discover_early_surge_candidates(
    scanner_result: Dict[str, Any],
    observation_result: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Discover and classify early-surge candidates.

    Parameters
    ----------
    scanner_result:
        Output returned by V21.2.18 scan_current_nifty_options().

    observation_result:
        Optional output returned by
        V21.2.15 capture_unified_observation_session().

    Returns
    -------
    Dict[str, Any]
        Descriptive candidate-discovery result.

    No trading action is performed.
    """

    if not isinstance(scanner_result, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Scanner result must be a dictionary.",
            "Candidates": [],
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    scanner_status = scanner_result.get("Status")

    if scanner_status != "SCAN_COMPLETE":
        return {
            "Status": "REJECTED",
            "Reason": "Scanner did not complete successfully.",
            "Scanner Status": scanner_status,
            "Candidates": [],
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    scanner_candidates = scanner_result.get("Candidates", [])

    if not isinstance(scanner_candidates, list):
        scanner_candidates = []

    discovery_pool = [
        item
        for item in scanner_candidates
        if _is_candidate_candidate(item)
    ]

    observations_by_contract = {}

    if isinstance(observation_result, dict):
        observations_by_contract = (
            observation_result.get(
                "Observations By Contract",
                {},
            )
        )

        if not isinstance(observations_by_contract, dict):
            observations_by_contract = {}

    discovered = []

    for candidate in discovery_pool:

        supporting = _find_supporting_strikes(
            candidate,
            discovery_pool,
        )

        observation_analysis = _analyze_candidate_history(
            candidate,
            observations_by_contract,
        )

        analyzer = observation_analysis.get("Analyzer")

        state, reason = _determine_state(
            candidate,
            analyzer,
            supporting,
        )

        movement = _movement_since_915(candidate)
        daily_change = _daily_change(candidate)

        discovered.append(
            {
                "Trading Symbol": _symbol(candidate),
                "Option Type": _option_type(candidate),
                "Strike": _strike(candidate),
                "Expiry": candidate.get("Expiry"),

                "Daily Change %": daily_change,
                "Movement Since 9:15 %": movement,

                "State": state,
                "Reason": reason,

                "Supporting Strike Count": len(supporting),
                "Supporting Strikes": supporting,

                "Observation Status": (
                    observation_analysis.get("Status")
                ),
                "Observation Count": (
                    observation_analysis.get("Observation Count", 0)
                ),

                "Analyzer Overall State": (
                    analyzer.get("Overall State")
                    if analyzer
                    else None
                ),
                "Analyzer Latest State": (
                    analyzer.get("Latest State")
                    if analyzer
                    else None
                ),
                "Persistent Acceleration": (
                    analyzer.get("Persistent Acceleration")
                    if analyzer
                    else False
                ),

                "Live Order": LIVE_ORDER,
                "Paper Trade": PAPER_TRADE,
            }
        )

    return {
        "Status": "EARLY_SURGE_DISCOVERY_COMPLETE",

        "NIFTY Spot": scanner_result.get("NIFTY Spot"),
        "Expiry": scanner_result.get("Expiry"),

        "Scanner Candidate Count": len(scanner_candidates),
        "Discovery Candidate Count": len(discovered),

        "Candidates": discovered,

        "Live Order": LIVE_ORDER,
        "Paper Trade": PAPER_TRADE,
    }


# ----------------------------------------------------------------------
# Convenience function for observation results
# ----------------------------------------------------------------------

def discover_from_scanner_and_observations(
    scanner_result: Dict[str, Any],
    observation_result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Explicit convenience wrapper.

    Keeps the main workflow readable while retaining one underlying
    discovery implementation.
    """

    return discover_early_surge_candidates(
        scanner_result,
        observation_result,
    )
