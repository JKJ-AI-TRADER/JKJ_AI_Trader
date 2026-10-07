"""
JKJ AI Trader
V21.2.17 — Real-Market Integration Test

Flow:
    Candidate Preparation
        ↓
    Zerodha Session
        ↓
    ONE V21.2.15 Unified Observation Session
        ↓
    V21.2.16 Decision + Entry
        ↓
    V21.2.17 Risk + Stop + Targets

No second observation session.
No live orders.
No paper trades.
"""

from modules.nifty_option_v21_2_candidate_preparation import (
    prepare_nifty_candidates,
)

from modules.jkj_daily_zerodha_auth import (
    authenticate_today,
)

from modules.nifty_option_v21_2_15_unified_observation import (
    capture_unified_observation_session,
)

from modules.nifty_option_v21_2_16_decision_entry import (
    evaluate_unified_decision_entry,
)

from modules.nifty_option_v21_2_17_risk_stop_targets import (
    evaluate_real_market_risk_stop_targets,
)


def main():

    print()
    print("=" * 70)
    print("V21.2.17 REAL-MARKET RISK + STOP + TARGET TEST")
    print("=" * 70)

    # ---------------------------------------------------------
    # 1. Prepare today's NIFTY candidates
    # ---------------------------------------------------------

    candidate_result = prepare_nifty_candidates(
        contracts_per_side=2
    )

    print()
    print("Candidate Preparation:",
          candidate_result.get("Status"))

    if candidate_result.get("Status") != "CANDIDATES_READY":
        print("Candidate preparation failed.")
        print(candidate_result)
        return

    contracts = candidate_result.get("All Candidates")

    if not isinstance(contracts, list) or not contracts:
        print("No candidate contracts available.")
        return

    print("Candidate Count:", len(contracts))

    # ---------------------------------------------------------
    # 2. Authenticate / reuse today's Zerodha session
    # ---------------------------------------------------------

    session_result = authenticate_today()

    print("Zerodha Session:",
          session_result.get("Status"))

    if session_result.get("Status") not in {
        "SESSION_REUSED",
        "AUTHENTICATED_AND_SAVED",
    }:
        print("Zerodha authentication failed.")
        print(session_result)
        return

    kite = session_result.get("Kite")

    if kite is None:
        print("Kite session object missing.")
        return

    # ---------------------------------------------------------
    # 3. ONE unified observation session
    # ---------------------------------------------------------

    print()
    print("Starting ONE V21.2.15 observation session...")
    print("Observation Count: 4")
    print("Movement Intervals: 3")

    unified_observation = capture_unified_observation_session(
        kite,
        contracts,
        observation_count=4,
        interval_seconds=10,
    )

    print()
    print("Unified Observation:",
          unified_observation.get("Status"))

    if (
        unified_observation.get("Status")
        != "UNIFIED_OBSERVATION_COMPLETE"
    ):
        print("Unified observation failed.")
        print(unified_observation)
        return

    print("Observation Count:",
          unified_observation.get("Observation Count"))

    print("Movement Intervals:",
          unified_observation.get("Movement Intervals"))

    print("Contract Count:",
          unified_observation.get("Contract Count"))

    # ---------------------------------------------------------
    # 4. V21.2.16 Decision + Entry
    # ---------------------------------------------------------

    print()
    print("Evaluating V21.2.16 Decision + Entry...")

    decision_entry = evaluate_unified_decision_entry(
        unified_observation
    )

    print("Decision Entry:",
          decision_entry.get("Status"))

    if (
        decision_entry.get("Status")
        != "DECISION_ENTRY_COMPLETE"
    ):
        print("Decision entry evaluation failed.")
        print(decision_entry)
        return

    # ---------------------------------------------------------
    # 5. V21.2.17 Risk + Stop + Targets
    # ---------------------------------------------------------

    print()
    print("Evaluating V21.2.17 Risk + Stop + Targets...")

    risk_stop_targets = (
        evaluate_real_market_risk_stop_targets(
            decision_entry,
            unified_observation,
        )
    )

    print("V21.2.17 Status:",
          risk_stop_targets.get("Status"))

    print("Contract Count:",
          risk_stop_targets.get("Contract Count"))

    print("New Market Observations:",
          risk_stop_targets.get(
              "New Market Observations"
          ))

    print("Live Order:",
          risk_stop_targets.get("Live Order"))

    print("Paper Trade:",
          risk_stop_targets.get("Paper Trade"))

    print()
    print("-" * 70)

    for item in risk_stop_targets.get("Results", []):

        print("Trading Symbol:",
              item.get("Trading Symbol"))

        print("Status:",
              item.get("Status"))

        # -----------------------------------------------------
        # V21.2.16 Decision + Entry diagnostic fields
        # -----------------------------------------------------

        print("Option Direction:",
              item.get("Option Direction"))

        print("Momentum Confirmation:",
              item.get("Momentum Confirmation"))

        print("Market Context:",
              item.get("Market Context"))

        print("Movement Relationship:",
              item.get("Movement Relationship"))

        print("Momentum Context:",
              item.get("Momentum Context"))

        print("Opportunity Classification:",
              item.get("Opportunity Classification"))

        print("Opportunity Strength:",
              item.get("Opportunity Strength"))

        print("Risk Classification:",
              item.get("Risk Classification"))

        print("Trade Quality:",
              item.get("Trade Quality"))

        print("Entry Qualification:",
              item.get("Entry Qualification"))

        # -----------------------------------------------------
        # V21.2.17 Risk + Stop diagnostics
        # -----------------------------------------------------

        print("Entry Risk Context:",
              item.get("Entry Risk Context"))

        print("Stop-Loss Context:",
              item.get("Stop-Loss Context"))

        print("Observation Count:",
              item.get("Observation Count"))

        print("Price History:",
              item.get("Price History"))

        print("Entry Price:",
              item.get("Entry Price"))

        print("Structural Low:",
              item.get("Structural Low"))

        print("Stop Price:",
              item.get("Stop Price"))

        print("Stop Distance:",
              item.get("Stop Distance"))

        print("Target 1:",
              item.get("Target 1"))

        print("Target 2:",
              item.get("Target 2"))

        print("Target 3:",
              item.get("Target 3"))

        print("Live Order:",
              item.get("Live Order"))

        print("Paper Trade:",
              item.get("Paper Trade"))

        print("-" * 70)


if __name__ == "__main__":
    main()
