"""
JKJ AI Trader
V21.2.23 → V21.2.17 Real-Market Integration Test

Purpose:
    Prove that the new V21.2.23 discovery front end can feed the
    existing V21.2.20 → V21.2.17 evidence/decision/risk pipeline.

Safety:
    - No live orders
    - No paper trades
    - No BUY
    - No SELL
    - No position sizing
"""

from modules.intraday_zerodha_session_manager import get_kite_session

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

from modules.nifty_option_v21_2_22_b_candidate_refresh_v2 import (
    refresh_developing_candidates_v2,
)

from modules.nifty_option_v21_2_22_b1_candidate_selection import (
    select_candidates,
)

from modules.nifty_option_v21_2_22_b1_to_v21_2_16_adapter import (
    build_selected_qualification_result,
)

from modules.nifty_option_v21_2_22_b2_detailed_evidence import (
    collect_detailed_evidence,
)

from modules.nifty_option_v21_2_15_momentum_bridge import (
    evaluate_unified_observation_momentum,
)

from modules.nifty_option_v21_2_22_c_evidence_reconciliation import (
    reconcile_candidates,
)

from modules.nifty_option_v21_2_22_d_final_evidence_gate import (
    evaluate_final_evidence_gate,
)

from modules.nifty_option_v21_2_22_d1_entry_bridge import (
    build_entry_bridge,
)

from modules.nifty_option_v21_2_22_d1_to_b1_authorization import (
    build_d1_authorized_b1_result,
)

from modules.nifty_option_v21_2_20_to_v21_2_16_adapter import (
    build_unified_observation_from_qualified_candidates,
)

from modules.nifty_option_v21_2_16_decision_entry import (
    evaluate_unified_decision_entry,
)

from modules.nifty_option_v21_2_17_risk_stop_targets import (
    evaluate_real_market_risk_stop_targets,
)


LIVE_ORDER = False
PAPER_TRADE = False


def stop(status, **extra):
    result = {
        "Status": status,
        "Live Order": LIVE_ORDER,
        "Paper Trade": PAPER_TRADE,
    }
    result.update(extra)
    return result


