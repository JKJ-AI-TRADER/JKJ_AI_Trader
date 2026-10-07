"""
JKJ AI TRADER
V21.2.12 — REAL-MARKET OPPORTUNITY + RISK TEST

Purpose:
    Validate V12.8 Opportunity and V12.9 Risk/Trade Quality
    using the real-market V21.2.11 Market Context output.

Safety:
    NO LIVE ORDERS
    NO PAPER TRADE
"""

from modules.intraday_zerodha_session_manager import get_kite_session
from modules.nifty_option_v21_2_pre_market_controller import prepare_nifty_candidates
from modules.nifty_option_v21_2_momentum_confirmation import (
    evaluate_real_market_momentum_confirmation,
)
from modules.nifty_option_v21_2_11_market_context import (
    evaluate_real_market_market_context,
)
from modules.nifty_option_v21_2_12_opportunity_risk import (
    evaluate_real_market_opportunity_risk,
)


def main():

    print("=" * 70)
    print("JKJ AI TRADER")
    print("V21.2.12 — REAL-MARKET OPPORTUNITY + RISK")
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
    # 3. V21.2.10 Momentum Confirmation
    # ---------------------------------------------------------
    momentum_result = evaluate_real_market_momentum_confirmation(
        kite,
        contracts,
        observation_count=4,
        interval_seconds=10,
    )

    if momentum_result.get("Status") != "MOMENTUM_CONFIRMATION_COMPLETE":
        print("V21.2.10 failed.")
        print(momentum_result)
        return

    print()
    print(f"V21.2.10 Status: {momentum_result.get('Status')}")

    # ---------------------------------------------------------
    # 4. V21.2.11 Market Context
    # ---------------------------------------------------------
    market_context_results = []

    for momentum_item in momentum_result.get("Results", []):

        momentum_confirmation = momentum_item.get(
            "Momentum Confirmation"
        )

        if not momentum_confirmation:
            print("Missing Momentum Confirmation result.")
            continue

        market_context = evaluate_real_market_market_context(
            momentum_confirmation
        )

        market_context_results.append(market_context)

    if not market_context_results:
        print("No market-context results produced.")
        return

    # ---------------------------------------------------------
    # 5. V21.2.12 Opportunity + Risk
    # ---------------------------------------------------------
    completed = 0

    print()
    print("V21.2.12 RESULTS")
    print("-" * 70)

    for market_context in market_context_results:

        opportunity_risk = evaluate_real_market_opportunity_risk(
            market_context
        )

        symbol = opportunity_risk.get(
            "Trading Symbol",
            "UNKNOWN",
        )

        print(
            f"{symbol}: "
            f"Momentum {opportunity_risk.get('Momentum Confirmation')}, "
            f"Context {opportunity_risk.get('Market Context')}, "
            f"Opportunity {opportunity_risk.get('Opportunity Classification')}, "
            f"Strength {opportunity_risk.get('Opportunity Strength')}, "
            f"Risk {opportunity_risk.get('Risk Classification')}, "
            f"Trade Quality {opportunity_risk.get('Trade Quality')}"
        )

        print(
            f"  Status: {opportunity_risk.get('Status')} | "
            f"Live Order: {opportunity_risk.get('Live Order')} | "
            f"Paper Trade: {opportunity_risk.get('Paper Trade')}"
        )

        if opportunity_risk.get("Status") == "OPPORTUNITY_RISK_COMPLETE":
            completed += 1

    # ---------------------------------------------------------
    # 6. Final result
    # ---------------------------------------------------------
    print()
    print(f"Completed {completed}/{len(market_context_results)}")

    print("Live Order: FALSE")
    print("Paper Trade: FALSE")

    if completed == len(market_context_results):
        print("V21.2.12 TEST PASS")
    else:
        print("V21.2.12 TEST INCOMPLETE")


if __name__ == "__main__":
    main()