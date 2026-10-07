"""
JKJ AI Trader
V21.2.19-A - Persistent Intraday Observation Engine

Purpose:
    Maintain one persistent observation session for the NIFTY
    option universe and analyze the developing movement of every
    observed contract.

Safety:
    - Observation only
    - NO live orders
    - NO paper trades
    - NO entry decisions
    - NO exit decisions

Design:
    - One option universe for the session
    - Initial snapshot establishes observation starting prices
    - Repeated LTP observations every N seconds
    - Full universe stored using V21.2.18.5.3
    - Movement analyzed using V21.2.18.5.4
    - Candidate history preserved separately
"""

from __future__ import annotations

import time
from datetime import datetime
from typing import Any, Dict, List

from modules.nifty_option_v21_2_18_5_3_intraday_observation_store import (
    create_intraday_observation_store,
    record_scan_observations,
    get_intraday_store_summary,
)

from modules.nifty_option_v21_2_18_5_4_intraday_movement_analyzer import (
    analyze_intraday_store,
)

from modules.nifty_option_v21_2_18_early_surge_scanner import (
    _build_universe,
    _get_nifty_spot,
    _quote_initial_data,
    _ltp_batch,
)

from modules.nifty_option_v21_2_18_baseline_store import (
    load_today_baseline,
)

from modules.nifty_option_v21_2_19_candidate_lifecycle import (
    update_candidate_lifecycle,
    print_lifecycle_summary,
)
from modules.nifty_option_v21_2_19_recovery_intelligence import (
    build_recovery_candidates,
    print_recovery_candidates,
)
from modules.nifty_option_v21_2_19_recovery_journey import (
    update_recovery_journey,
    print_recovery_journey,
    get_recovery_journey_summary,
)

LIVE_ORDER = False
PAPER_TRADE = False

DEFAULT_INTERVAL_SECONDS = 15
DEFAULT_MAX_OBSERVATIONS = 4
DEFAULT_STRIKES_EACH_SIDE = 10

# Minimum recent movement used only for observation/watch classification.
RECENT_MOVEMENT_WATCH_THRESHOLD = 0.50


def _timestamp() -> str:
    return datetime.now().astimezone().isoformat(
        timespec="seconds"
    )


def _build_observation_result(instrument, quote_item, baseline):
    """
    Build one observation record.

    A genuine 9:15 price is included only when today's stored
    GENUINE_915 baseline exists. Otherwise this observation is
    explicitly treated as session-start data.
    """

    symbol = instrument.get("tradingsymbol")
    latest_price = quote_item.get("last_price")

    ohlc = quote_item.get("ohlc", {}) or {}
    previous_close = ohlc.get("close")

    baseline_price = None

    if isinstance(baseline, dict):
        contracts = baseline.get(
            "Contracts",
            baseline.get("Results", [])
        )

        for item in contracts:
            if item.get("Trading Symbol") == symbol:
                baseline_price = item.get("9:15 Price")
                break

    result = {
        "Trading Symbol": symbol,
        "Option Type": instrument.get("instrument_type"),
        "Strike": instrument.get("strike"),
        "Expiry": str(instrument.get("expiry")),
        "Previous Close": previous_close,
        "Latest Price": latest_price,
        "Observation Timestamp": _timestamp(),
        "Live Order": False,
        "Paper Trade": False,
    }

    # Only genuine stored 9:15 data may populate this field.
    if baseline_price is not None:
        result["9:15 Price"] = baseline_price
        result["Baseline Source"] = "GENUINE_915"
    else:
        result["Session Start Price"] = latest_price
        result["Baseline Source"] = "SESSION_START"

    return result


def _classify_observation(
    movement: Dict[str, Any],
) -> str:
    """
    Observation-only classification.

    This does not represent a trade signal.
    """

    count = movement.get("Observation Count", 0)

    if count < 3:
        return "INSUFFICIENT_DATA"

    movement_state = movement.get(
        "Movement State",
        "STABLE",
    )

    recent_movement = movement.get(
        "Recent Movement %",
    )

    if recent_movement is None:
        return "WATCHING"

    if movement_state == "ACCELERATING":
        return "ACCELERATING"

    if movement_state == "DEVELOPING":
        return "DEVELOPING"

    if movement_state == "MOVING":
        return "MOVING"

    if abs(recent_movement) >= RECENT_MOVEMENT_WATCH_THRESHOLD:
        return "WATCHING"

    return "STABLE"


