"""
JKJ AI Trader
V21.2.11 — Real-Market Market Context Test

Safety:
- No live orders
- No paper trades
"""

from modules.intraday_zerodha_session_manager import (
    get_kite_session,
)

from modules.nifty_option_v21_2_candidate_preparation import (
    prepare_nifty_candidates,
)

from modules.nifty_option_v21_2_momentum_confirmation import (
    evaluate_real_market_momentum_confirmation,
)

from modules.nifty_option_v21_2_11_market_context import (
    evaluate_real_market_market_context,
)


def main():

    print("=" * 70)
    print("JKJ AI TRADER")
    print("V21.2.11 — REAL-MARKET MARKET CONTEXT")
    print("=" * 70)

    # --------------------------------------------------
    # 1. Zerodha session
    # --------------------------------------------------

    print("\n[1] Establishing Zerodha session...")

    session = get_kite_session()

    print("Session Status:", session.get("Status"))

    if session.get("Status") not in {
        "SESSION_REUSED",
        "SESSION_CREATED",
    }:
        print("ERROR:", session.get("Reason"))
        return

    kite = session.get("Kite")

    if kite is None:
        print("ERROR: Kite session object unavailable.")
        return

    print("Zerodha Session: READY")

    # --------------------------------------------------
    # 2. Candidate preparation
    # --------------------------------------------------

    print("\n[2] Preparing NIFTY option candidates...")

    preparation = prepare_nifty_candidates()

    print(
        "Preparation Status:",
        preparation.get("Status"),
    )

    if preparation.get("Status") != "CANDIDATES_READY":
        print("ERROR:", preparation.get("Reason"))
        return

    contracts = preparation.get("All Candidates")

    if not contracts:
        print("ERROR: No candidate contracts available.")
        return

    print(
        "NIFTY Spot:",
        preparation.get("NIFTY Spot"),
    )

    print(
        "Expiry:",
        preparation.get("Expiry"),
    )

    print(
        "Candidate Count:",
        len(contracts),
    )

    for contract in contracts:
        print(
            " -",
            contract.get("tradingsymbol"),
            "|",
            contract.get("instrument_type"),
            "| Strike:",
            contract.get("strike"),
        )

    # --------------------------------------------------
    # 3. V21.2.10 real-market momentum confirmation
    # --------------------------------------------------

    print("\n[3] Running V21.2.10 momentum confirmation...")

    print("Observation Count: 4")
    print("Movement Intervals: 3")
    print("Interval Seconds: 10")

    print("\nIMPORTANT:")
    print("Live Order: FALSE")
    print("Paper Trade: FALSE")

    momentum_result = (
        evaluate_real_market_momentum_confirmation(
            kite,
            contracts,
            observation_count=4,
            interval_seconds=10,
        )
    )

    if momentum_result.get("Status") != (
        "MOMENTUM_CONFIRMATION_COMPLETE"
    ):
        print(
            "\nERROR: V21.2.10 failed."
        )
        print(
            momentum_result.get("Reason")
        )
        return

    print(
        "\nV21.2.10 Status:",
        momentum_result.get("Status"),
    )

    # --------------------------------------------------
    # 4. Feed each confirmed V21.2.10 result
    #    into V21.2.11
    # --------------------------------------------------

    print("\n[4] Running V21.2.11 Market Context...")

    results = momentum_result.get("Results", [])

    if not results:
        print("ERROR: No V21.2.10 results returned.")
        return

    completed = 0

    for result in results:

        print("\n" + "-" * 70)

        momentum_confirmation = result.get(
            "Momentum Confirmation"
        )

        if not isinstance(momentum_confirmation, dict):
            print("ERROR: Invalid V21.2.10 momentum confirmation result.")
            continue

        symbol = momentum_confirmation.get(
            "Trading Symbol"
        )

        print("Trading Symbol:", symbol)

        print(
            "Momentum Confirmation:",
            momentum_confirmation.get(
                "Momentum Confirmation"
            ),
        )

        print(
            "Movement Relationship:",
            momentum_confirmation.get(
                "Movement Relationship"
            ),
        )

        context_result = (
            evaluate_real_market_market_context(
                momentum_confirmation
            )
        )

        print(
            "V21.2.11 Status:",
            context_result.get("Status"),
        )

        if context_result.get("Status") != (
            "MARKET_CONTEXT_COMPLETE"
        ):
            print(
                "Reason:",
                context_result.get("Reason"),
            )
            continue

        completed += 1

        print(
            "Option Direction:",
            context_result.get(
                "Option Direction"
            ),
        )

        print(
            "Market Context:",
            context_result.get(
                "Market Context"
            ),
        )

        print(
            "Momentum Context:",
            context_result.get(
                "Momentum Context"
            ),
        )

        print(
            "Live Order:",
            context_result.get(
                "Live Order"
            ),
        )

        print(
            "Paper Trade:",
            context_result.get(
                "Paper Trade"
            ),
        )

    # --------------------------------------------------
    # 5. Final result
    # --------------------------------------------------

    print("\n" + "=" * 70)
    print("V21.2.11 TEST RESULT")
    print("=" * 70)

    print(
        "V21.2.10 Contracts:",
        len(results),
    )

    print(
        "V21.2.11 Completed:",
        completed,
    )

    print("Live Order: FALSE")
    print("Paper Trade: FALSE")

    if completed == len(results):
        print("\nV21.2.11 TEST: PASS")
    else:
        print("\nV21.2.11 TEST: REVIEW REQUIRED")

    print("=" * 70)


if __name__ == "__main__":
    main()
