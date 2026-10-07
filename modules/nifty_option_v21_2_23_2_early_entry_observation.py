"""
JKJ AI Trader
V21.2.23.2 Early Entry Observation

Purpose:
- Deep-observe the small set of candidates selected by V21.2.23.1.
- Examine whether a developing option move is becoming
  an early-entry candidate.
- Evaluate movement, persistence, acceleration and NIFTY direction.
- Report premium separately for risk review.

Safety:
- NO LIVE ORDERS
- NO PAPER TRADES
- NO BUY / SELL
- NO POSITION SIZING
- NO STOP / TARGET
"""

from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Any, Dict, List
import time


LIVE_ORDER = False
PAPER_TRADE = False

DEFAULT_OBSERVATIONS = 4
DEFAULT_INTERVAL_SECONDS = 15

# This is deliberately a REVIEW threshold, not a BUY threshold.
DEFAULT_REVIEW_PREMIUM = 100.0


def _now_ist() -> datetime:
    return datetime.now(ZoneInfo("Asia/Kolkata"))


def _get_nifty_spot(kite) -> float:
    data = kite.ltp(["NSE:NIFTY 50"])
    quote = data.get("NSE:NIFTY 50", {})
    price = quote.get("last_price")

    if price is None:
        raise RuntimeError("Unable to obtain NIFTY spot.")

    return float(price)


def _quote_candidates(kite, candidates: List[Dict[str, Any]]):
    symbols = [
        f"NFO:{item['Trading Symbol']}"
        for item in candidates
        if item.get("Trading Symbol")
    ]

    if not symbols:
        return {}

    return kite.quote(symbols)


def _movement(previous: float, current: float) -> float:
    if previous <= 0:
        return 0.0

    return ((current - previous) / previous) * 100.0


