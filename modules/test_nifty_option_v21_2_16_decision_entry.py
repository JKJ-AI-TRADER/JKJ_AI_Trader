"""
JKJ AI Trader
V21.2.16 — Unified Decision & Entry Test

Uses ONE V21.2.15 unified observation session
and processes the resulting observations through:

V12.6 -> V12.7 -> V12.8 -> V12.9 -> V13.1 -> V13.2

Safety:
- No live order
- No paper trade
- No second observation session
"""

from modules.jkj_daily_zerodha_auth import authenticate_today

from modules.nifty_option_v21_2_15_unified_observation import (
    capture_unified_observation_session,
)

from modules.nifty_option_v21_2_16_decision_entry import (
    evaluate_unified_decision_entry,
)

from modules.nifty_option_v21_2_candidate_preparation import (
    prepare_nifty_candidates,
)


def main():

    print("=" * 70)
    print("V21.2.16 UNIFIED DECISION + ENTRY TEST")
    print("=" * 70)

    # --------------------------------------------------
    # Step 1 — Prepare candidates
    # --------------------------------------------------

    preparation = prepare_nifty_candidates(
        contracts_per_side=2
    )

    if preparation.get("Status") != "CANDIDATES_READY":
        print("Candidate preparation failed.")
        print(preparation)
        return

    candidates = preparation.get("All Candidates", [])

    if not candidates:
        print("No candidates available.")
        return

    print(
        f"Candidates prepared: {len(candidates)}"
    )

    # --------------------------------------------------
    # Step 2 — Authenticate once
    # --------------------------------------------------

    session = authenticate_today()

    if session.get("Status") not in {
        "SESSION_REUSED",
        "AUTHENTICATED_AND_SAVED",
    }:
        print("Zerodha authentication failed.")
        print(session)
        return

    kite = session.get("Kite")

    if kite is None:
        print("Kite session unavailable.")
        return

    print(
        f"Zerodha Session: {session.get('Status')}"
    )

    # --------------------------------------------------
    # Step 3 — ONE unified observation session
    # --------------------------------------------------

    print()
    print("Starting ONE V21.2.15 unified observation session...")
    print()

    unified_observation = (
        capture_unified_observation_session(
            kite,
            candidates,
            observation_count=4,
            interval_seconds=10,
        )
    )

    print(
        "Unified Observation:",
        unified_observation.get("Status"),
    )

    print(
        "Observation Count:",
        unified_observation.get("Observation Count"),
    )

    print(
        "Movement Intervals:",
        unified_observation.get("Movement Intervals"),
    )

    print(
        "Contract Count:",
        unified_observation.get("Contract Count"),
    )

    if unified_observation.get("Status") != (
        "UNIFIED_OBSERVATION_COMPLETE"
    ):
        print("Unified observation failed.")
        return

    # --------------------------------------------------
    # Step 4 — V21.2.16
    # --------------------------------------------------

    print()
    print("Running V21.2.16...")
    print()

    result = evaluate_unified_decision_entry(
        unified_observation
    )

    print("=" * 70)
    print("V21.2.16 RESULT")
    print("=" * 70)

    print("Status:", result.get("Status"))
    print("Contract Count:", result.get("Contract Count"))
    print(
        "New Market Observations:",
        result.get("New Market Observations"),
    )
    print("Live Order:", result.get("Live Order"))
    print("Paper Trade:", result.get("Paper Trade"))

    print()
    print("-" * 70)
    print("CONTRACT RESULTS")
    print("-" * 70)

    results = result.get("Results", [])

    for item in results:

        print()
        print(
            "Trading Symbol:",
            item.get("Trading Symbol"),
        )

        print(
            "Option Type:",
            item.get("Option Type"),
        )

        print(
            "Option Direction:",
            item.get("Option Direction"),
        )

        print(
            "Momentum Confirmation:",
            item.get("Momentum Confirmation"),
        )

        print(
            "Market Context:",
            item.get("Market Context"),
        )

        print(
            "Momentum Context:",
            item.get("Momentum Context"),
        )

        print(
            "Opportunity Classification:",
            item.get("Opportunity Classification"),
        )

        print(
            "Opportunity Strength:",
            item.get("Opportunity Strength"),
        )

        print(
            "Risk Classification:",
            item.get("Risk Classification"),
        )

        print(
            "Trade Quality:",
            item.get("Trade Quality"),
        )

        print(
            "Entry Qualification:",
            item.get("Entry Qualification"),
        )

    print()
    print("=" * 70)
    print("V21.2.16 TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