def _print_top_movers(
    analysis: Dict[str, Dict[str, Any]],
    limit: int = 10,
) -> None:

    ranked = []

    for symbol, movement in analysis.items():

        recent = movement.get(
            "Recent Movement %"
        )

        if recent is None:
            continue

        ranked.append(
            (
                abs(float(recent)),
                symbol,
                movement,
            )
        )

    ranked.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    print()
    print("TOP RECENT MOVERS")
    print("-" * 90)

    if not ranked:
        print("No movement data available.")
        return

    for _, symbol, movement in ranked[:limit]:

        recent = movement.get(
            "Recent Movement %",
            0,
        )

        velocity = movement.get(
            "Latest Velocity %/sec"
        )

        acceleration = movement.get(
            "Latest Acceleration %/sec2"
        )

        state = _classify_observation(
            movement
        )

        print(
            f"{symbol} | "
            f"Price {movement.get('Latest Price', 0):.2f} | "
            f"Recent {recent:+.2f}% | "
            f"Velocity "
            f"{velocity if velocity is not None else 'N/A'} | "
            f"Acceleration "
            f"{acceleration if acceleration is not None else 'N/A'} | "
            f"{state}"
        )


def _print_active_movement(
    analysis: Dict[str, Dict[str, Any]],
) -> None:

    active = []

    for symbol, movement in analysis.items():

        state = _classify_observation(
            movement
        )

        if state in {
            "ACCELERATING",
            "DEVELOPING",
        }:

            active.append(
                (
                    symbol,
                    movement,
                    state,
                )
            )

    active.sort(
        key=lambda item: abs(
            item[1].get(
                "Recent Movement %",
                0,
            )
        ),
        reverse=True,
    )

    print()
    print("ACTIVE DEVELOPING MOVEMENT")
    print("-" * 90)

    if not active:
        print("None")
        return

    for symbol, movement, state in active[:10]:

        print(
            f"{symbol} | "
            f"{movement.get('Latest Price', 0):.2f} | "
            f"Recent "
            f"{movement.get('Recent Movement %', 0):+.2f}% | "
            f"Velocity "
            f"{movement.get('Latest Velocity %/sec', 'N/A')} | "
            f"Acceleration "
            f"{movement.get('Latest Acceleration %/sec2', 'N/A')} | "
            f"{state}"
        )


