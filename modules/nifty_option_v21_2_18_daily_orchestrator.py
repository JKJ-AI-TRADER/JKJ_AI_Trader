"""
JKJ AI Trader
V21.2.18 Daily Orchestrator

Flow:
09:00–09:15  -> V21.2 pre-market preparation
09:14:30–09:16 -> Genuine 09:15 baseline capture
After baseline -> V21.2.18 early-surge observation

Safety:
- No live orders
- No paper trades
- Does not modify V21.2.0–V21.2.17 modules
- Never creates a synthetic baseline
"""

from datetime import datetime, time
from zoneinfo import ZoneInfo
from typing import Any, Dict, Optional

from modules.nifty_option_v21_2_pre_market_controller import (
    evaluate_pre_market_controller,
    get_market_session_state,
)
from modules.nifty_option_v21_2_18_baseline import capture_915_baseline
from modules.nifty_option_v21_2_18_baseline_store import (
    load_today_baseline,
    save_baseline,
)
from modules.nifty_option_v21_2_18_early_surge_scanner import (
    run_early_surge_session,
)
from modules.intraday_zerodha_session_manager import get_kite_session


def _get_kite() -> Dict[str, Any]:
    """
    Obtain the existing Zerodha session.

    The existing session manager is reused.
    No new authentication flow is created here.
    """
    session = get_kite_session()

    if not session:
        return {
            "Status": "SESSION_NOT_AVAILABLE",
            "Reason": "No Zerodha session returned",
        }

    kite = session.get("Kite")

    if kite is None:
        return {
            "Status": "SESSION_NOT_AVAILABLE",
            "Reason": "Kite object missing from session",
        }

    return {
        "Status": "SESSION_READY",
        "Kite": kite,
        "Session": session,
    }