def observe_selected_candidates(
    kite,
    selection_result: Dict[str, Any],
    observation_count: int = DEFAULT_OBSERVATIONS,
    interval_seconds: int = DEFAULT_INTERVAL_SECONDS,
    review_premium: float = DEFAULT_REVIEW_PREMIUM,
) -> Dict[str, Any]:

    if selection_result.get("Status") != (
        "DISCOVERY_CANDIDATE_SELECTION_COMPLETE"
    ):
        return {
            "Status": "EARLY_ENTRY_OBSERVATION_REJECTED",
            "Reason": "Invalid V21.2.23.1 selection result.",
            "Live Order": False,
            "Paper Trade": False,
        }

    candidates = selection_result.get(
        "Selected Candidates",
        [],
    )

    if not candidates:
        return {
            "Status": "EARLY_ENTRY_OBSERVATION_COMPLETE",
            "Observation Count": 0,
            "Candidates Observed": 0,
            "Early Entry Candidates": [],
            "Live Order": False,
            "Paper Trade": False,
        }

    print()
    print("=" * 70)
    print("V21.2.23.2 EARLY ENTRY OBSERVATION")
    print("=" * 70)
    print(f"Candidates: {len(candidates)}")
    print(f"Observations: {observation_count}")
    print(f"Interval: {interval_seconds} seconds")
    print(f"Premium Review Level: Rs {review_premium:.2f}")
    print("Premium level is REVIEW ONLY — NOT a BUY threshold.")
    print("Live Order: False")
    print("Paper Trade: False")

    previous_prices: Dict[str, float] = {}
    previous_movements: Dict[str, float] = {}
    observation_history: List[List[Dict[str, Any]]] = []

    initial_nifty = _get_nifty_spot(kite)

    print(f"Initial NIFTY Spot: {initial_nifty:.2f}")

    for cycle in range(1, observation_count + 1):

        nifty_spot = _get_nifty_spot(kite)
        quotes = _quote_candidates(kite, candidates)

        cycle_results = []

        nifty_move = _movement(
            initial_nifty,
            nifty_spot,
        )

        for candidate in candidates:

            symbol = candidate["Trading Symbol"]
            key = f"NFO:{symbol}"

            quote = quotes.get(key, {})
            price = quote.get("last_price")

            if price is None:
                continue

            price = float(price)

            previous = previous_prices.get(symbol)

            move = None
            acceleration = None

            if previous is not None:
                move = _movement(previous, price)

                old_move = previous_movements.get(symbol)

                if old_move is not None:
                    acceleration = move - old_move

            volume = quote.get("volume")
            oi = quote.get("oi")

            cycle_results.append(
                {
                    "Trading Symbol": symbol,
                    "Option Type": candidate.get("Option Type"),
                    "Expiry": candidate.get("Expiry"),
                    "Strike": candidate.get("Strike"),
                    "Latest Price": price,
                    "Movement %": move,
                    "Acceleration": acceleration,
                    "NIFTY Spot": nifty_spot,
                    "NIFTY Session Movement %": nifty_move,
                    "Volume": volume,
                    "Open Interest": oi,
                    "Premium Review": (
                        "WITHIN_REVIEW_LEVEL"
                        if price <= review_premium
                        else "ABOVE_REVIEW_LEVEL"
                    ),
                    "Observation Number": cycle,
                    "Observation Timestamp": _now_ist().isoformat(),
                    "Live Order": False,
                    "Paper Trade": False,
                }
            )

            previous_prices[symbol] = price

            if move is not None:
                previous_movements[symbol] = move

        observation_history.append(cycle_results)

        print()
        print(
            f"Observation {cycle}/{observation_count}: "
            f"{len(cycle_results)}/{len(candidates)}"
        )
        print(
            f"NIFTY: {nifty_spot:.2f} "
            f"({nifty_move:+.2f}% from observation start)"
        )

        ranked = sorted(
            cycle_results,
            key=lambda item: (
                -(item.get("Acceleration") or -999.0),
                -(item.get("Movement %") or -999.0),
            ),
        )

        for item in ranked[:5]:
            move = item.get("Movement %")
            accel = item.get("Acceleration")

            print(
                f"  {item['Trading Symbol']} | "
                f"Price={item['Latest Price']:.2f} | "
                f"Move="
                f"{move:.2f}%"
                if move is not None
                else
                f"  {item['Trading Symbol']} | "
                f"Price={item['Latest Price']:.2f} | "
                f"Move=N/A",
                end="",
            )

            print(
                f" | Acc="
                f"{accel:.2f}"
                if accel is not None
                else " | Acc=N/A"
            )

        if cycle < observation_count:
            time.sleep(interval_seconds)

    # ---------------------------------------------------------
    # Final early-entry observation gate
    # ---------------------------------------------------------

    final = observation_history[-1] if observation_history else []

    early_candidates = []

    for item in final:

        symbol = item["Trading Symbol"]

        price = item.get("Latest Price")
        movement = item.get("Movement %")
        acceleration = item.get("Acceleration")

        # Find first observation for the same symbol.
        first_price = None

        for observation in observation_history:
            for historical in observation:
                if historical["Trading Symbol"] == symbol:
                    first_price = historical["Latest Price"]
                    break

            if first_price is not None:
                break

        total_move = None

        if first_price and first_price > 0:
            total_move = _movement(
                first_price,
                price,
            )

        # -----------------------------------------------------
        # JKJ standard early-entry conditions.
        #
        # Premium is NOT a qualification condition.
        # Every option must meet the same movement standard.
        # -----------------------------------------------------

        positive_total_move = (
            total_move is not None and total_move > 0
        )

        positive_latest_move = (
            movement is not None and movement > 0
        )

        positive_acceleration = (
            acceleration is not None and acceleration > 0
        )

        # We do not hard-code CE/PE interpretation here.
        # Underlying confirmation is handled by V21.2.23.3.
        underlying_move = item.get(
            "NIFTY Session Movement %",
            0.0,
        )

        if (
            positive_total_move
            and positive_latest_move
            and positive_acceleration
        ):
            status = "EARLY_ENTRY_CANDIDATE"

        elif (
            positive_total_move
            or positive_latest_move
            or positive_acceleration
        ):
            status = "DEVELOPING_BUT_NOT_ENTRY_READY"

        else:
            status = "NOT_DEVELOPING"

        record = {
            **item,
            "Total Observation Movement %": total_move,
            "Early Entry Status": status,
            "Underlying Movement": underlying_move,
            "Entry Evaluation": "OBSERVATION_ONLY",
            "Live Order": False,
            "Paper Trade": False,
        }

        if status == "EARLY_ENTRY_CANDIDATE":
            early_candidates.append(record)

    early_candidates.sort(
        key=lambda item: (
            -(item.get("Acceleration") or 0.0),
            -(item.get("Total Observation Movement %") or 0.0),
        )
    )

    print()
    print("=" * 70)
    print("V21.2.23.2 EARLY ENTRY OBSERVATION RESULT")
    print("=" * 70)

    print(
        f"Early Entry Candidates: "
        f"{len(early_candidates)}"
    )

    for rank, item in enumerate(
        early_candidates[:10],
        start=1,
    ):
        print(
            f"{rank:02d}. "
            f"{item['Trading Symbol']} | "
            f"Price={item['Latest Price']:.2f} | "
            f"Move={item.get('Total Observation Movement %', 0.0):.2f}% | "
            f"Last Move={item.get('Movement %', 0.0):.2f}% | "
            f"Acceleration={item.get('Acceleration', 0.0):.2f} | "
            f"NIFTY={item.get('NIFTY Session Movement %', 0.0):+.2f}%"
        )

    print()
    print("IMPORTANT:")
    print("Early Entry Candidate != BUY")
    print("No order was generated.")
    print("No paper trade was generated.")
    print("No position sizing was performed.")
    print("No stop or target was generated.")

    return {
        "Status": "EARLY_ENTRY_OBSERVATION_COMPLETE",
        "Initial NIFTY Spot": initial_nifty,
        "Candidates Observed": len(candidates),
        "Observation Count": len(observation_history),
        "Observation History": observation_history,
        "Early Entry Candidates": early_candidates,
        "Review Premium": review_premium,
        "Next Stage": "EVIDENCE / ENTRY QUALIFICATION",
        "Live Order": False,
        "Paper Trade": False,
    }
