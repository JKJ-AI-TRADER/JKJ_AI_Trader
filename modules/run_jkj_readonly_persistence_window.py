"""Read-only option persistence capture; no trading actions."""
import math
import time
from datetime import datetime, time as clock_time
from pathlib import Path
from zoneinfo import ZoneInfo

from modules.intraday_zerodha_session_manager import read_session_token, _build_kite_from_token
from modules.intraday_zerodha_option_adapter import adapt_zerodha_option_quote
from modules.intraday_option_market_data import create_option_market_data
from modules.intraday_option_real_market_observer import observe_option_market
from modules.jkj_research_json_io import write_json_new

IST = ZoneInfo("Asia/Kolkata")
SYMBOL = "NIFTY26O1322400CE"
KEY = f"NFO:{SYMBOL}"
COUNT = 6
INTERVAL = 13


def _finite(value):
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and math.isfinite(value)
    )


def _market_open():
    current = datetime.now(IST).time().replace(tzinfo=None)
    return clock_time(9, 15) <= current <= clock_time(15, 30)


def main():
    started = datetime.now(IST)
    output = Path("research_data") / (
        f"jkj_persistence_window_{started:%Y%m%d_%H%M%S}_validated.json"
    )

    if output.exists() or output.with_name(output.name + ".tmp").exists():
        print("STOP: output path already exists; no quotes requested.")
        return

    print("JKJ READ-ONLY PERSISTENCE CAPTURE")
    print("Start:", started.isoformat(timespec="seconds"))
    print("Contract:", SYMBOL)
    print("Target:", COUNT, "snapshots,", INTERVAL, "seconds apart")
    print("Live orders: NOT CALLED | Paper trades: NOT CALLED")
    print("Baseline: NOT READ OR WRITTEN")

    if not _market_open():
        print("STOP: outside regular market hours.")
        return

    token = read_session_token()
    if not token:
        print("STOP: no saved session; no login fallback attempted.")
        return

    kite = _build_kite_from_token(token)
    token = None
    if kite is None:
        print("STOP: saved session validation failed.")
        return

    try:
        instruments = kite.instruments("NFO")
    except Exception as exc:
        print("STOP: instrument lookup failed:", type(exc).__name__)
        return

    today = datetime.now(IST).date()
    contract = next(
        (
            item for item in instruments
            if isinstance(item, dict)
            and item.get("tradingsymbol") == SYMBOL
            and item.get("name") == "NIFTY"
            and item.get("instrument_type") == "CE"
            and item.get("expiry") is not None
            and str(item.get("expiry"))[:10] >= today.isoformat()
        ),
        None,
    )
    if contract is None:
        print("STOP: eligible contract not found.")
        return
    print("Contract verified; no quote requested yet.")

    records = []
    schedule_start = time.monotonic()

    for index in range(COUNT):
        due = schedule_start + index * INTERVAL
        time.sleep(max(0.0, due - time.monotonic()))

        if not _market_open():
            print("Stopped: market session ended.")
            break

        try:
            response = kite.quote(KEY)
        except Exception as exc:
            print("Quote request failed:", type(exc).__name__)
            break

        raw = response.get(KEY) if isinstance(response, dict) else None
        if not isinstance(raw, dict) or not raw.get("last_trade_time"):
            print("Stopped: quote or last-trade time missing.")
            break

        adapted = adapt_zerodha_option_quote(
            response,
            trading_symbol=SYMBOL,
            instrument_token=contract["instrument_token"],
            underlying="NIFTY",
        )
        if not isinstance(adapted, dict) or adapted.get("Reasons"):
            print("Stopped: adapter rejected quote.")
            break

        current = adapted.get("Current Price")
        open_price = adapted.get("Open")
        high = adapted.get("High")
        low = adapted.get("Low")
        volume = adapted.get("Volume")

        if not all(_finite(v) for v in (current, open_price, high, low, volume)):
            print("Stopped: numeric data invalid.")
            break
        if min(current, open_price, high, low) <= 0 or high < low:
            print("Stopped: price range invalid.")
            break
        if not (low <= current <= high and low <= open_price <= high):
            print("Stopped: price outside reported range.")
            break
        if volume <= 0 or not float(volume).is_integer():
            print("Stopped: volume invalid.")
            break

        normalized = create_option_market_data(
            trading_symbol=SYMBOL,
            instrument_token=contract["instrument_token"],
            underlying="NIFTY",
            expiry=str(contract["expiry"])[:10],
            strike=contract["strike"],
            option_type="CE",
            current_price=current,
            open_price=open_price,
            high_price=high,
            low_price=low,
            volume=volume,
            timestamp=adapted.get("Last Trade Time"),
        )
        if normalized.get("Status") != "READY":
            print("Normalizer rejected:", normalized.get("Reasons"))
            break

        observed = observe_option_market(normalized)
        if observed.get("Status") != "READY":
            print("Observer rejected:", observed.get("Reasons"))
            break

        record = {
            "Time": datetime.now(IST),
            "Symbol": SYMBOL,
            "Price": current,
            "Open": open_price,
            "High": high,
            "Low": low,
            "Volume": volume,
            "Quote Timestamp": raw.get("timestamp"),
            "Last Trade Time": adapted.get("Last Trade Time"),
            "Normalizer": normalized["Status"],
            "Observer": observed["Status"],
        }
        records.append(record)
        print(
            f"Snapshot {index + 1}/{COUNT}: "
            f"₹{current:.2f} | normalizer=READY | observer=READY"
        )

    gaps = [
        (right["Time"] - left["Time"]).total_seconds()
        for left, right in zip(records, records[1:])
    ]
    duration = (
        (records[-1]["Time"] - records[0]["Time"]).total_seconds()
        if len(records) >= 2 else 0.0
    )
    complete = (
        len(records) == COUNT
        and duration >= 60
        and all(0 < gap <= 15 for gap in gaps)
    )

    payload = {
        "Schema": "JKJ_PERSISTENCE_WINDOW_V1",
        "Trading Date": datetime.now(IST).date().isoformat(),
        "Symbol": SYMBOL,
        "Target Samples": COUNT,
        "Target Interval Seconds": INTERVAL,
        "Live Observations": records,
        "Capture Gaps Seconds": gaps,
        "Duration Seconds": duration,
        "Status": "COMPLETE" if complete else "INCOMPLETE",
        "Trading Decision": False,
        "Live Order": False,
        "Paper Trade": False,
        "Baseline Write": False,
    }

    saved = write_json_new(output, payload)
    print("-" * 50)
    print("Saved:", saved)
    print("Accepted snapshots:", len(records), "/", COUNT)
    print("Capture gaps (seconds):", gaps)
    print("Duration (seconds):", duration)
    print("Status:", payload["Status"])
    print("Live orders: NOT CALLED | Paper trades: NOT CALLED")
    print("Baseline: NOT READ OR WRITTEN")


if __name__ == "__main__":
    main()