def main():
    print("=" * 78)
    print(
        "V21.2.23 → V21.2.17 REAL-MARKET INTEGRATION TEST"
    )
    print("=" * 78)
    print("Live Order:", LIVE_ORDER)
    print("Paper Trade:", PAPER_TRADE)
    print()

    # ---------------------------------------------------------
    # 1. Zerodha session
    # ---------------------------------------------------------

    session_result = get_kite_session()

    if not isinstance(session_result, dict):
        return stop("SESSION_RESULT_INVALID")

    kite = session_result.get("Kite")

    if kite is None:
        return stop(
            "SESSION_NOT_READY",
            Session_Result=session_result,
        )

    print("STEP 1 — Zerodha Session: PASS")

    # ---------------------------------------------------------
    # 2. V21.2.23 multi-expiry discovery
    # ---------------------------------------------------------

    print()
    print("STEP 2 — V21.2.23 Multi-Expiry Discovery")

    discovery_result = run_multi_expiry_discovery(
        kite=kite,
        observation_count=4,
        interval_seconds=15,
    )

    if not isinstance(discovery_result, dict):
        return stop(
            "DISCOVERY_RESULT_INVALID",
            Discovery_Result=discovery_result,
        )

    if discovery_result.get("Status") != (
        "MULTI_EXPIRY_DISCOVERY_COMPLETE"
    ):
        return stop(
            "DISCOVERY_NOT_COMPLETE",
            Discovery_Result=discovery_result,
        )

    print(
        "Discovery Universe:",
        discovery_result.get("Universe Count"),
    )
    print(
        "Discovery Expiries:",
        discovery_result.get("Expiries"),
    )

    # ---------------------------------------------------------
    # 3. V21.2.23.1 selection
    # ---------------------------------------------------------

    print()
    print("STEP 3 — V21.2.23.1 Discovery Selection")

    selection_result = select_discovery_candidates(
        discovery_result,
        max_selected=10,
    )

    if selection_result.get("Status") != (
        "DISCOVERY_CANDIDATE_SELECTION_COMPLETE"
    ):
        return stop(
            "DISCOVERY_SELECTION_NOT_COMPLETE",
            Selection_Result=selection_result,
        )

    selected = selection_result.get(
        "Selected Candidates",
        [],
    )

    print("Selected Candidates:", len(selected))

    if not selected:
        return stop(
            "NO_DISCOVERY_CANDIDATES",
            Discovery_Result=discovery_result,
            Selection_Result=selection_result,
        )

    # ---------------------------------------------------------
    # 4. V21.2.23.2 early-entry observation
    # ---------------------------------------------------------

    print()
    print("STEP 4 — V21.2.23.2 Early Entry Observation")

    early_entry_result = observe_selected_candidates(
        kite=kite,
        selection_result=selection_result,
        observation_count=4,
        interval_seconds=15,
    )

    if early_entry_result.get("Status") != (
        "EARLY_ENTRY_OBSERVATION_COMPLETE"
    ):
        return stop(
            "EARLY_ENTRY_OBSERVATION_NOT_COMPLETE",
            Early_Entry_Result=early_entry_result,
        )

    early_candidates = early_entry_result.get(
        "Early Entry Candidates",
        [],
    )

    print(
        "Early-Entry Candidates:",
        len(early_candidates),
    )

    if not early_candidates:
        print()
        print("NO EARLY-ENTRY CANDIDATES")
        print(
            "Discovery and deep observation completed, "
            "but no candidate satisfied the early-entry rules."
        )
        print("Live Order: False")
        print("Paper Trade: False")
        print("BUY/SELL: NOT EXECUTED")
        return stop(
            "NO_EARLY_ENTRY_CANDIDATES",
            Discovery_Result=discovery_result,
            Selection_Result=selection_result,
            Early_Entry_Result=early_entry_result,
        )

    # ---------------------------------------------------------
    # 5. V21.2.23.3 underlying confirmation
    # ---------------------------------------------------------

    print()
    print("STEP 5 — V21.2.23.3 Underlying Confirmation")

    confirmation_result = (
        evaluate_underlying_confirmation_gate(
            early_entry_result
        )
    )

    if confirmation_result.get("Status") != (
        "UNDERLYING_CONFIRMATION_GATE_COMPLETE"
    ):
        return stop(
            "UNDERLYING_CONFIRMATION_NOT_COMPLETE",
            Confirmation_Result=confirmation_result,
        )

    confirmed = confirmation_result.get(
        "Confirmed Candidates",
        [],
    )

    print(
        "Underlying-Confirmed Candidates:",
        len(confirmed),
    )

    if not confirmed:
        print()
        print("NO UNDERLYING-CONFIRMED CANDIDATES")
        print(
            "No candidate satisfied the underlying "
            "confirmation requirement."
        )
        print("Live Order: False")
        print("Paper Trade: False")
        print("BUY/SELL: NOT EXECUTED")
        return stop(
            "NO_UNDERLYING_CONFIRMED_CANDIDATES",
            Discovery_Result=discovery_result,
            Selection_Result=selection_result,
            Early_Entry_Result=early_entry_result,
            Confirmation_Result=confirmation_result,
        )

    # ---------------------------------------------------------
    # 6. V21.2.23.4 discovery → lifecycle
    # ---------------------------------------------------------

    print()
    print("STEP 6 — V21.2.23.4 Discovery → Lifecycle")

    lifecycle_result = adapt_discovery_to_lifecycle(
        early_entry_result,
        confirmation_result,
    )

    if lifecycle_result.get("Status") != (
        "DISCOVERY_TO_LIFECYCLE_ADAPTER_COMPLETE"
    ):
        return stop(
            "DISCOVERY_LIFECYCLE_ADAPTER_NOT_COMPLETE",
            Lifecycle_Result=lifecycle_result,
        )

    lifecycle_store = lifecycle_result.get(
        "Lifecycle Store",
        {},
    )

    observation_store = lifecycle_result.get(
        "Observation Store",
        {},
    )

    print(
        "Lifecycle Candidates:",
        len(lifecycle_store),
    )

    # ---------------------------------------------------------
    # 7. V21.2.20 qualification
    # ---------------------------------------------------------

    print()
    print("STEP 7 — V21.2.20 Candidate Qualification")

    qualification_result = qualify_candidates(
        lifecycle_store
    )

    if qualification_result.get("Status") != (
        "CANDIDATE_QUALIFICATION_COMPLETE"
    ):
        return stop(
            "QUALIFICATION_NOT_COMPLETE",
            Qualification_Result=qualification_result,
        )

    qualified = qualification_result.get(
        "Qualified Candidates",
        [],
    )

    print("Qualified Candidates:", len(qualified))

    if not qualified:
        return stop(
            "NO_QUALIFIED_CANDIDATES",
            Lifecycle_Result=lifecycle_result,
            Qualification_Result=qualification_result,
        )

    # ---------------------------------------------------------
    # 8. B v2 refresh
    # ---------------------------------------------------------

    print()
    print("STEP 8 — B v2 Developing-Candidate Refresh")

    refresh_result = refresh_developing_candidates_v2(
        lifecycle_store
    )

    if refresh_result.get("Status") != (
        "DEVELOPING_CANDIDATE_REFRESH_V2_COMPLETE"
    ):
        return stop(
            "B_REFRESH_NOT_COMPLETE",
            Refresh_Result=refresh_result,
        )

    if not refresh_result.get(
        "Developing Candidates",
        [],
    ):
        return stop(
            "NO_DEVELOPING_CANDIDATES",
            Refresh_Result=refresh_result,
        )

    # ---------------------------------------------------------
    # 9. B.1 selection
    # ---------------------------------------------------------

    print()
    print("STEP 9 — B.1 Candidate Selection")

    b1_result = select_candidates(
        refresh_result
    )

    if b1_result.get("Status") != (
        "CANDIDATE_SELECTION_COMPLETE"
    ):
        return stop(
            "B1_SELECTION_NOT_COMPLETE",
            B1_Result=b1_result,
        )

    b1_candidates = b1_result.get(
        "Selected Candidates",
        [],
    )

    print("B.1 Selected:", len(b1_candidates))

    if not b1_candidates:
        return stop(
            "NO_B1_SELECTED_CANDIDATES",
            B1_Result=b1_result,
        )

    # ---------------------------------------------------------
    # 10. B.1 → V21.2.16 restriction
    # ---------------------------------------------------------

    selected_qualification = (
        build_selected_qualification_result(
            qualification_result,
            b1_result,
        )
    )

    if selected_qualification.get("Status") != (
        "CANDIDATE_QUALIFICATION_COMPLETE"
    ):
        return stop(
            "SELECTED_QUALIFICATION_NOT_COMPLETE",
            Selected_Qualification=selected_qualification,
        )

    # ---------------------------------------------------------
    # 11. B.2 detailed evidence
    # ---------------------------------------------------------

    print()
    print("STEP 11 — B.2 Detailed Evidence")

    detailed_evidence = collect_detailed_evidence(
        kite=kite,
        selection_result=b1_result,
        observation_count=4,
        interval_seconds=15,
    )

    if detailed_evidence.get("Status") != (
    "DETAILED_EVIDENCE_COMPLETE"
    ):
        return stop(
            "B2_NOT_COMPLETE",
            Detailed_Evidence=detailed_evidence,
        )

    print(
        "B.2 Candidate Count:",
        detailed_evidence.get("Candidate Count"),
    )

    # ---------------------------------------------------------
    # 12. V12.6 momentum
    # ---------------------------------------------------------

    print()
    print("STEP 12 — V12.6 Momentum")

    momentum_result = evaluate_unified_observation_momentum(
        detailed_evidence
    )

    if momentum_result.get("Status") != (
        "MOMENTUM_CONFIRMATION_COMPLETE"
    ):
        return stop(
            "MOMENTUM_NOT_COMPLETE",
            Momentum_Result=momentum_result,
        )

    # ---------------------------------------------------------
    # 13. C reconciliation
    # ---------------------------------------------------------

    print()
    print("STEP 13 — C Evidence Reconciliation")

    reconciliation_result = reconcile_candidates(
        selected_qualification,
        detailed_evidence,
        momentum_result,
    )

    if reconciliation_result.get("Status") != (
        "EVIDENCE_RECONCILIATION_COMPLETE"
    ):
        return stop(
            "RECONCILIATION_NOT_COMPLETE",
            Reconciliation_Result=reconciliation_result,
        )

    # ---------------------------------------------------------
    # 14. D final evidence gate
    # ---------------------------------------------------------

    print()
    print("STEP 14 — D Final Evidence Gate")

    final_gate_result = evaluate_final_evidence_gate(
        reconciliation_result
    )

    if final_gate_result.get("Status") != (
        "FINAL_EVIDENCE_GATE_COMPLETE"
    ):
        return stop(
            "FINAL_EVIDENCE_GATE_NOT_COMPLETE",
            Final_Gate_Result=final_gate_result,
        )

    # ---------------------------------------------------------
    # 15. D.1 entry bridge
    # ---------------------------------------------------------

    print()
    print("STEP 15 — D.1 Evidence-Gated Entry Bridge")

    bridge_result = build_entry_bridge(
        final_gate_result
    )

    if bridge_result.get("Status") != (
        "EVIDENCE_GATED_ENTRY_BRIDGE_COMPLETE"
    ):
        return stop(
            "D1_BRIDGE_NOT_COMPLETE",
            D1_Result=bridge_result,
        )

    accepted_count = bridge_result.get(
        "Accepted Candidate Count",
        0,
    )

    print("D.1 Accepted:", accepted_count)

    if accepted_count == 0:
        return stop(
            "NO_D1_AUTHORIZED_CANDIDATES",
            D1_Result=bridge_result,
        )

    # ---------------------------------------------------------
    # 16. D.1 → B.1 authorization
    # ---------------------------------------------------------

    print()
    print("STEP 16 — D.1 → B.1 Authorization")

    d1_authorized = build_d1_authorized_b1_result(
        b1_result,
        bridge_result,
    )

    if d1_authorized.get("Status") != (
        "D1_AUTHORIZED_B1_RESULT_COMPLETE"
    ):
        return stop(
            "D1_AUTHORIZATION_NOT_COMPLETE",
            D1_Authorization_Result=d1_authorized,
        )

    authorized_count = len(
        d1_authorized.get(
            "Qualified Candidates",
            [],
        )
    )

    print("D.1 Authorized:", authorized_count)

    if authorized_count == 0:
        return stop(
            "NO_D1_AUTHORIZED_CANDIDATES",
            D1_Authorization_Result=d1_authorized,
        )

    # ---------------------------------------------------------
    # 17. Authorized qualification handoff
    # ---------------------------------------------------------

    authorized_qualification = {
        "Status": "CANDIDATE_QUALIFICATION_COMPLETE",
        "Candidates": d1_authorized.get(
            "Candidates",
            {},
        ),
        "Qualified Candidates": d1_authorized.get(
            "Qualified Candidates",
            [],
        ),
        "Selection Applied": True,
        "D1 Authorization Applied": True,
        "Qualified Candidate Count": authorized_count,
        "Live Order": False,
        "Paper Trade": False,
    }

    # ---------------------------------------------------------
    # 18. V21.2.20 → V21.2.16 adapter
    # ---------------------------------------------------------

    print()
    print("STEP 18 — V21.2.20 → V21.2.16 Adapter")

    unified_observation = (
        build_unified_observation_from_qualified_candidates(
            observation_store,
            authorized_qualification,
        )
    )

    if unified_observation.get("Status") != (
        "UNIFIED_OBSERVATION_COMPLETE"
    ):
        return stop(
            "UNIFIED_OBSERVATION_NOT_COMPLETE",
            Unified_Observation=unified_observation,
        )

    # ---------------------------------------------------------
    # 19. V21.2.16 decision / entry
    # ---------------------------------------------------------

    print()
    print("STEP 19 — V21.2.16 Decision / Entry")

    decision_result = evaluate_unified_decision_entry(
        unified_observation
    )

    if decision_result.get("Status") != (
        "DECISION_ENTRY_COMPLETE"
    ):
        return stop(
            "DECISION_ENTRY_NOT_COMPLETE",
            Decision_Result=decision_result,
        )

    decision_results = decision_result.get(
        "Results",
        [],
    )

    print(
        "Decision Candidates:",
        len(decision_results),
    )

    # ---------------------------------------------------------
    # 20. V21.2.17 risk
    # ---------------------------------------------------------

    print()
    print("STEP 20 — V21.2.17 Risk / Stop / Targets")

    risk_result = evaluate_real_market_risk_stop_targets(
        decision_result,
        unified_observation,
    )

    if risk_result.get("Status") != (
        "RISK_STOP_TARGETS_COMPLETE"
    ):
        return stop(
            "RISK_NOT_COMPLETE",
            Risk_Result=risk_result,
        )

    print(
        "Risk Candidates:",
        risk_result.get("Contract Count"),
    )

    print()
    print("=" * 78)
    print(
        "V21.2.23 → V21.2.17 REAL-MARKET INTEGRATION TEST PASS"
    )
    print("=" * 78)
    print("Live Order: False")
    print("Paper Trade: False")
    print("BUY/SELL: NOT EXECUTED")
    print("=" * 78)

    return {
        "Status": "V21_2_23_TO_V21_2_17_INTEGRATION_COMPLETE",
        "Discovery": discovery_result,
        "Selection": selection_result,
        "Early Entry": early_entry_result,
        "Underlying Confirmation": confirmation_result,
        "Lifecycle": lifecycle_result,
        "Qualification": qualification_result,
        "B1": b1_result,
        "Detailed Evidence": detailed_evidence,
        "Momentum": momentum_result,
        "Reconciliation": reconciliation_result,
        "Final Gate": final_gate_result,
        "D1": bridge_result,
        "D1 Authorization": d1_authorized,
        "Unified Observation": unified_observation,
        "Decision": decision_result,
        "Risk": risk_result,
        "Live Order": False,
        "Paper Trade": False,
    }


if __name__ == "__main__":
    main()
