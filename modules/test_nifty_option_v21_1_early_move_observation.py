"""
JKJ AI Trader
V21.1 — Real-Market Early-Move Observation

Purpose:
Observe whether a selected NIFTY option shows persistent
directional movement after the market opens.

This module does NOT:
- place live orders
- create paper trades
- make BUY/SELL decisions
- calculate opportunity scores
- modify V12.1-V20 production modules
- modify main.py

Architecture:

Zerodha
    ↓
Same Contract Observation 1
        ↓
Same Contract Observation 2
        ↓
Same Contract Observation 3
        ↓
Same Contract Observation 4
    ↓
V12.4 Movement Analysis
    ↓
V12.5 Direction
    ↓
V12.6 Persistence
"""

import time

from modules.intraday_zerodha_session_manager import (
    get_kite_session,
)

from modules.nifty_option_contract_selector import (
    select_nearby_contracts,
)

from modules.intraday_zerodha_option_adapter import (
    adapt_zerodha_option_quote,
)

from modules.intraday_option_real_market_observer import (
    observe_option_market,
)

from modules.intraday_option_observation_record import (
    create_option_observation_record,
)

from modules.nifty_option_movement_analyzer import (
    analyze_option_movement,
)

from modules.nifty_option_movement_direction import (
    interpret_movement_direction,
)

from modules.nifty_option_momentum_sequence import (
    evaluate_momentum_sequence,
)


def _select_contract(kite, option_type):
    """
    Select one current NIFTY option contract and return
    the locked contract identity.
    """

    instruments = kite.instruments("NFO")

    if not isinstance(instruments, list):
        return {
            "Status": "REJECTED",
            "Reason": "NFO instrument list unavailable.",
        }

    nifty_spot = kite.ltp(
        "NSE:NIFTY 50"
    )["NSE:NIFTY 50"]["last_price"]

    if not isinstance(
        nifty_spot,
        (int, float),
    ) or nifty_spot <= 0:
        return {
            "Status": "REJECTED",
            "Reason": "Invalid NIFTY spot price.",
        }

    nifty_options = [
        item
        for item in instruments
        if item.get("name") == "NIFTY"
        and item.get("instrument_type") in ("CE", "PE")
    ]

    expiries = sorted({
        item.get("expiry")
        for item in nifty_options
        if item.get("expiry")
    })

    if not expiries:
        return {
            "Status": "REJECTED",
            "Reason": "No NIFTY option expiry found.",
        }

    selected_expiry = expiries[0]

    selection = select_nearby_contracts(
        instruments=nifty_options,
        nifty_spot=nifty_spot,
        expiry=selected_expiry,
        contracts_per_side=2,
    )

    if selection.get("Status") != "SELECTED":
        return {
            "Status": "REJECTED",
            "Reason": selection.get(
                "Reason",
                "NIFTY option contract selection failed.",
            ),
        }

    contracts = [
        contract
        for contract in selection.get("Contracts", [])
        if contract.get("instrument_type") == option_type
    ]

    if not contracts:
        return {
            "Status": "REJECTED",
            "Reason": (
                f"No {option_type} contract was selected."
            ),
        }

    contract = contracts[0]

    trading_symbol = contract.get("tradingsymbol")
    instrument_token = contract.get("instrument_token")

    if not trading_symbol or not instrument_token:
        return {
            "Status": "REJECTED",
            "Reason": "Selected contract is incomplete.",
        }

    return {
        "Status": "SELECTED",
        "NIFTY Spot": nifty_spot,
        "Expiry": selected_expiry,
        "Trading Symbol": trading_symbol,
        "Option Type": option_type,
        "Instrument Token": instrument_token,
        "Strike": contract.get("strike"),
    }


def _capture_same_contract_observation(
    kite,
    trading_symbol,
    instrument_token,
    expiry,
    strike,
    option_type,
):
    """
    Capture one fresh observation for the already locked
    contract.
    """

    quote_response = kite.quote(
        [
            f"NFO:{trading_symbol}",
            "NSE:NIFTY 50",
        ]
    )

    underlying_price = quote_response[
        "NSE:NIFTY 50"
    ].get("last_price")

    underlying_data = {
        "Underlying": "NIFTY",
        "Current Price": underlying_price,
    }

    adapted_data = adapt_zerodha_option_quote(
        quote_response,
        trading_symbol,
        instrument_token,
    )

    observed_data = observe_option_market(
        adapted_data,
        underlying_data,
    )

    if observed_data.get("Status") != "READY":
        return {
            "Status": "REJECTED",
            "Reason": observed_data.get(
                "Reasons",
                ["Real-market observation was not READY."],
            ),
        }

    record = create_option_observation_record(
        observed_data
    )

    nifty_spot = quote_response[
        "NSE:NIFTY 50"
    ].get("last_price")

    record["NIFTY Spot Price"] = nifty_spot

    record["Expiry"] = expiry
    record["Strike"] = strike
    record["Option Type"] = option_type
    record["Timestamp"] = record.get("Observation Timestamp")

    record["Expiry"] = expiry
    record["Strike"] = strike
    record["Option Type"] = option_type
    record["Timestamp"] = record.get("Observation Timestamp")

    if record.get("Status") != "RECORDED":
        return {
            "Status": "REJECTED",
            "Reason": record.get(
                "Reason",
                "Observation record was not created.",
            ),
        }

    return record


