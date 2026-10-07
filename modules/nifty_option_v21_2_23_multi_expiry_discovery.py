"""
JKJ AI Trader
V21.2.23 Multi-Expiry NIFTY Option Discovery

Purpose:
- Discover NIFTY options across multiple near-term expiries.
- Observe current market movement using batched Zerodha LTP requests.
- Maintain short observation history.
- Identify developing upward movers.
- Observation only.

Safety:
- NO LIVE ORDERS
- NO PAPER TRADES
- NO BUY / SELL
- NO ENTRY / STOP / TARGET / POSITION SIZING
"""

from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Any, Dict, List


LIVE_ORDER = False
PAPER_TRADE = False

DEFAULT_EXPIRIES = 6
DEFAULT_STRIKES_EACH_SIDE = 15
DEFAULT_BATCH_SIZE = 100
DEFAULT_OBSERVATIONS = 4
DEFAULT_INTERVAL_SECONDS = 15


def _now_ist() -> datetime:
    return datetime.now(ZoneInfo("Asia/Kolkata"))


def _get_nifty_spot(kite) -> float:
    data = kite.ltp(["NSE:NIFTY 50"])
    value = data.get("NSE:NIFTY 50", {}).get("last_price")

    if value is None:
        raise RuntimeError("Unable to obtain NIFTY spot price.")

    return float(value)


def _get_near_term_expiries(
    instruments: List[Dict[str, Any]],
    expiry_count: int = DEFAULT_EXPIRIES,
) -> List[Any]:
    today = _now_ist().date()

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

    return expiries[:expiry_count]


def _build_multi_expiry_universe(
    instruments: List[Dict[str, Any]],
    nifty_spot: float,
    expiries: List[Any],
    strikes_each_side: int = DEFAULT_STRIKES_EACH_SIDE,
) -> List[Dict[str, Any]]:
    universe = []

    for expiry in expiries:
        expiry_options = [
            item
            for item in instruments
            if (
                item.get("name") == "NIFTY"
                and item.get("expiry") == expiry
                and item.get("instrument_type") in ("CE", "PE")
                and item.get("strike") is not None
                and item.get("tradingsymbol")
            )
        ]

        strikes = sorted(
            {
                float(item["strike"])
                for item in expiry_options
            }
        )

        if not strikes:
            continue

        atm_index = min(
            range(len(strikes)),
            key=lambda i: abs(strikes[i] - nifty_spot),
        )

        low_index = max(0, atm_index - strikes_each_side)
        high_index = min(
            len(strikes),
            atm_index + strikes_each_side + 1,
        )

        selected_strikes = set(strikes[low_index:high_index])

        for item in expiry_options:
            if float(item["strike"]) in selected_strikes:
                universe.append(
                    {
                        "tradingsymbol": item["tradingsymbol"],
                        "instrument_token": item.get("instrument_token"),
                        "expiry": item.get("expiry"),
                        "strike": float(item["strike"]),
                        "instrument_type": item.get("instrument_type"),
                        "name": item.get("name"),
                    }
                )

    return universe


def _chunks(items: List[str], size: int):
    for start in range(0, len(items), size):
        yield items[start:start + size]


