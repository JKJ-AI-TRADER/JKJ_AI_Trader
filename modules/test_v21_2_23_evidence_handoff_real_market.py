"""
JKJ AI Trader
V21.2.23 → V21.2.22-C Evidence Handoff Real-Market Test

Flow:
V21.2.23 Discovery
    ->
V21.2.23.1 Selection
    ->
V21.2.23.2 Early Entry Observation
    ->
V21.2.23.3 Underlying Confirmation
    ->
V21.2.23.4 Discovery -> Lifecycle
    ->
V21.2.20 Candidate Qualification
    ->
V21.2.22-B.1 Candidate Selection
    ->
V21.2.22-B.2 Detailed Evidence
    ->
V21.2.20 -> V21.2.16 Unified Observation
    ->
V12.6 Momentum
    ->
V21.2.22-C Evidence Reconciliation

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

from modules.nifty_option_v21_2_23_4_discovery_to_lifecycle_adapter import (
    adapt_discovery_to_lifecycle,
)

from modules.nifty_option_v21_2_20_candidate_qualification import (
    qualify_candidates,
)

from modules.nifty_option_v21_2_22_b2_detailed_evidence import (
    collect_detailed_evidence,
)

from modules.nifty_option_v21_2_20_to_v21_2_16_adapter import (
    build_unified_observation_from_qualified_candidates,
)

from modules.nifty_option_v21_2_15_momentum_bridge import (
    evaluate_unified_observation_momentum,
)

from modules.nifty_option_v21_2_22_c_evidence_reconciliation import (
    reconcile_candidates,
)


def main():

    print()
    print("=" * 80)
    print("V21.2.23 → V21.2.22-C EVIDENCE HANDOFF REAL-MARKET TEST")
    print("=" * 80)
    print("Safety: Live Order=False")
    print("Safety: Paper Trade=False")
    print("BUY/SELL: NOT EXECUTED")

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

    print()
    print(
        "Discovery Universe:",
        discovery_result.get("Universe Count"),
    )

    # ---------------------------------------------------------
    # 3. Discovery candidate selection
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

    print(
        "Discovery Selected:",
        selection_result.get(
            "Selected Candidate Count",
            len(
                selection_result.get(
                    "Selected Candidates",
                    [],
                )
            ),
        ),
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

    early_candidates = early_entry_result.get(
        "Early Entry Candidates",
        [],
    )

    print(
        "Early Entry Candidates:",
        len(early_candidates),
    )

    # ---------------------------------------------------------
    # No-candidate boundary
    #
    # If V21.2.23.2 produces no early-entry candidates,
    # there is nothing legitimate to pass into lifecycle,
    # qualification, or evidence stages.
    #
    # This is a valid no-trade outcome.
    # ---------------------------------------------------------

    if not early_candidates:
        print()
        print("=" * 80)
        print("NO EARLY-ENTRY CANDIDATES")
        print("=" * 80)
        print(
            "No candidate survived V21.2.23 discovery "
            "and early-entry observation."
        )
        print(
            "Lifecycle/Evidence handoff not required."
        )
        print("Live Order: False")
        print("Paper Trade: False")
        print("BUY/SELL: NOT EXECUTED")
        return

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

    confirmed_count = confirmation_result.get(
        "Confirmed Candidate Count",
        0,
    )

    print(
        "Underlying Confirmed:",
        confirmed_count,
    )

    # ---------------------------------------------------------
    # No-confirmation boundary
    #
    # V21.2.23.4 intentionally promotes ONLY candidates
    # explicitly confirmed by V21.2.23.3.
    #
    # If confirmation produces zero candidates, the correct
    # JKJ behavior is to stop here. This is a valid no-trade
    # outcome, not a lifecycle-adapter failure.
    # ---------------------------------------------------------

    if confirmed_count == 0:
        print()
        print("=" * 80)
        print("NO UNDERLYING-CONFIRMED CANDIDATES")
        print("=" * 80)
        print(
            "No V21.2.23 candidate satisfied the "
            "underlying confirmation gate."
        )
        print(
            "V21.2.23.4 lifecycle handoff not required."
        )
        print("Live Order: False")
        print("Paper Trade: False")
        print("BUY/SELL: NOT EXECUTED")
        return

    # ---------------------------------------------------------
    # 6. Discovery → V21.2.19 lifecycle
    #
    # IMPORTANT:
    # We pass the actual confirmation result, but the
    # existing lifecycle engine remains authoritative.
    # No lifecycle state is manually assigned here.
    # ---------------------------------------------------------

    lifecycle_result = adapt_discovery_to_lifecycle(
        early_entry_result,
        confirmation_result=confirmation_result,
    )

    if lifecycle_result.get("Status") != (
        "DISCOVERY_LIFECYCLE_ADAPTER_COMPLETE"
    ):
        raise RuntimeError(
            "V21.2.23.4 lifecycle adaptation failed."
        )

    lifecycle_store = lifecycle_result.get(
        "Candidate Lifecycle",
        {},
    )

    print(
        "Lifecycle Candidates:",
        len(lifecycle_store),
    )

    # ---------------------------------------------------------
    # 7. V21.2.20 candidate qualification
    # ---------------------------------------------------------

    qualification_result = qualify_candidates(
        lifecycle_store
    )

    if qualification_result.get("Status") != (
        "CANDIDATE_QUALIFICATION_COMPLETE"
    ):
        raise RuntimeError(
            "V21.2.20 qualification failed."
        )

    qualified_candidates = qualification_result.get(
        "Qualified Candidates",
        [],
    )

    print(
        "V21.2.20 Qualified:",
        len(qualified_candidates),
    )

    if not qualified_candidates:
        print()
        print("=" * 80)
        print("NO V21.2.20 QUALIFIED CANDIDATES")
        print("=" * 80)
        print(
            "Evidence handoff cannot continue because "
            "B.2 requires selected candidates."
        )
        print("This is a valid no-trade outcome.")
        print("Live Order: False")
        print("Paper Trade: False")
        return

    # ---------------------------------------------------------
    # 8. B.1 selection
    # ---------------------------------------------------------

    from modules.nifty_option_v21_2_22_b1_candidate_selection import (
        select_candidates,
    )

    b1_result = select_candidates(
        qualification_result,
        max_selected=3,
    )

    if b1_result.get("Status") != (
        "CANDIDATE_SELECTION_COMPLETE"
    ):
        raise RuntimeError(
            "V21.2.22-B.1 selection failed."
        )

    selected_candidates = b1_result.get(
        "Selected Candidates",
        [],
    )

    print(
        "B.1 Selected:",
        len(selected_candidates),
    )

    if not selected_candidates:
        print()
        print("=" * 80)
        print("NO B.1 SELECTED CANDIDATES")
        print("=" * 80)
        print("Valid no-trade outcome.")
        print("Live Order: False")
        print("Paper Trade: False")
        return

    # ---------------------------------------------------------
    # 9. B.2 detailed evidence
    # ---------------------------------------------------------

    detailed_evidence = collect_detailed_evidence(
        kite,
        b1_result,
        observation_count=4,
        interval_seconds=15,
    )

    if detailed_evidence.get("Status") != (
        "DETAILED_EVIDENCE_COMPLETE"
    ):
        raise RuntimeError(
            "V21.2.22-B.2 detailed evidence failed."
        )

    print(
        "B.2 Detailed Evidence:",
        detailed_evidence.get("Status"),
    )

    # ---------------------------------------------------------
    # 10. Existing V21.2.20 → V21.2.16 adapter
    #
    # Restrict the unified observation to the candidates
    # that actually survived V21.2.20 qualification.
    # ---------------------------------------------------------

    unified_observation = (
        build_unified_observation_from_qualified_candidates(
            detailed_evidence.get(
                "Observations",
                {},
            ),
            qualification_result,
        )
    )

    if unified_observation.get("Status") != (
        "UNIFIED_OBSERVATION_COMPLETE"
    ):
        raise RuntimeError(
            "Unified observation construction failed."
        )

    print(
        "Unified Observation:",
        unified_observation.get("Status"),
    )

    print(
        "Unified Observation Count:",
        unified_observation.get(
            "Observation Count"
        ),
    )

    # ---------------------------------------------------------
    # 11. V12.6 classical momentum
    # ---------------------------------------------------------

    momentum_result = (
        evaluate_unified_observation_momentum(
            unified_observation
        )
    )

    if momentum_result.get("Status") != (
        "MOMENTUM_EVALUATION_COMPLETE"
    ):
        raise RuntimeError(
            "V12.6 momentum evaluation failed."
        )

    print(
        "V12.6 Momentum:",
        momentum_result.get("Status"),
    )

    # ---------------------------------------------------------
    # 12. V21.2.22-C Evidence Reconciliation
    # ---------------------------------------------------------

    reconciliation_result = reconcile_candidates(
        qualification_result,
        detailed_evidence,
        momentum_result,
    )

    if reconciliation_result.get("Status") != (
        "EVIDENCE_RECONCILIATION_COMPLETE"
    ):
        raise RuntimeError(
            "V21.2.22-C reconciliation failed."
        )

    # ---------------------------------------------------------
    # 13. Final summary
    # ---------------------------------------------------------

    print()
    print("=" * 80)
    print("V21.2.23 → V21.2.22-C REAL-MARKET TEST RESULT")
    print("=" * 80)

    print(
        "Discovery Universe:",
        discovery_result.get("Universe Count"),
    )

    print(
        "Discovery Selected:",
        len(
            selection_result.get(
                "Selected Candidates",
                [],
            )
        ),
    )

    print(
        "Early Entry Candidates:",
        len(early_candidates),
    )

    print(
        "Underlying Confirmed:",
        confirmation_result.get(
            "Confirmed Candidate Count",
            0,
        ),
    )

    print(
        "Lifecycle Candidates:",
        len(lifecycle_store),
    )

    print(
        "V21.2.20 Qualified:",
        len(qualified_candidates),
    )

    print(
        "B.1 Selected:",
        len(selected_candidates),
    )

    print(
        "B.2 Status:",
        detailed_evidence.get("Status"),
    )

    print(
        "Unified Observation:",
        unified_observation.get("Status"),
    )

    print(
        "V12.6 Momentum:",
        momentum_result.get("Status"),
    )

    print(
        "V21.2.22-C:",
        reconciliation_result.get("Status"),
    )

    print(
        "Reconciliation Counts:",
        reconciliation_result.get(
            "Reconciliation Counts",
            {},
        ),
    )

    print()
    print("Live Order: False")
    print("Paper Trade: False")
    print("BUY/SELL: NOT EXECUTED")

    print()
    print("=" * 80)
    print("V21.2.23 → V21.2.22-C TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