def collect_v21_1_observation(
    option_type="CE",
    observation_count=4,
    interval_seconds=10,
):
    """
    Collect a same-contract real-market observation sequence
    and evaluate V12.4 → V12.5 → V12.6.

    Observation only.
    """

    if option_type not in ("CE", "PE"):
        return {
            "Status": "REJECTED",
            "Reason": "Option type must be CE or PE.",
        }

    if not isinstance(observation_count, int):
        return {
            "Status": "REJECTED",
            "Reason": "Observation count must be an integer.",
        }

    if observation_count < 3:
        return {
            "Status": "REJECTED",
            "Reason": (
                "At least 3 observations are required "
                "for persistence analysis."
            ),
        }

    if not isinstance(
        interval_seconds,
        (int, float),
    ) or interval_seconds < 0:
        return {
            "Status": "REJECTED",
            "Reason": "Interval must be a non-negative number.",
        }

    session_result = get_kite_session()

    if session_result.get("Kite") is None:
        return {
            "Status": "REJECTED",
            "Stage": "SESSION",
            "Reason": session_result.get(
                "Reason",
                "Zerodha session unavailable.",
            ),
        }

    kite = session_result["Kite"]

    contract_result = _select_contract(
        kite,
        option_type,
    )

    if contract_result.get("Status") != "SELECTED":
        return contract_result

    trading_symbol = contract_result["Trading Symbol"]
    instrument_token = contract_result["Instrument Token"]

    observations = []

    for index in range(observation_count):

        if index > 0 and interval_seconds > 0:
            time.sleep(interval_seconds)

        observation = _capture_same_contract_observation(
            kite,
            trading_symbol,
            instrument_token,
            contract_result["Expiry"],
            contract_result["Strike"],
            option_type,
        )

        if observation.get("Status") != "RECORDED":
            return {
                "Status": "REJECTED",
                "Stage": "OBSERVATION",
                "Trading Symbol": trading_symbol,
                "Observation Count": len(observations),
                "Reason": observation.get(
                    "Reason",
                    "Observation failed.",
                ),
            }

        observations.append(observation)

    print("\nV21.1 OBSERVATION CHECK:")
    for item in observations:
        print(item)

    movement_results = []
    direction_results = []

    for index in range(1, len(observations)):

        movement = analyze_option_movement(
            observations[index - 1],
            observations[index],
        )

        if movement.get("Status") != "ANALYZED":
            return {
                "Status": "REJECTED",
                "Stage": "V12.4_MOVEMENT",
                "Trading Symbol": trading_symbol,
                "Reason": movement.get(
                    "Reason",
                    "Movement analysis failed.",
                ),
            }

        direction = interpret_movement_direction(
            movement
        )

        if direction.get("Status") != "INTERPRETED":
            return {
                "Status": "REJECTED",
                "Stage": "V12.5_DIRECTION",
                "Trading Symbol": trading_symbol,
                "Reason": direction.get(
                    "Reason",
                    "Direction interpretation failed.",
                ),
            }

        movement_results.append(movement)
        direction_results.append(direction)

    persistence = evaluate_momentum_sequence(
        direction_results
    )

    return {
        "Status": "OBSERVATION_COMPLETE",
        "Stage": "V21.1",
        "Session Status": session_result.get("Status"),
        "NIFTY Spot": contract_result["NIFTY Spot"],
        "Expiry": contract_result["Expiry"],
        "Trading Symbol": trading_symbol,
        "Option Type": option_type,
        "Instrument Token": instrument_token,
        "Strike": contract_result.get("Strike"),
        "Observation Count": len(observations),
        "Observations": observations,
        "Movement Results": movement_results,
        "Direction Results": direction_results,
        "Persistence": persistence,
        "Live Order": False,
        "Paper Trade": False,
    }


if __name__ == "__main__":

    print()
    print("=" * 60)
    print("JKJ AI Trader")
    print("V21.1 — Real-Market Early-Move Observation")
    print("=" * 60)
    print()

    result = collect_v21_1_observation(
        option_type="CE",
        observation_count=4,
        interval_seconds=10,
    )

    print("Status:", result.get("Status"))
    print("Stage:", result.get("Stage"))
    print("Trading Symbol:", result.get("Trading Symbol"))
    print("Option Type:", result.get("Option Type"))
    print("NIFTY Spot:", result.get("NIFTY Spot"))
    print("Observation Count:", result.get("Observation Count"))

    persistence = result.get("Persistence", {})

    print()
    print("Persistence Status:",
          persistence.get("Persistence Status"))
    print("Direction:",
          persistence.get("Direction"))
    print("Direction Sequence:",
          persistence.get("Direction Sequence"))

    print()
    print("Live Order:", result.get("Live Order"))
    print("Paper Trade:", result.get("Paper Trade"))
    print()

    if result.get("Status") == "OBSERVATION_COMPLETE":
        print("V21.1 OBSERVATION COMPLETE")
    else:
        print("V21.1 STOPPED SAFELY")
