"""
JKJ AI Trader
V21.2.21 — Automated Intraday Engine

Purpose:
    Connect the existing V21.2 observation, qualification,
    candidate-selection, evidence, decision, and risk layers
    into one controlled workflow.

Flow:

    Kite Session
        ↓
    Market Session Check
        ↓
    V21.2.19 Persistent Observer
        ↓
    V21.2.20 Candidate Qualification
        ↓
    V21.2.22-B Candidate Refresh
        ↓
    V21.2.22-B.1 Candidate Selection
        ↓
    B.1 → V21.2.16 Selection Restriction
        ↓
    V21.2.22-B.2 Detailed Evidence
        ↓
    V12.6 Momentum
        ↓
    V21.2.22-C Evidence Reconciliation
        ↓
    V21.2.22-D Final Evidence Gate
        ↓
    V21.2.22-D.1 Evidence-Gated Entry Bridge
        ↓
    D.1 → B.1 Authorization
        ↓
    Authorized Qualification Handoff
        ↓
    Existing V21.2.20 → V21.2.16 Adapter
        ↓
    V21.2.16 Decision + Entry Qualification
        ↓
    V21.2.17 Risk + Stop + Targets

Safety:
    - No live orders
    - No paper trades
    - No position sizing
    - No automatic BUY
    - No automatic SELL

D.1 is an authorization boundary:
    A candidate rejected by D.1 must not reach V21.2.16.
"""

from typing import Any, Dict

from modules.intraday_zerodha_session_manager import (
    get_kite_session,
)

from modules.nifty_option_v21_2_market_session import (
    get_market_session_state,
)

