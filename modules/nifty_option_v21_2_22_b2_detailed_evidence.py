"""
JKJ AI Trader
V21.2.22-B.2 — Detailed Candidate Evidence Collector

Purpose:
    Collect genuine detailed market evidence for the small number
    of candidates selected by V21.2.22-B.1.

Safety:
    - Observation only
    - No BUY/SELL decisions
    - No live orders
    - No paper trades
    - No position sizing

Candidate != Trade.
"""

from __future__ import annotations

import time
from datetime import datetime
from typing import Any, Dict, List

from modules.intraday_zerodha_option_adapter import (
    adapt_zerodha_option_quote,
)


LIVE_ORDER = False
PAPER_TRADE = False

REQUIRED_OBSERVATIONS = 4
DEFAULT_INTERVAL_SECONDS = 15


def _timestamp() -> str:
    return datetime.now().isoformat()


def _get_nifty_spot(kite):
    try:
        data = kite.ltp("NSE:NIFTY 50")
        item = data.get("NSE:NIFTY 50", {})

        if item.get("last_price") is not None:
            return float(item["last_price"])

    except Exception:
        pass

    return None


def _build_instrument_map(kite):
    instruments = kite.instruments("NFO")

    result = {}

    for instrument in instruments:

        symbol = instrument.get("tradingsymbol")

        if not symbol:
            continue

        if instrument.get("name") != "NIFTY":
            continue

        if instrument.get("instrument_type") not in (
            "CE",
            "PE",
        ):
            continue

        result[symbol] = instrument

    return result


def _validate_selected_candidates(
    selection_result: Dict[str, Any],
):
    if not isinstance(selection_result, dict):
        return None, "Selection result must be a dictionary."

    if selection_result.get("Status") != (
        "CANDIDATE_SELECTION_COMPLETE"
    ):
        return (
            None,
            "Selection result must be "
            "CANDIDATE_SELECTION_COMPLETE.",
        )

    candidates = selection_result.get(
        "Selected Candidates",
        [],
    )

    if not isinstance(candidates, list):
        return None, "Selected Candidates must be a list."

    return candidates, None


def _build_record(
    candidate: Dict[str, Any],
    instrument: Dict[str, Any],
    normalized_quote: Dict[str, Any],
    nifty_spot: float,
):
    current_price = normalized_quote.get(
        "Current Price"
    )

    volume = normalized_quote.get(
        "Volume"
    )

    open_interest = normalized_quote.get(
        "Open Interest"
    )

    if current_price is None:
        return None, "Current Price unavailable."

    if volume is None:
        return None, "Volume unavailable."

    if open_interest is None:
        return None, "Open Interest unavailable."

    record = {
        "Status": "RECORDED",

        "Trading Symbol": candidate.get(
            "Trading Symbol"
        ),

        "Instrument Token": instrument.get(
            "instrument_token"
        ),

        "Underlying": "NIFTY",

        "Expiry": instrument.get(
            "expiry"
        ),

        "Strike": float(
            instrument.get(
                "strike",
                0,
            )
        ),

        "Option Type": instrument.get(
            "instrument_type"
        ),

        "Current Price": float(
            current_price
        ),

        "NIFTY Spot Price": float(
            nifty_spot
        ),

        "Volume": float(
            volume
        ),

        "Open Interest": float(
            open_interest
        ),

        "Previous Close": normalized_quote.get(
            "Previous Close"
        ),

        "Timestamp": _timestamp(),

        "Last Trade Time": normalized_quote.get(
            "Last Trade Time"
        ),

        "Selection Rank": candidate.get(
            "Selection Rank"
        ),

        "Candidate Category": candidate.get(
            "Category"
        ),

        "Lifecycle State": candidate.get(
            "Lifecycle State"
        ),

        "Live Order": False,
        "Paper Trade": False,
    }

    return record, None


