"""
JKJ AI Trader
V21.2.10 — Real-Market Momentum Confirmation Test

Purpose:
Test V21.2.10 against live Zerodha market data.

Safety:
- No live orders
- No paper trades
- Observation and analysis only
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


def main():

    print("=" * 70)
    print("JKJ AI TRADER")
    print("V21.2.10 — REAL-MARKET MOMENTUM CONFIRMATION")
    print("=" * 70)

    print("\n[1] Establishing Zerodha session...")

    session_result = get_kite_session()

    if not isinstance(session_result, dict):
        print("SESSION RESULT INVALID")
        return

    print("Session Status:",
          session_result.get("Status"))

    if session_result.get("Status") not in {
        "SESSION_REUSED",
        "SESSION_CREATED",
    }:
        print("ZERODHA SESSION NOT READY")
        print(session_result)
        return

    kite = session_result.get("Kite")

    if kite is None:
        print("KITE SESSION OBJECT NOT AVAILABLE")
        return

    print("Zerodha Session: READY")

    print("\n[2] Preparing NIFTY option candidates...")

    preparation = prepare_nifty_candidates()

    print("Preparation Status:",
          preparation.get("Status"))

    if preparation.get("Status") != "CANDIDATES_READY":
        print("CANDIDATE PREPARATION FAILED")
        print(preparation)
        return

    contracts = preparation.get("All Candidates")

    if not isinstance(contracts, list) or not contracts:
        print("NO CANDIDATES AVAILABLE")
        return

    print("NIFTY Spot:",
          preparation.get("NIFTY Spot"))

    print("Expiry:",
          preparation.get("Expiry"))

    print("Candidate Count:",
          len(contracts))

    for contract in contracts:
        print(
            " -",
            contract.get("tradingsymbol"),
            "|",
            contract.get("instrument_type"),
            "| Strike:",
            contract.get("strike"),
        )

    print("\n[3] Starting V21.2.10 observation...")

    print("Observation Count: 4")
    print("Movement Intervals: 3")
    print("Interval Seconds: 10")

    print("\nIMPORTANT:")
    print("Live Order: FALSE")
    print("Paper Trade: FALSE")

    result = evaluate_real_market_momentum_confirmation(
        kite,
        contracts,
        observation_count=4,
        interval_seconds=10,
    )

    print("\n" + "=" * 70)
    print("V21.2.10 RESULT")
    print("=" * 70)

    print("Status:",
          result.get("Status"))

    print("Observation Count:",
          result.get("Observation Count"))

    print("Movement Intervals:",
          result.get("Movement Intervals"))

    print("Contract Count:",
          result.get("Contract Count"))

    print()

    for item in result.get("Results", []):

        print("-" * 70)

        print("Trading Symbol:",
              item.get("Trading Symbol"))

        print("Option Type:",
              item.get("Option Type"))

        print("Observation Count:",
              item.get("Observation Count"))

        print("Movement Intervals:",
              item.get("Movement Intervals"))

        sequence = item.get("Momentum Sequence", {})

        print("Persistence Status:",
              sequence.get("Persistence Status"))

        print("Direction Sequence:",
              sequence.get("Direction Sequence"))

        evidence = item.get("Momentum Evidence", {})

        print("Price Movement Evidence:",
              evidence.get("Price Movement Evidence"))

        print("NIFTY Movement Evidence:",
              evidence.get("NIFTY Movement Evidence"))

        print("Volume Evidence:",
              evidence.get("Volume Evidence"))

        print("Open Interest Evidence:",
              evidence.get("Open Interest Evidence"))

        confirmation = item.get(
            "Momentum Confirmation",
            {},
        )

        print("Momentum Confirmation:",
              confirmation.get(
                  "Momentum Confirmation"
              ))

        print("Live Order:",
              item.get("Live Order"))

        print("Paper Trade:",
              item.get("Paper Trade"))

    print("\n" + "=" * 70)
    print("V21.2.10 TEST COMPLETE")
    print("NO ORDERS PLACED")
    print("NO PAPER TRADES CREATED")
    print("=" * 70)


if __name__ == "__main__":
    main()
