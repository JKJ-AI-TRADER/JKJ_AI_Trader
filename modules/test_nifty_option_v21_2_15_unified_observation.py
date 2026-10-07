"""
JKJ AI Trader
V21.2.15 — Unified Observation Session Test

Safety:
    NO LIVE ORDERS
    NO PAPER TRADE
"""

from modules.jkj_daily_zerodha_auth import (
    authenticate_today,
)

from modules.nifty_option_v21_2_candidate_preparation import (
    prepare_nifty_candidates,
)

from modules.nifty_option_v21_2_15_unified_observation import (
    capture_unified_observation_session,
)


def main():

    print("=" * 70)
    print("JKJ AI TRADER")
    print("V21.2.15 — UNIFIED REAL-MARKET OBSERVATION")
    print("=" * 70)

    # ---------------------------------------------------------
    # Zerodha session
    # ---------------------------------------------------------

    session = authenticate_today()

    if session.get("Status") not in (
        "SESSION_REUSED",
        "AUTHENTICATED_AND_SAVED",
    ):
        print("Session failed")
        print(session)
        return

    kite = session.get("Kite")

    if kite is None:
        print("Kite session object missing")
        return

    print(
        f"Session Status: {session.get('Status')}"
    )

    # ---------------------------------------------------------
    # Candidate preparation
    # ---------------------------------------------------------

    preparation = prepare_nifty_candidates(
        contracts_per_side=2,
    )

    if preparation.get("Status") != (
        "CANDIDATES_READY"
    ):
        print("Candidate preparation failed")
        print(preparation)
        return

    candidates = preparation.get(
        "All Candidates"
    )

    if not isinstance(candidates, list):
        print("All Candidates list missing")
        return

    print(
        f"NIFTY Spot: "
        f"{preparation.get('NIFTY Spot')}"
    )

    print(
        f"Expiry: "
        f"{preparation.get('Expiry')}"
    )

    print(
        f"Candidate Count: "
        f"{len(candidates)}"
    )

    for candidate in candidates:
        print(
            f" - {candidate.get('tradingsymbol')} | "
            f"{candidate.get('instrument_type')} | "
            f"Strike {candidate.get('strike')}"
        )

    # ---------------------------------------------------------
    # Unified observation session
    # ---------------------------------------------------------

    result = capture_unified_observation_session(
        kite,
        candidates,
        observation_count=4,
        interval_seconds=10,
    )

    print()
    print("V21.2.15 RESULT")
    print("-" * 70)

    print(
        f"Status: {result.get('Status')}"
    )

    if result.get("Status") != (
        "UNIFIED_OBSERVATION_COMPLETE"
    ):
        print(
            f"Reason: {result.get('Reason')}"
        )

        print(
            f"Live Order: "
            f"{result.get('Live Order')}"
        )

        print(
            f"Paper Trade: "
            f"{result.get('Paper Trade')}"
        )

        print()
        print("V21.2.15 TEST INCOMPLETE")
        return

    print(
        f"Observation Count: "
        f"{result.get('Observation Count')}"
    )

    print(
        f"Movement Intervals: "
        f"{result.get('Movement Intervals')}"
    )

    print(
        f"Interval Seconds: "
        f"{result.get('Interval Seconds')}"
    )

    print(
        f"Contract Count: "
        f"{result.get('Contract Count')}"
    )

    observations_by_contract = result.get(
        "Observations By Contract",
        {},
    )

    for identity, history in (
        observations_by_contract.items()
    ):

        print()
        print(
            f"{identity[0]}:"
        )

        print(
            f"  Observations: "
            f"{len(history)}"
        )

        for observation in history:

            print(
                f"  Price: "
                f"{observation.get('Current Price')} | "
                f"NIFTY: "
                f"{observation.get('NIFTY Spot Price')} | "
                f"Time: "
                f"{observation.get('Observation Timestamp')}"
            )

    print()
    print(
        f"Live Order: "
        f"{result.get('Live Order')}"
    )

    print(
        f"Paper Trade: "
        f"{result.get('Paper Trade')}"
    )

    print()
    print("V21.2.15 TEST PASS")


if __name__ == "__main__":
    main()