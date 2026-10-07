"""
JKJ AI TRADER
V21.2.18 - NIFTY Option 9:15 AM Baseline

Purpose:
    Capture and maintain the market-open baseline for the
    current NIFTY option universe.

Design:
    - Observation only.
    - No trading decisions.
    - No live orders.
    - No paper trades.

The baseline allows later analysis of:

    Current Price vs 9:15 Price
    Current Price vs Previous Close
    Recent movement vs Current Price
"""

from __future__ import annotations

from datetime import datetime, time
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Any, Dict, List, Optional


BASELINE_TIME = "09:15"

BASELINE_CAPTURE_START = time(9, 14, 30)
BASELINE_CAPTURE_END = time(9, 16, 0)


def _get_nifty_spot(kite) -> Optional[float]:
    """Get current NIFTY spot price."""

    try:
        data = kite.ltp("NSE:NIFTY 50")
        item = data.get("NSE:NIFTY 50", {})

        if item.get("last_price") is not None:
            return float(item["last_price"])

    except Exception:
        pass

    return None


def _get_current_expiry(
    instruments: List[Dict[str, Any]]
):
    """Return the nearest available NIFTY option expiry."""

    today = datetime.now(ZoneInfo("Asia/Kolkata")).date()

    expiries = sorted(
        {
            item.get("expiry")
            for item in instruments
            if item.get("name") == "NIFTY"
            and item.get("instrument_type") in ("CE", "PE")
            and item.get("expiry") is not None
            and item.get("expiry") >= today
        }
    )

    return expiries[0] if expiries else None


def _build_option_universe(
    instruments: List[Dict[str, Any]],
    nifty_spot: float,
    strikes_each_side: int = 10,
):
    """
    Build the same nearby-strike universe used by V21.2.18.
    """

    expiry = _get_current_expiry(instruments)

    if expiry is None:
        return None, []

    option_rows = [
        item
        for item in instruments
        if item.get("name") == "NIFTY"
        and item.get("expiry") == expiry
        and item.get("instrument_type") in ("CE", "PE")
    ]

    strikes = sorted(
        {
            float(item["strike"])
            for item in option_rows
            if item.get("strike") is not None
        }
    )

    if not strikes:
        return expiry, []

    atm_index = min(
        range(len(strikes)),
        key=lambda i: abs(strikes[i] - nifty_spot),
    )

    low = max(
        0,
        atm_index - strikes_each_side,
    )

    high = min(
        len(strikes),
        atm_index + strikes_each_side + 1,
    )

    selected_strikes = set(
        strikes[low:high]
    )

    universe = [
        item
        for item in option_rows
        if float(item.get("strike", 0))
        in selected_strikes
    ]

    universe.sort(
        key=lambda item: (
            float(item.get("strike", 0)),
            item.get("instrument_type", ""),
        )
    )

    return expiry, universe


def _get_previous_close(
    quote_item: Dict[str, Any]
) -> Optional[float]:

    ohlc = quote_item.get("ohlc") or {}

    close = ohlc.get("close")

    if close is None:
        return None

    try:
        return float(close)
    except Exception:
        return None


def capture_915_baseline(
    kite,
    strikes_each_side: int = 10,
) -> Dict[str, Any]:
    """
    Capture the current option prices as the genuine 9:15 baseline.

    Capture is permitted only during the controlled 09:14:30-09:16:00
    market-open window.
    """

    now = datetime.now(ZoneInfo("Asia/Kolkata"))

    if not (
        BASELINE_CAPTURE_START
        <= now.time()
        <= BASELINE_CAPTURE_END
    ):
        return {
            "Status": "BASELINE_CAPTURE_OUTSIDE_WINDOW",
            "Baseline Time": BASELINE_TIME,
            "Captured At": now.isoformat(timespec="seconds"),
            "Reason": (
                "Genuine 09:15 baseline can only be captured "
                "between 09:14:30 and 09:16:00."
            ),
            "Live Order": False,
            "Paper Trade": False,
        }

    instruments = kite.instruments("NFO")

    nifty_spot = _get_nifty_spot(kite)

    if nifty_spot is None:
        return {
            "Status": "NIFTY_SPOT_UNAVAILABLE",
            "Live Order": False,
            "Paper Trade": False,
        }

    expiry, universe = _build_option_universe(
        instruments,
        nifty_spot,
        strikes_each_side,
    )

    if not universe:
        return {
            "Status": "OPTION_UNIVERSE_UNAVAILABLE",
            "NIFTY Spot": nifty_spot,
            "Expiry": expiry,
            "Live Order": False,
            "Paper Trade": False,
        }

    symbols = [
        f"NFO:{item['tradingsymbol']}"
        for item in universe
        if item.get("tradingsymbol")
    ]

    quote_data = kite.quote(symbols)

    captured_at = datetime.now(ZoneInfo("Asia/Kolkata"))

    baseline = []

    for instrument in universe:

        symbol = instrument.get("tradingsymbol")

        if not symbol:
            continue

        quote_item = quote_data.get(
            f"NFO:{symbol}"
        )

        if not quote_item:
            continue

        current_price = quote_item.get(
            "last_price"
        )

        if current_price is None:
            continue

        previous_close = _get_previous_close(
            quote_item
        )

        baseline.append(
            {
                "Trading Symbol": symbol,
                "Option Type": instrument.get(
                    "instrument_type"
                ),
                "Strike": float(
                    instrument.get("strike", 0)
                ),
                "Expiry": instrument.get(
                    "expiry"
                ),
                "Baseline Time": BASELINE_TIME,
                "Captured At": captured_at.isoformat(
                    timespec="seconds"
                ),
                "9:15 Price": float(
                    current_price
                ),
                "Previous Close": previous_close,
            }
        )

    return {
        "Status": "BASELINE_CAPTURE_COMPLETE",
        "Baseline Type": "GENUINE_915",
        "Baseline Time": BASELINE_TIME,
        "Captured At": captured_at.isoformat(
            timespec="seconds"
        ),
        "NIFTY Spot": nifty_spot,
        "Expiry": expiry,
        "Universe Count": len(universe),
        "Baseline Count": len(baseline),
        "Baseline": baseline,
        "Live Order": False,
        "Paper Trade": False,
    }


def calculate_movement_from_baseline(
    baseline_record: Dict[str, Any],
    current_price: float,
) -> Dict[str, Any]:
    """
    Calculate current movement relative to the 9:15 baseline.
    """

    baseline_price = baseline_record.get(
        "9:15 Price"
    )

    if not baseline_price or baseline_price <= 0:
        movement_pct = 0.0
    else:
        movement_pct = (
            (current_price - baseline_price)
            / baseline_price
        ) * 100.0

    previous_close = baseline_record.get(
        "Previous Close"
    )

    if previous_close and previous_close > 0:
        daily_change_pct = (
            (current_price - previous_close)
            / previous_close
        ) * 100.0
    else:
        daily_change_pct = 0.0

    return {
        "Trading Symbol": baseline_record.get(
            "Trading Symbol"
        ),
        "Option Type": baseline_record.get(
            "Option Type"
        ),
        "Strike": baseline_record.get(
            "Strike"
        ),
        "Expiry": baseline_record.get(
            "Expiry"
        ),
        "9:15 Price": baseline_price,
        "Current Price": current_price,
        "Movement Since 9:15 %": round(
            movement_pct,
            2,
        ),
        "Daily Change %": round(
            daily_change_pct,
            2,
        ),
    }
