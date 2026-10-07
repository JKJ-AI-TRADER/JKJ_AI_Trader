import csv
import os
import sys
from collections import defaultdict

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from modules.nifty_option_early_surge_event_timeline import (
    build_event_timeline_from_observations,
)


CSV_FILE = os.path.join(
    PROJECT_ROOT,
    "nifty_option_observations.csv",
)


def load_histories():
    histories = defaultdict(list)

    with open(
        CSV_FILE,
        newline="",
        encoding="utf-8",
    ) as handle:

        reader = csv.DictReader(handle)

        for row in reader:

            symbol = row.get("Trading Symbol")

            if not symbol:
                continue

            try:
                price = float(
                    row.get("Current Price")
                )
            except (TypeError, ValueError):
                continue

            histories[symbol].append(
                {
                    "Status": "RECORDED",
                    "Trading Symbol": symbol,
                    "Observation Number": (
                        len(histories[symbol]) + 1
                    ),
                    "Timestamp": row.get(
                        "Timestamp"
                    ),
                    "Current Price": price,
                }
            )

    return histories


def main():

    histories = load_histories()

    print()
    print("=" * 80)
    print("JKJ V21.2.18.3 EARLY SURGE EVENT TIMELINE")
    print("=" * 80)

    for symbol, observations in histories.items():

        print()
        print("=" * 80)
        print(symbol)
        print("=" * 80)

        timeline = (
            build_event_timeline_from_observations(
                observations
            )
        )

        print(
            "Status:",
            timeline.get("Status"),
        )

        print(
            "Observation Count:",
            timeline.get(
                "Observation Count"
            ),
        )

        print(
            "Overall State:",
            timeline.get(
                "Overall State"
            ),
        )

        print(
            "Latest State:",
            timeline.get(
                "Latest State"
            ),
        )

        print(
            "Persistent Acceleration:",
            timeline.get(
                "Persistent Acceleration"
            ),
        )

        print(
            "Peak Price:",
            timeline.get(
                "Peak Price"
            ),
        )

        print(
            "Peak Observation:",
            timeline.get(
                "Peak Observation Number"
            ),
        )

        print()
        print("EVENT TIMELINE")
        print("-" * 80)

        for event in timeline.get(
            "Events",
            [],
        ):

            print(
                f"Obs {event.get('Observation Number'):>2} | "
                f"{event.get('Event'):<32} | "
                f"Price={event.get('Price')} | "
                f"Move={event.get('Movement %')} | "
                f"Vel={event.get('Velocity %/sec')} | "
                f"Acc={event.get('Acceleration %/sec²')}"
            )

            print(
                "       ",
                event.get("Reason"),
            )

        print()
        print(
            "EVENT COUNTS:",
            timeline.get(
                "Event Counts"
            ),
        )

        print(
            "Live Order:",
            timeline.get(
                "Live Order"
            ),
        )

        print(
            "Paper Trade:",
            timeline.get(
                "Paper Trade"
            ),
        )

    print()
    print("=" * 80)
    print("V21.2.18.3 REPLAY COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
