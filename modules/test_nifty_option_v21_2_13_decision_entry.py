"""
JKJ AI TRADER
V21.2.13 — REAL-MARKET DECISION + ENTRY QUALIFICATION TEST

Safety:
    NO LIVE ORDERS
    NO PAPER TRADE
"""

from modules.intraday_zerodha_session_manager import get_kite_session
from modules.nifty_option_v21_2_pre_market_controller import (
    prepare_nifty_candidates,
)
from modules.nifty_option_v21_2_momentum_confirmation import (
    evaluate_real_market_momentum_confirmation,
)
from modules.nifty_option_v21_2_11_market_context import (
    evaluate_real_market_market_context,
)
from modules.nifty_option_v21_2_12_opportunity_risk import (
    evaluate_real_market_opportunity_risk,
)
from modules.nifty_option_v21_2_13_decision_entry import (
    evaluate_real_market_decision_entry,
)


def main():

    print("=" * 70)
    print("JKJ AI TRADER")
    print("V21.2.13 — REAL-MARKET DECISION + ENTRY QUALIFICATION")
    print("=" * 70)

    # ---------------------------------------------------------
    # 1. Zerodha session
    # ---------------------------------------------------------
    session = get_kite_session()

    print(f"Session Status: {session.get('Status')}")

    if session.get("Status") not in {
        "SESSION_REUSED",
        "SESSION_CREATED",
    }:
        print("SESSION FAILED")
        print(session)
        return

    kite = session.get("Kite")

    if kite is None:
        print("Kite session object missing.")
        return

    # ---------------------------------------------------------
    # 2. Prepare candidates
    # ---------------------------------------------------------
    preparation = prepare_nifty_candidates()

    if preparation.get("Status") != "CANDIDATES_READY":
        print("Candidate preparation failed.")
        print(preparation)
        return

    all_candidates = preparation.get("All Candidates", [])

    print(f"NIFTY Spot: {preparation.get('NIFTY Spot')}")
    print(f"Expiry: {preparation.get('Expiry')}")
    print(f"Candidate Count: {len(all_candidates)}")

    contracts = []

    for candidate in all_candidates:
        print(
            f" - {candidate.get('tradingsymbol')} | "
            f"{candidate.get('instrument_type')} | "
            f"Strike {candidate.get('strike')}"
        )
        contracts.append(candidate)

    # ---------------------------------------------------------
    # 3. V21.2.10 — Momentum Confirmation
    # ---------------------------------------------------------
    momentum_result = evaluate_real_market_momentum_confirmation(
        kite,
        contracts,
        observation_count=4,
        interval_seconds=10,
    )

    if momentum_result.get("Status") != (
        "MOMENTUM_CONFIRMATION_COMPLETE"
    ):
        print("V21.2.10 failed.")
        print(momentum_result)
        return

    print()
    print(f"V21.2.10 Status: {momentum_result.get('Status')}")

    # ---------------------------------------------------------
    # 4. V21.2.11 + V21.2.12 + V21.2.13
    # ---------------------------------------------------------
    completed = 0

    print()
    print("V21.2.13 RESULTS")
    print("-" * 70)

    for momentum_item in momentum_result.get("Results", []):

        momentum_confirmation = momentum_item.get(
            "Momentum Confirmation"
        )

        if not momentum_confirmation:
            print("Missing Momentum Confirmation result.")
            continue

        # V21.2.11
        market_context = evaluate_real_market_market_context(
            momentum_confirmation
        )

        if market_context.get("Status") != (
            "MARKET_CONTEXT_COMPLETE"
        ):
            print(
                "V21.2.11 failed for "
                f"{momentum_confirmation.get('Trading Symbol')}"
            )
            continue

        # V21.2.12
        opportunity_risk = evaluate_real_market_opportunity_risk(
            market_context
        )

        if opportunity_risk.get("Status") != (
            "OPPORTUNITY_RISK_COMPLETE"
        ):
            print(
                "V21.2.12 failed for "
                f"{market_context.get('Trading Symbol')}"
            )
            continue

        # V21.2.13
        decision_entry = evaluate_real_market_decision_entry(
            opportunity_risk
        )

        symbol = decision_entry.get(
            "Trading Symbol",
            opportunity_risk.get(
                "Trading Symbol",
                "UNKNOWN",
            ),
        )

        print(
            f"{symbol}: "
            f"Momentum "
            f"{decision_entry.get('Momentum Confirmation')}, "
            f"Context "
            f"{decision_entry.get('Market Context')}, "
            f"Opportunity "
            f"{decision_entry.get('Opportunity Classification')}, "
            f"Strength "
            f"{decision_entry.get('Opportunity Strength')}, "
            f"Risk "
            f"{decision_entry.get('Risk Classification')}, "
            f"Quality "
            f"{decision_entry.get('Trade Quality')}, "
            f"Entry "
            f"{decision_entry.get('Entry Qualification')}"
        )

        print(
            f"  Status: {decision_entry.get('Status')} | "
            f"Live Order: {decision_entry.get('Live Order')} | "
            f"Paper Trade: {decision_entry.get('Paper Trade')}"
        )

        if decision_entry.get("Status") == (
            "DECISION_ENTRY_COMPLETE"
        ):
            completed += 1

    # ---------------------------------------------------------
    # 5. Final result
    # ---------------------------------------------------------
    print()
    print(f"Completed {completed}/{len(momentum_result.get('Results', []))}")
    print("Live Order: FALSE")
    print("Paper Trade: FALSE")

    if completed == len(momentum_result.get("Results", [])):
        print("V21.2.13 TEST PASS")
    else:
        print("V21.2.13 TEST INCOMPLETE")


if __name__ == "__main__":
    main()