from modules.nifty_option_v21_2_19_persistent_observer import (
    run_persistent_observer,
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


def _safety_result(status: str, **extra) -> Dict[str, Any]:
    """Build a consistent safety-preserving result."""
    result = {
        "Status": status,
        "Live Order": LIVE_ORDER,
        "Paper Trade": PAPER_TRADE,
    }
    result.update(extra)
    return result


def _build_authorized_qualification_result(
    d1_authorized_b1_result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Convert the D.1-authorized B.1 result into the exact
    qualification-shaped contract required by the existing
    V21.2.20 → V21.2.16 observation adapter.

    This is only a data handoff.
    It does not alter the existing adapter.
    It does not make a trading decision.
    """
    if not isinstance(d1_authorized_b1_result, dict):
        return _safety_result(
            "AUTHORIZED_QUALIFICATION_HANDOFF_REJECTED",
            Reason="D.1 authorization result must be a dictionary.",
        )

    if d1_authorized_b1_result.get("Status") != (
        "D1_AUTHORIZED_B1_RESULT_COMPLETE"
    ):
        return _safety_result(
            "AUTHORIZED_QUALIFICATION_HANDOFF_REJECTED",
            Reason=(
                "D.1 authorization must be complete before "
                "creating the authorized qualification handoff."
            ),
        )

    authorized_candidates = d1_authorized_b1_result.get(
        "Qualified Candidates",
        [],
    )

    if not isinstance(authorized_candidates, list):
        return _safety_result(
            "AUTHORIZED_QUALIFICATION_HANDOFF_REJECTED",
            Reason="Authorized Qualified Candidates must be a list.",
        )

    return {
        "Status": "CANDIDATE_QUALIFICATION_COMPLETE",
        "Candidates": d1_authorized_b1_result.get(
            "Candidates",
            {},
        ),
        "Qualified Candidates": authorized_candidates,
        "Selection Applied": True,
        "D1 Authorization Applied": True,
        "Qualified Candidate Count": len(
            authorized_candidates
        ),
        "Authorization Source": (
            "V21.2.22-D.1 Evidence-Gated Entry Bridge"
        ),
        "Original Qualification Source": (
            d1_authorized_b1_result.get(
                "Original Qualification Source",
                "V21.2.20 Candidate Qualification",
            )
        ),
        "Selection Source": d1_authorized_b1_result.get(
            "Selection Source",
            "V21.2.22-B.1 Candidate Selection",
        ),
        "Live Order": LIVE_ORDER,
        "Paper Trade": PAPER_TRADE,
    }


def run_v21_2_21_automated_engine(
    interval_seconds: int = 15,
    max_observations: int = 4,
    strikes_each_side: int = 10,
    current_time=None,
) -> Dict[str, Any]:
    """
    Run the V21.2.21 automated observation-to-risk pipeline.

    This version deliberately stops before any execution.
    """

    print()
    print("=" * 75)
    print("JKJ AI TRADER — V21.2.21 AUTOMATED ENGINE")
    print("=" * 75)
    print("Mode: OBSERVATION / EVIDENCE / DECISION / RISK ONLY")
    print("Live Order:", LIVE_ORDER)
    print("Paper Trade:", PAPER_TRADE)
    print()

    # ---------------------------------------------------------
    # 1. Zerodha session
    # ---------------------------------------------------------

    print("STEP 1 — Zerodha session validation")

    session_result = get_kite_session()

    if not isinstance(session_result, dict):
        return _safety_result(
            "SESSION_RESULT_INVALID"
        )

    kite = session_result.get("Kite")

    if kite is None:
        return _safety_result(
            "SESSION_NOT_READY",
            Session_Result=session_result,
        )

    print("Session: READY")

    # ---------------------------------------------------------
    # 2. Market session
    # ---------------------------------------------------------

    print()
    print("STEP 2 — Market session check")

    market_session_result = get_market_session_state(
        current_time=current_time
    )

    if not isinstance(market_session_result, dict):
        return _safety_result(
            "MARKET_SESSION_RESULT_INVALID",
            Market_Session_Result=market_session_result,
        )

    session_state = market_session_result.get(
        "Session State"
    )

    print("Market Session:", session_state)

    if session_state in {
        "BEFORE_PRE_MARKET",
        "PRE_MARKET",
        "MARKET_CLOSED",
    }:
        return _safety_result(
            "MARKET_NOT_AVAILABLE",
            Market_Session=session_state,
        )

    # ---------------------------------------------------------
    # 3. V21.2.19 persistent observation
    # ---------------------------------------------------------

    print()
    print("STEP 3 — V21.2.19 persistent observation")

    observer_result = run_persistent_observer(
        kite=kite,
        interval_seconds=interval_seconds,
        max_observations=max_observations,
        strikes_each_side=strikes_each_side,
    )

    if not isinstance(observer_result, dict):
        return _safety_result(
            "OBSERVER_RESULT_INVALID"
        )

    if observer_result.get("Status") != (
        "PERSISTENT_OBSERVER_COMPLETE"
    ):
        return _safety_result(
            "OBSERVER_NOT_COMPLETE",
            Observer_Result=observer_result,
        )

    lifecycle_store = observer_result.get(
        "Candidate Lifecycle",
        {},
    )

    observation_store = observer_result.get(
        "Observation Store",
        {},
    )

    # ---------------------------------------------------------
    # Observation baseline mode
    # ---------------------------------------------------------

    baseline_sources = set()

    if isinstance(observation_store, dict):
        for observations in observation_store.values():

            if not isinstance(observations, list):
                continue

            for observation in observations:

                if not isinstance(observation, dict):
                    continue

                source = observation.get(
                    "Baseline Source"
                )

                if source:
                    baseline_sources.add(source)

    if "GENUINE_915" in baseline_sources:
        baseline_mode = "GENUINE_915"
    elif "SESSION_START" in baseline_sources:
        baseline_mode = "SESSION_START"
    else:
        baseline_mode = "UNSPECIFIED"

    print(
        "Observation Baseline Mode:",
        baseline_mode,
    )

    # ---------------------------------------------------------
    # 4. V21.2.20 qualification
    # ---------------------------------------------------------

    print()
    print("STEP 4 — V21.2.20 candidate qualification")

    qualification_result = qualify_candidates(
        lifecycle_store
    )

    if qualification_result.get("Status") != (
        "CANDIDATE_QUALIFICATION_COMPLETE"
    ):
        return _safety_result(
            "QUALIFICATION_NOT_COMPLETE",
            Qualification_Result=qualification_result,
            Observer_Result=observer_result,
        )

    qualified_candidates = qualification_result.get(
        "Qualified Candidates",
        [],
    )

    print(
        "Qualified Candidates:",
        len(qualified_candidates),
    )

    if not qualified_candidates:
        return _safety_result(
            "NO_QUALIFIED_CANDIDATES",
            Observer_Result=observer_result,
            Qualification_Result=qualification_result,
        )

    # ---------------------------------------------------------
    # 5. B v2 developing-candidate refresh
    # ---------------------------------------------------------

    print()
    print(
        "STEP 5 — V21.2.22-B developing-candidate refresh"
    )

    refresh_result = refresh_developing_candidates_v2(
        lifecycle_store
    )

    if not isinstance(refresh_result, dict):
        return _safety_result(
            "B_REFRESH_RESULT_INVALID",
            Refresh_Result=refresh_result,
        )

    if refresh_result.get("Status") != (
        "DEVELOPING_CANDIDATE_REFRESH_V2_COMPLETE"
    ):
        return _safety_result(
            "B_REFRESH_NOT_COMPLETE",
            Refresh_Result=refresh_result,
        )

    developing_candidates = refresh_result.get(
        "Developing Candidates",
        [],
    )

    print(
        "Developing Candidates:",
        len(developing_candidates),
    )

    if not developing_candidates:
        return _safety_result(
            "NO_DEVELOPING_CANDIDATES",
            Observer_Result=observer_result,
            Qualification_Result=qualification_result,
            Refresh_Result=refresh_result,
        )

    # ---------------------------------------------------------
    # 6. B.1 candidate selection
    # ---------------------------------------------------------

    print()
    print("STEP 6 — V21.2.22-B.1 candidate selection")

    selection_result = select_candidates(
        refresh_result
    )

    if not isinstance(selection_result, dict):
        return _safety_result(
            "B1_SELECTION_RESULT_INVALID",
            Selection_Result=selection_result,
        )

    if selection_result.get("Status") != (
        "CANDIDATE_SELECTION_COMPLETE"
    ):
        return _safety_result(
            "B1_SELECTION_NOT_COMPLETE",
            Selection_Result=selection_result,
        )

    selected_candidates = selection_result.get(
        "Selected Candidates",
        [],
    )

    print(
        "Selected Candidates:",
        len(selected_candidates),
    )

    for candidate in selected_candidates:
        print(
            "  -",
            candidate.get("Trading Symbol"),
            candidate.get("Category"),
        )

    if not selected_candidates:
        return _safety_result(
            "NO_SELECTED_CANDIDATES",
            Observer_Result=observer_result,
            Qualification_Result=qualification_result,
            Refresh_Result=refresh_result,
            Selection_Result=selection_result,
        )

    # ---------------------------------------------------------
    # 7. B.1 → V21.2.16 qualification restriction
    # ---------------------------------------------------------

    print()
    print(
        "STEP 7 — B.1 → V21.2.16 qualification restriction"
    )

    selected_qualification = (
        build_selected_qualification_result(
            qualification_result,
            selection_result,
        )
    )

    if selected_qualification.get("Status") != (
        "CANDIDATE_QUALIFICATION_COMPLETE"
    ):
        return _safety_result(
            "SELECTED_QUALIFICATION_NOT_COMPLETE",
            Selected_Qualification=selected_qualification,
        )

    selected_qualified_candidates = (
        selected_qualification.get(
            "Qualified Candidates",
            [],
        )
    )

    print(
        "B.1 Restricted Candidates:",
        len(selected_qualified_candidates),
    )

    if not selected_qualified_candidates:
        return _safety_result(
            "NO_RESTRICTED_B1_CANDIDATES",
            Selection_Result=selection_result,
            Selected_Qualification=selected_qualification,
        )

    # ---------------------------------------------------------
    # 8. B.2 detailed evidence
    # ---------------------------------------------------------

    print()
    print("STEP 8 — V21.2.22-B.2 detailed evidence")

    detailed_evidence = collect_detailed_evidence(
        kite=kite,
        selection_result=selection_result,
        observation_count=4,
        interval_seconds=interval_seconds,
    )

    if not isinstance(detailed_evidence, dict):
        return _safety_result(
            "B2_RESULT_INVALID",
            Detailed_Evidence=detailed_evidence,
        )

    b2_status = detailed_evidence.get("Status")

    print("B.2 Status:", b2_status)

    if b2_status not in {
        "COMPLETE",
        "DETAILED_EVIDENCE_COMPLETE",
    }:
        return _safety_result(
            "B2_NOT_COMPLETE",
            Detailed_Evidence=detailed_evidence,
        )

    # ---------------------------------------------------------
    # 9. V12.6 momentum
    # ---------------------------------------------------------

    print()
    print("STEP 9 — V12.6 momentum bridge")

    momentum_result = evaluate_unified_observation_momentum(
        detailed_evidence
    )

    if not isinstance(momentum_result, dict):
        return _safety_result(
            "MOMENTUM_RESULT_INVALID",
            Momentum_Result=momentum_result,
        )

    print(
        "Momentum Status:",
        momentum_result.get("Status"),
    )

    # ---------------------------------------------------------
    # 10. V21.2.22-C reconciliation
    # ---------------------------------------------------------

    print()
    print("STEP 10 — V21.2.22-C evidence reconciliation")

    reconciliation_result = reconcile_candidates(
        selected_qualification,
        detailed_evidence,
        momentum_result,
    )

    if not isinstance(reconciliation_result, dict):
        return _safety_result(
            "RECONCILIATION_RESULT_INVALID",
            Reconciliation_Result=reconciliation_result,
        )

    if reconciliation_result.get("Status") != (
        "EVIDENCE_RECONCILIATION_COMPLETE"
    ):
        return _safety_result(
            "RECONCILIATION_NOT_COMPLETE",
            Reconciliation_Result=reconciliation_result,
        )

    reconciled_candidates = reconciliation_result.get(
        "Candidates",
        [],
    )

    print(
        "Reconciled Candidates:",
        len(reconciled_candidates),
    )

    # ---------------------------------------------------------
    # 11. V21.2.22-D final evidence gate
    # ---------------------------------------------------------

    print()
    print("STEP 11 — V21.2.22-D final evidence gate")

    final_gate_result = evaluate_final_evidence_gate(
        reconciliation_result
    )

    if not isinstance(final_gate_result, dict):
        return _safety_result(
            "FINAL_GATE_RESULT_INVALID",
            Final_Gate_Result=final_gate_result,
        )

    if final_gate_result.get("Status") != (
        "FINAL_EVIDENCE_GATE_COMPLETE"
    ):
        return _safety_result(
            "FINAL_GATE_NOT_COMPLETE",
            Final_Gate_Result=final_gate_result,
        )

    accepted_candidates = final_gate_result.get(
        "Accepted Candidates",
        [],
    )

    rejected_candidates = final_gate_result.get(
        "Rejected Candidates",
        [],
    )

    print(
        "D Accepted:",
        len(accepted_candidates),
    )
    print(
        "D Rejected:",
        len(rejected_candidates),
    )

    for candidate in accepted_candidates:
        print(
            "  D ACCEPTED:",
            candidate.get("Trading Symbol"),
        )

    for candidate in rejected_candidates:
        print(
            "  D REJECTED:",
            candidate.get("Trading Symbol"),
        )

    # ---------------------------------------------------------
    # 12. D.1 evidence-gated entry bridge
    # ---------------------------------------------------------

    print()
    print(
        "STEP 12 — V21.2.22-D.1 evidence-gated entry bridge"
    )

    bridge_result = build_entry_bridge(
        final_gate_result
    )

    if not isinstance(bridge_result, dict):
        return _safety_result(
            "D1_BRIDGE_RESULT_INVALID",
            Bridge_Result=bridge_result,
        )

    if bridge_result.get("Status") != (
        "EVIDENCE_GATED_ENTRY_BRIDGE_COMPLETE"
    ):
        return _safety_result(
            "D1_BRIDGE_NOT_COMPLETE",
            Bridge_Result=bridge_result,
        )

    d1_accepted_count = bridge_result.get(
        "Accepted Candidate Count",
        0,
    )

    d1_rejected_count = bridge_result.get(
        "Rejected Candidate Count",
        0,
    )

    print("D.1 Accepted:", d1_accepted_count)
    print("D.1 Rejected:", d1_rejected_count)

    for candidate in bridge_result.get(
        "Accepted Candidates",
        [],
    ):
        print(
            "  BRIDGED:",
            candidate.get("Trading Symbol"),
            "| Entry Evaluation:",
            candidate.get("Entry Evaluation"),
        )

    # ---------------------------------------------------------
    # 13. D.1 → B.1 authorization boundary
    # ---------------------------------------------------------

    print()
    print(
        "STEP 13 — D.1 → B.1 authorization boundary"
    )

    d1_authorized_b1_result = (
        build_d1_authorized_b1_result(
            selected_qualification,
            bridge_result,
        )
    )

    if not isinstance(
        d1_authorized_b1_result,
        dict,
    ):
        return _safety_result(
            "D1_AUTHORIZATION_RESULT_INVALID",
            D1_Authorization_Result=d1_authorized_b1_result,
        )

    if d1_authorized_b1_result.get("Status") != (
        "D1_AUTHORIZED_B1_RESULT_COMPLETE"
    ):
        return _safety_result(
            "D1_AUTHORIZATION_NOT_COMPLETE",
            D1_Authorization_Result=d1_authorized_b1_result,
        )

    authorized_candidates = (
        d1_authorized_b1_result.get(
            "Qualified Candidates",
            [],
        )
    )

    authorized_count = len(
        authorized_candidates
        if isinstance(authorized_candidates, list)
        else []
    )

    print(
        "Original B.1 Qualified:",
        d1_authorized_b1_result.get(
            "Original B1 Qualified Candidate Count"
        ),
    )

    print(
        "D.1 Accepted:",
        d1_authorized_b1_result.get(
            "D1 Accepted Candidate Count"
        ),
    )

    print(
        "Authorized For V21.2.16:",
        authorized_count,
    )

    print(
        "Blocked By D.1:",
        d1_authorized_b1_result.get(
            "Rejected By D1 Count"
        ),
    )

    for candidate in authorized_candidates:
        print(
            "  AUTHORIZED:",
            candidate.get("Trading Symbol"),
        )

    for candidate in d1_authorized_b1_result.get(
        "Rejected By D1 Candidates",
        [],
    ):
        print(
            "  BLOCKED BY D.1:",
            candidate.get("Trading Symbol"),
        )

    # HARD AUTHORIZATION STOP:
    # No D.1 authorization means no V21.2.16 handoff.
    if authorized_count == 0:
        return _safety_result(
            "NO_D1_AUTHORIZED_CANDIDATES",
            Observer_Result=observer_result,
            Observation_Baseline_Mode=baseline_mode,
            Qualification_Result=qualification_result,
            Refresh_Result=refresh_result,
            Selection_Result=selection_result,
            Selected_Qualification=selected_qualification,
            Detailed_Evidence=detailed_evidence,
            Momentum_Result=momentum_result,
            Reconciliation_Result=reconciliation_result,
            Final_Gate_Result=final_gate_result,
            Bridge_Result=bridge_result,
            D1_Authorization_Result=d1_authorized_b1_result,
            Authorized_Candidate_Count=0,
            Execution_Performed=False,
        )

    if authorized_count != d1_accepted_count:
        return _safety_result(
            "D1_AUTHORIZATION_COUNT_MISMATCH",
            Reason=(
                "Authorized candidate count does not match "
                "the D.1 accepted candidate count."
            ),
            D1_Authorization_Result=d1_authorized_b1_result,
            Authorized_Candidate_Count=authorized_count,
            D1_Accepted_Candidate_Count=d1_accepted_count,
            Execution_Performed=False,
        )

    # ---------------------------------------------------------
    # 14. Authorized qualification handoff
    # ---------------------------------------------------------

    print()
    print(
        "STEP 14 — D.1 authorized qualification handoff"
    )

    authorized_qualification = (
        _build_authorized_qualification_result(
            d1_authorized_b1_result
        )
    )

    if authorized_qualification.get("Status") != (
        "CANDIDATE_QUALIFICATION_COMPLETE"
    ):
        return _safety_result(
            "AUTHORIZED_QUALIFICATION_HANDOFF_REJECTED",
            Authorized_Qualification=authorized_qualification,
            D1_Authorization_Result=d1_authorized_b1_result,
        )

    print(
        "Authorized Qualification Candidates:",
        len(
            authorized_qualification.get(
                "Qualified Candidates",
                [],
            )
        ),
    )

    # ---------------------------------------------------------
    # 15. Existing V21.2.20 → V21.2.16 adapter
    # ---------------------------------------------------------

    print()
    print(
        "STEP 15 — Existing V21.2.20 → V21.2.16 adapter"
    )

    unified_observation = (
        build_unified_observation_from_qualified_candidates(
            observation_store,
            authorized_qualification,
        )
    )

    if not isinstance(unified_observation, dict):
        return _safety_result(
            "UNIFIED_OBSERVATION_RESULT_INVALID",
            Unified_Observation=unified_observation,
        )

    if unified_observation.get("Status") != (
        "UNIFIED_OBSERVATION_COMPLETE"
    ):
        return _safety_result(
            "UNIFIED_OBSERVATION_NOT_COMPLETE",
            Unified_Observation=unified_observation,
            Authorized_Qualification=authorized_qualification,
        )

    print(
        "Unified Observation Status:",
        unified_observation.get("Status"),
    )

    print(
        "Unified Observation Count:",
        unified_observation.get("Observation Count"),
    )

    print(
        "Unified Contract Count:",
        unified_observation.get("Contract Count"),
    )

    # ---------------------------------------------------------
    # 16. V21.2.16 decision + entry
    # ---------------------------------------------------------

    print()
    print(
        "STEP 16 — V21.2.16 decision + entry qualification"
    )

    decision_result = evaluate_unified_decision_entry(
        unified_observation
    )

    if not isinstance(decision_result, dict):
        return _safety_result(
            "DECISION_RESULT_INVALID",
            Decision_Result=decision_result,
        )

    if decision_result.get("Status") != (
        "DECISION_ENTRY_COMPLETE"
    ):
        return _safety_result(
            "DECISION_ENTRY_NOT_COMPLETE",
            Decision_Result=decision_result,
        )

    print(
        "Decision Status:",
        decision_result.get("Status"),
    )

    # ---------------------------------------------------------
    # 17. V21.2.17 risk / stop / targets
    # ---------------------------------------------------------

    print()
    print(
        "STEP 17 — V21.2.17 risk + stop + targets"
    )

    risk_result = evaluate_real_market_risk_stop_targets(
        decision_result,
        unified_observation,
    )

    if not isinstance(risk_result, dict):
        return _safety_result(
            "RISK_RESULT_INVALID",
            Risk_Result=risk_result,
        )

    if risk_result.get("Status") != (
        "RISK_STOP_TARGETS_COMPLETE"
    ):
        return _safety_result(
            "RISK_ANALYSIS_NOT_COMPLETE",
            Risk_Result=risk_result,
            Decision_Result=decision_result,
        )

    print(
        "Risk Status:",
        risk_result.get("Status"),
    )

    # ---------------------------------------------------------
    # Final result
    # ---------------------------------------------------------

    print()
    print("=" * 75)
    print("V21.2.21 AUTOMATED ENGINE COMPLETE")
    print("=" * 75)
    print(
        "D.1 Authorized Candidates:",
        authorized_count,
    )
    print(
        "V21.2.16 Decision: COMPLETE"
    )
    print(
        "V21.2.17 Risk: COMPLETE"
    )
    print("Live Order:", LIVE_ORDER)
    print("Paper Trade:", PAPER_TRADE)
    print("Execution: NOT PERFORMED")
    print("BUY/SELL: NOT EXECUTED")
    print("=" * 75)

    return {
        "Status": "V21_2_21_AUTOMATED_ENGINE_COMPLETE",
        "Observer Result": observer_result,
        "Observation Baseline Mode": baseline_mode,
        "Qualification Result": qualification_result,
        "Refresh Result": refresh_result,
        "Selection Result": selection_result,
        "Selected Qualification": selected_qualification,
        "Detailed Evidence": detailed_evidence,
        "Momentum Result": momentum_result,
        "Reconciliation Result": reconciliation_result,
        "Final Gate Result": final_gate_result,
        "Bridge Result": bridge_result,
        "D1 Authorization Result": d1_authorized_b1_result,
        "Authorized Qualification": authorized_qualification,
        "Unified Observation": unified_observation,
        "Decision Result": decision_result,
        "Risk Result": risk_result,
        "Authorized Candidate Count": authorized_count,
        "Live Order": LIVE_ORDER,
        "Paper Trade": PAPER_TRADE,
        "Execution Performed": False,
        "BUY/SELL Executed": False,
    }


if __name__ == "__main__":

    result = run_v21_2_21_automated_engine()

    print()
    print("FINAL STATUS:", result.get("Status"))
    print("Live Order:", result.get("Live Order"))
    print("Paper Trade:", result.get("Paper Trade"))
    print(
        "Authorized Candidate Count:",
        result.get("Authorized Candidate Count"),
    )
    print(
        "Execution Performed:",
        result.get("Execution Performed"),
    )
    print(
        "BUY/SELL Executed:",
        result.get("BUY/SELL Executed"),
    )
