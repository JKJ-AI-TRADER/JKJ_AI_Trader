"""
JKJ AI Trader
Intraday Option Entry Bridge V8

Purpose:
Connect the Option Opportunity Decision with the existing
Cost Engine, Risk Engine and Entry Gate.

This module does NOT:
- place orders
- connect to Zerodha
- modify main.py
- modify the existing Momentum Engine
- replace the Entry Gate
"""

from modules.intraday_cost_engine import (
    calculate_intraday_cost
)

from modules.intraday_risk_engine import (
    analyse_intraday_risk
)

from modules.intraday_entry_gate import (
    evaluate_intraday_entry
)


def evaluate_option_entry(
    opportunity_result,
    momentum_result,
    option_type,
    entry_price,
    stop_loss_price,
    target_price,
    quantity,
    peak_price=None,
):
    """
    Evaluate an option candidate through:

        Opportunity
            ↓
        Cost
            ↓
        Risk
            ↓
        Entry Gate

    Returns a final pre-entry assessment.

    No broker order is placed.
    """

    # ---------------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------------

    if not isinstance(opportunity_result, dict):
        return {
            "Status": "INVALID",
            "Decision": "NO TRADE",
            "Reasons": [
                "Opportunity result must be a dictionary."
            ],
        }

    if not isinstance(momentum_result, dict):
        return {
            "Status": "INVALID",
            "Decision": "NO TRADE",
            "Reasons": [
                "Momentum result must be a dictionary."
            ],
        }

    if opportunity_result.get("Status") != "READY":
        return {
            "Status": "READY",
            "Decision": "NO TRADE",
            "Reasons": [
                "Opportunity decision is not ready."
            ],
        }

    if momentum_result.get("Status") != "READY":
        return {
            "Status": "READY",
            "Decision": "NO TRADE",
            "Reasons": [
                "Momentum result is not ready."
            ],
        }

    if opportunity_result.get(
        "Decision"
    ) not in (
        "ENTRY CANDIDATE",
        "STRONG ENTRY CANDIDATE",
    ):
        return {
            "Status": "READY",
            "Decision": "NO TRADE",
            "Reasons": [
                "Option opportunity has not reached "
                "entry-candidate status."
            ],
        }

    if option_type not in (
        "CE",
        "PE",
    ):
        return {
            "Status": "INVALID",
            "Decision": "NO TRADE",
            "Reasons": [
                "Option type must be CE or PE."
            ],
        }

    numeric_values = {
        "Entry Price": entry_price,
        "Stop Loss": stop_loss_price,
        "Target Price": target_price,
        "Quantity": quantity,
    }

    for field, value in numeric_values.items():

        if not isinstance(
            value,
            (int, float)
        ):
            return {
                "Status": "INVALID",
                "Decision": "NO TRADE",
                "Reasons": [
                    f"{field} must be numeric."
                ],
            }

    if entry_price <= 0:
        return {
            "Status": "INVALID",
            "Decision": "NO TRADE",
            "Reasons": [
                "Entry price must be greater than zero."
            ],
        }

    if stop_loss_price >= entry_price:
        return {
            "Status": "INVALID",
            "Decision": "NO TRADE",
            "Reasons": [
                "Stop loss must be below entry price."
            ],
        }

    if target_price <= entry_price:
        return {
            "Status": "INVALID",
            "Decision": "NO TRADE",
            "Reasons": [
                "Target price must be above entry price."
            ],
        }

    if quantity <= 0:
        return {
            "Status": "INVALID",
            "Decision": "NO TRADE",
            "Reasons": [
                "Quantity must be greater than zero."
            ],
        }

    # ---------------------------------------------------------
    # OPPORTUNITY INFORMATION
    # ---------------------------------------------------------

    opportunity_decision = opportunity_result[
        "Decision"
    ]

    momentum_score = momentum_result.get(
        "Momentum Score",
        0
    )

    exhaustion_score = momentum_result.get("Exhaustion Penalty",0)
    

    # ---------------------------------------------------------
    # RISK / REWARD
    # ---------------------------------------------------------

    risk_amount = (
        entry_price
        - stop_loss_price
    )

    reward_amount = (
        target_price
        - entry_price
    )

    if risk_amount <= 0:
        return {
            "Status": "INVALID",
            "Decision": "NO TRADE",
            "Reasons": [
                "Risk amount must be greater than zero."
            ],
        }

    risk_reward_ratio = (
        reward_amount
        / risk_amount
    )

    # ---------------------------------------------------------
    # COST ENGINE
    # ---------------------------------------------------------

    cost_result = calculate_intraday_cost(
        instrument_type="options",
        buy_price=entry_price,
        sell_price=target_price,
        quantity=quantity,
    )

    if cost_result.get("Status") not in ("PROFITABLE", "BREAKEVEN"):
        return {
            "Status": "READY",
            "Decision": "NO TRADE",
            "Reasons": [
                "Cost calculation failed."
            ],
            "Cost Result": cost_result,
        }

    # ---------------------------------------------------------
    # RISK ENGINE
    # ---------------------------------------------------------

    risk_result = analyse_intraday_risk(
        entry_price=entry_price,
        stop_loss=stop_loss_price,
        target_price=target_price,
        setup_score=momentum_score,
        trading_allowed=True,
    )

    # ---------------------------------------------------------
    # ENTRY GATE
    # ---------------------------------------------------------

    entry_gate_result = evaluate_intraday_entry(
        momentum_result=momentum_result,
        cost_result=cost_result,
        risk_reward_ratio=risk_reward_ratio,
        current_price=entry_price,
        peak_price=peak_price,
    )

    # ---------------------------------------------------------
    # FINAL DECISION
    # ---------------------------------------------------------

    if not entry_gate_result.get("Entry Allowed",False):
    
        final_decision = "NO TRADE"

    else:
        final_decision = opportunity_decision

    return {
        "Status": "READY",
        "Decision": final_decision,
        "Option Type": option_type,
        "Entry Price": entry_price,
        "Stop Loss": stop_loss_price,
        "Target Price": target_price,
        "Quantity": quantity,
        "Risk Amount": round(
            risk_amount,
            4
        ),
        "Reward Amount": round(
            reward_amount,
            4
        ),
        "Risk Reward Ratio": round(
            risk_reward_ratio,
            4
        ),
        "Momentum Score": momentum_score,
        "Exhaustion Score": exhaustion_score,
        "Opportunity Decision": opportunity_decision,
        "Cost Result": cost_result,
        "Risk Result": risk_result,
        "Entry Gate Result": entry_gate_result,
        "Reasons": [
            "Option opportunity evaluated through "
            "cost, risk and entry-gate controls."
        ],
    }