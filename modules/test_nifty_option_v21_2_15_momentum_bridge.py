"""
JKJ AI Trader
V21.2.15 — Unified Observation → Momentum Bridge Test

Safety:
    NO LIVE ORDERS
    NO PAPER TRADE
"""

from modules.nifty_option_v21_2_15_momentum_bridge import (
    evaluate_unified_observation_momentum,
)

from modules.nifty_option_v21_2_15_unified_observation import (
    capture_unified_observation_session,
)

from modules.nifty_option_v21_2_candidate_preparation import (
    prepare_nifty_candidates,
)
from modules.jkj_daily_zerodha_auth import (
    authenticate_today,
)


def main():

    print("=" * 70)
    print("JKJ AI TRADER")
    print("V21.2.15 — UNIFIED OBSERVATION → MOMENTUM")
    print("=" * 70)

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
        print("All Candidates missing")
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
    # IMPORTANT:
    # Candidate preparation internally provides the
    # Zerodha session, but the unified observation function
    # requires the Kite object.
    #
    # We obtain it from the candidate preparation result.
    # ---------------------------------------------------------

    session = authenticate_today()

    if session.get("Status") not in (
        "SESSION_REUSED",
        "AUTHENTICATED_AND_SAVED",
    ):
        print("Zerodha session failed")
        print(session)
        return

    kite = session.get("Kite")

    if kite is None:
        print("Kite session object missing")
        return

    # ---------------------------------------------------------
    # ONE unified observation session
    # ---------------------------------------------------------

    observation_result = (
        capture_unified_observation_session(
            kite,
            candidates,
            observation_count=4,
            interval_seconds=10,
        )
    )



    if observation_result.get("Status") != (
        "UNIFIED_OBSERVATION_COMPLETE"
    ):
        print("Unified observation failed")
        print(observation_result)
        return

    print()
    print(
        "Unified Observation: "
        "UNIFIED_OBSERVATION_COMPLETE"
    )

    print(
        f"Observation Count: "
        f"{observation_result.get('Observation Count')}"
    )

    print(
        f"Movement Intervals: "
        f"{observation_result.get('Movement Intervals')}"
    )

    # ---------------------------------------------------------
    # Process SAME observations through V12.6
    # ---------------------------------------------------------

    momentum_result = (
        evaluate_unified_observation_momentum(
            observation_result
        )
    )

    print()
    print("V21.2.15 MOMENTUM RESULT")
    print("-" * 70)

    print(
        f"Status: "
        f"{momentum_result.get('Status')}"
    )

    print(
        f"Observation Count: "
        f"{momentum_result.get('Observation Count')}"
    )

    print(
        f"Movement Intervals: "
        f"{momentum_result.get('Movement Intervals')}"
    )

    print(
        f"Contract Count: "
        f"{momentum_result.get('Contract Count')}"
    )

    for result in momentum_result.get(
        "Results",
        [],
    ):

        print()

        print(
            f"{result.get('Trading Symbol')}: "
            f"{result.get('Status')}"
        )

        print(
            f"  Observation Count: "
            f"{result.get('Observation Count')}"
        )

        print(
            f"  Movement Intervals: "
            f"{result.get('Movement Intervals')}"
        )

        momentum_sequence = result.get(
            "Momentum Sequence"
        )

        if isinstance(momentum_sequence, dict):
            print(
                f"  Persistence: "
                f"{momentum_sequence.get('Persistence Status')}"
            )

            print(
                f"  Direction: "
                f"{momentum_sequence.get('Direction')}"
            )

        momentum_confirmation = result.get(
            "Momentum Confirmation"
        )

        if isinstance(
            momentum_confirmation,
            dict,
        ):
            print(
                f"  Confirmation: "
                f"{momentum_confirmation.get('Momentum Confirmation')}"
            )

    print()

    print(
        f"New Market Observations: "
        f"{momentum_result.get('New Market Observations')}"
    )

    print(
        f"Live Order: "
        f"{momentum_result.get('Live Order')}"
    )

    print(
        f"Paper Trade: "
        f"{momentum_result.get('Paper Trade')}"
    )

    if momentum_result.get("Status") == (
        "UNIFIED_MOMENTUM_COMPLETE"
    ):
        print()
        print("V21.2.15 MOMENTUM BRIDGE TEST PASS")
    else:
        print()
        print(
            "V21.2.15 MOMENTUM BRIDGE TEST INCOMPLETE"
        )


if __name__ == "__main__":
    main()