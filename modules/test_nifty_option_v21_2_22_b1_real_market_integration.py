"""
JKJ AI Trader
V21.2.22-B.1 Real-Market Integration Test

Flow:

    V21.2.19 Persistent Observer
            ↓
    V21.2.20 Candidate Qualification
            ↓
    V21.2.22-B v2 Developing Candidate Refresh
            ↓
    V21.2.22-B.1 Candidate Selection
            ↓
    B.1 → V21.2.20/V21.2.16 Selected Qualification Adapter
            ↓
    Existing V21.2.20 → V21.2.16 Adapter
            ↓
    V21.2.16 Unified Decision + Entry

Safety:
    - Observation only
    - No live orders
    - No paper trades
    - No BUY
    - No SELL
    - No position sizing
"""

from __future__ import annotations

from modules.intraday_zerodha_session_manager import (
    get_kite_session,
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

from modules.nifty_option_v21_2_20_to_v21_2_16_adapter import (
    build_unified_observation_from_qualified_candidates,
)

from modules.nifty_option_v21_2_16_decision_entry import (
    evaluate_unified_decision_entry,
)


LIVE_ORDER = False
PAPER_TRADE = False


def main():

    print()
    print("=" * 78)
    print("V21.2.22-B.1 REAL-MARKET INTEGRATION TEST")
    print("=" * 78)

    print()
    print("SAFETY")
    print("Live Order:", LIVE_ORDER)
    print("Paper Trade:", PAPER_TRADE)

    # ------------------------------------------------------------
    # STEP 1 — Zerodha session
    # ------------------------------------------------------------
    print()
    print("-" * 78)
    print("STEP 1 — ZERODHA SESSION")
    print("-" * 78)

    session_result = get_kite_session()

    if not isinstance(session_result, dict):
        print("Session validation failed.")
        return

    kite = session_result.get("Kite")

    if kite is None:
        print("Kite session unavailable.")
        return

    print("Zerodha Session: READY")

    # ------------------------------------------------------------
    # STEP 2 — V21.2.19 Persistent Observer
    # ------------------------------------------------------------
    print()
    print("-" * 78)
    print("STEP 2 — V21.2.19 PERSISTENT OBSERVER")
    print("-" * 78)

    observer_result = run_persistent_observer(
        kite=kite,
        interval_seconds=15,
        max_observations=4,
        strikes_each_side=10,
    )

    print(
        "Observer Status:",
        observer_result.get("Status"),
    )

    if observer_result.get("Status") != (
        "PERSISTENT_OBSERVER_COMPLETE"
    ):
        print("Observer did not complete.")
        return

    observation_store = observer_result.get(
        "Observation Store"
    )

    lifecycle_store = observer_result.get(
        "Candidate Lifecycle"
    )

    if not isinstance(observation_store, dict):
        print("Observation Store unavailable.")
        return

    if not isinstance(lifecycle_store, dict):
        print("Candidate Lifecycle unavailable.")
        return

    print(
        "Observation Count:",
        observer_result.get("Observation Count"),
    )

    print(
        "Universe Count:",
        observer_result.get("Universe Count"),
    )

    # ------------------------------------------------------------
    # STEP 3 — V21.2.20 Candidate Qualification
    # ------------------------------------------------------------
    print()
    print("-" * 78)
    print("STEP 3 — V21.2.20 CANDIDATE QUALIFICATION")
    print("-" * 78)

    qualification_result = qualify_candidates(
        lifecycle_store
    )

    print(
        "Qualification Status:",
        qualification_result.get("Status"),
    )

    print(
        "Observed Candidates:",
        qualification_result.get(
            "Observed Candidate Count",
            0,
        ),
    )

    print(
        "Qualified Candidates:",
        qualification_result.get(
            "Qualified Candidate Count",
            0,
        ),
    )

    if qualification_result.get("Status") != (
        "CANDIDATE_QUALIFICATION_COMPLETE"
    ):
        print("Qualification did not complete.")
        return

    # ------------------------------------------------------------
    # STEP 4 — B v2 Developing Candidate Refresh
    # ------------------------------------------------------------
    print()
    print("-" * 78)
    print("STEP 4 — V21.2.22-B v2 DEVELOPING CANDIDATES")
    print("-" * 78)

    b2_result = refresh_developing_candidates_v2(
        lifecycle_store
    )

    print(
        "B v2 Status:",
        b2_result.get("Status"),
    )

    print(
        "B v2 Candidate Count:",
        b2_result.get("Candidate Count", 0),
    )

    print(
        "Category Counts:",
        b2_result.get("Category Counts", {}),
    )

    if b2_result.get("Status") != (
        "DEVELOPING_CANDIDATE_REFRESH_V2_COMPLETE"
    ):
        print("B v2 did not complete.")
        return

    # ------------------------------------------------------------
    # STEP 5 — B.1 Candidate Selection
    # ------------------------------------------------------------
    print()
    print("-" * 78)
    print("STEP 5 — V21.2.22-B.1 CANDIDATE SELECTION")
    print("-" * 78)

    selection_result = select_candidates(
        b2_result,
        max_candidates=3,
    )

    print(
        "Selection Status:",
        selection_result.get("Status"),
    )

    print(
        "Eligible Candidates:",
        selection_result.get(
            "Eligible Candidate Count",
            0,
        ),
    )

    print(
        "Selected Candidates:",
        selection_result.get(
            "Selected Count",
            0,
        ),
    )

    if selection_result.get("Status") != (
        "CANDIDATE_SELECTION_COMPLETE"
    ):
        print("Candidate selection did not complete.")
        return

    selected_candidates = selection_result.get(
        "Selected Candidates",
        [],
    )

    if not selected_candidates:
        print()
        print("No B.1 candidates selected.")
        print("Integration stops safely.")
        return

    print()
    print("SELECTED SYMBOLS")

    for candidate in selected_candidates:
        print(
            f"  Rank {candidate.get('Selection Rank')}: "
            f"{candidate.get('Trading Symbol')} "
            f"[{candidate.get('Category')}]"
        )

    # ------------------------------------------------------------
    # STEP 6 — B.1 → V21.2.20 qualification handoff
    # ------------------------------------------------------------
    print()
    print("-" * 78)
    print("STEP 6 — B.1 → V21.2.16 QUALIFICATION HANDOFF")
    print("-" * 78)

    selected_qualification = (
        build_selected_qualification_result(
            qualification_result,
            selection_result,
        )
    )

    print(
        "Handoff Status:",
        selected_qualification.get("Status"),
    )

    print(
        "Selection Applied:",
        selected_qualification.get(
            "Selection Applied"
        ),
    )

    print(
        "Selected:",
        selected_qualification.get(
            "Selected Candidate Count",
            0,
        ),
    )

    print(
        "Accepted:",
        selected_qualification.get(
            "Accepted Selected Candidate Count",
            0,
        ),
    )

    print(
        "Rejected:",
        selected_qualification.get(
            "Rejected Selected Candidate Count",
            0,
        ),
    )

    if selected_qualification.get("Status") != (
        "CANDIDATE_QUALIFICATION_COMPLETE"
    ):
        print("B.1 handoff failed.")
        return

    # ------------------------------------------------------------
    # DIAGNOSTIC — Candidate symbols vs observation-store keys
    # ------------------------------------------------------------
    print()
    print("-" * 78)
    print("DIAGNOSTIC — SYMBOL / OBSERVATION STORE CHECK")
    print("-" * 78)

    print("Observation Store Keys:")
    for key in observation_store.keys():
        print(" ", repr(key))

    print()
    print("Qualified Candidate Symbols:")

    for candidate in selected_qualification.get(
        "Qualified Candidates",
        [],
    ):
        symbol = candidate.get("Trading Symbol")
        print(
            " ",
            repr(symbol),
            "FOUND=",
            symbol in observation_store,
            "HISTORY_COUNT=",
            len(observation_store.get(symbol, [])),
        )

    # ------------------------------------------------------------
    # STEP 7 — Existing V21.2.20 → V21.2.16 Adapter
    # ------------------------------------------------------------
    print()
    print("-" * 78)
    print("STEP 7 — EXISTING V21.2.20 → V21.2.16 ADAPTER")
    print("-" * 78)

    unified_observation = (
        build_unified_observation_from_qualified_candidates(
            observation_store,
            selected_qualification,
        )
    )

    print(
        "Unified Status:",
        unified_observation.get("Status"),
    )

    print(
        "Contract Count:",
        unified_observation.get(
            "Contract Count",
            0,
        ),
    )

    print(
        "Observation Count:",
        unified_observation.get(
            "Observation Count",
            0,
        ),
    )

    if unified_observation.get("Status") != (
        "UNIFIED_OBSERVATION_COMPLETE"
    ):
        print("Unified observation adapter failed.")
        print(
            "Reason:",
            unified_observation.get("Reason"),
        )
        return

    # ------------------------------------------------------------
    # STEP 8 — V21.2.16 Decision + Entry
    # ------------------------------------------------------------
    print()
    print("-" * 78)
    print("STEP 8 — V21.2.16 DECISION + ENTRY")
    print("-" * 78)

    decision_result = evaluate_unified_decision_entry(
        unified_observation
    )

    print(
        "Decision Status:",
        decision_result.get("Status"),
    )

    print(
        "Contract Count:",
        decision_result.get(
            "Contract Count",
            0,
        ),
    )

    # ------------------------------------------------------------
    # CONTRACT RESULTS
    # ------------------------------------------------------------
    print()
    print("-" * 78)
    print("FINAL CONTRACT RESULTS")
    print("-" * 78)

    contract_results = decision_result.get(
        "Contract Results",
        [],
    )

    for result in contract_results:

        print()
        print(
            "Trading Symbol:",
            result.get("Trading Symbol"),
        )

        print(
            "Status:",
            result.get("Status"),
        )

        print(
            "Momentum Confirmation:",
            result.get("Momentum Confirmation"),
        )

        print(
            "Market Context:",
            result.get("Market Context"),
        )

        print(
            "Opportunity Classification:",
            result.get(
                "Opportunity Classification"
            ),
        )

        print(
            "Opportunity Strength:",
            result.get("Opportunity Strength"),
        )

        print(
            "Risk Classification:",
            result.get("Risk Classification"),
        )

        print(
            "Trade Quality:",
            result.get("Trade Quality"),
        )

        print(
            "Entry Qualification:",
            result.get("Entry Qualification"),
        )

    # ------------------------------------------------------------
    # FINAL SAFETY
    # ------------------------------------------------------------
    print()
    print("=" * 78)
    print("INTEGRATION RESULT")
    print("=" * 78)

    print(
        "V21.2.19 Observer:",
        observer_result.get("Status"),
    )

    print(
        "V21.2.20 Qualification:",
        qualification_result.get("Status"),
    )

    print(
        "B v2:",
        b2_result.get("Status"),
    )

    print(
        "B.1 Selection:",
        selection_result.get("Status"),
    )

    print(
        "B.1 Handoff:",
        selected_qualification.get("Status"),
    )

    print(
        "Unified Observation:",
        unified_observation.get("Status"),
    )

    print(
        "V21.2.16 Decision:",
        decision_result.get("Status"),
    )

    print(
        "Live Order:",
        LIVE_ORDER,
    )

    print(
        "Paper Trade:",
        PAPER_TRADE,
    )

    print()
    print("SAFETY: PASS")
    print("=" * 78)


if __name__ == "__main__":
    main()
