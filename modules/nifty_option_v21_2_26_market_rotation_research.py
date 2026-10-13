
"""
JKJ AI Trader
V21.2.26 - Market Leadership & Rotation Research

Research-only layer.

Purpose:
- Compare CE and PE opportunity fields.
- Measure breadth and average movement.
- Identify side leadership.
- Detect possible CE <-> PE leadership transitions.
- Study whether a new side strengthens while the previous side weakens.

Safety:
- No BUY
- No SELL
- No paper trade
- No live order
"""
import math
from typing import Any, Dict, List, Optional


def _safe_float(value: Any) -> Optional[float]:
    if value is None or isinstance(value, bool):
        return None

    try:
        converted = float(value)
    except (TypeError, ValueError, OverflowError):
        return None

    return converted if math.isfinite(converted) else None


def _side_metrics(
    candidates: List[Dict[str, Any]],
    option_type: str,
) -> Dict[str, Any]:

    side = []

    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue

        if candidate.get("Option Type") != option_type:
            continue

        movement = _safe_float(
            candidate.get("Movement %")
        )

        if movement is None:
            continue

        acceleration = _safe_float(
            candidate.get("Acceleration")
        )

        side.append(
            {
                "Trading Symbol": candidate.get(
                    "Trading Symbol"
                ),
                "Movement %": movement,
                "Acceleration": acceleration,
                "Strike": candidate.get("Strike"),
                "Expiry": candidate.get("Expiry"),
            }
        )

    positive = [
        item for item in side
        if item["Movement %"] > 0
    ]

    accelerating = [
        item for item in side
        if (
            item.get("Acceleration") is not None
            and item["Acceleration"] > 0
        )
    ]

    if side:
        average_movement = sum(
            item["Movement %"]
            for item in side
        ) / len(side)
    else:
        average_movement = 0.0

    if positive:
        average_positive_movement = sum(
            item["Movement %"]
            for item in positive
        ) / len(positive)
    else:
        average_positive_movement = 0.0

    strongest = (
        max(
            side,
            key=lambda item: item["Movement %"],
        )
        if side
        else None
    )

    strongest_acceleration = (
        max(
            accelerating,
            key=lambda item: item["Acceleration"],
        )
        if accelerating
        else None
    )

    return {
        "Option Type": option_type,
        "Candidate Count": len(side),
        "Positive Count": len(positive),
        "Accelerating Count": len(accelerating),
        "Positive Breadth %": round(
            (len(positive) / len(side)) * 100.0,
            4,
        )
        if side
        else 0.0,
        "Average Movement %": round(
            average_movement,
            4,
        ),
        "Average Positive Movement %": round(
            average_positive_movement,
            4,
        ),
        "Strongest Candidate": strongest,
        "Strongest Acceleration Candidate":
            strongest_acceleration,
    }


def _leadership_score(
    metrics: Dict[str, Any],
) -> float:

    breadth = metrics["Positive Breadth %"]
    average = metrics["Average Positive Movement %"]

    # Research ranking only.
    # This is NOT a trading score.
    return (
        breadth * 0.50
        + average * 5.0
    )


def _determine_leader(
    ce: Dict[str, Any],
    pe: Dict[str, Any],
) -> str:

    ce_score = _leadership_score(ce)
    pe_score = _leadership_score(pe)

    if ce_score <= 0 and pe_score <= 0:
        return "NEUTRAL"

    if abs(ce_score - pe_score) < 2.0:
        return "BALANCED"

    if ce_score > pe_score:
        return "CE"

    return "PE"


def _rotation_state(
    previous_leader: Optional[str],
    current_leader: str,
    previous_ce: Optional[Dict[str, Any]],
    previous_pe: Optional[Dict[str, Any]],
    current_ce: Dict[str, Any],
    current_pe: Dict[str, Any],
) -> str:

    if previous_leader is None:
        return "INITIAL"

    if current_leader == previous_leader:
        return "CONTINUING"

    if current_leader == "BALANCED":
        return "BALANCING"

    if current_leader == "NEUTRAL":
        return "NEUTRAL"

    if previous_leader in ("CE", "PE"):
        return "ROTATION_DETECTED"

    return "LEADERSHIP_EMERGING"


def analyze_market_rotation(
    observation_result: Dict[str, Any],
) -> Dict[str, Any]:

    if not isinstance(observation_result, dict):
        return {
            "Status": "INVALID_OBSERVATION_RESULT",
            "Trading Decision": False,
            "Live Order": False,
            "Paper Trade": False,
            "BUY": False,
            "SELL": False,
        }

    if observation_result.get("Status") != (
        "ONE_HOUR_OBSERVATION_COMPLETE"
    ):
        return {
            "Status": "INVALID_OBSERVATION_STATUS",
            "Received Status": observation_result.get(
                "Status"
            ),
            "Trading Decision": False,
            "Live Order": False,
            "Paper Trade": False,
            "BUY": False,
            "SELL": False,
        }

    history = observation_result.get(
        "Observation History",
        [],
    )

    if not isinstance(history, list):
        return {
            "Status": "INVALID_OBSERVATION_HISTORY",
            "Trading Decision": False,
            "Live Order": False,
            "Paper Trade": False,
            "BUY": False,
            "SELL": False,
        }

    timeline = []

    previous_leader = None
    previous_ce = None
    previous_pe = None

    for cycle in history:

        if not isinstance(cycle, dict):
            continue

        candidates = cycle.get(
            "Candidates",
            [],
        )

        if not isinstance(candidates, list):
            continue

        ce = _side_metrics(
            candidates,
            "CE",
        )

        pe = _side_metrics(
            candidates,
            "PE",
        )

        leader = _determine_leader(
            ce,
            pe,
        )

        rotation = _rotation_state(
            previous_leader,
            leader,
            previous_ce,
            previous_pe,
            ce,
            pe,
        )

        ce_score = _leadership_score(ce)
        pe_score = _leadership_score(pe)

        timeline.append(
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
                "CE": ce,
                "PE": pe,
                "CE Research Score": round(
                    ce_score,
                    4,
                ),
                "PE Research Score": round(
                    pe_score,
                    4,
                ),
                "Leader": leader,
                "Rotation State": rotation,
            }
        )

        previous_leader = leader
        previous_ce = ce
        previous_pe = pe

    rotation_events = [
        item
        for item in timeline
        if item.get("Rotation State")
        == "ROTATION_DETECTED"
    ]

    leader_counts: Dict[str, int] = {}

    for item in timeline:
        leader = item.get("Leader")
        leader_counts[leader] = (
            leader_counts.get(leader, 0) + 1
        )

    return {
        "Status": "MARKET_LEADERSHIP_ROTATION_RESEARCH_COMPLETE",
        "Observation Status": observation_result.get(
            "Status"
        ),
        "Observation Count": len(timeline),
        "Leadership Counts": leader_counts,
        "Rotation Event Count": len(rotation_events),
        "Rotation Events": rotation_events,
        "Timeline": timeline,
        "Research Purpose": (
            "Compare CE and PE opportunity fields and "
            "study intraday leadership rotation."
        ),
        "Trading Decision": False,
        "Live Order": False,
        "Paper Trade": False,
        "BUY": False,
        "SELL": False,
    }
