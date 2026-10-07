"""
JKJ AI Trader
V21.2.18 Genuine 09:15 Baseline Runner

Purpose:
    Repeatedly call the existing V21.2.18 daily orchestrator
    during the morning transition so that the genuine 09:15
    baseline is actually captured.

Safety:
    - No live orders
    - No paper trades
    - No trading decisions
    - Does not create a synthetic baseline
    - Reuses the existing V21.2.18 orchestrator
    - Does not modify the baseline capture logic
"""

import time
from datetime import datetime, time as dt_time
from zoneinfo import ZoneInfo

from modules.nifty_option_v21_2_18_daily_orchestrator import (
    run_v21_2_18_daily_orchestrator,
)
from modules.nifty_option_v21_2_18_baseline_store import (
    load_today_baseline,
)


IST = ZoneInfo("Asia/Kolkata")

RUN_START = dt_time(9, 13, 30)
RUN_END = dt_time(9, 16, 30)

POLL_INTERVAL_SECONDS = 10


def run_baseline_runner():
    """
    Run the controlled baseline-capture polling loop.
    """

    print("=" * 70)
    print("JKJ V21.2.18 — GENUINE 09:15 BASELINE RUNNER")
    print("=" * 70)
    print("Safety: Live Order = False")
    print("Safety: Paper Trade = False")
    print()

    while True:

        now = datetime.now(IST)
        current_clock = now.time()

        # -------------------------------------------------
        # Before runner window
        # -------------------------------------------------

        if current_clock < RUN_START:

            print(
                f"[{now.strftime('%H:%M:%S')}] "
                f"Waiting for baseline runner window..."
            )

            time.sleep(POLL_INTERVAL_SECONDS)
            continue

        # -------------------------------------------------
        # Runner window expired
        # -------------------------------------------------

        if current_clock > RUN_END:

            baseline = load_today_baseline()

            if baseline is not None:
                print()
                print("09:15 BASELINE: AVAILABLE")
                print("Baseline Type:",
                      baseline.get("Baseline Type"))
                print("Baseline Time:",
                      baseline.get("Baseline Time"))
                print("Captured At:",
                      baseline.get("Captured At"))
            else:
                print()
                print("09:15 BASELINE: NOT AVAILABLE")

            print()
            print("BASELINE RUNNER: COMPLETE")
            return

        # -------------------------------------------------
        # Already captured?
        # -------------------------------------------------

        baseline = load_today_baseline()

        if baseline is not None:

            print()
            print("09:15 BASELINE CAPTURE CONFIRMED")
            print("Baseline Type:",
                  baseline.get("Baseline Type"))
            print("Baseline Time:",
                  baseline.get("Baseline Time"))
            print("Captured At:",
                  baseline.get("Captured At"))

            print()
            print("BASELINE RUNNER: COMPLETE")
            return

        # -------------------------------------------------
        # Call existing orchestrator
        # -------------------------------------------------

        print()
        print(
            f"[{now.strftime('%H:%M:%S')}] "
            "Calling V21.2.18 daily orchestrator..."
        )

        try:

            result = run_v21_2_18_daily_orchestrator(
                current_time=now,
                strikes_each_side=10,
                window_seconds=60,
                interval_seconds=15,
            )

            print(
                "Orchestrator Status:",
                result.get("Status"),
            )

            print(
                "Baseline Status:",
                result.get("Baseline Status"),
            )

        except Exception as exc:

            print(
                "ORCHESTRATOR ERROR:",
                type(exc).__name__,
                str(exc),
            )

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    run_baseline_runner()
