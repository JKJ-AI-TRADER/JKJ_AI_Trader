"""
JKJ AI Trader
V21.2.17 — Real-Market Risk + Stop-Loss + Targets

Consumes:
    V21.2.16 Decision + Entry Qualification
    V21.2.15 Unified Observation

Uses:
    V14.1 Entry Risk Context
    V14.2 Stop-Loss Context
    V14.3 Stop-Loss Price
    V14.4 Targets 1–3

Important:
    No new market observations.
    No live orders.
    No paper trades.
    No position sizing.
    No exit decisions.

Diagnostic principle:
    Even when risk/stop processing rejects a contract,
    preserve the V21.2.16 decision information so the
    complete JKJ decision chain remains explainable.
"""

from modules.nifty_option_entry_risk_context import (
    evaluate_entry_risk_context,
)

from modules.nifty_option_stop_loss_context import (
    evaluate_stop_loss_context,
)

from modules.nifty_option_stop_loss_price import (
    evaluate_stop_loss_price,
)

from modules.nifty_option_targets import (
    evaluate_targets,
)


def _base_contract_data(decision_item):
    """
    Preserve the V21.2.16 decision information in every
    downstream V21.2.17 contract result.
    """

    return {
        "Trading Symbol": decision_item.get(
            "Trading Symbol"
        ),
        "Underlying": decision_item.get(
            "Underlying"
        ),
        "Expiry": decision_item.get(
            "Expiry"
        ),
        "Strike": decision_item.get(
            "Strike"
        ),
        "Option Type": decision_item.get(
            "Option Type"
        ),

        "Option Direction": decision_item.get(
            "Option Direction"
        ),
        "Momentum Confirmation": decision_item.get(
            "Momentum Confirmation"
        ),
        "Market Context": decision_item.get(
            "Market Context"
        ),
        "Movement Relationship": decision_item.get(
            "Movement Relationship"
        ),
        "Momentum Context": decision_item.get(
            "Momentum Context"
        ),

        "Opportunity Classification": decision_item.get(
            "Opportunity Classification"
        ),
        "Opportunity Strength": decision_item.get(
            "Opportunity Strength"
        ),
        "Risk Classification": decision_item.get(
            "Risk Classification"
        ),
        "Trade Quality": decision_item.get(
            "Trade Quality"
        ),
        "Entry Qualification": decision_item.get(
            "Entry Qualification"
        ),
    }


