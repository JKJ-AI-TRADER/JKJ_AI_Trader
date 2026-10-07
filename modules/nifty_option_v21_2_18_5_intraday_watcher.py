"""
JKJ AI Trader
V21.2.18.5.2 - Repeated Intraday Opportunity Watcher

Purpose:
    Run repeated real-market early-surge scans and preserve
    the developing candidate history.

Safety:
    - Observation only
    - No live orders
    - No paper trades
    - No entry decisions
    - No exit decisions
"""

import time
from typing import Any, Dict

from modules.nifty_option_v21_2_18_early_surge_scanner import (
    scan_current_nifty_options,
)

from modules.nifty_option_v21_2_18_5_candidate_history import (
    create_candidate_history,
    record_scan,
    get_history_summary,
)


LIVE_ORDER = False
PAPER_TRADE = False

DEFAULT_SCAN_COUNT = 3
DEFAULT_INTERVAL_SECONDS = 60
DEFAULT_STRIKES_EACH_SIDE = 15


def run_intraday_watcher(
    kite,
    scan_count: int = DEFAULT_SCAN_COUNT,
    interval_seconds: int = DEFAULT_INTERVAL_SECONDS,
    strikes_each_side: int = DEFAULT_STRIKES_EACH_SIDE,
) -> Dict[str, Any]:
    """
    Run repeated early-surge scans and preserve candidate history.
    """

    if scan_count < 1:
        return {
            "Status": "REJECTED",
            "Reason": "scan_count must be at least 1.",
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    if interval_seconds < 0:
        return {
            "Status": "REJECTED",
            "Reason": "interval_seconds cannot be negative.",
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    if strikes_each_side < 1:
        return {
            "Status": "REJECTED",
            "Reason": "strikes_each_side must be at least 1.",
            "Live Order": LIVE_ORDER,
            "Paper Trade": PAPER_TRADE,
        }

    history = create_candidate_history()

    scan_records = []

    print()
    print("=" * 75)
    print("JKJ V21.2.18.5.2 INTRADAY OPPORTUNITY WATCHER")
    print("=" * 75)

    print(f"Scan Count: {scan_count}")
    print(f"Interval: {interval_seconds} seconds")
    print(f"Strikes Each Side: {strikes_each_side}")
    print("Live Order: False")
    print("Paper Trade: False")

    for scan_number in range(
        1,
        scan_count + 1,
    ):

        print()
        print("-" * 75)
        print(
            f"SCAN {scan_number}/{scan_count}"
        )
        print("-" * 75)

        started = time.time()

        try:

            result = scan_current_nifty_options(
                kite,
                strikes_each_side=strikes_each_side,
            )

        except Exception as exc:

            print(
                "SCAN ERROR:",
                type(exc).__name__,
                str(exc),
            )

            scan_records.append(
                {
                    "Scan Number": scan_number,
                    "Status": "SCAN_ERROR",
                    "Error": str(exc),
                }
            )

        else:

            history_result = record_scan(
                history,
                result,
            )

            scan_record = {
                "Scan Number": scan_number,
                "Status": result.get(
                    "Status"
                ),
                "NIFTY Spot": result.get(
                    "NIFTY Spot"
                ),
                "Expiry": result.get(
                    "Expiry"
                ),
                "Universe Count": result.get(
                    "Universe Count"
                ),
                "Candidate Count": len(
                    result.get(
                        "Candidates",
                        [],
                    )
                ),
                "History Recorded": history_result.get(
                    "Candidates Recorded",
                    0,
                ),
            }

            scan_records.append(
                scan_record
            )

            print(
                "Status:",
                scan_record["Status"],
            )

            print(
                "NIFTY Spot:",
                scan_record["NIFTY Spot"],
            )

            print(
                "Expiry:",
                scan_record["Expiry"],
            )

            print(
                "Universe:",
                scan_record["Universe Count"],
            )

            print(
                "Candidates:",
                scan_record["Candidate Count"],
            )

            print(
                "History Recorded:",
                scan_record["History Recorded"],
            )

        if scan_number < scan_count:

            elapsed = time.time() - started

            wait_time = max(
                0,
                interval_seconds - elapsed,
            )

            print(
                f"Waiting {wait_time:.1f} seconds..."
            )

            time.sleep(wait_time)

    summary = get_history_summary(
        history
    )

    print()
    print("=" * 75)
    print("WATCHER COMPLETE")
    print("=" * 75)

    print(
        "Scans Completed:",
        len(scan_records),
    )

    print(
        "Tracked Symbols:",
        summary.get(
            "Tracked Symbols"
        ),
    )

    print(
        "Total Candidate Observations:",
        summary.get(
            "Total Observations"
        ),
    )

    if summary.get("Symbols"):

        print()
        print("TRACKED SYMBOLS:")

        for symbol in summary[
            "Symbols"
        ]:
            print(
                " ",
                symbol,
            )

    return {
        "Status": "WATCHER_COMPLETE",
        "Scan Count": scan_count,
        "Interval Seconds": interval_seconds,
        "Strikes Each Side": strikes_each_side,
        "Scan Records": scan_records,
        "Candidate History": history,
        "History Summary": summary,
        "Live Order": LIVE_ORDER,
        "Paper Trade": PAPER_TRADE,
    }
