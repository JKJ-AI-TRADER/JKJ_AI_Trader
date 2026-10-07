"""
JKJ AI Trader
V21.2.23.1 Real-Market Discovery Selection Test

Safety:
- Observation only
- No live orders
- No paper trades
"""

from modules.jkj_daily_zerodha_auth import authenticate_today
from modules.nifty_option_v21_2_23_multi_expiry_discovery import (
    run_multi_expiry_discovery,
)
from modules.nifty_option_v21_2_23_1_discovery_selector import (
    select_discovery_candidates,
)


def main():
    print()
    print("=" * 70)
    print("V21.2.23.1 REAL-MARKET INTEGRATION TEST")
    print("=" * 70)
    print("Safety: Live Order=False")
    print("Safety: Paper Trade=False")

    auth = authenticate_today()
    kite = auth.get("Kite")

    if kite is None:
        raise RuntimeError("Kite session unavailable.")

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

    print()
    print("=" * 70)
    print("V21.2.23.1 REAL-MARKET TEST RESULT")
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
        f"Selected Candidates: "
        f"{selection_result.get('Selected Candidate Count')}"
    )

    print()
    print("NEXT STAGE:")
    print(selection_result.get("Next Stage"))

    print()
    print("Live Order: False")
    print("Paper Trade: False")
    print("BUY/SELL: NOT EXECUTED")

    print()
    print(
        "V21.2.23.1 REAL-MARKET INTEGRATION TEST: PASS"
    )


if __name__ == "__main__":
    main()
