"""
JKJ AI Trader
V21.2.18 — Early Surge Scanner Test

Observation only.
No live orders.
No paper trades.
"""

from modules.intraday_zerodha_session_manager import (
    get_kite_session,
)

from modules.nifty_option_v21_2_18_early_surge_scanner import (
    scan_current_nifty_options,
    run_early_surge_session,
)


def main():

    print("=" * 70)
    print("JKJ AI TRADER")
    print("V21.2.18 EARLY SURGE / ACCELERATION SCANNER")
    print("=" * 70)

    session = get_kite_session()

    if session.get("Kite") is None:
        print("SESSION REJECTED")
        print(
            session.get(
                "Reason",
                "Zerodha session unavailable.",
            )
        )
        return

    kite = session["Kite"]

    print()
    print("ZERODHA SESSION:", session.get("Status"))
    print()

    print("===== INITIAL SCAN =====")

    initial = scan_current_nifty_options(
        kite,
        strikes_each_side=10,
    )

    print(
        "Initial Status:",
        initial.get("Status"),
    )

    print(
        "NIFTY Spot:",
        initial.get("NIFTY Spot"),
    )

    print(
        "Expiry:",
        initial.get("Expiry"),
    )

    print(
        "Universe Count:",
        initial.get("Universe Count"),
    )

    print()

    candidates = initial.get(
        "Candidates",
        [],
    )

    print(
        "Initial Candidates:",
        len(candidates),
    )

    for item in candidates:

        print(
            item["Trading Symbol"],
            "|",
            item["Option Type"],
            "|",
            "Price:",
            item["Latest Price"],
            "|",
            "Daily:",
            f"{item['Daily Change %']:.2f}%",
            "|",
            item["Final Classification"],
        )

    print()
    print("=" * 70)
    print("STARTING 5-MINUTE EARLY SURGE OBSERVATION")
    print("NO LIVE ORDER")
    print("NO PAPER TRADE")
    print("=" * 70)
    print()

    result = run_early_surge_session(
        kite,
        window_seconds=60,
        interval_seconds=15,
        strikes_each_side=10,
    )

    print()
    print("=" * 70)
    print("V21.2.18 RESULT")
    print("=" * 70)

    print(
        "Status:",
        result.get("Status"),
    )

    print(
        "Observation Count:",
        result.get("Observation Count"),
    )

    print(
        "Universe Count:",
        result.get("Universe Count"),
    )

    print(
        "Candidate Count:",
        len(result.get("Candidates", [])),
    )

    print()

    for item in result.get(
        "Candidates",
        [],
    ):

        print(
            item["Trading Symbol"],
            "|",
            item["Option Type"],
            "|",
            "Current:",
            item["Latest Price"],
            "|",
            "Previous Close:",
            item["Previous Close"],
            "|",
            "Daily:",
            f"{item['Daily Change %']:.2f}%",
            "|",
            "5m:",
            (
                f"{item['Window Change %']:.2f}%"
                if isinstance(
                    item["Window Change %"],
                    (int, float),
                )
                else "N/A"
            ),
            "|",
            "Reversal:",
            item["Weak To Strong Reversal"],
            "|",
            "Class:",
            item["Window Classification"],
        )

    print()
    print(
        "Live Order:",
        result.get("Live Order"),
    )

    print(
        "Paper Trade:",
        result.get("Paper Trade"),
    )


if __name__ == "__main__":
    main()
