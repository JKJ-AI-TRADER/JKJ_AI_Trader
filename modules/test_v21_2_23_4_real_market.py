"""
JKJ AI Trader
V21.2.23.4 Real-Market Integration Test

Pipeline:
V21.2.23 Discovery
    -> V21.2.23.1 Selection
    -> V21.2.23.2 Deep Observation
    -> V21.2.23.4 Discovery -> Lifecycle Adapter
    -> Existing V21.2.19 Lifecycle

Observation only.
No live orders.
No paper trades.
No BUY/SELL.
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

from modules.nifty_option_v21_2_23_4_discovery_to_lifecycle_adapter import (
    adapt_discovery_to_lifecycle,
)


LIVE_ORDER = False
PAPER_TRADE = False


def main() -> None:

    print()
    print("=" * 70)
    print("V21.2.23.4 REAL-MARKET LIFECYCLE INTEGRATION TEST")
    print("=" * 70)
    print("Live Order: False")
    print("Paper Trade: False")

    # ---------------------------------------------------------
    # Zerodha session
    # ---------------------------------------------------------

    auth_result = authenticate_today()

    if not isinstance(auth_result, dict):
        raise RuntimeError(
            "Invalid Zerodha authentication result."
        )

    kite = auth_result.get("Kite")

    if kite is None:
        raise RuntimeError(
            "Zerodha Kite session is not available."
        )

    print()
    print("Zerodha Session:", auth_result.get("Status"))
    print("Reason:", auth_result.get("Reason"))

    # ---------------------------------------------------------
    # V21.2.23 — Broad multi-expiry discovery
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
        print()
        print(
            "Discovery did not complete:",
            discovery_result.get("Status"),
        )
        return

    # ---------------------------------------------------------
    # V21.2.23.1 — Select strongest developing movers
    # ---------------------------------------------------------

    selection_result = select_discovery_candidates(
        discovery_result,
        max_selected=10,
    )

    print()
    print("=" * 70)
    print("V21.2.23.1 SELECTION RESULT")
    print("=" * 70)

    print(
        "Status:",
        selection_result.get("Status"),
    )
    print(
        "Selected Candidates:",
        len(
            selection_result.get(
                "Selected Candidates",
                [],
            )
        ),
    )

    if selection_result.get("Status") != (
        "DISCOVERY_CANDIDATE_SELECTION_COMPLETE"
    ):
        print("Selection failed.")
        return

    if not selection_result.get(
        "Selected Candidates"
    ):
        print("No candidates selected.")
        return

    # ---------------------------------------------------------
    # V21.2.23.2 — Deep observation
    # ---------------------------------------------------------

    early_entry_result = observe_selected_candidates(
        kite,
        selection_result,
        observation_count=4,
        interval_seconds=15,
        review_premium=100.0,
    )

    print()
    print("=" * 70)
    print("V21.2.23.2 OBSERVATION RESULT")
    print("=" * 70)

    print(
        "Status:",
        early_entry_result.get("Status"),
    )
    print(
        "Observation Count:",
        early_entry_result.get(
            "Observation Count",
            0,
        ),
    )
    print(
        "Candidates Observed:",
        early_entry_result.get(
            "Candidates Observed",
            0,
        ),
    )

    if early_entry_result.get("Status") != (
        "EARLY_ENTRY_OBSERVATION_COMPLETE"
    ):
        print("Deep observation did not complete.")
        return

    # ---------------------------------------------------------
    # V21.2.23.4 — Existing lifecycle path
    #
    # IMPORTANT:
    # We intentionally do NOT call V21.2.23.3 here.
    #
    # This test determines whether the existing V21.2.19
    # lifecycle engine can independently evaluate the
    # V21.2.23 deep-observation candidates.
    # ---------------------------------------------------------

    lifecycle_result = adapt_discovery_to_lifecycle(
        early_entry_result,
        confirmation_result=None,
    )

    print()
    print("=" * 70)
    print("V21.2.23.4 → V21.2.19 LIFECYCLE RESULT")
    print("=" * 70)

    print(
        "Status:",
        lifecycle_result.get("Status"),
    )
    print(
        "Observation Count:",
        lifecycle_result.get(
            "Observation Count",
            0,
        ),
    )
    print(
        "Tracked Symbols:",
        lifecycle_result.get(
            "Tracked Symbols",
            0,
        ),
    )

    lifecycle_store = lifecycle_result.get(
        "Lifecycle Store",
        {},
    )

    analysis = lifecycle_result.get(
        "Analysis",
        {},
    )

    print()
    print("LIFECYCLE STATES:")

    for symbol, lifecycle in lifecycle_store.items():

        latest = lifecycle.get(
            "Latest",
            {},
        )

        movement = latest.get(
            "Recent Movement %",
        )

        velocity = latest.get(
            "Latest Velocity %/sec",
        )

        acceleration = latest.get(
            "Latest Acceleration %/sec2",
        )

        state = lifecycle.get(
            "State",
        )

        print(
            f"{symbol} | "
            f"State={state} | "
            f"Move={movement} | "
            f"Velocity={velocity} | "
            f"Acceleration={acceleration}"
        )

    # ---------------------------------------------------------
    # Safety assertions
    # ---------------------------------------------------------

    assert (
        lifecycle_result.get("Status")
        == "DISCOVERY_TO_LIFECYCLE_ADAPTER_COMPLETE"
    )

    assert lifecycle_result.get(
        "Live Order"
    ) is False

    assert lifecycle_result.get(
        "Paper Trade"
    ) is False

    assert (
        len(lifecycle_store)
        == lifecycle_result.get(
            "Tracked Symbols"
        )
    )

    # ---------------------------------------------------------
    # Final
    # ---------------------------------------------------------

    print()
    print("=" * 70)
    print("V21.2.23.4 REAL-MARKET INTEGRATION TEST: PASS")
    print("=" * 70)
    print(
        "Discovery → Selection → Deep Observation → "
        "Lifecycle: PASS"
    )
    print("Live Order: False")
    print("Paper Trade: False")
    print("BUY/SELL: NOT EXECUTED")


if __name__ == "__main__":
    main()
