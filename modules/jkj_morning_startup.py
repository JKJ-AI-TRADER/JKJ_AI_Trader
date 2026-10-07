"""
JKJ AI Trader - Morning Startup
--------------------------------
Safe daily startup and connectivity verification.

Purpose:
- Prepare the JKJ environment from 07:00 onward.
- Reuse today's Zerodha session when available.
- Never automate Zerodha login.
- Verify read-only access to Kite, NIFTY and NFO.
- Do not place orders.
- Do not create paper trades.
- Do not make trading decisions.
"""

from datetime import datetime, time
from zoneinfo import ZoneInfo
from modules.intraday_zerodha_session_manager import get_kite_session


STARTUP_TIME = time(7, 0)
PRE_MARKET_TIME = time(9, 0)
MARKET_OPEN_TIME = time(9, 15)
MARKET_CLOSE_TIME = time(15, 30)


def _get_kite():
    """Reuse the existing daily Zerodha session."""
    session = get_kite_session()

    if not isinstance(session, dict):
        return {
            "Status": "SESSION_ERROR",
            "Reason": "Unexpected Zerodha session response.",
        }

    kite = session.get("Kite")

    if kite is None:
        return {
            "Status": session.get("Status", "SESSION_NOT_AVAILABLE"),
            "Reason": "Today's Zerodha session is not available.",
        }

    return {
        "Status": "SESSION_READY",
        "Kite": kite,
        "Session": session,
    }


def _verify_nifty(kite):
    """Read-only NIFTY verification."""
    try:
        quote = kite.ltp("NSE:NIFTY 50")

        if not quote:
            return {
                "Status": "NIFTY_NOT_AVAILABLE",
                "Reason": "No NIFTY quote returned.",
            }

        return {
            "Status": "NIFTY_READY",
            "NIFTY Spot": quote["NSE:NIFTY 50"]["last_price"],
        }

    except Exception as exc:
        return {
            "Status": "NIFTY_ERROR",
            "Reason": str(exc),
        }


def _verify_nfo(kite):
    """Read-only NFO instrument verification."""
    try:
        instruments = kite.instruments("NFO")

        if not instruments:
            return {
                "Status": "NFO_NOT_AVAILABLE",
                "Reason": "No NFO instruments returned.",
            }

        return {
            "Status": "NFO_READY",
            "NFO Instruments": len(instruments),
        }

    except Exception as exc:
        return {
            "Status": "NFO_ERROR",
            "Reason": str(exc),
        }


def run_morning_startup(current_time=None):
    """
    Run the safe JKJ morning startup check.

    current_time may be supplied for testing.
    """

    now = current_time or datetime.now(ZoneInfo("Asia/Kolkata"))

    current_clock = now.time()

    result = {
        "Status": "STARTUP_CHECK",
        "Current Time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "Live Trading": False,
        "Paper Trading": False,
        "Order Placement Permitted": False,
    }

    # Before 07:00
    if current_clock < STARTUP_TIME:
        result["Status"] = "WAITING_FOR_STARTUP"
        result["Reason"] = "JKJ morning startup begins at 07:00."
        return result

    # After market close
    if current_clock >= MARKET_CLOSE_TIME:
        result["Status"] = "DAY_CLOSED"
        result["Reason"] = "Today's market session is closed."
        return result

    # Zerodha session check
    session_result = _get_kite()

    result["Zerodha Session"] = session_result["Status"]

    if session_result["Status"] != "SESSION_READY":
        result["Status"] = "AUTHENTICATION_REQUIRED"
        result["Reason"] = (
            "Today's Zerodha session is not available. "
            "Manual Zerodha authentication is required."
        )
        return result

    kite = session_result["Kite"]

    # Verify NIFTY
    nifty_result = _verify_nifty(kite)
    result["NIFTY"] = nifty_result

    if nifty_result["Status"] != "NIFTY_READY":
        result["Status"] = "NIFTY_VERIFICATION_FAILED"
        return result

    # Verify NFO
    nfo_result = _verify_nfo(kite)
    result["NFO"] = nfo_result

    if nfo_result["Status"] != "NFO_READY":
        result["Status"] = "NFO_VERIFICATION_FAILED"
        return result

    # Before 09:00
    if current_clock < PRE_MARKET_TIME:
        result["Status"] = "MORNING_READY"
        result["Next Stage"] = "PRE_MARKET_09_00"
        return result

    # 09:00–09:14:59
    if current_clock < MARKET_OPEN_TIME:
        result["Status"] = "PRE_MARKET_READY"
        result["Next Stage"] = "GENUINE_915_BASELINE"
        return result

    # 09:15 onward
    result["Status"] = "MARKET_SESSION_READY"
    result["Next Stage"] = "V21_2_18_ORCHESTRATION"

    return result


if __name__ == "__main__":
    result = run_morning_startup()

    print("\n===== JKJ MORNING STARTUP =====")

    for key, value in result.items():
        print(f"{key}: {value}")

    print("================================")
