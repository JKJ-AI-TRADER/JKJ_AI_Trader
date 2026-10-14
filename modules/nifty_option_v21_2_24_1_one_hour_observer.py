"""
JKJ AI Trader
V21.2.24.1 — One-Hour Observation Engine

Purpose:
    Observe selected V21.2.23 discovery candidates for up to one hour
    and record their real-market movement.

Safety:
    - Observation only
    - No BUY
    - No SELL
    - No live orders
    - No paper trades
    - No position sizing
    - No stop/target generation

This module does NOT decide whether a candidate should be traded.
It only records market behaviour for later research.
"""

import time
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Any, Dict, List


LIVE_ORDER = False
PAPER_TRADE = False

DEFAULT_INTERVAL_SECONDS = 60
DEFAULT_DURATION_MINUTES = 60

CHECKPOINT_MINUTES = (
    5,
    10,
    15,
    30,
    45,
    60,
)


def _timestamp() -> str:
    return datetime.now(
        ZoneInfo("Asia/Kolkata")
    ).isoformat()


def _safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _movement_percent(initial_price, latest_price):
    initial = _safe_float(initial_price)
    latest = _safe_float(latest_price)

    if initial is None or latest is None or initial <= 0:
        return None

    return ((latest - initial) / initial) * 100.0


def _nifty_movement_percent(initial_spot, latest_spot):
    initial = _safe_float(initial_spot)
    latest = _safe_float(latest_spot)

    if initial is None or latest is None or initial <= 0:
        return None

    return ((latest - initial) / initial) * 100.0


def _build_candidate_map(selection_result):
    candidates = selection_result.get(
        "Selected Candidates",
        [],
    )

    candidate_map = {}

    for candidate in candidates:
        symbol = candidate.get("Trading Symbol")

        if not symbol:
            continue

        candidate_map[symbol] = candidate

    return candidate_map


