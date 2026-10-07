"""
JKJ AI TRADER
V21.2.18 - Early Surge / Acceleration Scanner

Purpose:
    Detect rapid upward movement in NIFTY option contracts.

Design:
    - Discovery / early-warning layer only.
    - Does NOT make an entry decision.
    - Does NOT place live orders.
    - Does NOT create paper trades.
    - Feeds only qualified candidates toward the existing
      V21.2.15 -> V21.2.16 -> V21.2.17 decision pipeline.

Important:
    Repeated observations use kite.ltp() rather than repeatedly
    calling kite.quote(), because the scanner only needs current
    prices during the observation window.

Thresholds:
    +20% = EARLY_WATCH
    +30% = STRONG
    +40% = SURGE
"""

from __future__ import annotations

import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from modules.nifty_option_v21_2_18_baseline_store import load_today_baseline


EARLY_MOVE_THRESHOLD = 20.0
STRONG_MOVE_THRESHOLD = 30.0
SURGE_THRESHOLD = 40.0

# Early-transition thresholds
REVERSAL_MIN_IMPROVEMENT = 15.0
ACCELERATION_MIN_IMPROVEMENT = 10.0
MULTI_STRIKE_MIN_COUNT = 2

# Graduated movement levels.
EARLY_WATCH_MOVEMENT_THRESHOLD = 2.0
EARLY_MOVEMENT_THRESHOLD = 3.0
DEVELOPING_MOVEMENT_THRESHOLD = 5.0
STRONG_MOVEMENT_THRESHOLD = 10.0
MAJOR_MOVEMENT_THRESHOLD = 15.0
VERY_STRONG_MOVEMENT_THRESHOLD = 20.0
EXTENDED_MOVEMENT_THRESHOLD = 30.0
SURGE_MOVEMENT_THRESHOLD = 40.0


def classify_graduated_movement(change_pct: float) -> str:
    """Classify upward movement for observation/discovery only."""

    if change_pct >= SURGE_MOVEMENT_THRESHOLD:
        return "SURGE"

    if change_pct >= EXTENDED_MOVEMENT_THRESHOLD:
        return "EXTENDED"

    if change_pct >= VERY_STRONG_MOVEMENT_THRESHOLD:
        return "VERY_STRONG"

    if change_pct >= MAJOR_MOVEMENT_THRESHOLD:
        return "MAJOR"

    if change_pct >= STRONG_MOVEMENT_THRESHOLD:
        return "STRONG"

    if change_pct >= DEVELOPING_MOVEMENT_THRESHOLD:
        return "DEVELOPING"

    if change_pct >= EARLY_MOVEMENT_THRESHOLD:
        return "EARLY"

    if change_pct >= EARLY_WATCH_MOVEMENT_THRESHOLD:
        return "EARLY_WATCH"

    return "NORMAL"

DEFAULT_WINDOW_SECONDS = 60
DEFAULT_INTERVAL_SECONDS = 15
DEFAULT_STRIKES_EACH_SIDE = 10


def _percentage_change(previous_price: float, current_price: float) -> float:
    if previous_price is None or current_price is None:
        return 0.0

    if previous_price <= 0:
        return 0.0

    return ((current_price - previous_price) / previous_price) * 100.0


def _classify_move(change_pct: float) -> str:
    if change_pct >= SURGE_THRESHOLD:
        return "SURGE"

    if change_pct >= STRONG_MOVE_THRESHOLD:
        return "STRONG"

    if change_pct >= EARLY_MOVE_THRESHOLD:
        return "EARLY_WATCH"

    if change_pct <= -SURGE_THRESHOLD:
        return "STRONG_DOWN"

    if change_pct <= -STRONG_MOVE_THRESHOLD:
        return "DOWN_STRONG"

    if change_pct <= -EARLY_MOVE_THRESHOLD:
        return "DOWN_WATCH"

    return "NORMAL"


