"""
JKJ AI Trader
V21.2.22-A — Continuous Intraday Orchestrator

Purpose:
    Provide the session-level orchestration layer for the JKJ
    intraday observation workflow.

Safety:
    - Observation / orchestration only
    - NO live orders
    - NO paper trades
    - NO automatic BUY
    - NO automatic SELL
    - NO position sizing

This first version deliberately focuses on:
    - Asia/Kolkata session control
    - Zerodha session validation
    - market-session boundaries
    - genuine 09:15 baseline awareness
    - late-start / intraday-development mode

The existing V21.2.18–V21.2.21 modules are not modified.
"""

from __future__ import annotations

from datetime import datetime, time
from typing import Any, Dict
from zoneinfo import ZoneInfo

from modules.intraday_zerodha_session_manager import (
    get_kite_session,
)

from modules.nifty_option_v21_2_market_session import (
    get_market_session_state,
)


LIVE_ORDER = False
PAPER_TRADE = False

IST = ZoneInfo("Asia/Kolkata")

MARKET_OPEN = time(9, 15)
MARKET_CLOSE = time(15, 30)


def _now_ist() -> datetime:
    """Return current timezone-aware India time."""
    return datetime.now(IST)


def _time_mode(current_time: datetime) -> str:
    """
    Determine the intraday operating mode.

    No synthetic baseline is created here.
    """

    current = current_time.timetz().replace(tzinfo=None)

    if current < MARKET_OPEN:
        return "WAITING_FOR_0915_BASELINE"

    if current < MARKET_CLOSE:
        return "INTRADAY_DEVELOPMENT_MODE"

    return "MARKET_CLOSED"


def run_v21_2_22_a(
    current_time: datetime | None = None,
) -> Dict[str, Any]:
    """
    Run V21.2.22-A session/orchestration safety checks.

    This version deliberately does NOT start the persistent observer.
    It establishes the safe controller boundary first.
    """

    now = current_time or _now_ist()

    # Ensure supplied test times are timezone-aware and interpreted
    # explicitly as India time.
    if now.tzinfo is None:
        now = now.replace(tzinfo=IST)

    print()
    print("=" * 75)
    print("JKJ AI TRADER — V21.2.22-A INTRADAY ORCHESTRATOR")
    print("=" * 75)

    print("Current IST:", now.isoformat())
    print("Live Order:", LIVE_ORDER)
    print("Paper Trade:", PAPER_TRADE)

    # ---------------------------------------------------------
    # 1. Zerodha session
    # ---------------------------------------------------------

    print()
    print("STEP 1 — Zerodha session validation")

    session_result = get_kite_session()

    if not isinstance(session_result, dict):
        return {
            "Status": "SESSION_RESULT_INVALID",
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    kite = session_result.get("Kite")

    if kite is None:
        return {
            "Status": "SESSION_NOT_READY",
            "Session Result": session_result,
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    print("Session: READY")

    # ---------------------------------------------------------
    # 2. Market session
    # ---------------------------------------------------------

    print()
    print("STEP 2 — Market session check")

    market_result = get_market_session_state(
        current_time=now,
    )

    if not isinstance(market_result, dict):
        return {
            "Status": "MARKET_SESSION_RESULT_INVALID",
            "Market Session Result": market_result,
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    session_state = market_result.get("Session State")

    print("Market Session:", session_state)

    # ---------------------------------------------------------
    # 3. Controller mode
    # ---------------------------------------------------------

    controller_mode = _time_mode(now)

    print("Controller Mode:", controller_mode)

    if session_state in {
        "BEFORE_PRE_MARKET",
        "PRE_MARKET",
        "MARKET_CLOSED",
    }:
        return {
            "Status": "CONTROLLER_NOT_ACTIVE",
            "Market Session": session_state,
            "Controller Mode": controller_mode,
            "Current IST": now.isoformat(),
            "Kite Ready": True,
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    # ---------------------------------------------------------
    # 4. Active intraday boundary
    # ---------------------------------------------------------

    return {
        "Status": "V21_2_22_A_CONTROLLER_READY",
        "Market Session": session_state,
        "Controller Mode": controller_mode,
        "Current IST": now.isoformat(),
        "Kite Ready": True,
        "Baseline Policy": "GENUINE_915_ONLY",
        "Late Start Policy": "INTRADAY_DEVELOPMENT_MODE",
        "Live Order": LIVE_ORDER,
        "Paper Trade": PAPER_TRADE,
        "Execution Performed": False,
    }


if __name__ == "__main__":

    result = run_v21_2_22_a()

    print()
    print("FINAL STATUS:", result.get("Status"))
    print("Controller Mode:", result.get("Controller Mode"))
    print("Live Order:", result.get("Live Order"))
    print("Paper Trade:", result.get("Paper Trade"))