def observe_for_one_hour(
    kite,
    selection_result,
    duration_minutes: int = DEFAULT_DURATION_MINUTES,
    interval_seconds: int = DEFAULT_INTERVAL_SECONDS,
) -> Dict[str, Any]:
    """
    Observe selected discovery candidates for up to one hour.

    The function records:
        - candidate price
        - NIFTY spot
        - movement from observation start
        - timestamp
        - volume
        - open interest
        - checkpoint timing

    It does not make trading decisions.
    """

    if not isinstance(selection_result, dict):
        return {
            "Status": "INVALID_SELECTION_RESULT",
            "Live Order": False,
            "Paper Trade": False,
        }

    if selection_result.get("Status") != (
        "DISCOVERY_CANDIDATE_SELECTION_COMPLETE"
    ):
        return {
            "Status": "INVALID_SELECTION_STATUS",
            "Live Order": False,
            "Paper Trade": False,
        }

    if kite is None:
        return {
            "Status": "KITE_SESSION_NOT_AVAILABLE",
            "Live Order": False,
            "Paper Trade": False,
        }

    candidate_map = _build_candidate_map(
        selection_result
    )

    if not candidate_map:
        return {
            "Status": "NO_SELECTED_CANDIDATES",
            "Live Order": False,
            "Paper Trade": False,
        }

    if duration_minutes <= 0:
        return {
            "Status": "INVALID_DURATION",
            "Live Order": False,
            "Paper Trade": False,
        }

    if interval_seconds <= 0:
        return {
            "Status": "INVALID_INTERVAL",
            "Live Order": False,
            "Paper Trade": False,
        }

    symbols = list(candidate_map.keys())

    # ---------------------------------------------------------
    # Initial NIFTY snapshot
    # ---------------------------------------------------------

    nifty_quote = kite.ltp(
        ["NSE:NIFTY 50"]
    )

    nifty_item = nifty_quote.get(
        "NSE:NIFTY 50",
        {},
    )

    initial_nifty = _safe_float(
        nifty_item.get("last_price")
    )

    # ---------------------------------------------------------
    # Initial candidate snapshot
    # ---------------------------------------------------------

    instrument_keys = [
        f"NFO:{symbol}"
        for symbol in symbols
    ]

    initial_quotes = kite.ltp(
        instrument_keys
    )

    initial_prices = {}

    for symbol in symbols:
        quote = initial_quotes.get(
            f"NFO:{symbol}",
            {},
        )

        initial_prices[symbol] = _safe_float(
            quote.get("last_price")
        )

    observation_start = datetime.now(
        ZoneInfo("Asia/Kolkata")
    )

    observation_history: List[Dict[str, Any]] = []

    checkpoint_results: Dict[
        str,
        Dict[str, Any],
    ] = {}

    max_duration_seconds = (
        duration_minutes * 60
    )

    elapsed_seconds = 0

    print()
    print("=" * 70)
    print(
        "JKJ AI TRADER — V21.2.24.1 "
        "ONE-HOUR OBSERVATION"
    )
    print("=" * 70)
    print("Mode: OBSERVATION ONLY")
    print("Candidates:", len(symbols))
    print(
        "Duration Minutes:",
        duration_minutes,
    )
    print(
        "Interval Seconds:",
        interval_seconds,
    )
    print(
        "Initial NIFTY Spot:",
        initial_nifty,
    )
    print("Live Order: False")
    print("Paper Trade: False")
    print()

    while elapsed_seconds < max_duration_seconds:

        if elapsed_seconds > 0:
            time.sleep(interval_seconds)

        quote = kite.ltp(
            ["NSE:NIFTY 50"]
            + instrument_keys
        )

        nifty_item = quote.get(
            "NSE:NIFTY 50",
            {},
        )

        latest_nifty = _safe_float(
            nifty_item.get("last_price")
        )

        now = datetime.now(
            ZoneInfo("Asia/Kolkata")
        )

        elapsed_minutes = (
            now - observation_start
        ).total_seconds() / 60.0

        cycle = {
            "Timestamp": now.isoformat(),
            "Elapsed Minutes": round(
                elapsed_minutes,
                2,
            ),
            "NIFTY Spot": latest_nifty,
            "NIFTY Movement %": _nifty_movement_percent(
                initial_nifty,
                latest_nifty,
            ),
            "Candidates": [],
            "Live Order": False,
            "Paper Trade": False,
        }

        for symbol in symbols:

            quote_item = quote.get(
                f"NFO:{symbol}",
                {},
            )

            latest_price = _safe_float(
                quote_item.get("last_price")
            )

            movement = _movement_percent(
                initial_prices.get(symbol),
                latest_price,
            )

            record = {
                "Trading Symbol": symbol,
                "Option Type": candidate_map[
                    symbol
                ].get("Option Type"),
                "Expiry": candidate_map[
                    symbol
                ].get("Expiry"),
                "Strike": candidate_map[
                    symbol
                ].get("Strike"),
                "Initial Price": initial_prices.get(
                    symbol
                ),
                "Current Price": latest_price,
                "Movement %": movement,
                "NIFTY Spot": latest_nifty,
                "NIFTY Movement %": cycle[
                    "NIFTY Movement %"
                ],
                "Volume": quote_item.get(
                    "volume"
                ),
                "Open Interest": quote_item.get(
                    "oi"
                ),
                "Timestamp": now.isoformat(),
                "Elapsed Minutes": round(
                    elapsed_minutes,
                    2,
                ),
                "Live Order": False,
                "Paper Trade": False,
            }

            cycle["Candidates"].append(
                record
            )

        observation_history.append(
            cycle
        )

        # -----------------------------------------------------
        # Checkpoint recording
        # -----------------------------------------------------

        completed_minutes = [
            minute
            for minute in CHECKPOINT_MINUTES
            if minute <= duration_minutes
            and elapsed_minutes >= minute
            and str(minute) not in checkpoint_results
        ]

        for minute in completed_minutes:
            checkpoint_results[str(minute)] = {
                "Checkpoint Minutes": minute,
                "Timestamp": cycle["Timestamp"],
                "NIFTY Spot": latest_nifty,
                "NIFTY Movement %": cycle[
                    "NIFTY Movement %"
                ],
                "Candidates": cycle[
                    "Candidates"
                ],
                "Live Order": False,
                "Paper Trade": False,
            }

            print(
                f"CHECKPOINT {minute} MINUTES"
            )

            ranked = sorted(
                cycle["Candidates"],
                key=lambda item: (
                    item.get("Movement %")
                    if item.get("Movement %")
                    is not None
                    else -999999
                ),
                reverse=True,
            )

            for item in ranked[:10]:
                movement = item.get(
                    "Movement %"
                )

                print(
                    f"  {item['Trading Symbol']} | "
                    f"{movement:.2f}%"
                    if movement is not None
                    else
                    f"  {item['Trading Symbol']} | "
                    f"Movement=N/A"
                )

            print()

        elapsed_seconds = (
            now - observation_start
        ).total_seconds()

        if elapsed_seconds >= max_duration_seconds:
            break

    return {
        "Status": (
            "ONE_HOUR_OBSERVATION_COMPLETE"
        ),
        "Observation Start": (
            observation_start.isoformat()
        ),
        "Observation End": _timestamp(),
        "Duration Minutes": duration_minutes,
        "Interval Seconds": interval_seconds,
        "Candidate Count": len(symbols),
        "Initial NIFTY Spot": initial_nifty,
        "Initial Prices": initial_prices,
        "Observation History": observation_history,
        "Checkpoints": checkpoint_results,
        "Live Order": False,
        "Paper Trade": False,
        "Next Stage": (
            "V21.2.24.2 Movement / "
            "Peak / Giveback Analysis"
        ),
    }
