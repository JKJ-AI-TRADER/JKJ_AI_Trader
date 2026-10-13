
"""
JKJ AI Trader
V21.2.25 - Opportunity Evolution & Leadership Research

Research-only layer.

Purpose:
- Reconstruct how selected candidates evolved during observation.
- Measure threshold crossings.
- Measure interval acceleration.
- Track leadership/ranking changes.
- Identify early leaders, emerging leaders and late surges.
- Measure post-threshold peak and giveback.

Safety:
- No BUY
- No SELL
- No paper trade
- No live order
"""

import math

from typing import Any, Dict, List, Optional


THRESHOLDS = [5.0, 10.0, 15.0, 20.0, 25.0, 30.0]


def _safe_float(value: Any) -> Optional[float]:
    if value is None or isinstance(value, bool):
        return None
    try:
        converted = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return converted if math.isfinite(converted) else None


def _build_candidate_history(
    observation_result: Dict[str, Any],
) -> Dict[str, List[Dict[str, Any]]]:

    history = observation_result.get("Observation History", [])

    by_symbol: Dict[str, List[Dict[str, Any]]] = {}

    if not isinstance(history, list):
        return by_symbol

    for cycle in history:
        if not isinstance(cycle, dict):
            continue

        candidates = cycle.get("Candidates", [])

        if not isinstance(candidates, list):
            continue

        for candidate in candidates:
            if not isinstance(candidate, dict):
                continue

            symbol = candidate.get("Trading Symbol")

            if not symbol:
                continue

            movement = _safe_float(candidate.get("Movement %"))

            if movement is None:
                continue

            by_symbol.setdefault(symbol, []).append(
                {
                    "Trading Symbol": symbol,
                    "Option Type": candidate.get("Option Type"),
                    "Expiry": candidate.get("Expiry"),
                    "Strike": candidate.get("Strike"),
                    "Timestamp": candidate.get("Timestamp"),
                    "Elapsed Minutes": _safe_float(
                        candidate.get("Elapsed Minutes")
                    ),
                    "Movement %": movement,
                    "Initial Price": _safe_float(
                        candidate.get("Initial Price")
                    ),
                    "Current Price": _safe_float(
                        candidate.get("Current Price")
                    ),
                    "NIFTY Movement %": _safe_float(
                        candidate.get("NIFTY Movement %")
                    ),
                }
            )

    return by_symbol


