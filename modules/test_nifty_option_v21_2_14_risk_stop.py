"""
JKJ AI TRADER
V21.2.14 — REAL-MARKET RISK + STOP-LOSS TEST

Safety:
    NO LIVE ORDERS
    NO PAPER TRADE
"""

from modules.intraday_zerodha_session_manager import (
    get_kite_session,
)

from modules.nifty_option_v21_2_pre_market_controller import (
    prepare_nifty_candidates,
)

from modules.nifty_option_v21_2_observation_cycle import (
    capture_observation_cycle,
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

from modules.nifty_option_v21_2_14_risk_stop import (
    evaluate_real_market_risk_stop,
)


def main():

    print("=" * 70)
    print("JKJ AI TRADER")
    print("V21.2.14 — REAL-MARKET RISK + STOP-LOSS")
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
    # 2. Candidate preparation
    # ---------------------------------------------------------

    preparation = prepare_nifty_candidates()

    if preparation.get("Status") != "CANDIDATES_READY":
        print("Candidate preparation failed.")
        print(preparation)
        return

    contracts = preparation.get(
        "All Candidates",
        [],
    )

    print(f"NIFTY Spot: {preparation.get('NIFTY Spot')}")
    print(f"Expiry: {preparation.get('Expiry')}")
    print(f"Candidate Count: {len(contracts)}")

    for candidate in contracts:
        print(
            f" - {candidate.get('tradingsymbol')} | "
            f"{candidate.get('instrument_type')} | "
            f"Strike {candidate.get('strike')}"
        )

    # ---------------------------------------------------------
    # 3. Capture one fresh observation window
    #
    # Four cycles give three movement intervals and
    # at least three prices for V14.3.
    # ---------------------------------------------------------

    observation_cycles = []

    for cycle_number in range(4):

        cycle = capture_observation_cycle(
            kite,
            contracts,
        )

        if cycle.get("Status") != (
            "OBSERVATION_CYCLE_COMPLETE"
        ):
            print(
                f"Observation cycle {cycle_number + 1} failed."
            )
            print(cycle)
            return

        observation_cycles.append(
            cycle.get("Observations", [])
        )

        if cycle_number < 3:
            import time
            time.sleep(10)

    # ---------------------------------------------------------
    # 4. Build contract-specific observation histories
    # ---------------------------------------------------------

    contract_observations = {}

    for cycle in observation_cycles:

        for observation in cycle:

            symbol = observation.get(
                "Trading Symbol"
            )

            if symbol not in contract_observations:
                contract_observations[symbol] = []

            contract_observations[symbol].append(
                observation
            )

    # ---------------------------------------------------------
    # 5. V21.2.10 Momentum Confirmation
    #
    # This deliberately captures its own internal observation
    # window because the existing V21.2.10 interface does not
    # expose its observation history.
    # ---------------------------------------------------------

    momentum_result = (
        evaluate_real_market_momentum_confirmation(
            kite,
            contracts,
            observation_count=4,
            interval_seconds=10,
        )
    )

    if momentum_result.get("Status") != (
        "MOMENTUM_CONFIRMATION_COMPLETE"
    ):
        print("V21.2.10 failed.")
        print(momentum_result)
        return

    print()
    print(
        f"V21.2.10 Status: "
        f"{momentum_result.get('Status')}"
    )

    # ---------------------------------------------------------
    # 6. V21.2.11 → V21.2.12 → V21.2.13 → V21.2.14
    # ---------------------------------------------------------

    completed = 0

    print()
    print("V21.2.14 RESULTS")
    print("-" * 70)

    for momentum_item in momentum_result.get(
        "Results",
        [],
    ):

        symbol = momentum_item.get(
            "Trading Symbol"
        )

        momentum_confirmation = momentum_item.get(
            "Momentum Confirmation"
        )

        if not momentum_confirmation:
            print(
                f"{symbol}: Missing Momentum Confirmation"
            )
            continue

        # -----------------------------------------------------
        # V21.2.11
        # -----------------------------------------------------

        market_context = (
            evaluate_real_market_market_context(
                momentum_confirmation
            )
        )

        if market_context.get("Status") != (
            "MARKET_CONTEXT_COMPLETE"
        ):
            print(
                f"{symbol}: V21.2.11 failed"
            )
            continue

        # -----------------------------------------------------
        # V21.2.12
        # -----------------------------------------------------

        opportunity_risk = (
            evaluate_real_market_opportunity_risk(
                market_context
            )
        )

        if opportunity_risk.get("Status") != (
            "OPPORTUNITY_RISK_COMPLETE"
        ):
            print(
                f"{symbol}: V21.2.12 failed"
            )
            continue

        # -----------------------------------------------------
        # V21.2.13
        # -----------------------------------------------------

        decision_entry = (
            evaluate_real_market_decision_entry(
                opportunity_risk
            )
        )

        if decision_entry.get("Status") != (
            "DECISION_ENTRY_COMPLETE"
        ):
            print(
                f"{symbol}: V21.2.13 failed"
            )
            continue

        # -----------------------------------------------------
        # Contract-specific price history
        # -----------------------------------------------------

        observations = contract_observations.get(
            symbol,
            [],
        )

        # -----------------------------------------------------
        # V21.2.14
        # -----------------------------------------------------

        risk_stop = evaluate_real_market_risk_stop(
            decision_entry,
            observations,
        )

        print(
            f"{symbol}: "
            f"Entry {decision_entry.get('Entry Qualification')}, "
            f"Risk {decision_entry.get('Risk Classification')}, "
            f"Quality {decision_entry.get('Trade Quality')}, "
            f"Entry Risk "
            f"{risk_stop.get('Entry Risk Context')}, "
            f"Stop Context "
            f"{risk_stop.get('Stop-Loss Context')}"
        )

        stop_result = risk_stop.get(
            "Stop-Loss Result",
            {},
        )

        print(
            f"  Status: {risk_stop.get('Status')} | "
            f"Stop Result: "
            f"{stop_result.get('Status')} | "
            f"Entry Price: "
            f"{risk_stop.get('Entry Price')} | "
            f"Stop Price: "
            f"{stop_result.get('Stop Price')}"
        )

        print(
            f"  Live Order: "
            f"{risk_stop.get('Live Order')} | "
            f"Paper Trade: "
            f"{risk_stop.get('Paper Trade')}"
        )

        if risk_stop.get("Status") == (
            "RISK_STOP_COMPLETE"
        ):
            completed += 1

    # ---------------------------------------------------------
    # 7. Final result
    # ---------------------------------------------------------

    print()
    print(
        f"Completed {completed}/"
        f"{len(momentum_result.get('Results', []))}"
    )

    print("Live Order: FALSE")
    print("Paper Trade: FALSE")

    if completed == len(
        momentum_result.get("Results", [])
    ):
        print("V21.2.14 TEST PASS")
    else:
        print("V21.2.14 TEST INCOMPLETE")


if __name__ == "__main__":
    main()