def evaluate_real_market_risk_stop_targets(
    decision_entry_result,
    unified_observation_result,
):
    """
    Process the existing V21.2.16 decision result through:

        V14.1 → V14.2 → V14.3 → V14.4

    using the SAME V21.2.15 observation history.
    """

    if not isinstance(decision_entry_result, dict):
        return {
            "Status": "REJECTED",
            "Reason": (
                "Decision Entry result must be a dictionary"
            ),
            "Live Order": False,
            "Paper Trade": False,
        }

    if decision_entry_result.get("Status") != (
        "DECISION_ENTRY_COMPLETE"
    ):
        return {
            "Status": "REJECTED",
            "Reason": (
                "Decision Entry result must be "
                "DECISION_ENTRY_COMPLETE"
            ),
            "Live Order": False,
            "Paper Trade": False,
        }

    if not isinstance(unified_observation_result, dict):
        return {
            "Status": "REJECTED",
            "Reason": (
                "Unified Observation result must be "
                "a dictionary"
            ),
            "Live Order": False,
            "Paper Trade": False,
        }

    if unified_observation_result.get("Status") != (
        "UNIFIED_OBSERVATION_COMPLETE"
    ):
        return {
            "Status": "REJECTED",
            "Reason": (
                "Unified Observation result must be "
                "UNIFIED_OBSERVATION_COMPLETE"
            ),
            "Live Order": False,
            "Paper Trade": False,
        }

    decision_results = decision_entry_result.get(
        "Results"
    )

    if not isinstance(decision_results, list):
        return {
            "Status": "REJECTED",
            "Reason": (
                "Decision Entry Results must be a list"
            ),
            "Live Order": False,
            "Paper Trade": False,
        }

    observations_by_contract = (
        unified_observation_result.get(
            "Observations By Contract"
        )
    )

    if not isinstance(
        observations_by_contract,
        dict,
    ):
        return {
            "Status": "REJECTED",
            "Reason": (
                "Unified Observation must contain "
                "'Observations By Contract'"
            ),
            "Live Order": False,
            "Paper Trade": False,
        }

    results = []

    for decision_item in decision_results:

        if not isinstance(
            decision_item,
            dict,
        ):
            results.append({
                "Status": "REJECTED",
                "Reason": (
                    "Decision result item must be "
                    "a dictionary"
                ),
                "Live Order": False,
                "Paper Trade": False,
            })
            continue

        contract_data = _base_contract_data(
            decision_item
        )

        trading_symbol = contract_data.get(
            "Trading Symbol"
        )

        # ---------------------------------------------------------
        # V21.2.15 identity
        # ---------------------------------------------------------

        observation_identity = (
            decision_item.get("Trading Symbol"),
            decision_item.get("Underlying"),
            decision_item.get("Expiry"),
            decision_item.get("Strike"),
            decision_item.get("Option Type"),
        )

        contract_observations = (
            observations_by_contract.get(
                observation_identity
            )
        )

        if not isinstance(
            contract_observations,
            list,
        ):
            results.append({
                "Status": "RISK_STOP_TARGETS_REJECTED",
                **contract_data,
                "Reason": (
                    "No observation history found "
                    "for contract identity"
                ),
                "Observation Identity": (
                    observation_identity
                ),
                "Live Order": False,
                "Paper Trade": False,
            })
            continue

        # ---------------------------------------------------------
        # V13.2 result
        # ---------------------------------------------------------

        entry_qualification_result = (
            decision_item.get(
                "Entry Qualification Result"
            )
        )

        if not isinstance(
            entry_qualification_result,
            dict,
        ):
            results.append({
                "Status": "RISK_STOP_TARGETS_REJECTED",
                **contract_data,
                "Reason": (
                    "Missing Entry Qualification Result"
                ),
                "Observation Identity": (
                    observation_identity
                ),
                "Observation Count": len(
                    contract_observations
                ),
                "Live Order": False,
                "Paper Trade": False,
            })
            continue

        # ---------------------------------------------------------
        # V14.1 — Entry Risk Context
        # ---------------------------------------------------------

        entry_risk_context = (
            evaluate_entry_risk_context(
                entry_qualification_result
            )
        )

        if entry_risk_context.get(
            "Status"
        ) != "EVALUATED":

            results.append({
                "Status": "RISK_STOP_TARGETS_REJECTED",
                **contract_data,
                "Reason": (
                    "V14.1 Entry Risk Context "
                    "evaluation rejected"
                ),
                "Entry Risk Context Result": (
                    entry_risk_context
                ),
                "Observation Count": len(
                    contract_observations
                ),
                "Live Order": False,
                "Paper Trade": False,
            })
            continue

        # ---------------------------------------------------------
        # V14.2 — Stop-Loss Context
        # ---------------------------------------------------------

        stop_loss_context = (
            evaluate_stop_loss_context(
                entry_risk_context
            )
        )

        if stop_loss_context.get(
            "Status"
        ) != "EVALUATED":

            results.append({
                "Status": "RISK_STOP_TARGETS_REJECTED",
                **contract_data,
                "Entry Risk Context": (
                    entry_risk_context.get(
                        "Entry Risk Context"
                    )
                ),
                "Reason": (
                    "V14.2 Stop-Loss Context "
                    "evaluation rejected"
                ),
                "Entry Risk Context Result": (
                    entry_risk_context
                ),
                "Stop-Loss Context Result": (
                    stop_loss_context
                ),
                "Observation Count": len(
                    contract_observations
                ),
                "Live Order": False,
                "Paper Trade": False,
            })
            continue

        # ---------------------------------------------------------
        # Build price history
        # ---------------------------------------------------------

        if len(contract_observations) < 3:

            results.append({
                "Status": "RISK_STOP_TARGETS_REJECTED",
                **contract_data,
                "Entry Risk Context": (
                    entry_risk_context.get(
                        "Entry Risk Context"
                    )
                ),
                "Stop-Loss Context": (
                    stop_loss_context.get(
                        "Stop-Loss Context"
                    )
                ),
                "Reason": (
                    "At least 3 observations are "
                    "required for V14.3"
                ),
                "Observation Count": len(
                    contract_observations
                ),
                "Live Order": False,
                "Paper Trade": False,
            })
            continue

        observation_history = []
        invalid_observation = None

        for observation in contract_observations:

            if not isinstance(
                observation,
                dict,
            ):
                invalid_observation = (
                    "Observation must be a dictionary"
                )
                break

            if observation.get(
                "Status"
            ) != "RECORDED":
                invalid_observation = (
                    "Observation must have "
                    "Status RECORDED"
                )
                break

            if observation.get(
                "Trading Symbol"
            ) != trading_symbol:
                invalid_observation = (
                    "Observation Trading Symbol "
                    "does not match decision "
                    "Trading Symbol"
                )
                break

            current_price = observation.get(
                "Current Price"
            )

            if not isinstance(
                current_price,
                (int, float),
            ):
                invalid_observation = (
                    "Observation Current Price "
                    "must be numeric"
                )
                break

            if current_price <= 0:
                invalid_observation = (
                    "Observation Current Price "
                    "must be positive"
                )
                break

            observation_history.append(
                current_price
            )

        if invalid_observation:

            results.append({
                "Status": "RISK_STOP_TARGETS_REJECTED",
                **contract_data,
                "Entry Risk Context": (
                    entry_risk_context.get(
                        "Entry Risk Context"
                    )
                ),
                "Stop-Loss Context": (
                    stop_loss_context.get(
                        "Stop-Loss Context"
                    )
                ),
                "Reason": invalid_observation,
                "Observation Count": len(
                    contract_observations
                ),
                "Observation History": (
                    observation_history
                ),
                "Price History": (
                    observation_history[:-1]
                ),
                "Live Order": False,
                "Paper Trade": False,
            })
            continue

        if len(observation_history) < 2:

            results.append({
                "Status": "RISK_STOP_TARGETS_REJECTED",
                **contract_data,
                "Entry Risk Context": (
                    entry_risk_context.get(
                        "Entry Risk Context"
                    )
                ),
                "Stop-Loss Context": (
                    stop_loss_context.get(
                        "Stop-Loss Context"
                    )
                ),
                "Reason": (
                    "At least 2 observations are "
                    "required to separate entry "
                    "price from pre-entry stop-loss "
                    "history"
                ),
                "Observation Count": len(
                    observation_history
                ),
                "Observation History": (
                    observation_history
                ),
                "Price History": (
                    observation_history[:-1]
                ),
                "Live Order": False,
                "Paper Trade": False,
            })
            continue

        # ---------------------------------------------------------
        # Latest observation = entry reference
        # Earlier observations = V14.3 stop-loss history
        # ---------------------------------------------------------

        entry_price = observation_history[-1]

        price_history = observation_history[:-1]

        # ---------------------------------------------------------
        # V14.3 — Stop-Loss Price
        # ---------------------------------------------------------

        stop_loss_price = (
            evaluate_stop_loss_price(
                stop_loss_context,
                entry_price,
                price_history,
            )
        )

        if stop_loss_price.get(
            "Status"
        ) != "STOP_VALIDATED":

            results.append({
                "Status": "RISK_STOP_TARGETS_REJECTED",
                **contract_data,
                "Entry Risk Context": (
                    entry_risk_context.get(
                        "Entry Risk Context"
                    )
                ),
                "Stop-Loss Context": (
                    stop_loss_context.get(
                        "Stop-Loss Context"
                    )
                ),
                "Observation Count": len(
                    contract_observations
                ),
                "Price History": price_history,
                "Entry Price": entry_price,
                "Reason": (
                    "V14.3 Stop-Loss Price "
                    "validation rejected"
                ),
                "Stop-Loss Price Result": (
                    stop_loss_price
                ),
                "Live Order": False,
                "Paper Trade": False,
            })
            continue

        # ---------------------------------------------------------
        # V14.4 — Targets 1–3
        # ---------------------------------------------------------

        targets = evaluate_targets(
            stop_loss_price
        )

        if targets.get(
            "Status"
        ) != "TARGETS_VALIDATED":

            results.append({
                "Status": "RISK_STOP_TARGETS_REJECTED",
                **contract_data,
                "Entry Risk Context": (
                    entry_risk_context.get(
                        "Entry Risk Context"
                    )
                ),
                "Stop-Loss Context": (
                    stop_loss_context.get(
                        "Stop-Loss Context"
                    )
                ),
                "Observation Count": len(
                    contract_observations
                ),
                "Price History": price_history,
                "Entry Price": entry_price,
                "Reason": (
                    "V14.4 Targets validation "
                    "rejected"
                ),
                "Stop-Loss Price Result": (
                    stop_loss_price
                ),
                "Targets Result": targets,
                "Live Order": False,
                "Paper Trade": False,
            })
            continue

        # ---------------------------------------------------------
        # Complete successful result
        # ---------------------------------------------------------

        results.append({
            "Status": "RISK_STOP_TARGETS_COMPLETE",
            **contract_data,

            "Entry Risk Context": (
                entry_risk_context.get(
                    "Entry Risk Context"
                )
            ),
            "Stop-Loss Context": (
                stop_loss_context.get(
                    "Stop-Loss Context"
                )
            ),

            "Observation Count": len(
                contract_observations
            ),
            "Price History": price_history,

            "Entry Price": stop_loss_price.get(
                "Entry Price"
            ),
            "Structural Low": stop_loss_price.get(
                "Structural Low"
            ),
            "Stop Price": stop_loss_price.get(
                "Stop Price"
            ),
            "Stop Distance": stop_loss_price.get(
                "Stop Distance"
            ),

            "Target 1": targets.get(
                "Target 1"
            ),
            "Target 2": targets.get(
                "Target 2"
            ),
            "Target 3": targets.get(
                "Target 3"
            ),

            "Entry Risk Context Result": (
                entry_risk_context
            ),
            "Stop-Loss Context Result": (
                stop_loss_context
            ),
            "Stop-Loss Price Result": (
                stop_loss_price
            ),
            "Targets Result": targets,

            "Live Order": False,
            "Paper Trade": False,
        })

    return {
        "Status": "RISK_STOP_TARGETS_COMPLETE",
        "Contract Count": len(results),
        "Results": results,
        "New Market Observations": False,
        "Live Order": False,
        "Paper Trade": False,
    }
