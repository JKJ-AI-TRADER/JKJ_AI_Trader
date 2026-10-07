"""
JKJ AI Trader
V21.2.23.3 Real-Market Integration Test

Flow:
V21.2.23 Discovery
    ->
V21.2.23.1 Selection
    ->
V21.2.23.2 Early Entry Observation
    ->
V21.2.23.3 Underlying Confirmation

Safety:
- Observation only
- No live orders
- No paper trades
- No BUY / SELL
"""

from modules.jkj_daily_zerodha_auth import authenticate_today

from modules.nifty_option_v21_2_23_multi_expiry_discovery import (
    run_multi_expiry_discovery,
)

from modules.nifty_option_v21_2_23_1_discovery_selector import (
    select_discovery_candidates,
)

from modules.nifty_option_v21_2_23_2_early_entry_observation import (
    observe_selected_candidates,
)

from modules.nifty_option_v21_2_23_3_underlying_confirmation import (
    evaluate_underlying_confirmation_gate,
)


def main():

    print()
    print("=" * 70)
    print("V21.2.23.3 REAL-MARKET INTEGRATION TEST")
    print("=" * 70)
    print("Safety: Live Order=False")
    print("Safety: Paper Trade=False")

    # ---------------------------------------------------------
    # 1. Zerodha session
    # ---------------------------------------------------------

    auth = authenticate_today()
    kite = auth.get("Kite")

    if kite is None:
        raise RuntimeError(
            "Kite session unavailable."
        )

    # ---------------------------------------------------------
    # 2. Broad multi-expiry discovery
    # ---------------------------------------------------------

    discovery_result = run_multi_expiry_discovery(
        kite,
        expiry_count=6,
        strikes_each_side=15,
        batch_size=100,
        observation_count=4,
        interval_seconds=15,
    )

    if discovery_result.get("Status") != (
        "MULTI_EXPIRY_DISCOVERY_COMPLETE"
    ):
        raise RuntimeError(
            "V21.2.23 discovery did not complete."
        )

    # ---------------------------------------------------------
    # 3. Select strongest developing movers
    # ---------------------------------------------------------

    selection_result = select_discovery_candidates(
        discovery_result,
        max_selected=10,
    )

    if selection_result.get("Status") != (
        "DISCOVERY_CANDIDATE_SELECTION_COMPLETE"
    ):
        raise RuntimeError(
            "V21.2.23.1 selection did not complete."
        )

    # ---------------------------------------------------------
    # 4. Early-entry observation
    # ---------------------------------------------------------

    early_entry_result = observe_selected_candidates(
        kite,
        selection_result,
        observation_count=4,
        interval_seconds=15,
        review_premium=100.0,
    )

    if early_entry_result.get("Status") != (
        "EARLY_ENTRY_OBSERVATION_COMPLETE"
    ):
        raise RuntimeError(
            "V21.2.23.2 observation did not complete."
        )

    # ---------------------------------------------------------
    # 5. Underlying confirmation
    # ---------------------------------------------------------

    confirmation_result = (
        evaluate_underlying_confirmation_gate(
            early_entry_result
        )
    )

    if confirmation_result.get("Status") != (
        "UNDERLYING_CONFIRMATION_GATE_COMPLETE"
    ):
        raise RuntimeError(
            "V21.2.23.3 confirmation gate failed."
        )

    # ---------------------------------------------------------
    # 6. Final test summary
    # ---------------------------------------------------------

    confirmed = confirmation_result.get(
        "Confirmed Candidates",
        [],
    )

    rejected = confirmation_result.get(
        "Rejected Candidates",
        [],
    )

    print()
    print("=" * 70)
    print("V21.2.23.3 REAL-MARKET TEST RESULT")
    print("=" * 70)

    print(
        f"Discovery Universe: "
        f"{discovery_result.get('Universe Count')}"
    )

    print(
        f"Developing Movers: "
        f"{selection_result.get('Developing Movers Received')}"
    )

    print(
        f"Selected For Deep Observation: "
        f"{selection_result.get('Selected Candidate Count')}"
    )

    print(
        f"Early Entry Candidates: "
        f"{len(early_entry_result.get('Early Entry Candidates', []))}"
    )

    print(
        f"Underlying Confirmed: "
        f"{len(confirmed)}"
    )

    print(
        f"Underlying Rejected: "
        f"{len(rejected)}"
    )

    if confirmed:
        print()
        print("UNDERLYING-CONFIRMED CANDIDATES:")

        for item in confirmed:
            print(
                f"  {item['Trading Symbol']} | "
                f"{item.get('Option Type')} | "
                f"Option Move="
                f"{item.get('Total Observation Movement %', 0.0):.2f}% | "
                f"NIFTY Move="
                f"{item.get('NIFTY Session Movement %', 0.0):+.2f}%"
            )

    print()
    print("NEXT STAGE:")
    print("Evidence Reconciliation / Existing JKJ Evidence Standards")

    print()
    print("Live Order: False")
    print("Paper Trade: False")
    print("BUY/SELL: NOT EXECUTED")

    print()
    print(
        "V21.2.23.3 REAL-MARKET INTEGRATION TEST: PASS"
    )


if __name__ == "__main__":
    main()