def run_v21_2_18_daily_orchestrator(
    current_time: Optional[datetime] = None,
    contracts_per_side: int = 2,
    strikes_each_side: int = 10,
    window_seconds: int = 60,
    interval_seconds: int = 15,
) -> Dict[str, Any]:
    """
    Run one controlled V21.2.18 daily-orchestration step.

    The function is intentionally non-blocking with respect to the
    market-session stages:

    1. Pre-market preparation
    2. 09:15 baseline capture when inside the protected window
    3. Early-surge observation after a valid baseline exists

    It does not place live orders or paper trades.
    """

    now = current_time or datetime.now(ZoneInfo("Asia/Kolkata"))

    result: Dict[str, Any] = {
        "Status": "ORCHESTRATOR_STARTED",
        "Current Time": now.isoformat(),
        "Live Order": False,
        "Paper Trade": False,
    }

    # ---------------------------------------------------------
    # 1. Determine the current market-session stage
    # ---------------------------------------------------------
    session_state_result = get_market_session_state(
        current_time=now,
    )

    result["Market Session Result"] = session_state_result

    session_state = session_state_result.get("Session State")

    # ---------------------------------------------------------
    # 3. Protect the genuine 09:15 baseline capture window.
    #    Never start pre-market network preparation inside it.
    # ---------------------------------------------------------
    ist = ZoneInfo("Asia/Kolkata")
    current_clock = now.astimezone(ist).time()
    baseline_window_start = time(9, 14, 30)
    baseline_window_end = time(9, 16, 0)
    inside_baseline_window = (
        baseline_window_start <= current_clock <= baseline_window_end
    )

    if session_state == "PRE_MARKET" and inside_baseline_window:
        pre_market_status = "CAPTURE_WINDOW_PRIORITY"

    elif session_state == "PRE_MARKET":
        pre_market_result = evaluate_pre_market_controller(
            current_time=now,
            contracts_per_side=contracts_per_side,
        )

        result["Pre-Market Result"] = pre_market_result
        pre_market_status = pre_market_result.get("Status")

        if pre_market_status != "PRE_MARKET_READY":
            result["Status"] = "WAITING_FOR_PRE_MARKET"
            result["Reason"] = (
                f"Pre-market controller returned {pre_market_status}"
            )
            return result

    elif session_state == "BEFORE_PRE_MARKET":
        result["Status"] = "WAITING_FOR_MARKET_STAGE"
        result["Reason"] = "Before 09:00 pre-market preparation."
        return result

    elif session_state == "MARKET_CLOSED":
        result["Status"] = "MARKET_CLOSED"
        result["Reason"] = "Market session has ended."
        return result

    elif session_state == "MARKET_SESSION":
        pre_market_status = "MARKET_SESSION"

    else:
        result["Status"] = "WAITING_FOR_MARKET_STAGE"
        result["Reason"] = (
            f"Unknown market session state: {session_state}"
        )
        return result

    # ---------------------------------------------------------
    # 4. Continue to the existing genuine-baseline checks.
    # ---------------------------------------------------------

    # ---------------------------------------------------------
    # 4. Genuine 09:15 baseline
    # ---------------------------------------------------------
    baseline = load_today_baseline()

    if baseline is not None:
        result["Baseline Status"] = "AVAILABLE"
        result["Baseline Source"] = "STORED_GENUINE_915"

    else:
        # Only attempt a real baseline capture during the
        # protected 09:14:30–09:16:00 capture window.
        current_clock = now.astimezone(ist).time()

        baseline_window_start = time(9, 14, 30)
        baseline_window_end = time(9, 16, 0)

        inside_baseline_window = (
            baseline_window_start <= current_clock <= baseline_window_end
        )

        if not inside_baseline_window:
            result["Baseline Status"] = "NOT_AVAILABLE"

            if pre_market_status == "PRE_MARKET_READY":
                result["Status"] = "WAITING_FOR_915_BASELINE"
                result["Reason"] = (
                    "Waiting for the protected 09:15 baseline "
                    "capture window."
                )
            else:
                result["Status"] = "BASELINE_REQUIRED"
                result["Reason"] = (
                    "No genuine 09:15 baseline is available today."
                )

            return result

        # We are now inside the protected capture window.
        session_result = _get_kite()

        if session_result["Status"] != "SESSION_READY":
            result.update({
                "Status": "SESSION_NOT_READY",
                "Reason": session_result["Reason"],
            })
            return result

        kite = session_result["Kite"]
        result["Session Status"] = "SESSION_READY"

        baseline_capture = capture_915_baseline(
            kite,
            strikes_each_side=strikes_each_side,
        )

        result["Baseline Capture Result"] = baseline_capture

        if baseline_capture.get("Status") == "BASELINE_CAPTURE_COMPLETE":
            save_result = save_baseline(baseline_capture)
            result["Baseline Save Result"] = save_result

            if save_result.get("Status") == "BASELINE_SAVED":
                baseline = load_today_baseline()

        if baseline is None:
            result["Baseline Status"] = "NOT_AVAILABLE"
            result["Status"] = "BASELINE_CAPTURE_NOT_CONFIRMED"
            result["Reason"] = (
                "A genuine 09:15 baseline was not successfully "
                "captured and verified."
            )
            return result

    # ---------------------------------------------------------
    # 5. Early-surge observation
    # ---------------------------------------------------------
    if pre_market_status != "MARKET_SESSION":
        result["Status"] = "BASELINE_READY_WAITING_FOR_MARKET_SESSION"
        result["Reason"] = (
            "Baseline is available. Early-surge observation begins "
            "during the market session."
        )
        return result

    # Obtain the existing Zerodha session only when
    # early-surge market observation is actually required.
    session_result = _get_kite()

    if session_result["Status"] != "SESSION_READY":
        result.update({
            "Status": "SESSION_NOT_READY",
            "Reason": session_result["Reason"],
        })
        return result

    kite = session_result["Kite"]
    result["Session Status"] = "SESSION_READY"

    surge_result = run_early_surge_session(
        kite,
        window_seconds=window_seconds,
        interval_seconds=interval_seconds,
        strikes_each_side=strikes_each_side,
    )

    result["Early Surge Result"] = surge_result

    # ---------------------------------------------------------
    # 6. Final safety state
    # ---------------------------------------------------------
    result["Status"] = "V21_2_18_ORCHESTRATION_COMPLETE"
    result["Live Order"] = False
    result["Paper Trade"] = False

    return result


if __name__ == "__main__":
    result = run_v21_2_18_daily_orchestrator()

    print("\n=== JKJ V21.2.18 DAILY ORCHESTRATOR ===")
    print("Status:", result.get("Status"))
    print("Current Time:", result.get("Current Time"))
    print("Session Status:", result.get("Session Status"))
    print("Baseline Status:", result.get("Baseline Status"))
    print("Live Order:", result.get("Live Order"))
    print("Paper Trade:", result.get("Paper Trade"))
