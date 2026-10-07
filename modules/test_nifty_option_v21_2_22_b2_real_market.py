"""
V21.2.22-B.2 Real-Market Integration Test

Pipeline:

V21.2.19 Persistent Observer
        ↓
V21.2.20 Qualification
        ↓
V21.2.22-B v2
        ↓
V21.2.22-B.1 Selection
        ↓
V21.2.22-B.2 Detailed Evidence
        ↓
V21.2.15 Momentum
        ↓
V12.6

Safety:
    LIVE_ORDER=False
    PAPER_TRADE=False
"""

from modules.jkj_daily_zerodha_auth import (
    authenticate_today,
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

from modules.nifty_option_v21_2_22_b2_detailed_evidence import (
    collect_detailed_evidence,
)

from modules.nifty_option_v21_2_15_momentum_bridge import (
    evaluate_unified_observation_momentum,
)

from modules.nifty_option_v21_2_22_b1_to_v21_2_16_adapter import (
    build_selected_qualification_result,
)

from modules.nifty_option_v21_2_22_c_evidence_reconciliation import (
    reconcile_candidates,
)

from modules.nifty_option_v21_2_22_b1_to_v21_2_16_adapter import (
    build_selected_qualification_result,
)

from modules.nifty_option_v21_2_22_c_evidence_reconciliation import (
    reconcile_candidates,
)


def main():

    print("=" * 110)
    print("JKJ AI TRADER")
    print("V21.2.22-B.2 REAL-MARKET INTEGRATION TEST")
    print("=" * 110)

    print()
    print(
        "Safety: LIVE_ORDER=False | PAPER_TRADE=False"
    )

    # ---------------------------------------------------------
    # Zerodha session
    # ---------------------------------------------------------

    session = authenticate_today()

    if session.get("Status") not in (
        "SESSION_REUSED",
        "AUTHENTICATED_AND_SAVED",
    ):
        print()
        print("Zerodha authentication failed.")
        print(session)
        return

    kite = session.get("Kite")

    if kite is None:
        print()
        print("Kite session object missing.")
        return

    print()
    print(
        "Zerodha Session:",
        session.get("Status"),
    )

    # ---------------------------------------------------------
    # V21.2.19 Persistent Observation
    # ---------------------------------------------------------

    print()
    print("STEP 1 — V21.2.19 PERSISTENT OBSERVER")

    observer_result = run_persistent_observer(
        kite,
        interval_seconds=15,
        max_observations=4,
        strikes_each_side=10,
    )

    print()
    print(
        "Observer Status:",
        observer_result.get("Status"),
    )

    if observer_result.get("Status") != (
        "PERSISTENT_OBSERVER_COMPLETE"
    ):
        print("Observer failed.")
        return

    lifecycle_store = observer_result.get(
        "Candidate Lifecycle",
        {},
    )

    observation_store = observer_result.get(
        "Observation Store",
        {},
    )

    print(
        "Observer Observation Count:",
        observer_result.get(
            "Observation Count"
        ),
    )

    print(
        "Observation Store Symbols:",
        len(observation_store),
    )

    # ---------------------------------------------------------
    # V21.2.20 Qualification
    # ---------------------------------------------------------

    print()
    print("STEP 2 — V21.2.20 QUALIFICATION")

    qualification_result = qualify_candidates(
        lifecycle_store
    )

    print(
        "Qualification Status:",
        qualification_result.get("Status"),
    )

    print(
        "Qualified Candidate Count:",
        qualification_result.get(
            "Qualified Candidate Count"
        ),
    )

    # ---------------------------------------------------------
    # B v2
    # ---------------------------------------------------------

    print()
    print("STEP 3 — V21.2.22-B v2")

    b2_result = refresh_developing_candidates_v2(
        lifecycle_store
    )

    print(
        "B v2 Status:",
        b2_result.get("Status"),
    )

    print(
        "B v2 Candidate Count:",
        b2_result.get("Candidate Count"),
    )

    print(
        "B v2 Category Counts:",
        b2_result.get("Category Counts"),
    )

    # ---------------------------------------------------------
    # B.1
    # ---------------------------------------------------------

    print()
    print("STEP 4 — V21.2.22-B.1 SELECTION")

    selection_result = select_candidates(
        b2_result,
        max_candidates=3,
    )

    print(
        "B.1 Status:",
        selection_result.get("Status"),
    )

    print(
        "Selected Count:",
        selection_result.get(
            "Selected Count"
        ),
    )

    for candidate in selection_result.get(
        "Selected Candidates",
        [],
    ):
        print(
            f"  Rank {candidate.get('Selection Rank')}: "
            f"{candidate.get('Trading Symbol')} | "
            f"{candidate.get('Category')} | "
            f"{candidate.get('Lifecycle State')}"
        )

    if selection_result.get("Selected Count", 0) == 0:
        print()
        print(
            "No candidates selected. "
            "B.2 detailed evidence will not run."
        )
        return

    # ---------------------------------------------------------
    # B.1 → Selected Qualification
    # ---------------------------------------------------------

    selected_qualification_result = (
        build_selected_qualification_result(
            qualification_result,
            selection_result,
        )
    )

    print()
    print(
        "Selected Qualification Status:",
        selected_qualification_result.get(
            "Status"
        ),
    )

    print(
        "Accepted Selected Candidates:",
        selected_qualification_result.get(
            "Accepted Selected Candidate Count"
        ),
    )

    print(
        "Rejected Selected Candidates:",
        selected_qualification_result.get(
            "Rejected Selected Candidate Count"
        ),
    )

    if selected_qualification_result.get(
        "Status"
    ) != "CANDIDATE_QUALIFICATION_COMPLETE":
        print()
        print(
            "Selected qualification bridge failed. "
            "B.2 detailed evidence will not run."
        )
        return

    # ---------------------------------------------------------
    # B.2 Detailed Evidence
    # ---------------------------------------------------------

    print()
    print("STEP 5 — V21.2.22-B.2 DETAILED EVIDENCE")

    detailed_result = collect_detailed_evidence(
        kite,
        selection_result,
        observation_count=4,
        interval_seconds=10,
    )

    print()
    print(
        "B.2 Status:",
        detailed_result.get("Status"),
    )

    print(
        "B.2 Observation Count:",
        detailed_result.get(
            "Observation Count"
        ),
    )

    print(
        "B.2 Candidate Count:",
        detailed_result.get(
            "Candidate Count"
        ),
    )

    if detailed_result.get("Status") != (
        "DETAILED_EVIDENCE_COMPLETE"
    ):
        print()
        print("B.2 detailed evidence did not complete.")
        print(detailed_result)
        return

    # ---------------------------------------------------------
    # Build V21.2.15 unified observation
    # ---------------------------------------------------------

    observations_by_contract = {}

    for symbol, history in detailed_result.get(
        "Observations",
        {},
    ).items():

        if not history:
            continue

        first = history[0]

        identity = (
            first.get("Trading Symbol"),
            first.get("Underlying"),
            first.get("Expiry"),
            first.get("Strike"),
            first.get("Option Type"),
        )

        observations_by_contract[
            identity
        ] = history

    unified_observation = {
        "Status": "UNIFIED_OBSERVATION_COMPLETE",
        "Observation Count": detailed_result.get(
            "Observation Count"
        ),
        "Movement Intervals": (
            detailed_result.get(
                "Observation Count",
                0,
            ) - 1
        ),
        "Observations By Contract":
            observations_by_contract,
        "Live Order": False,
        "Paper Trade": False,
    }

    print()
    print(
        "V21.2.15 Unified Observation:",
        "UNIFIED_OBSERVATION_COMPLETE",
    )

    print(
        "Unified Contract Count:",
        len(observations_by_contract),
    )

    # ---------------------------------------------------------
    # V21.2.15 → V12.6
    # ---------------------------------------------------------

    print()
    print("STEP 6 — V21.2.15 → V12.6")

    momentum_result = (
        evaluate_unified_observation_momentum(
            unified_observation
        )
    )

    print()
    print(
        "Momentum Status:",
        momentum_result.get("Status"),
    )

    print(
        "Momentum Observation Count:",
        momentum_result.get(
            "Observation Count"
        ),
    )

    print(
        "Momentum Contract Count:",
        momentum_result.get(
            "Contract Count"
        ),
    )

    for result in momentum_result.get(
        "Results",
        [],
    ):

        print()
        print(
            "Contract:",
            result.get("Trading Symbol"),
        )

        print(
            "  Direction:",
            (
                result.get(
                    "Momentum Sequence",
                    {},
                ).get("Direction")
                if isinstance(
                    result.get(
                        "Momentum Sequence"
                    ),
                    dict,
                )
                else None
            ),
        )

        print(
            "  Persistence:",
            (
                result.get(
                    "Momentum Sequence",
                    {},
                ).get("Persistence Status")
                if isinstance(
                    result.get(
                        "Momentum Sequence"
                    ),
                    dict,
                )
                else None
            ),
        )

        print(
            "  Confirmation:",
            (
                result.get(
                    "Momentum Confirmation",
                    {},
                ).get(
                    "Momentum Confirmation"
                )
                if isinstance(
                    result.get(
                        "Momentum Confirmation"
                    ),
                    dict,
                )
                else None
            ),
        )

    # ---------------------------------------------------------
    # V21.2.22-C Evidence Reconciliation
    # ---------------------------------------------------------

    print()
    print(
        "STEP 7 — V21.2.22-C EVIDENCE RECONCILIATION"
    )

    reconciliation_result = reconcile_candidates(
        selected_qualification_result,
        detailed_result,
        momentum_result,
    )

    print()
    print(
        "Reconciliation Status:",
        reconciliation_result.get(
            "Status"
        ),
    )

    print(
        "Reconciliation Candidate Count:",
        reconciliation_result.get(
            "Candidate Count"
        ),
    )

    print(
        "Reconciliation Counts:",
        reconciliation_result.get(
            "Reconciliation Counts"
        ),
    )

    for result in reconciliation_result.get(
        "Candidates",
        [],
    ):

        print()
        print(
            "Contract:",
            result.get(
                "Trading Symbol"
            ),
        )

        print(
            "  Lifecycle:",
            result.get(
                "Lifecycle State"
            ),
        )

        print(
            "  Qualification:",
            result.get(
                "Qualification"
            ),
        )

        print(
            "  V12.6 Persistence:",
            result.get(
                "V12.6 Persistence"
            ),
        )

        print(
            "  V12.6 Confirmation:",
            result.get(
                "V12.6 Confirmation"
            ),
        )

        print(
            "  First Price:",
            result.get(
                "First Price"
            ),
        )

        print(
            "  Latest Price:",
            result.get(
                "Latest Price"
            ),
        )

        print(
            "  Overall Movement %:",
            result.get(
                "Overall Movement %"
            ),
        )

        print(
            "  Latest Movement %:",
            result.get(
                "Latest Movement %"
            ),
        )

        print(
            "  Reconciliation:",
            result.get(
                "Reconciliation"
            ),
        )

        print(
            "  Reason:",
            result.get(
                "Reason"
            ),
        )

    print()
    print(
        "Safety:",
        "LIVE_ORDER=False | PAPER_TRADE=False",
    )

    if momentum_result.get("Status") == (
        "UNIFIED_MOMENTUM_COMPLETE"
    ) and reconciliation_result.get(
        "Status"
    ) == "EVIDENCE_RECONCILIATION_COMPLETE":
        print()
        print(
            "V21.2.22-B.2 REAL-MARKET "
            "EVIDENCE → V12.6 → V21.2.22-C TEST PASS"
        )
    else:
        print()
        print(
            "V21.2.22-B.2 REAL-MARKET "
            "EVIDENCE → V12.6 INCOMPLETE"
        )


if __name__ == "__main__":
    main()