def _ltp_batch(
    kite,
    universe: List[Dict[str, Any]],
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> Dict[str, float]:
    symbols = [
        f"NFO:{item['tradingsymbol']}"
        for item in universe
        if item.get("tradingsymbol")
    ]

    result = {}

    for batch in _chunks(symbols, batch_size):
        data = kite.ltp(batch)

        for symbol, quote in data.items():
            price = quote.get("last_price")

            if price is not None:
                result[symbol] = float(price)

    return result


def _calculate_movement(
    previous_price: float,
    current_price: float,
) -> float:
    if previous_price <= 0:
        return 0.0

    return ((current_price - previous_price) / previous_price) * 100.0


def _build_observation(
    universe: List[Dict[str, Any]],
    prices: Dict[str, float],
    previous_prices: Dict[str, float],
    observation_number: int,
) -> List[Dict[str, Any]]:
    timestamp = _now_ist().isoformat()
    results = []

    for item in universe:
        symbol = item["tradingsymbol"]
        quote_key = f"NFO:{symbol}"

        current_price = prices.get(quote_key)

        if current_price is None:
            continue

        previous_price = previous_prices.get(symbol)

        movement = None

        if previous_price is not None:
            movement = _calculate_movement(
                previous_price,
                current_price,
            )

        results.append(
            {
                "Trading Symbol": symbol,
                "Expiry": str(item["expiry"]),
                "Strike": item["strike"],
                "Option Type": item["instrument_type"],
                "Latest Price": current_price,
                "Previous Observation Price": previous_price,
                "Movement %": movement,
                "Observation Number": observation_number,
                "Observation Timestamp": timestamp,
                "Live Order": False,
                "Paper Trade": False,
            }
        )

    return results


def _rank_developing_movers(
    observation_history: List[List[Dict[str, Any]]],
) -> List[Dict[str, Any]]:
    if len(observation_history) < 2:
        return []

    previous = {
        item["Trading Symbol"]: item
        for item in observation_history[-2]
    }

    latest = observation_history[-1]

    candidates = []

    for item in latest:
        symbol = item["Trading Symbol"]
        movement = item.get("Movement %")

        if movement is None or movement <= 0:
            continue

        previous_item = previous.get(symbol)

        if previous_item is None:
            continue

        previous_movement = previous_item.get("Movement %")

        acceleration = None

        if previous_movement is not None:
            acceleration = movement - previous_movement

        candidates.append(
            {
                **item,
                "Acceleration": acceleration,
                "Discovery State": (
                    "DEVELOPING"
                    if acceleration is not None and acceleration > 0
                    else "MOVING"
                ),
            }
        )

    candidates.sort(
        key=lambda item: (
            item.get("Acceleration") or 0.0,
            item.get("Movement %") or 0.0,
        ),
        reverse=True,
    )

    return candidates


def run_multi_expiry_discovery(
    kite,
    expiry_count: int = DEFAULT_EXPIRIES,
    strikes_each_side: int = DEFAULT_STRIKES_EACH_SIDE,
    batch_size: int = DEFAULT_BATCH_SIZE,
    observation_count: int = DEFAULT_OBSERVATIONS,
    interval_seconds: int = DEFAULT_INTERVAL_SECONDS,
) -> Dict[str, Any]:
    """
    Run a short observation-only multi-expiry discovery scan.
    """

    print()
    print("=" * 70)
    print("JKJ AI TRADER — V21.2.23 MULTI-EXPIRY DISCOVERY")
    print("=" * 70)
    print("Mode: OBSERVATION ONLY")
    print("Live Order: False")
    print("Paper Trade: False")

    nifty_spot = _get_nifty_spot(kite)
    print(f"NIFTY Spot: {nifty_spot}")

    instruments = kite.instruments("NFO")

    expiries = _get_near_term_expiries(
        instruments,
        expiry_count,
    )

    print(f"Near-Term Expiries: {len(expiries)}")

    for expiry in expiries:
        print(f"  - {expiry}")

    universe = _build_multi_expiry_universe(
        instruments,
        nifty_spot,
        expiries,
        strikes_each_side,
    )

    print(f"Discovery Universe: {len(universe)} contracts")
    print(f"LTP Batch Size: {batch_size}")
    print(f"Observation Count: {observation_count}")
    print(f"Interval Seconds: {interval_seconds}")

    if not universe:
        return {
            "Status": "DISCOVERY_FAILED",
            "Reason": "No NIFTY option contracts found.",
            "Live Order": False,
            "Paper Trade": False,
        }

    observation_history = []
    previous_prices = {}

    for observation_number in range(1, observation_count + 1):

        prices = _ltp_batch(
            kite,
            universe,
            batch_size,
        )

        observations = _build_observation(
            universe,
            prices,
            previous_prices,
            observation_number,
        )

        observation_history.append(observations)

        developing = _rank_developing_movers(
            observation_history
        )

        print()
        print(
            f"Observation {observation_number}/{observation_count}: "
            f"{len(observations)}/{len(universe)}"
        )

        if developing:
            print(
                f"Positive movers: {len(developing)}"
            )

            for candidate in developing[:10]:
                print(
                    f"  {candidate['Trading Symbol']} | "
                    f"{candidate['Option Type']} | "
                    f"Movement={candidate.get('Movement %', 0.0):.2f}% | "
                    f"Acceleration="
                    f"{candidate.get('Acceleration') or 0.0:.2f} | "
                    f"{candidate['Discovery State']}"
                )
        else:
            print("Developing movers: 0")

        previous_prices = {
            item["Trading Symbol"]: item["Latest Price"]
            for item in observations
        }

        if observation_number < observation_count:
            import time
            time.sleep(interval_seconds)

    final_candidates = _rank_developing_movers(
        observation_history
    )

    print()
    print("=" * 70)
    print("V21.2.23 DISCOVERY COMPLETE")
    print("=" * 70)
    print(f"Contracts Observed: {len(universe)}")
    print(f"Observations: {len(observation_history)}")
    print(f"Developing Movers: {len(final_candidates)}")
    print("Live Order: False")
    print("Paper Trade: False")

    return {
        "Status": "MULTI_EXPIRY_DISCOVERY_COMPLETE",
        "NIFTY Spot": nifty_spot,
        "Expiries": [str(item) for item in expiries],
        "Expiry Count": len(expiries),
        "Universe Count": len(universe),
        "Observation Count": len(observation_history),
        "Batch Size": batch_size,
        "Interval Seconds": interval_seconds,
        "Observation History": observation_history,
        "Developing Candidates": final_candidates,
        "Live Order": False,
        "Paper Trade": False,
    }


if __name__ == "__main__":
    from modules.jkj_daily_zerodha_auth import authenticate_today

    result = authenticate_today()
    kite = result.get("Kite")

    if kite is None:
        print("Kite session unavailable")
        raise SystemExit(1)

    run_multi_expiry_discovery(kite)
