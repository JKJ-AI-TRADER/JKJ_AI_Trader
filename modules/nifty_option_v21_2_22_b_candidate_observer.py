"""
JKJ AI Trader
V21.2.22-B — Continuous Candidate Observation Orchestrator

Purpose:
    Orchestrate repeated observation + candidate qualification cycles
    during the intraday market session.

Architecture:
    V21.2.22-A
        ↓
    V21.2.19 Persistent Observer
        ↓
    V21.2.20 Candidate Qualification

Safety:
    - Observation only
    - NO live orders
    - NO paper trades
    - NO BUY
    - NO SELL
    - NO position sizing
    - Does not modify V21.2.18–V21.2.21
"""

from __future__ import annotations

import time as time_module
from datetime import datetime
from typing import Any, Dict
from zoneinfo import ZoneInfo

from modules.intraday_zerodha_session_manager import get_kite_session

from modules.nifty_option_v21_2_market_session import (
    get_market_session_state,
)

from modules.nifty_option_v21_2_19_persistent_observer import (
    run_persistent_observer,
)

from modules.nifty_option_v21_2_20_candidate_qualification import (
    qualify_candidates,
)


LIVE_ORDER = False
PAPER_TRADE = False

IST = ZoneInfo("Asia/Kolkata")


def _now_ist() -> datetime:
    return datetime.now(IST)


def run_v21_2_22_b(
    interval_seconds: int = 15,
    observations_per_cycle: int = 4,
    strikes_each_side: int = 10,
    max_cycles: int = 1,
    cycle_gap_seconds: int = 5,
    current_time: datetime | None = None,
) -> Dict[str, Any]:
    """
    Run repeated observation + candidate qualification cycles.

    max_cycles defaults to 1 for safe validation.

    This version does not execute any BUY/SELL action.
    """

    now = current_time or _now_ist()

    if now.tzinfo is None:
        now = now.replace(tzinfo=IST)

    print()
    print("=" * 78)
    print("JKJ AI TRADER — V21.2.22-B CANDIDATE OBSERVATION ORCHESTRATOR")
    print("=" * 78)
    print(f"Current IST: {now.isoformat()}")
    print(f"Live Order: {LIVE_ORDER}")
    print(f"Paper Trade: {PAPER_TRADE}")

    # ------------------------------------------------------------
    # STEP 1 — Zerodha session
    # ------------------------------------------------------------
    print()
    print("STEP 1 — Zerodha session validation")

    session_result = get_kite_session()

    if not isinstance(session_result, dict):
        return {
            "Status": "SESSION_VALIDATION_FAILED",
            "Reason": "Invalid session result.",
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    kite = session_result.get("Kite")

    if kite is None:
        return {
            "Status": "SESSION_VALIDATION_FAILED",
            "Reason": "Kite session unavailable.",
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    print("Session: READY")

    # ------------------------------------------------------------
    # STEP 2 — Market session
    # ------------------------------------------------------------
    print()
    print("STEP 2 — Market session check")

    market_result = get_market_session_state(current_time=now)

    if not isinstance(market_result, dict):
        return {
            "Status": "MARKET_SESSION_CHECK_FAILED",
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    session_state = market_result.get("Session State")

    print(f"Market Session: {session_state}")

    if session_state != "MARKET_SESSION":
        print("Candidate observer is not active.")

        return {
            "Status": "CANDIDATE_OBSERVER_NOT_ACTIVE",
            "Market Session": session_state,
            "Current IST": now.isoformat(),
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
            "Execution Performed": False,
        }

    # ------------------------------------------------------------
    # STEP 3 — Observation / qualification cycles
    # ------------------------------------------------------------
    print()
    print("STEP 3 — Continuous candidate observation")

    cycle_results = []

    for cycle_number in range(1, max_cycles + 1):

        cycle_now = _now_ist()

        # Re-check market session before every cycle.
        cycle_session = get_market_session_state(
            current_time=cycle_now
        )

        cycle_state = cycle_session.get("Session State")

        print()
        print("-" * 78)
        print(f"CYCLE {cycle_number}/{max_cycles}")
        print(f"Cycle IST: {cycle_now.isoformat()}")
        print(f"Market Session: {cycle_state}")
        print("-" * 78)

        if cycle_state != "MARKET_SESSION":
            print("Market session ended. Stopping candidate observation.")

            break

        # --------------------------------------------------------
        # V21.2.19 persistent observation
        # --------------------------------------------------------
        observer_result = run_persistent_observer(
            kite=kite,
            interval_seconds=interval_seconds,
            max_observations=observations_per_cycle,
            strikes_each_side=strikes_each_side,
        )

        if not isinstance(observer_result, dict):
            print("Observer returned an invalid result.")
            continue

        observer_status = observer_result.get("Status")

        print()
        print(f"Observer Status: {observer_status}")

        if observer_status != "PERSISTENT_OBSERVER_COMPLETE":
            print("Observation cycle did not complete.")
            continue

        # --------------------------------------------------------
        # V21.2.20 candidate qualification
        # --------------------------------------------------------
        lifecycle_store = observer_result.get("Candidate Lifecycle")

        if not isinstance(lifecycle_store, dict):
            print("Candidate lifecycle store unavailable.")
            continue

        qualification_result = qualify_candidates(
            lifecycle_store
        )

        if not isinstance(qualification_result, dict):
            print("Qualification returned an invalid result.")
            continue

        qualification_status = qualification_result.get("Status")

        qualified_count = qualification_result.get(
            "Qualified Candidate Count",
            0,
        )

        observed_count = qualification_result.get(
            "Observed Candidate Count",
            0,
        )

        print()
        print(f"Qualification Status: {qualification_status}")
        print(f"Observed Candidates: {observed_count}")
        print(f"Qualified Candidates: {qualified_count}")

        cycle_results.append(
            {
                "Cycle": cycle_number,
                "Cycle Time": cycle_now.isoformat(),
                "Observer Status": observer_status,
                "Qualification Status": qualification_status,
                "Observed Candidate Count": observed_count,
                "Qualified Candidate Count": qualified_count,
                "Qualification Result": qualification_result,
            }
        )

        # --------------------------------------------------------
        # Safety: never execute here
        # --------------------------------------------------------
        print("Execution: DISABLED")

        if cycle_number < max_cycles and cycle_gap_seconds > 0:
            print(
                f"Waiting {cycle_gap_seconds} seconds "
                "before next observation cycle..."
            )
            time_module.sleep(cycle_gap_seconds)

    # ------------------------------------------------------------
    # FINAL RESULT
    # ------------------------------------------------------------
    print()
    print("=" * 78)
    print("V21.2.22-B CANDIDATE OBSERVATION COMPLETE")
    print("=" * 78)
    print(f"Cycles Completed: {len(cycle_results)}")
    print(f"Live Order: {LIVE_ORDER}")
    print(f"Paper Trade: {PAPER_TRADE}")
    print("Execution Performed: False")

    return {
        "Status": "V21_2_22_B_CANDIDATE_OBSERVATION_COMPLETE",
        "Cycles Completed": len(cycle_results),
        "Cycle Results": cycle_results,
        "Live Order": LIVE_ORDER,
        "Paper Trade": PAPER_TRADE,
        "Execution Performed": False,
    }


if __name__ == "__main__":
    result = run_v21_2_22_b()

    print()
    print("FINAL STATUS:", result.get("Status"))
    print("CYCLES:", result.get("Cycles Completed"))
    print("LIVE ORDER:", result.get("Live Order"))
    print("PAPER TRADE:", result.get("Paper Trade"))
    print("EXECUTION:", result.get("Execution Performed"))