def run_persistent_observer(
    kite,
    interval_seconds: int = DEFAULT_INTERVAL_SECONDS,
    max_observations: int = DEFAULT_MAX_OBSERVATIONS,
    strikes_each_side: int = DEFAULT_STRIKES_EACH_SIDE,
) -> Dict[str, Any]:
    """
    Run one persistent observation session.

    All contracts remain in one observation store for the
    duration of this session.
    """

    print()
    print("=" * 70)
    print("JKJ V21.2.19-A PERSISTENT INTRADAY OBSERVER")
    print("=" * 70)

    print(f"Started: {_timestamp()}")
    print(f"Interval: {interval_seconds}s")
    print(f"Maximum Observations: {max_observations}")
    print(f"Strikes Each Side: {strikes_each_side}")
    print("Mode: OBSERVATION ONLY")
    print("Live Order: False")
    print("Paper Trade: False")

    # ---------------------------------------------------------
    # Prepare universe once
    # ---------------------------------------------------------

    print()
    print("Loading NFO instruments...")

    instruments = kite.instruments("NFO")

    print(
        f"NFO instruments loaded: "
        f"{len(instruments)}"
    )

    nifty_spot = _get_nifty_spot(kite)

    if nifty_spot is None:

        return {
            "Status": "NIFTY_SPOT_UNAVAILABLE",
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
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
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    print(f"NIFTY Spot: {nifty_spot}")
    print(f"Expiry: {expiry}")
    print(
        f"Observation Universe: "
        f"{len(universe)} contracts"
    )

    # ---------------------------------------------------------
    # Genuine 09:15 baseline
    # ---------------------------------------------------------

    stored_baseline = load_today_baseline()

    print(
        "09:15 baseline:",
        "AVAILABLE"
        if stored_baseline is not None
        else "NOT AVAILABLE",
    )

    # ---------------------------------------------------------
    # Initial snapshot
    # ---------------------------------------------------------

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

    if not initial_quote:

        return {
            "Status": "INITIAL_QUOTE_EMPTY",
            "NIFTY Spot": nifty_spot,
            "Expiry": expiry,
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    store = create_intraday_observation_store()
    lifecycle_store = {}
    recovery_journey_store = {}

    # ---------------------------------------------------------
    # Record initial observation
    # ---------------------------------------------------------

    initial_results = []

    for instrument in universe:

        key = (
            f"NFO:"
            f"{instrument['tradingsymbol']}"
        )

        quote_item = initial_quote.get(key)

        if not quote_item:
            continue

        observation = _build_observation_result(
            instrument,
            quote_item,
            stored_baseline,
        )

        if observation:
            initial_results.append(
                observation
            )

    record_scan_observations(
        store,
        {
            "Results": initial_results,
        },
    )

    print(
        f"Initial observations recorded: "
        f"{len(initial_results)}"
    )

    # ---------------------------------------------------------
    # Repeated observations
    # ---------------------------------------------------------

    observation_history = []

    for observation_number in range(
        1,
        max_observations + 1,
    ):

        print()
        print("=" * 70)
        print(
            f"OBSERVATION "
            f"{observation_number}/"
            f"{max_observations}"
        )
        print(
            f"Timestamp: {_timestamp()}"
        )
        print("=" * 70)

        try:

            prices = _ltp_batch(
                kite,
                universe,
            )

        except Exception as exc:

            print(
                f"LTP ERROR: "
                f"{type(exc).__name__}: {exc}"
            )

            observation_history.append(
                {
                    "Observation": observation_number,
                    "Status": "LTP_ERROR",
                    "Error": str(exc),
                    "Timestamp": _timestamp(),
                }
            )

            time.sleep(
                interval_seconds
            )

            continue

        current_results = []

        for instrument in universe:

            symbol = instrument.get(
                "tradingsymbol"
            )

            if not symbol:
                continue

            key = f"NFO:{symbol}"

            latest_price = prices.get(key)

            if latest_price is None:
                continue

            current_results.append(
                {
                    "Trading Symbol": symbol,
                    "Option Type": instrument.get(
                        "instrument_type"
                    ),
                    "Strike": float(
                        instrument.get(
                            "strike",
                            0,
                        )
                    ),
                    "Expiry": instrument.get(
                        "expiry"
                    ),
                    "Latest Price": float(
                        latest_price
                    ),
                    "Observation Timestamp": (
                        _timestamp()
                    ),
                    "Live Order": False,
                    "Paper Trade": False,
                }
            )

        record_result = record_scan_observations(
            store,
            {
                "Results": current_results,
            },
        )

        analysis = analyze_intraday_store(
            store
        )
        update_candidate_lifecycle(
            lifecycle_store,
            analysis,
        )

        print_lifecycle_summary(
            lifecycle_store
        )

        print_recovery_candidates(
            lifecycle_store
        )

        recovery_candidates = build_recovery_candidates(
            lifecycle_store
        )

        update_recovery_journey(
            recovery_journey_store,
            recovery_candidates,
        )

        print_recovery_journey(
            recovery_journey_store
        )

        observation_history.append(
            {
                "Observation": observation_number,
                "Timestamp": _timestamp(),
                "LTP Count": len(prices),
                "Recorded": record_result.get(
                    "Observations Recorded",
                    0,
                ),
                "Analysis": analysis,
            }
        )

        print(
            f"LTP response: "
            f"{len(prices)}/"
            f"{len(universe)}"
        )

        print(
            f"Observations recorded: "
            f"{record_result.get('Observations Recorded', 0)}"
        )

        _print_active_movement(
            analysis
        )

        _print_top_movers(
            analysis
        )

        if observation_number < max_observations:

            print()
            print(
                f"Waiting "
                f"{interval_seconds}s..."
            )

            time.sleep(
                interval_seconds
            )

    # ---------------------------------------------------------
    # Final summary
    # ---------------------------------------------------------

    store_summary = (
        get_intraday_store_summary(
            store
        )
    )

    final_analysis = analyze_intraday_store(
        store
    )

    print()
    print("=" * 70)
    print("V21.2.19-A OBSERVATION COMPLETE")
    print("=" * 70)

    print(
        f"Tracked Symbols: "
        f"{store_summary['Tracked Symbols']}"
    )

    print(
        f"Total Observations: "
        f"{store_summary['Total Observations']}"
    )

    _print_active_movement(
        final_analysis
    )

    _print_top_movers(
        final_analysis
    )

    return {
        "Status": "PERSISTENT_OBSERVER_COMPLETE",
        "NIFTY Spot": nifty_spot,
        "Expiry": expiry,
        "Universe Count": len(universe),
        "Observation Count": max_observations,
        "Interval Seconds": interval_seconds,
        "Store Summary": store_summary,
        "Observation History": observation_history,
        "Observation Store": store,
        "Final Analysis": final_analysis,
        "Candidate Lifecycle": lifecycle_store,
        "Recovery Journey": get_recovery_journey_summary(
            recovery_journey_store
        ),
        "Live Order": LIVE_ORDER,
        "Paper Trade": PAPER_TRADE,
    }


if __name__ == "__main__":

    print(
        "This module requires an authenticated Kite session."
    )
    print(
        "Use run_persistent_observer(kite, ...) "
        "from the JKJ runtime."
    )