def collect_detailed_evidence(
    kite,
    selection_result: Dict[str, Any],
    observation_count: int = REQUIRED_OBSERVATIONS,
    interval_seconds: int = DEFAULT_INTERVAL_SECONDS,
):
    """
    Collect genuine detailed market observations for B.1 selections.

    Maximum intended candidate count is three.
    """

    candidates, error = _validate_selected_candidates(
        selection_result
    )

    if error:
        return {
            "Status": "REJECTED",
            "Reason": error,
            "Observations": {},
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    if not candidates:
        return {
            "Status": "NO_SELECTED_CANDIDATES",
            "Observations": {},
            "Observation Count": 0,
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    try:
        required_count = int(observation_count)
    except (TypeError, ValueError):
        required_count = REQUIRED_OBSERVATIONS

    if required_count < REQUIRED_OBSERVATIONS:
        required_count = REQUIRED_OBSERVATIONS

    try:
        interval = int(interval_seconds)
    except (TypeError, ValueError):
        interval = DEFAULT_INTERVAL_SECONDS

    if interval < 1:
        interval = DEFAULT_INTERVAL_SECONDS

    instrument_map = _build_instrument_map(kite)

    observations = {
        candidate.get("Trading Symbol"): []
        for candidate in candidates
        if candidate.get("Trading Symbol")
    }

    rejected = []

    for candidate in candidates:

        symbol = candidate.get("Trading Symbol")

        if not symbol:
            rejected.append({
                "Trading Symbol": symbol,
                "Reason": "Selected candidate has no Trading Symbol.",
            })
            continue

        instrument = instrument_map.get(symbol)

        if instrument is None:
            rejected.append({
                "Trading Symbol": symbol,
                "Reason": "NFO instrument not found.",
            })

    valid_candidates = [
        candidate
        for candidate in candidates
        if candidate.get("Trading Symbol") in observations
        and candidate.get("Trading Symbol")
        not in {
            item.get("Trading Symbol")
            for item in rejected
        }
    ]

    if not valid_candidates:
        return {
            "Status": "REJECTED",
            "Reason": "No selected candidates could be resolved.",
            "Observations": observations,
            "Rejected Candidates": rejected,
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    for observation_number in range(
        1,
        required_count + 1,
    ):

        print()
        print("=" * 100)
        print(
            "V21.2.22-B.2 DETAILED EVIDENCE "
            f"{observation_number}/{required_count}"
        )
        print(
            f"Timestamp: {_timestamp()}"
        )
        print("=" * 100)

        nifty_spot = _get_nifty_spot(kite)

        if nifty_spot is None:
            print(
                "NIFTY spot unavailable. "
                "Observation rejected."
            )
        else:

            symbols = [
                f"NFO:{candidate['Trading Symbol']}"
                for candidate in valid_candidates
            ]

            try:
                quote_response = kite.quote(
                    symbols
                )
            except Exception as exc:
                print(
                    "Quote error:",
                    type(exc).__name__,
                    str(exc),
                )
                quote_response = {}

            for candidate in valid_candidates:

                symbol = candidate[
                    "Trading Symbol"
                ]

                instrument = instrument_map.get(
                    symbol
                )

                if instrument is None:
                    continue

                normalized = (
                    adapt_zerodha_option_quote(
                        quote_response,
                        symbol,
                        instrument.get(
                            "instrument_token"
                        ),
                        underlying="NIFTY",
                    )
                )

                if normalized.get("Status") in (
                    "INVALID",
                    "INCOMPLETE",
                ):
                    print(
                        symbol,
                        "quote rejected:",
                        normalized.get("Reasons"),
                    )
                    continue

                record, reason = _build_record(
                    candidate,
                    instrument,
                    normalized,
                    nifty_spot,
                )

                if record is None:
                    print(
                        symbol,
                        "observation rejected:",
                        reason,
                    )
                    continue

                observations[symbol].append(
                    record
                )

                print(
                    f"{symbol}: "
                    f"Price={record['Current Price']:.2f} | "
                    f"NIFTY={record['NIFTY Spot Price']:.2f} | "
                    f"Volume={record['Volume']:.0f} | "
                    f"OI={record['Open Interest']:.0f}"
                )

        if observation_number < required_count:
            time.sleep(interval)

    incomplete = []

    for candidate in valid_candidates:

        symbol = candidate["Trading Symbol"]

        count = len(
            observations.get(symbol, [])
        )

        if count < required_count:
            incomplete.append({
                "Trading Symbol": symbol,
                "Observation Count": count,
                "Required": required_count,
                "Reason": (
                    "Insufficient complete detailed "
                    "observations."
                ),
            })

    if incomplete:
        return {
            "Status": "REJECTED",
            "Reason": (
                "One or more selected candidates "
                "did not produce the required "
                "complete detailed observation history."
            ),
            "Observation Count": required_count,
            "Observations": observations,
            "Incomplete Candidates": incomplete,
            "Rejected Candidates": rejected,
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    return {
        "Status": "DETAILED_EVIDENCE_COMPLETE",
        "Observation Count": required_count,
        "Candidate Count": len(valid_candidates),
        "Observations": observations,
        "Rejected Candidates": rejected,
        "Live Order": LIVE_ORDER,
        "Paper Trade": PAPER_TRADE,
    }


def print_detailed_evidence(
    result: Dict[str, Any],
) -> None:

    print()
    print("=" * 110)
    print("V21.2.22-B.2 DETAILED EVIDENCE RESULT")
    print("=" * 110)

    print(
        "Status:",
        result.get("Status"),
    )

    print(
        "Observation Count:",
        result.get("Observation Count", 0),
    )

    print(
        "Candidate Count:",
        result.get("Candidate Count", 0),
    )

    print(
        "Safety:",
        "LIVE_ORDER=False | PAPER_TRADE=False",
    )

    observations = result.get(
        "Observations",
        {},
    )

    for symbol, history in observations.items():

        print()
        print(
            f"{symbol}: "
            f"{len(history)} observations"
        )

        for item in history:

            print(
                f"  {item.get('Timestamp')} | "
                f"Price={item.get('Current Price')} | "
                f"NIFTY={item.get('NIFTY Spot Price')} | "
                f"Volume={item.get('Volume')} | "
                f"OI={item.get('Open Interest')}"
            )