def _get_nifty_spot(kite) -> Optional[float]:
    try:
        data = kite.ltp("NSE:NIFTY 50")
        item = data.get("NSE:NIFTY 50", {})

        if "last_price" in item:
            return float(item["last_price"])

    except Exception:
        pass

    return None


def _select_current_expiry(instruments: List[Dict[str, Any]]):
    today = datetime.now().date()

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


def _build_universe(
    instruments: List[Dict[str, Any]],
    nifty_spot: float,
    strikes_each_side: int = DEFAULT_STRIKES_EACH_SIDE,
) -> Tuple[Optional[Any], List[Dict[str, Any]]]:

    expiry = _select_current_expiry(instruments)

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

    low = max(0, atm_index - strikes_each_side)
    high = min(len(strikes), atm_index + strikes_each_side + 1)

    selected_strikes = set(strikes[low:high])

    universe = [
        item
        for item in option_rows
        if float(item.get("strike", 0)) in selected_strikes
    ]

    universe.sort(
        key=lambda item: (
            float(item.get("strike", 0)),
            item.get("instrument_type", ""),
        )
    )

    return expiry, universe


def _quote_initial_data(
    kite,
    instruments: List[Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:

    symbols = [
        f"NFO:{item['tradingsymbol']}"
        for item in instruments
        if item.get("tradingsymbol")
    ]

    if not symbols:
        return {}

    return kite.quote(symbols)


def _ltp_batch(
    kite,
    instruments: List[Dict[str, Any]],
) -> Dict[str, float]:

    symbols = [
        f"NFO:{item['tradingsymbol']}"
        for item in instruments
        if item.get("tradingsymbol")
    ]

    if not symbols:
        return {}

    data = kite.ltp(symbols)

    result = {}

    for symbol, item in data.items():
        if item.get("last_price") is not None:
            result[symbol] = float(item["last_price"])

    return result


def _extract_previous_close(item: Dict[str, Any]) -> Optional[float]:

    ohlc = item.get("ohlc") or {}

    close = ohlc.get("close")

    if close is None:
        return None

    try:
        return float(close)
    except Exception:
        return None



def _baseline_price_for_symbol(
    baseline: Optional[Dict[str, Any]],
    trading_symbol: str,
) -> Optional[float]:
    """
    Return the genuine 09:15 baseline price for one option.

    Test/synthetic snapshots are never accepted.
    """

    if not baseline:
        return None

    if baseline.get("Baseline Type") != "GENUINE_915":
        return None

    records = baseline.get("Baseline", [])

    if not isinstance(records, list):
        return None

    for item in records:
        if item.get("Trading Symbol") != trading_symbol:
            continue

        price = item.get("9:15 Price")

        if price is None:
            return None

        try:
            price = float(price)
        except (TypeError, ValueError):
            return None

        if price <= 0:
            return None

        return price

    return None


def _movement_since_915(
    baseline_price: Optional[float],
    current_price: float,
) -> Optional[float]:
    """Calculate movement from the genuine stored 09:15 price."""

    if baseline_price is None:
        return None

    if baseline_price <= 0:
        return None

    return _percentage_change(
        baseline_price,
        current_price,
    )


def _build_initial_candidate(
    instrument: Dict[str, Any],
    quote_item: Dict[str, Any],
    baseline: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:

    symbol = instrument.get("tradingsymbol")

    if not symbol:
        return None

    current_price = quote_item.get("last_price")

    if current_price is None:
        return None

    current_price = float(current_price)

    previous_close = _extract_previous_close(quote_item)

    daily_change = (
        _percentage_change(previous_close, current_price)
        if previous_close
        else 0.0
    )

    baseline_price = _baseline_price_for_symbol(
        baseline,
        symbol,
    )

    movement_since_915 = _movement_since_915(
        baseline_price,
        current_price,
    )

    return {
        "Trading Symbol": symbol,
        "Option Type": instrument.get("instrument_type"),
        "Strike": float(instrument.get("strike", 0)),
        "Expiry": instrument.get("expiry"),
        "Previous Close": previous_close,
        "9:15 Price": baseline_price,
        "Initial Price": current_price,
        "Latest Price": current_price,
        "Movement Since 9:15 %": (
            round(movement_since_915, 2)
            if movement_since_915 is not None
            else None
        ),
        "9:15 Movement Level": (
            classify_graduated_movement(movement_since_915)
            if movement_since_915 is not None
            else "BASELINE_UNAVAILABLE"
        ),
        "Daily Change %": round(daily_change, 2),
        "Window Change %": 0.0,
        "Acceleration %": 0.0,
        "Initial Classification": _classify_move(daily_change),
        "Final Classification": "NORMAL",
        "Reversal Up": False,
        "Upward Acceleration": False,
    }


def _evaluate_candidate(
    candidate: Dict[str, Any],
    latest_price: float,
) -> Dict[str, Any]:
    """
    Evaluate the transition from the initial observation to the
    latest observation.

    This is an observation/discovery layer only.
    It does not qualify an entry.
    """

    initial_price = candidate["Initial Price"]
    previous_close = candidate["Previous Close"]

    final_daily_change = (
        _percentage_change(previous_close, latest_price)
        if previous_close
        else 0.0
    )

    window_change = _percentage_change(
        initial_price,
        latest_price,
    )

    initial_daily_change = candidate["Daily Change %"]

    # Improvement in daily position from the initial observation.
    daily_improvement = (
        final_daily_change - initial_daily_change
    )

    # Weak -> positive reversal.
    reversal_up = (
        initial_daily_change < 0
        and final_daily_change > 0
        and daily_improvement >= REVERSAL_MIN_IMPROVEMENT
    )

    # Early acceleration can be detected even before +20% is reached.
    upward_acceleration = (
        window_change >= ACCELERATION_MIN_IMPROVEMENT
        or daily_improvement >= ACCELERATION_MIN_IMPROVEMENT
    )

    # Stronger classification.
    if final_daily_change >= SURGE_THRESHOLD:
        classification = "SURGE"

    elif final_daily_change >= STRONG_MOVE_THRESHOLD:
        classification = "STRONG"

    elif final_daily_change >= EARLY_MOVE_THRESHOLD:
        classification = "EARLY_WATCH"

    elif reversal_up:
        classification = "REVERSAL_UP"

    elif upward_acceleration:
        classification = "ACCELERATING_UP"

    else:
        classification = "NORMAL"

    candidate["Latest Price"] = latest_price
    candidate["Window Change %"] = round(window_change, 2)
    candidate["Acceleration %"] = round(daily_improvement, 2)
    candidate["Daily Change %"] = round(final_daily_change, 2)

    candidate["Graduated Movement"] = classify_graduated_movement(
        window_change
    )

    candidate["Final Classification"] = classification
    candidate["Reversal Up"] = reversal_up
    candidate["Upward Acceleration"] = upward_acceleration

    candidate["Early Surge Candidate"] = bool(
        reversal_up or upward_acceleration
    )

    return candidate


def scan_current_nifty_options(
    kite,
    strikes_each_side: int = DEFAULT_STRIKES_EACH_SIDE,
) -> Dict[str, Any]:

    instruments = kite.instruments("NFO")

    nifty_spot = _get_nifty_spot(kite)

    if nifty_spot is None:
        return {
            "Status": "NIFTY_SPOT_UNAVAILABLE",
            "Live Order": False,
            "Paper Trade": False,
        }

    expiry, universe = _build_universe(
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

    stored_baseline = load_today_baseline()

    quote_data = _quote_initial_data(kite, universe)

    results = []

    for instrument in universe:
        key = f"NFO:{instrument['tradingsymbol']}"
        quote_item = quote_data.get(key)

        if not quote_item:
            continue

        candidate = _build_initial_candidate(
            instrument,
            quote_item,
            stored_baseline,
        )

        if candidate:
            results.append(candidate)

    candidates = [
        item
        for item in results
        if (
            (
                item.get("Movement Since 9:15 %") is not None
                and item.get("Movement Since 9:15 %", 0)
                >= EARLY_WATCH_MOVEMENT_THRESHOLD
            )
            or item.get("Early Surge Candidate", False)
        )
    ]

    return {
        "Status": "SCAN_COMPLETE",
        "NIFTY Spot": nifty_spot,
        "Expiry": expiry,
        "Universe Count": len(universe),
        "Results": results,
        "Candidates": candidates,
        "Live Order": False,
        "Paper Trade": False,
    }


def run_early_surge_session(
    kite,
    window_seconds: int = DEFAULT_WINDOW_SECONDS,
    interval_seconds: int = DEFAULT_INTERVAL_SECONDS,
    strikes_each_side: int = DEFAULT_STRIKES_EACH_SIDE,
) -> Dict[str, Any]:

    print()
    print("=" * 70)
    print("V21.2.18 EARLY SURGE OBSERVATION")
    print("=" * 70)

    print("Loading NFO instruments...")

    instruments = kite.instruments("NFO")

    print(f"NFO instruments loaded: {len(instruments)}")

    nifty_spot = _get_nifty_spot(kite)

    if nifty_spot is None:
        return {
            "Status": "NIFTY_SPOT_UNAVAILABLE",
            "Live Order": False,
            "Paper Trade": False,
        }

    print(f"NIFTY Spot: {nifty_spot}")

    expiry, universe = _build_universe(
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

    print(f"Expiry: {expiry}")
    print(f"Observation Universe: {len(universe)} contracts")
    print(f"Window: {window_seconds} seconds")
    print(f"Interval: {interval_seconds} seconds")

    # ------------------------------------------------------------
    # Genuine 09:15 baseline
    # ------------------------------------------------------------

    stored_baseline = load_today_baseline()

    if stored_baseline is not None:
        print("09:15 baseline: AVAILABLE")
    else:
        print("09:15 baseline: NOT AVAILABLE")
        print(
            "Movement Since 9:15 will remain unavailable "
            "until a genuine 09:15 baseline is captured."
        )

    # ------------------------------------------------------------
    # Initial quote:
    # Establish previous close + baseline price.
    # This is the only heavy quote call.
    # ------------------------------------------------------------

    print()
    print("Getting initial option snapshot...")

    initial_quote = _quote_initial_data(
        kite,
        universe,
    )

    print(
        f"Initial quote received: "
        f"{len(initial_quote)} contracts"
    )

    candidates = {}

    for instrument in universe:
        key = f"NFO:{instrument['tradingsymbol']}"
        quote_item = initial_quote.get(key)

        if not quote_item:
            continue

        candidate = _build_initial_candidate(
            instrument,
            quote_item,
            stored_baseline,
        )

        if candidate:
            candidates[instrument["tradingsymbol"]] = candidate

    if not candidates:
        return {
            "Status": "INITIAL_QUOTE_EMPTY",
            "NIFTY Spot": nifty_spot,
            "Expiry": expiry,
            "Live Order": False,
            "Paper Trade": False,
        }

    print(
        f"Baseline established for "
        f"{len(candidates)} contracts."
    )

    # ------------------------------------------------------------
    # Observation cycles
    # ------------------------------------------------------------

    observation_count = max(
        1,
        int(window_seconds / interval_seconds),
    )

    start_time = time.time()

    for cycle in range(1, observation_count + 1):

        elapsed = int(time.time() - start_time)

        print()
        print(
            f"[Observation {cycle}/{observation_count}] "
            f"Elapsed: {elapsed}s"
        )

        try:
            prices = _ltp_batch(
                kite,
                universe,
            )

        except Exception as exc:

            print(
                "LTP ERROR: "
                f"{type(exc).__name__}: {exc}"
            )

            prices = {}

        print(
            f"LTP response: "
            f"{len(prices)}/{len(universe)} contracts"
        )

        updated = 0

        for symbol, latest_price in prices.items():

            tradingsymbol = symbol.replace("NFO:", "")

            candidate = candidates.get(tradingsymbol)

            if not candidate:
                continue

            _evaluate_candidate(
                candidate,
                latest_price,
            )

            updated += 1

        print(
            f"Updated candidates: {updated}"
        )

        upward = [
            item
            for item in candidates.values()
            if item.get("Early Surge Candidate")
        ]

        print(
            f"Current upward candidates: {len(upward)}"
        )

        for item in sorted(
            upward,
            key=lambda x: x.get("Window Change %", 0),
            reverse=True,
        )[:5]:

            movement_915 = item.get("Movement Since 9:15 %")
            movement_915_text = (
                f"{movement_915:+.2f}%"
                if movement_915 is not None
                else "N/A"
            )

            print(
                f"  {item['Trading Symbol']} | "
                f"{item['Option Type']} | "
                f"Price {item['Latest Price']:.2f} | "
                f"9:15 {item.get('9:15 Price') if item.get('9:15 Price') is not None else 'N/A'} | "
                f"Since 9:15 {movement_915_text} | "
                f"Level {item.get('9:15 Movement Level', 'N/A')} | "
                f"Window {item['Window Change %']:+.2f}% | "
                f"Daily {item['Daily Change %']:+.2f}% | "
                f"Acceleration {item['Acceleration %']:+.2f}% | "
                f"Reversal: {item['Reversal Up']} | "
                f"{item['Final Classification']}"
            )

        if cycle < observation_count:

            remaining = interval_seconds

            print(
                f"Waiting {remaining}s for next observation..."
            )

            time.sleep(remaining)

    # ------------------------------------------------------------
    # Final evaluation
    # ------------------------------------------------------------

    final_upward_candidates = [
        item
        for item in candidates.values()
        if item.get("Early Surge Candidate")
    ]

    # Multi-strike confirmation
    ce_upward = [
        item
        for item in final_upward_candidates
        if item.get("Option Type") == "CE"
    ]

    pe_upward = [
        item
        for item in final_upward_candidates
        if item.get("Option Type") == "PE"
    ]

    ce_multi_strike_confirmation = (
        len(ce_upward) >= MULTI_STRIKE_MIN_COUNT
    )

    pe_multi_strike_confirmation = (
        len(pe_upward) >= MULTI_STRIKE_MIN_COUNT
    )

    print()
    print("=" * 70)
    print("V21.2.18 OBSERVATION COMPLETE")
    print("=" * 70)

    print(
        f"Upward candidates: "
        f"{len(final_upward_candidates)}"
    )

    print(
        f"CE upward candidates: "
        f"{len(ce_upward)}"
    )

    print(
        f"PE upward candidates: "
        f"{len(pe_upward)}"
    )

    if final_upward_candidates:

        print()
        print("TOP EARLY-SURGE CANDIDATES:")

        for item in sorted(
            final_upward_candidates,
            key=lambda x: (
                x.get("Window Change %", 0),
                x.get("Acceleration %", 0),
            ),
            reverse=True,
        )[:10]:

            print(
                f"{item['Trading Symbol']} | "
                f"{item['Option Type']} | "
                f"Price: {item['Latest Price']:.2f} | "
                f"Window: {item['Window Change %']:+.2f}% | "
                f"Daily: {item['Daily Change %']:+.2f}% | "
                f"Acceleration: {item['Acceleration %']:+.2f}% | "
                f"Reversal: {item['Reversal Up']} | "
                f"{item['Final Classification']}"
            )

    return {
        "Status": "EARLY_SURGE_SCAN_COMPLETE",
        "NIFTY Spot": nifty_spot,
        "Expiry": expiry,
        "Universe Count": len(universe),
        "Observation Count": observation_count,
        "Interval Seconds": interval_seconds,
        "Candidates": final_upward_candidates,
        "All Results": list(candidates.values()),
        "CE Upward Candidates": ce_upward,
        "PE Upward Candidates": pe_upward,
        "CE Multi-Strike Confirmation": ce_multi_strike_confirmation,
        "PE Multi-Strike Confirmation": pe_multi_strike_confirmation,
        "Live Order": False,
        "Paper Trade": False,
    }
