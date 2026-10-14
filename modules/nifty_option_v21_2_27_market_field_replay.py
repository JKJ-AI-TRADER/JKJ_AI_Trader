
"""
JKJ AI Trader
V21.2.27 - Continuous CE/PE Market Field Replay

Purpose:
    Research the broad NIFTY option field continuously after the
    genuine 09:15 baseline.

This module is observation/research only.

Safety:
    - No live orders
    - No paper trades
    - No entry qualification
    - No BUY/SELL decisions

Architecture:
    V21.2.18 baseline store
        +
    V21.2.23 broad multi-expiry universe
        +
    Continuous CE/PE field observation
        +
    Market leadership / rotation research
"""

from __future__ import annotations

import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from modules.nifty_option_v21_2_18_baseline_store import (
    load_today_baseline,
)
from modules.nifty_option_v21_2_23_multi_expiry_discovery import (
    _build_multi_expiry_universe,
    _get_near_term_expiries,
    _get_nifty_spot,
    _ltp_batch,
)


DEFAULT_OBSERVATION_COUNT = 20
DEFAULT_INTERVAL_SECONDS = 60
DEFAULT_EXPIRY_COUNT = 6
DEFAULT_STRIKES_EACH_SIDE = 15
DEFAULT_BATCH_SIZE = 100


def _now_ist() -> str:
    """Return current IST timestamp."""
    try:
        from zoneinfo import ZoneInfo

        return datetime.now(
            ZoneInfo("Asia/Kolkata")
        ).isoformat()

    except Exception:
        return datetime.now().isoformat()


def _percentage_change(
    previous: Optional[float],
    current: Optional[float],
) -> Optional[float]:

    if previous is None or current is None:
        return None

    if previous <= 0:
        return None

    return ((current - previous) / previous) * 100.0


def _baseline_price_for_symbol(
    baseline: Optional[Dict[str, Any]],
    trading_symbol: str,
) -> Optional[float]:
    """
    Read only a genuine stored 09:15 baseline.

    Synthetic/test baselines are rejected.
    """

    if not baseline:
        return None

    if baseline.get("Baseline Type") != "GENUINE_915":
        return None

    records = baseline.get("Baseline", [])

    if not isinstance(records, list):
        return None

    for item in records:

        if not isinstance(item, dict):
            continue

        if item.get("Trading Symbol") != trading_symbol:
            continue

        price = item.get("9:15 Price")

        try:
            price = float(price)
        except (TypeError, ValueError):
            return None

        if price <= 0:
            return None

        return price

    return None