def _calculate_interval_metrics(
    observations: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:

    result = []

    previous_movement = None

    for index, observation in enumerate(observations):

        movement = observation["Movement %"]

        interval_change = None
        acceleration = None

        if previous_movement is not None:
            interval_change = movement - previous_movement

            if index >= 2:
                previous_change = (
                    observations[index - 1]["Movement %"]
                    - observations[index - 2]["Movement %"]
                )
                acceleration = interval_change - previous_change

        item = dict(observation)

        item["Interval Movement %"] = (
            round(interval_change, 4)
            if interval_change is not None
            else None
        )

        item["Acceleration"] = (
            round(acceleration, 4)
            if acceleration is not None
            else None
        )

        result.append(item)

        previous_movement = movement

    return result


def _threshold_crossings(
    observations: List[Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:

    crossings: Dict[str, Dict[str, Any]] = {}

    for threshold in THRESHOLDS:

        first = None

        for item in observations:
            if item["Movement %"] >= threshold:
                first = item
                break

        key = f"{threshold:.0f}%"

        if first is None:
            crossings[key] = {
                "Reached": False,
                "Elapsed Minutes": None,
                "Movement %": None,
                "Timestamp": None,
            }
        else:
            crossings[key] = {
                "Reached": True,
                "Elapsed Minutes": first["Elapsed Minutes"],
                "Movement %": first["Movement %"],
                "Timestamp": first["Timestamp"],
            }

    return crossings


def _post_threshold_analysis(
    observations: List[Dict[str, Any]],
    crossings: Dict[str, Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:

    result = {}

    for threshold_key, crossing in crossings.items():

        if not crossing["Reached"]:
            result[threshold_key] = {
                "Reached": False,
            }
            continue

        crossing_time = crossing["Elapsed Minutes"]

        future = [
            item
            for item in observations
            if (
                item["Elapsed Minutes"] is not None
                and crossing_time is not None
                and item["Elapsed Minutes"] >= crossing_time
            )
        ]

        if not future:
            result[threshold_key] = {
                "Reached": True,
                "Post Threshold Peak %": crossing["Movement %"],
                "Additional Upside From Threshold %": 0.0,
                "Maximum Giveback Percentage Points": 0.0,
                "Final Movement %": crossing["Movement %"],
            }
            continue

        peak = max(
            item["Movement %"]
            for item in future
        )

        final = future[-1]["Movement %"]

        maximum_giveback = 0.0
        running_peak = future[0]["Movement %"]

        for item in future:
            running_peak = max(
                running_peak,
                item["Movement %"],
            )
            giveback = running_peak - item["Movement %"]
            maximum_giveback = max(
                maximum_giveback,
                giveback,
            )

        result[threshold_key] = {
            "Reached": True,
            "Post Threshold Peak %": round(peak, 4),
            "Additional Upside From Threshold %": round(
                peak - crossing["Movement %"],
                4,
            ),
            "Maximum Giveback Percentage Points": round(
                maximum_giveback,
                4,
            ),
            "Final Movement %": round(
                final,
                4,
            ),
        }

    return result


def _classify_evolution(
    observations: List[Dict[str, Any]],
    peak_movement: float,
    peak_elapsed: Optional[float],
    first_5: Optional[float],
    first_20: Optional[float],
) -> str:

    if not observations:
        return "INSUFFICIENT"

    final_movement = observations[-1]["Movement %"]

    first_elapsed = observations[0]["Elapsed Minutes"]

    if (
        first_5 is not None
        and peak_elapsed is not None
        and first_elapsed is not None
        and peak_elapsed - first_elapsed <= 20.0
        and peak_movement >= 20.0
    ):
        return "EARLY_SURGE"

    if (
        first_20 is not None
        and first_5 is not None
        and peak_elapsed is not None
        and first_20 > first_5
        and peak_movement >= 20.0
    ):
        return "EMERGING_LEADER"

    if (
        peak_movement >= 20.0
        and final_movement > 0
        and final_movement >= peak_movement * 0.50
    ):
        return "SUSTAINED_LEADER"

    if (
        peak_movement >= 20.0
        and final_movement > 0
    ):
        return "LATE_SURGE_OR_GIVEBACK"

    if peak_movement > 0:
        return "DEVELOPING"

    return "FAILED"


def analyze_opportunity_evolution(
    observation_result: Dict[str, Any],
) -> Dict[str, Any]:

    if not isinstance(observation_result, dict):
        return {
            "Status": "INVALID_OBSERVATION_RESULT",
            "Trading Decision": False,
            "Live Order": False,
            "Paper Trade": False,
        }

    if observation_result.get("Status") != (
        "ONE_HOUR_OBSERVATION_COMPLETE"
    ):
        return {
            "Status": "INVALID_OBSERVATION_STATUS",
            "Received Status": observation_result.get("Status"),
            "Trading Decision": False,
            "Live Order": False,
            "Paper Trade": False,
        }

    by_symbol = _build_candidate_history(
        observation_result
    )

    candidate_results = []

    for symbol, raw_observations in by_symbol.items():

        observations = _calculate_interval_metrics(
            raw_observations
        )

        if not observations:
            continue

        crossings = _threshold_crossings(
            observations
        )

        post_threshold = _post_threshold_analysis(
            observations,
            crossings,
        )

        peak_item = max(
            observations,
            key=lambda item: item["Movement %"],
        )

        first_5 = None
        first_20 = None

        if crossings["5%"]["Reached"]:
            first_5 = crossings["5%"]["Elapsed Minutes"]

        if crossings["20%"]["Reached"]:
            first_20 = crossings["20%"]["Elapsed Minutes"]

        evolution = _classify_evolution(
            observations=observations,
            peak_movement=peak_item["Movement %"],
            peak_elapsed=peak_item["Elapsed Minutes"],
            first_5=first_5,
            first_20=first_20,
        )

        candidate_results.append(
            {
                "Trading Symbol": symbol,
                "Option Type": observations[0]["Option Type"],
                "Expiry": observations[0]["Expiry"],
                "Strike": observations[0]["Strike"],
                "Observation Count": len(observations),
                "Peak Movement %": round(
                    peak_item["Movement %"],
                    4,
                ),
                "Peak Time Minutes": peak_item[
                    "Elapsed Minutes"
                ],
                "Peak Timestamp": peak_item[
                    "Timestamp"
                ],
                "Final Movement %": round(
                    observations[-1]["Movement %"],
                    4,
                ),
                "Threshold Crossings": crossings,
                "Post Threshold Analysis": post_threshold,
                "Evolution Classification": evolution,
                "Timeline": observations,
            }
        )

    candidate_results.sort(
        key=lambda item: (
            item["Peak Movement %"],
            item["Final Movement %"],
        ),
        reverse=True,
    )

    # Leadership reconstruction:
    # At every observation time, rank candidates by movement.
    leadership = []

    history = observation_result.get(
        "Observation History",
        [],
    )

    if isinstance(history, list):

        for cycle in history:

            if not isinstance(cycle, dict):
                continue

            candidates = cycle.get(
                "Candidates",
                [],
            )

            if not isinstance(candidates, list):
                continue

            ranked = []

            for candidate in candidates:

                if not isinstance(candidate, dict):
                    continue

                symbol = candidate.get(
                    "Trading Symbol"
                )

                movement = _safe_float(
                    candidate.get("Movement %")
                )

                if symbol and movement is not None:
                    ranked.append(
                        {
                            "Trading Symbol": symbol,
                            "Movement %": movement,
                        }
                    )

            ranked.sort(
                key=lambda item: item["Movement %"],
                reverse=True,
            )

            for rank, item in enumerate(
                ranked,
                start=1,
            ):
                item["Rank"] = rank

            leadership.append(
                {
                    "Timestamp": cycle.get(
                        "Timestamp"
                    ),
                    "Elapsed Minutes": cycle.get(
                        "Elapsed Minutes"
                    ),
                    "NIFTY Spot": cycle.get(
                        "NIFTY Spot"
                    ),
                    "NIFTY Movement %": cycle.get(
                        "NIFTY Movement %"
                    ),
                    "Ranking": ranked,
                }
            )

    return {
        "Status": "OPPORTUNITY_EVOLUTION_RESEARCH_COMPLETE",
        "Observation Status": observation_result.get(
            "Status"
        ),
        "Observation Count": len(history)
        if isinstance(history, list)
        else 0,
        "Candidate Count": len(candidate_results),
        "Candidates": candidate_results,
        "Leadership Timeline": leadership,
        "Thresholds": THRESHOLDS,
        "Research Purpose": (
            "Reconstruct candidate evolution, threshold "
            "crossings, acceleration and leadership changes."
        ),
        "Trading Decision": False,
        "Live Order": False,
        "Paper Trade": False,
        "BUY": False,
        "SELL": False,
    }