def _classify_field_state(
    metrics: Dict[str, Any],
    previous_metrics: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Direction-neutral research classification of one CE/PE field.

    This is NOT an entry or exit signal.

    The classifier deliberately separates:
        1. historical strength from the 09:15 baseline
        2. current short-term movement
        3. acceleration
        4. breadth expansion/contraction

    A side cannot be classified as EMERGING or STRENGTHENING
    when its positive breadth is zero.
    """

    contract_count = int(
        metrics.get("Contract Count", 0) or 0
    )

    if contract_count <= 0:
        return "NEUTRAL"

    breadth = float(
        metrics.get("Positive Breadth %", 0.0) or 0.0
    )

    average_positive = float(
        metrics.get(
            "Average Positive Movement %",
            0.0,
        )
        or 0.0
    )

    average_interval = float(
        metrics.get(
            "Average Interval Movement %",
            0.0,
        )
        or 0.0
    )

    positive_interval_breadth = float(
        metrics.get(
            "Positive Interval Breadth %",
            0.0,
        )
        or 0.0
    )

    accelerating = int(
        metrics.get("Accelerating Count", 0) or 0
    )

    accelerating_breadth = (
        (accelerating / contract_count) * 100.0
    )

    previous_breadth = None
    previous_average = None
    previous_interval = None
    previous_accelerating = None

    if isinstance(previous_metrics, dict):

        previous_breadth = float(
            previous_metrics.get(
                "Positive Breadth %",
                0.0,
            )
            or 0.0
        )

        previous_average = float(
            previous_metrics.get(
                "Average Positive Movement %",
                0.0,
            )
            or 0.0
        )

        previous_interval = float(
            previous_metrics.get(
                "Average Interval Movement %",
                0.0,
            )
            or 0.0
        )

        previous_accelerating = int(
            previous_metrics.get(
                "Accelerating Count",
                0,
            )
            or 0
        )

    # First observation has no directional history.
    if previous_metrics is None:
        return "NEUTRAL"

    breadth_change = (
        breadth - previous_breadth
        if previous_breadth is not None
        else 0.0
    )

    average_change = (
        average_positive - previous_average
        if previous_average is not None
        else 0.0
    )

    interval_change = (
        average_interval - previous_interval
        if previous_interval is not None
        else 0.0
    )

    acceleration_change = (
        accelerating - previous_accelerating
        if previous_accelerating is not None
        else 0
    )

    # ------------------------------------------------------------
    # WEAKENING_BUT_ELEVATED
    #
    # The field has already made a meaningful move from 09:15,
    # but current short-term behaviour is deteriorating.
    # This is particularly important for detecting a possible
    # transition before another side emerges.
    # ------------------------------------------------------------

    if (
        average_positive >= 5.0
        and breadth >= 10.0
        and average_interval < 0.0
        and (
            interval_change < 0.0
            or breadth_change < 0.0
            or average_change < 0.0
            or acceleration_change < 0
        )
    ):
        return "WEAKENING_BUT_ELEVATED"

    # ------------------------------------------------------------
    # DOMINANT
    #
    # Broad participation, meaningful baseline movement and
    # positive/neutral current behaviour.
    # ------------------------------------------------------------

    if (
        breadth >= 60.0
        and average_positive >= 5.0
        and average_interval >= 0.0
        and accelerating_breadth >= 10.0
    ):
        return "DOMINANT"

    # ------------------------------------------------------------
    # EMERGING
    #
    # Positive breadth must actually exist and be developing.
    # Zero breadth can never be an emerging field.
    # ------------------------------------------------------------

    if (
        breadth > 0.0
        and breadth < 60.0
        and accelerating > 0
        and (
            breadth_change > 0.0
            or positive_interval_breadth > 0.0
        )
        and (
            average_interval > 0.0
            or interval_change > 0.0
            or acceleration_change > 0
        )
    ):
        return "EMERGING"

    # ------------------------------------------------------------
    # STRENGTHENING
    #
    # The field already has positive participation and its
    # current behaviour is improving.
    # ------------------------------------------------------------

    if (
        breadth > 0.0
        and (
            average_interval > 0.0
            or interval_change > 0.0
            or acceleration_change > 0
        )
        and (
            breadth_change > 0.0
            or average_change > 0.0
            or acceleration_change > 0
        )
    ):
        return "STRENGTHENING"

    # ------------------------------------------------------------
    # WEAKENING
    # ------------------------------------------------------------

    if (
        breadth > 0.0
        and (
            average_interval < 0.0
            or breadth_change < 0.0
            or average_change < 0.0
            or acceleration_change < 0
        )
    ):
        return "WEAKENING"

    return "NEUTRAL"



def _calculate_field_metrics(
    observations: List[Dict[str, Any]],
    previous_metrics: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Calculate CE/PE field-level research metrics.

    This function does not make a trading decision.
    """

    ce = [
        item
        for item in observations
        if item.get("Option Type") == "CE"
    ]

    pe = [
        item
        for item in observations
        if item.get("Option Type") == "PE"
    ]

    def side_metrics(
        items: List[Dict[str, Any]],
    ) -> Dict[str, Any]:

        if not items:
            return {
                "Contract Count": 0,
                "Positive Count": 0,
                "Positive Breadth %": 0.0,
                "Average Movement %": 0.0,
                "Average Positive Movement %": 0.0,
                "Accelerating Count": 0,
                "Strongest": None,
            }

        movements = [
            float(item["Movement Since 9:15 %"])
            for item in items
            if item.get("Movement Since 9:15 %") is not None
        ]

        positive = [
            value
            for value in movements
            if value > 0
        ]

        accelerating = [
            item
            for item in items
            if (
                item.get("Acceleration %") is not None
                and item.get("Acceleration %") > 0
            )
        ]

        strongest = None

        valid_items = [
            item
            for item in items
            if item.get("Movement Since 9:15 %") is not None
        ]

        if valid_items:
            strongest_item = max(
                valid_items,
                key=lambda item: item.get(
                    "Movement Since 9:15 %",
                    0.0,
                ),
            )

            strongest = {
                "Trading Symbol": strongest_item.get(
                    "Trading Symbol"
                ),
                "Movement Since 9:15 %": round(
                    float(
                        strongest_item.get(
                            "Movement Since 9:15 %",
                            0.0,
                        )
                    ),
                    2,
                ),
                "Interval Movement %": round(
                    float(
                        strongest_item.get(
                            "Interval Movement %",
                            0.0,
                        )
                    ),
                    2,
                ),
                "Acceleration %": round(
                    float(
                        strongest_item.get(
                            "Acceleration %",
                            0.0,
                        )
                    ),
                    2,
                ),
            }

        average_movement = (
            sum(movements) / len(movements)
            if movements
            else 0.0
        )

        average_positive = (
            sum(positive) / len(positive)
            if positive
            else 0.0
        )

        intervals = [
            float(item.get("Interval Movement %", 0.0) or 0.0)
            for item in items
            if item.get("Interval Movement %") is not None
        ]

        positive_intervals = [
            value
            for value in intervals
            if value > 0
        ]

        average_interval = (
            sum(intervals) / len(intervals)
            if intervals
            else 0.0
        )

        positive_interval_breadth = (
            (len(positive_intervals) / len(intervals)) * 100.0
            if intervals
            else 0.0
        )

        breadth = (
            (len(positive) / len(movements)) * 100.0
            if movements
            else 0.0
        )

        return {
            "Contract Count": len(items),
            "Positive Count": len(positive),
            "Positive Breadth %": round(
                breadth,
                2,
            ),
            "Average Movement %": round(
                average_movement,
                2,
            ),
            "Average Positive Movement %": round(
                average_positive,
                2,
            ),
            "Average Interval Movement %": round(
                average_interval,
                2,
            ),
            "Positive Interval Breadth %": round(
                positive_interval_breadth,
                2,
            ),
            "Accelerating Count": len(accelerating),
            "Strongest": strongest,
        }

    ce_metrics = side_metrics(ce)
    pe_metrics = side_metrics(pe)

    ce_score = (
        ce_metrics["Positive Breadth %"]
        + ce_metrics["Average Positive Movement %"]
        + ce_metrics["Accelerating Count"]
    )

    pe_score = (
        pe_metrics["Positive Breadth %"]
        + pe_metrics["Average Positive Movement %"]
        + pe_metrics["Accelerating Count"]
    )

    if ce_score > pe_score:
        leadership = "CE"

    elif pe_score > ce_score:
        leadership = "PE"

    else:
        leadership = "NEUTRAL"

    previous_ce = (
        previous_metrics.get("CE")
        if isinstance(previous_metrics, dict)
        else None
    )

    previous_pe = (
        previous_metrics.get("PE")
        if isinstance(previous_metrics, dict)
        else None
    )

    ce_state = _classify_field_state(
        ce_metrics,
        previous_ce,
    )

    pe_state = _classify_field_state(
        pe_metrics,
        previous_pe,
    )

    return {
        "CE": ce_metrics,
        "PE": pe_metrics,
        "Leadership": leadership,
        "CE Field State": ce_state,
        "PE Field State": pe_state,
        "CE Research Score": round(ce_score, 2),
        "PE Research Score": round(pe_score, 2),
    }



def _classify_candidate_opportunity_evidence(
    candidate: Dict[str, Any],
) -> Dict[str, Any]:
    """
    V21.2.28.1 — Direction-neutral individual opportunity evidence.

    Research only.

    This function does NOT create a BUY/SELL signal.
    It classifies the current movement behaviour of one
    CE/PE candidate using the existing snapshot evidence.

    The same rules apply to CE and PE.
    """

    movement = candidate.get(
        "Movement Since 9:15 %",
        0.0,
    )

    interval = candidate.get(
        "Interval Movement %",
        0.0,
    )

    acceleration = candidate.get(
        "Acceleration %",
        0.0,
    )

    try:
        movement = float(movement or 0.0)
    except (TypeError, ValueError):
        movement = 0.0

    try:
        interval = float(interval or 0.0)
    except (TypeError, ValueError):
        interval = 0.0

    try:
        acceleration = float(acceleration or 0.0)
    except (TypeError, ValueError):
        acceleration = 0.0

    # The first observation has no previous interval history.
    # This is an observation-state limitation, not negative evidence.
    if (
        interval == 0.0
        and acceleration == 0.0
    ):
        evidence_state = "INITIAL_OBSERVATION"

    elif (
        movement < 0.0
        and interval > 0.0
        and acceleration > 0.0
    ):
        evidence_state = "RECOVERY_ACCELERATION"

    elif interval > 0.0 and acceleration > 0.0:
        evidence_state = "FRESH_ACCELERATION"

    elif interval > 0.0:
        evidence_state = "CONTINUING_UP"

    elif movement > 0.0 and interval < 0.0:
        evidence_state = "ELEVATED_BUT_SLOWING"

    elif interval < 0.0 and acceleration < 0.0:
        evidence_state = "WEAKENING"

    else:
        evidence_state = "NO_POSITIVE_EVIDENCE"

    return {
        "Trading Symbol": candidate.get(
            "Trading Symbol"
        ),
        "Option Type": candidate.get(
            "Option Type"
        ),
        "Strike": candidate.get(
            "Strike"
        ),
        "Expiry": candidate.get(
            "Expiry"
        ),
        "Movement Since 9:15 %": round(
            movement,
            2,
        ),
        "Interval Movement %": round(
            interval,
            2,
        ),
        "Acceleration %": round(
            acceleration,
            2,
        ),
        "Evidence State": evidence_state,
        "Live Order": False,
        "Paper Trade": False,
    }



def _classify_candidate_field_relationship(
    candidate_evidence: Dict[str, Any],
    field_metrics: Dict[str, Any],
    market_leadership: str,
) -> Dict[str, Any]:
    """
    V21.2.28.2 — Candidate ↔ Field relationship.

    Research only.

    This function does NOT create a BUY/SELL signal.
    It contextualizes individual candidate evidence against
    the current CE/PE market field state.

    The same rules apply to CE and PE.
    """

    option_type = candidate_evidence.get(
        "Option Type",
        "",
    )

    evidence_state = candidate_evidence.get(
        "Evidence State",
        "INITIAL_OBSERVATION",
    )

    side_metrics = field_metrics.get(
        option_type,
        {},
    )

    if option_type == "CE":
        field_state = field_metrics.get(
            "CE Field State",
            "NEUTRAL",
        )
    elif option_type == "PE":
        field_state = field_metrics.get(
            "PE Field State",
            "NEUTRAL",
        )
    else:
        field_state = "NEUTRAL"

    positive_breadth = side_metrics.get(
        "Positive Breadth %",
        0.0,
    )

    average_interval = side_metrics.get(
        "Average Interval Movement %",
        0.0,
    )

    positive_interval_breadth = side_metrics.get(
        "Positive Interval Breadth %",
        0.0,
    )

    accelerating_count = side_metrics.get(
        "Accelerating Count",
        0,
    )

    positive_evidence_states = {
        "FRESH_ACCELERATION",
        "CONTINUING_UP",
    }

    accelerating_evidence = (
        evidence_state
        in positive_evidence_states
    )

    recovery_evidence = (
        evidence_state
        == "RECOVERY_ACCELERATION"
    )

    slowing_evidence = (
        evidence_state
        == "ELEVATED_BUT_SLOWING"
    )

    weakening_evidence = (
        evidence_state
        == "WEAKENING"
    )

    field_supportive = (
        field_state
        in {
            "DOMINANT",
            "STRENGTHENING",
        }
    )

    field_emerging = (
        field_state
        == "EMERGING"
    )

    field_weakening = (
        field_state
        in {
            "WEAKENING",
            "WEAKENING_BUT_ELEVATED",
        }
    )

    field_neutral = (
        field_state
        == "NEUTRAL"
    )

    if (
        accelerating_evidence
        and field_supportive
        and market_leadership == option_type
    ):
        relationship = "ALIGNED_WITH_FIELD"

    elif (
        (
            accelerating_evidence
            or recovery_evidence
        )
        and (
            field_supportive
            or field_emerging
        )
    ):
        relationship = "SUPPORTED_BY_FIELD"

    elif (
        (
            accelerating_evidence
            or recovery_evidence
        )
        and (
            field_weakening
            or field_neutral
            or market_leadership != option_type
        )
    ):
        relationship = "EMERGING_AGAINST_FIELD"

    elif (
        (
            slowing_evidence
            or weakening_evidence
        )
        and field_supportive
    ):
        relationship = "CONTRARY_TO_FIELD"

    else:
        relationship = "NEUTRAL_FIELD_CONTEXT"

    return {
        "Trading Symbol": candidate_evidence.get(
            "Trading Symbol"
        ),
        "Option Type": option_type,
        "Strike": candidate_evidence.get(
            "Strike"
        ),
        "Expiry": candidate_evidence.get(
            "Expiry"
        ),
        "Evidence State": evidence_state,
        "Field State": field_state,
        "Market Leadership": market_leadership,
        "Positive Breadth %": round(
            float(positive_breadth or 0.0),
            2,
        ),
        "Positive Interval Breadth %": round(
            float(
                positive_interval_breadth
                or 0.0
            ),
            2,
        ),
        "Average Interval Movement %": round(
            float(average_interval or 0.0),
            2,
        ),
        "Accelerating Count": accelerating_count,
        "Field Relationship": relationship,
        "Live Order": False,
        "Paper Trade": False,
    }


def _classify_candidate_qualification(
    candidate_evidence: Dict[str, Any],
    field_relationship: Dict[str, Any],
) -> Dict[str, Any]:
    """
    V21.2.28.3 — Candidate qualification evidence.

    Research only.

    Qualification means the candidate deserves continued
    observation by the future Opportunity Radar.

    It does NOT create a BUY/SELL signal.
    It does NOT create a paper trade.
    It does NOT rank candidates.

    The same rules apply to CE and PE.
    """

    evidence_state = candidate_evidence.get(
        "Evidence State",
        "INITIAL_OBSERVATION",
    )

    relationship = field_relationship.get(
        "Field Relationship",
        "NEUTRAL_FIELD_CONTEXT",
    )

    if evidence_state == "FRESH_ACCELERATION":
        if relationship in {
            "ALIGNED_WITH_FIELD",
            "SUPPORTED_BY_FIELD",
        }:
            qualification = "QUALIFIED_DEVELOPING"

        elif relationship == "EMERGING_AGAINST_FIELD":
            qualification = "COUNTER_FIELD_WATCH"

        else:
            qualification = "NOT_QUALIFIED"

    elif evidence_state == "CONTINUING_UP":
        if relationship in {
            "ALIGNED_WITH_FIELD",
            "SUPPORTED_BY_FIELD",
        }:
            qualification = "QUALIFIED_CONTINUING"

        elif relationship == "EMERGING_AGAINST_FIELD":
            qualification = "COUNTER_FIELD_WATCH"

        else:
            qualification = "NOT_QUALIFIED"

    elif evidence_state == "RECOVERY_ACCELERATION":
        qualification = "RECOVERY_WATCH"

    elif evidence_state == "ELEVATED_BUT_SLOWING":
        qualification = "EXTENDED_WATCH"

    elif evidence_state == "WEAKENING":
        qualification = "NOT_QUALIFIED"

    elif evidence_state == "INITIAL_OBSERVATION":
        qualification = "INSUFFICIENT_EVIDENCE"

    else:
        qualification = "NOT_QUALIFIED"

    return {
        "Trading Symbol": candidate_evidence.get(
            "Trading Symbol"
        ),
        "Option Type": candidate_evidence.get(
            "Option Type"
        ),
        "Strike": candidate_evidence.get(
            "Strike"
        ),
        "Expiry": candidate_evidence.get(
            "Expiry"
        ),
        "Evidence State": evidence_state,
        "Field Relationship": relationship,
        "Qualification State": qualification,
        "Live Order": False,
        "Paper Trade": False,
    }


def _classify_candidate_rank(
    qualification: Dict[str, Any],
    evidence: Dict[str, Any],
    field_relationship: Dict[str, Any],
    persistence_count: int = 0,
) -> Dict[str, Any]:
    """
    V21.2.29 — Opportunity ranking research.

    Research only.

    Ranking identifies which qualified candidate deserves
    attention first. It does NOT create a BUY/SELL signal.

    No numerical score is used at this stage.
    The same hierarchy applies to CE and PE.
    """

    qualification_state = qualification.get(
        "Qualification State",
        "NOT_QUALIFIED",
    )

    evidence_state = evidence.get(
        "Evidence State",
        "INITIAL_OBSERVATION",
    )

    relationship = field_relationship.get(
        "Field Relationship",
        "NEUTRAL_FIELD_CONTEXT",
    )

    try:
        persistence_count = int(persistence_count)
    except (TypeError, ValueError):
        persistence_count = 0

    movement = evidence.get(
        "Movement Since 9:15 %",
    )

    interval_movement = evidence.get(
        "Interval Movement %",
    )

    acceleration = evidence.get(
        "Acceleration %",
    )

    try:
        movement = float(movement)
    except (TypeError, ValueError):
        movement = 0.0

    try:
        interval_movement = float(interval_movement)
    except (TypeError, ValueError):
        interval_movement = 0.0

    try:
        acceleration = float(acceleration)
    except (TypeError, ValueError):
        acceleration = 0.0

    priority = "NOT_RANKED"
    reason = "Candidate does not currently qualify for opportunity ranking."

    if qualification_state == "QUALIFIED_DEVELOPING":
        priority = "PRIORITY_1_DEVELOPING_LEADER"

        if persistence_count >= 2:
            reason = (
                "Qualified developing candidate with positive "
                "recent evidence and persistent development."
            )
        elif acceleration > 0 and interval_movement > 0:
            reason = (
                "Qualified developing candidate with fresh "
                "positive acceleration and interval movement."
            )
        else:
            reason = (
                "Qualified developing candidate; persistence "
                "or recent-strength evidence is still developing."
            )

    elif qualification_state == "QUALIFIED_CONTINUING":
        priority = "PRIORITY_2_CONTINUING_LEADER"

        if persistence_count >= 2:
            reason = (
                "Qualified continuing candidate with persistent "
                "positive development."
            )
        else:
            reason = (
                "Qualified continuing candidate with ongoing "
                "positive evidence."
            )

    elif qualification_state == "RECOVERY_WATCH":
        priority = "PRIORITY_3_RECOVERY_CANDIDATE"
        reason = (
            "Candidate is recovering with positive interval "
            "movement and acceleration."
        )

    elif qualification_state == "COUNTER_FIELD_WATCH":
        priority = "PRIORITY_4_COUNTER_FIELD_WATCH"

        if relationship == "EMERGING_AGAINST_FIELD":
            reason = (
                "Candidate is developing against the prevailing "
                "field direction; retained for research attention."
            )
        else:
            reason = (
                "Candidate remains a counter-field research watch."
            )

    elif qualification_state == "EXTENDED_WATCH":
        priority = "PRIORITY_5_EXTENDED_CAUTION"
        reason = (
            "Candidate has elevated accumulated movement but "
            "recent evidence is slowing."
        )

    elif qualification_state in {
        "INSUFFICIENT_EVIDENCE",
        "NOT_QUALIFIED",
    }:
        priority = "NOT_RANKED"

    return {
        "Trading Symbol": qualification.get(
            "Trading Symbol"
        ),
        "Option Type": qualification.get(
            "Option Type"
        ),
        "Strike": qualification.get(
            "Strike"
        ),
        "Expiry": qualification.get(
            "Expiry"
        ),
        "Qualification State": qualification_state,
        "Evidence State": evidence_state,
        "Field Relationship": relationship,
        "Persistence Count": persistence_count,
        "Movement Since 9:15 %": movement,
        "Interval Movement %": interval_movement,
        "Acceleration %": acceleration,
        "Priority Tier": priority,
        "Ranking Reason": reason,
        "Live Order": False,
        "Paper Trade": False,
    }


def _calculate_candidate_persistence(
    history: List[Dict[str, Any]],
    trading_symbol: str,
) -> int:
    """
    V21.2.29 — Consecutive positive qualification persistence.

    Counts consecutive observations, working backward from the
    latest observation, in which the candidate remained:

        QUALIFIED_DEVELOPING
        or
        QUALIFIED_CONTINUING

    Any other qualification state breaks persistence.

    Research only.
    """

    positive_states = {
        "QUALIFIED_DEVELOPING",
        "QUALIFIED_CONTINUING",
    }

    count = 0

    for snapshot in reversed(history):

        qualifications = {
            item.get("Trading Symbol"): item
            for item in snapshot.get(
                "Candidate Qualifications",
                [],
            )
        }

        qualification = qualifications.get(
            trading_symbol
        )

        if not qualification:
            break

        state = qualification.get(
            "Qualification State",
            "NOT_QUALIFIED",
        )

        if state not in positive_states:
            break

        count += 1

    return count


def _build_snapshot(
    universe: List[Dict[str, Any]],
    prices: Dict[str, float],
    baseline: Optional[Dict[str, Any]],
    previous_prices: Dict[str, float],
    previous_intervals: Dict[str, float],
    previous_metrics: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:

    records: List[Dict[str, Any]] = []

    for instrument in universe:

        symbol = instrument.get("tradingsymbol")

        if not symbol:
            continue

        key = f"NFO:{symbol}"

        current_price = prices.get(key)

        if current_price is None:
            current_price = prices.get(symbol)

        if current_price is None:
            continue

        try:
            current_price = float(current_price)
        except (TypeError, ValueError):
            continue

        if current_price <= 0:
            continue

        baseline_price = _baseline_price_for_symbol(
            baseline,
            symbol,
        )

        movement_915 = _percentage_change(
            baseline_price,
            current_price,
        )

        previous_price = previous_prices.get(symbol)

        interval_movement = _percentage_change(
            previous_price,
            current_price,
        )

        if interval_movement is None:
            interval_movement = 0.0

        previous_interval = previous_intervals.get(
            symbol,
            0.0,
        )

        acceleration = (
            interval_movement
            - previous_interval
        )

        records.append(
            {
                "Trading Symbol": symbol,
                "Option Type": instrument.get(
                    "instrument_type"
                ),
                "Strike": float(
                    instrument.get("strike", 0)
                ),
                "Expiry": instrument.get("expiry"),
                "9:15 Price": baseline_price,
                "Current Price": round(
                    current_price,
                    4,
                ),
                "Movement Since 9:15 %": (
                    round(movement_915, 2)
                    if movement_915 is not None
                    else None
                ),
                "Interval Movement %": round(
                    interval_movement,
                    2,
                ),
                "Acceleration %": round(
                    acceleration,
                    2,
                ),
                "Timestamp": _now_ist(),
                "Live Order": False,
                "Paper Trade": False,
            }
        )

    metrics = _calculate_field_metrics(
        records,
        previous_metrics,
    )

    opportunity_evidence = [
        _classify_candidate_opportunity_evidence(
            candidate
        )
        for candidate in records
    ]

    field_relationships = [
        _classify_candidate_field_relationship(
            evidence,
            metrics,
            metrics.get("Leadership", "NEUTRAL"),
        )
        for evidence in opportunity_evidence
    ]

    candidate_qualifications = [
        _classify_candidate_qualification(
            evidence,
            relationship,
        )
        for evidence, relationship in zip(
            opportunity_evidence,
            field_relationships,
        )
    ]

    return {
        "Timestamp": _now_ist(),
        "Candidates": records,
        "Field Metrics": metrics,
        "Opportunity Evidence": opportunity_evidence,
        "Field Relationships": field_relationships,
        "Candidate Qualifications": candidate_qualifications,
        "Live Order": False,
        "Paper Trade": False,
    }


def run_market_field_replay(
    kite,
    observation_count: int = DEFAULT_OBSERVATION_COUNT,
    interval_seconds: int = DEFAULT_INTERVAL_SECONDS,
    expiry_count: int = DEFAULT_EXPIRY_COUNT,
    strikes_each_side: int = DEFAULT_STRIKES_EACH_SIDE,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> Dict[str, Any]:
    """
    Run continuous broad CE/PE market-field observation.

    Research only.
    """

    print("=" * 70)
    print("JKJ AI TRADER V21.2.27")
    print("CONTINUOUS CE/PE MARKET FIELD REPLAY")
    print("=" * 70)

    baseline = load_today_baseline()

    baseline_available = (
        baseline is not None
        and baseline.get("Baseline Type") == "GENUINE_915"
    )

    if baseline_available:
        print("09:15 baseline: AVAILABLE")
    else:
        print("09:15 baseline: NOT AVAILABLE")
        print(
            "Movement Since 9:15 will remain unavailable."
        )

    nifty_spot = _get_nifty_spot(kite)

    instruments = kite.instruments("NFO")

    expiries = _get_near_term_expiries(
        instruments,
        expiry_count,
    )

    universe = _build_multi_expiry_universe(
        instruments,
        nifty_spot,
        expiries,
        strikes_each_side,
    )

    print()
    print(f"NIFTY Spot: {nifty_spot}")
    print(f"Expiries: {len(expiries)}")
    print(f"Observation Universe: {len(universe)} contracts")
    print(f"Observations: {observation_count}")
    print(f"Interval: {interval_seconds}s")

    previous_prices: Dict[str, float] = {}
    previous_intervals: Dict[str, float] = {}
    previous_metrics: Optional[Dict[str, Any]] = None

    history: List[Dict[str, Any]] = []
    leadership_history: List[str] = []

    for observation_number in range(
        1,
        observation_count + 1,
    ):

        prices = _ltp_batch(
            kite,
            universe,
            batch_size,
        )

        snapshot = _build_snapshot(
            universe,
            prices,
            baseline,
            previous_prices,
            previous_intervals,
            previous_metrics,
        )

        snapshot["Observation Number"] = observation_number

        history.append(snapshot)

        opportunity_rankings = []

        evidence_by_symbol = {
            item.get("Trading Symbol"): item
            for item in snapshot.get(
                "Opportunity Evidence",
                [],
            )
        }

        relationship_by_symbol = {
            item.get("Trading Symbol"): item
            for item in snapshot.get(
                "Field Relationships",
                [],
            )
        }

        qualification_by_symbol = {
            item.get("Trading Symbol"): item
            for item in snapshot.get(
                "Candidate Qualifications",
                [],
            )
        }

        for symbol, qualification in (
            qualification_by_symbol.items()
        ):
            evidence = evidence_by_symbol.get(
                symbol,
                {},
            )

            relationship = relationship_by_symbol.get(
                symbol,
                {},
            )

            persistence_count = (
                _calculate_candidate_persistence(
                    history,
                    symbol,
                )
            )

            ranking = _classify_candidate_rank(
                qualification,
                evidence,
                relationship,
                persistence_count,
            )

            opportunity_rankings.append(ranking)

        snapshot["Opportunity Rankings"] = (
            opportunity_rankings
        )

        metrics = snapshot["Field Metrics"]

        leadership = metrics["Leadership"]

        leadership_history.append(leadership)

        previous_metrics = metrics

        ce = metrics["CE"]
        pe = metrics["PE"]

        print()
        print(
            f"Observation "
            f"{observation_number}/{observation_count}"
        )

        print(
            f"  CE | "
            f"Breadth={ce['Positive Breadth %']:.2f}% | "
            f"Avg+={ce['Average Positive Movement %']:.2f}% | "
            f"Accel={ce['Accelerating Count']} | "
            f"Leader={ce['Strongest']}"
        )

        print(
            f"  PE | "
            f"Breadth={pe['Positive Breadth %']:.2f}% | "
            f"Avg+={pe['Average Positive Movement %']:.2f}% | "
            f"Accel={pe['Accelerating Count']} | "
            f"Leader={pe['Strongest']}"
        )

        print(
            "  CE Field State: "
            f"{metrics.get('CE Field State', 'NEUTRAL')} | "
            f"Breadth={ce['Positive Breadth %']:.2f}% | "
            f"Avg+={ce['Average Positive Movement %']:.2f}% | "
            f"Interval Breadth={ce['Positive Interval Breadth %']:.2f}% | "
            f"Avg Interval={ce['Average Interval Movement %']:.2f}% | "
            f"Accel={ce['Accelerating Count']}"
        )

        print(
            "  PE Field State: "
            f"{metrics.get('PE Field State', 'NEUTRAL')} | "
            f"Breadth={pe['Positive Breadth %']:.2f}% | "
            f"Avg+={pe['Average Positive Movement %']:.2f}% | "
            f"Interval Breadth={pe['Positive Interval Breadth %']:.2f}% | "
            f"Avg Interval={pe['Average Interval Movement %']:.2f}% | "
            f"Accel={pe['Accelerating Count']}"
        )

        print(
            f"  Market Leadership: {leadership}"
        )

        relationship_counts = {}
        ce_relationship_counts = {}
        pe_relationship_counts = {}

        for relationship in snapshot.get(
            "Field Relationships",
            []
        ):
            state = relationship.get(
                "Field Relationship",
                "NEUTRAL_FIELD_CONTEXT",
            )

            option_type = relationship.get(
                "Option Type",
                "UNKNOWN",
            )

            relationship_counts[state] = (
                relationship_counts.get(state, 0)
                + 1
            )

            if option_type == "CE":
                ce_relationship_counts[state] = (
                    ce_relationship_counts.get(
                        state,
                        0,
                    )
                    + 1
                )

            elif option_type == "PE":
                pe_relationship_counts[state] = (
                    pe_relationship_counts.get(
                        state,
                        0,
                    )
                    + 1
                )

        print(
            "  Candidate ↔ Field Relationships: "
            + " | ".join(
                f"{state}={count}"
                for state, count
                in sorted(
                    relationship_counts.items()
                )
            )
        )

        print(
            "  CE Relationships: "
            + " | ".join(
                f"{state}={count}"
                for state, count
                in sorted(
                    ce_relationship_counts.items()
                )
            )
        )

        print(
            "  PE Relationships: "
            + " | ".join(
                f"{state}={count}"
                for state, count
                in sorted(
                    pe_relationship_counts.items()
                )
            )
        )

        qualification_counts = {}

        for qualification in snapshot.get(
            "Candidate Qualifications",
            []
        ):
            state = qualification.get(
                "Qualification State",
                "UNKNOWN",
            )

            qualification_counts[state] = (
                qualification_counts.get(state, 0)
                + 1
            )

        print(
            "  Candidate Qualification Summary: "
            + " | ".join(
                f"{state}={count}"
                for state, count
                in sorted(
                    qualification_counts.items()
                )
            )
        )

        ranked_candidates = [
            item
            for item in snapshot.get(
                "Opportunity Rankings",
                [],
            )
            if item.get("Priority Tier")
            != "NOT_RANKED"
        ]

        priority_order = {
            "PRIORITY_1_DEVELOPING_LEADER": 1,
            "PRIORITY_2_CONTINUING_LEADER": 2,
            "PRIORITY_3_RECOVERY_CANDIDATE": 3,
            "PRIORITY_4_COUNTER_FIELD_WATCH": 4,
            "PRIORITY_5_EXTENDED_CAUTION": 5,
        }

        ranked_candidates.sort(
            key=lambda item: (
                priority_order.get(
                    item.get("Priority Tier"),
                    99,
                ),
                -item.get(
                    "Persistence Count",
                    0,
                ),
                -item.get(
                    "Acceleration %",
                    0.0,
                ),
                -item.get(
                    "Interval Movement %",
                    0.0,
                ),
            )
        )

        print(
            "  Opportunity Ranking — Top 5:"
        )

        for item in ranked_candidates[:5]:
            print(
                "    "
                f"{item.get('Priority Tier')} | "
                f"{item.get('Trading Symbol')} | "
                f"{item.get('Option Type')} | "
                f"Persistence="
                f"{item.get('Persistence Count', 0)} | "
                f"Accel="
                f"{item.get('Acceleration %', 0.0):.2f}% | "
                f"Interval="
                f"{item.get('Interval Movement %', 0.0):.2f}%"
            )

        current_intervals = {}

        for item in snapshot["Candidates"]:

            symbol = item["Trading Symbol"]

            previous_prices[symbol] = item[
                "Current Price"
            ]

            current_intervals[symbol] = item[
                "Interval Movement %"
            ]

        previous_intervals = current_intervals

        if observation_number < observation_count:
            time.sleep(interval_seconds)

    rotations = []

    previous_leader = None

    for index, leader in enumerate(
        leadership_history
    ):

        if previous_leader is not None:
            if (
                leader != previous_leader
                and leader != "NEUTRAL"
                and previous_leader != "NEUTRAL"
            ):
                rotations.append(
                    {
                        "Observation Number": index + 1,
                        "From": previous_leader,
                        "To": leader,
                        "Timestamp": history[index][
                            "Timestamp"
                        ],
                    }
                )

        if leader != "NEUTRAL":
            previous_leader = leader

    print()
    print("=" * 70)
    print("V21.2.27 MARKET FIELD REPLAY COMPLETE")
    print("=" * 70)
    print(
        f"Contracts Observed: {len(universe)}"
    )
    print(
        f"Observations: {len(history)}"
    )
    print(
        f"Leadership Changes: {len(rotations)}"
    )
    print("Live Order: False")
    print("Paper Trade: False")

    return {
        "Status":
            "MARKET_FIELD_REPLAY_COMPLETE",
        "NIFTY Spot": nifty_spot,
        "Expiries":
            [str(item) for item in expiries],
        "Universe Count": len(universe),
        "Observation Count": len(history),
        "Baseline Available":
            baseline_available,
        "Observation History": history,
        "Leadership History":
            leadership_history,
        "Rotation Events": rotations,
        "Live Order": False,
        "Paper Trade": False,
    }


if __name__ == "__main__":

    from modules.jkj_daily_zerodha_auth import (
        authenticate_today,
    )

    session_result = authenticate_today()

    kite = session_result.get("Kite")

    if kite is None:
        print("Kite session unavailable")
        raise SystemExit(1)

    run_market_field_replay(kite)
