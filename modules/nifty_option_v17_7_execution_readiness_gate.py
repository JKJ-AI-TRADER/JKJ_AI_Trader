"""
JKJ AI Trader
V17.7.5 — Execution Readiness Gate

Purpose:
Provide a final safety gate after V17.7.4 final quantity-plan
validation.

This module:
- Accepts only a validated V17.7.4 final quantity plan.
- Verifies that executable candidates remain fully validated.
- Preserves Decision/Risk priority.
- Preserves contract identity and quantity integrity.
- Prevents blocked or unallocated candidates from becoming executable.
- Does NOT rank candidates.
- Does NOT reallocate capital.
- Does NOT modify quantity.
- Does NOT modify entry, stop-loss, or targets.
- Does NOT place orders.
"""

from typing import Any, Dict, List


def _blocked(reason: str) -> Dict[str, Any]:
    """Return a safely blocked execution-readiness result."""
    return {
        "Status": "EXECUTION_READINESS_BLOCKED",
        "Reason": reason,
        "Execution Ready Candidates": 0,
        "Blocked Candidates": 0,
        "Execution Candidates": [],
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Order Placement Permitted": False,
        "Wisdom Before Wealth": True,
    }


def validate_execution_readiness(
    final_quantity_plan: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Validate whether the final quantity plan is ready to enter
    a future execution layer.

    This function DOES NOT permit or place an order.

    Expected input:
        V17.7.4 FINAL_QUANTITY_PLAN_VALIDATED result.
    """

    if not isinstance(final_quantity_plan, dict):
        return _blocked(
            "Final quantity plan must be a dictionary"
        )

    if final_quantity_plan.get("Status") != (
        "FINAL_QUANTITY_PLAN_VALIDATED"
    ):
        return _blocked(
            "V17.7.4 final quantity plan is not validated"
        )

    if final_quantity_plan.get("Capital Reassignment") is not False:
        return _blocked(
            "Capital reassignment must remain False"
        )

    if final_quantity_plan.get("Automatic Ranking") is not False:
        return _blocked(
            "Automatic ranking must remain False"
        )

    if final_quantity_plan.get("Priority Source") != (
        "DECISION_RISK_LAYER"
    ):
        return _blocked(
            "Priority source must remain DECISION_RISK_LAYER"
        )

    if final_quantity_plan.get("Order Placement Permitted") is not False:
        return _blocked(
            "Order placement must remain disabled"
        )

    validation_results = final_quantity_plan.get(
        "Validation Results"
    )

    if not isinstance(validation_results, list):
        return _blocked(
            "Final quantity validation results are missing"
        )

    execution_candidates: List[Dict[str, Any]] = []
    blocked_candidates = 0
    seen_candidates = set()
    seen_priorities = set()

    for item in validation_results:

        if not isinstance(item, dict):
            return _blocked(
                "Invalid final quantity validation entry"
            )

        candidate = item.get("Candidate")

        if not candidate:
            return _blocked(
                "Candidate identity is missing"
            )

        if candidate in seen_candidates:
            return _blocked(
                f"Duplicate execution candidate: {candidate}"
            )

        seen_candidates.add(candidate)

        status = item.get("Status")

        # ---------------------------------------------------------
        # NOT ALLOCATED
        # ---------------------------------------------------------
        if status == "NOT_ALLOCATED":

            if item.get("Execution Eligible") is not False:
                return _blocked(
                    f"Unallocated candidate cannot be execution eligible: {candidate}"
                )

            if item.get("Order Placement Permitted") is not False:
                return _blocked(
                    f"Unallocated candidate cannot permit order placement: {candidate}"
                )

            continue

        # ---------------------------------------------------------
        # ONLY FINAL QUANTITY VALIDATED CANDIDATES MAY PROCEED
        # ---------------------------------------------------------
        if status != "FINAL_QUANTITY_VALIDATED":
            blocked_candidates += 1
            continue

        if item.get("Validated") is not True:
            return _blocked(
                f"Candidate is not validated: {candidate}"
            )

        if item.get("Execution Eligible") is not True:
            return _blocked(
                f"Candidate is not execution eligible: {candidate}"
            )

        if item.get("Order Placement Permitted") is not False:
            return _blocked(
                f"Order placement flag must remain False: {candidate}"
            )

        priority = item.get("Priority")

        if not isinstance(priority, int) or priority <= 0:
            return _blocked(
                f"Invalid priority: {candidate}"
            )

        if priority in seen_priorities:
            return _blocked(
                f"Duplicate priority: {candidate}"
            )

        seen_priorities.add(priority)

        quantity = item.get("Reconciled Quantity")
        lots = item.get("Reconciled Lots")
        lot_size = item.get("Lot Size")
        allocated_capital = item.get("Allocated Capital")
        required_capital = item.get("Required Capital")

        if not isinstance(quantity, int) or quantity <= 0:
            return _blocked(
                f"Invalid execution quantity: {candidate}"
            )

        if not isinstance(lots, int) or lots <= 0:
            return _blocked(
                f"Invalid execution lots: {candidate}"
            )

        if not isinstance(lot_size, int) or lot_size <= 0:
            return _blocked(
                f"Invalid contract lot size: {candidate}"
            )

        if quantity != lots * lot_size:
            return _blocked(
                f"Execution quantity does not match contract lot size: {candidate}"
            )

        if not isinstance(
            allocated_capital, (int, float)
        ) or allocated_capital <= 0:
            return _blocked(
                f"Invalid allocated capital: {candidate}"
            )

        if not isinstance(
            required_capital, (int, float)
        ) or required_capital <= 0:
            return _blocked(
                f"Invalid required capital: {candidate}"
            )

        if required_capital > allocated_capital + 0.01:
            return _blocked(
                f"Required capital exceeds allocation: {candidate}"
            )

        if item.get("Contract Identity Valid") is not True:
            return _blocked(
                f"Contract identity is not valid: {candidate}"
            )

        trading_symbol = item.get("Trading Symbol")
        instrument_token = item.get("Instrument Token")

        if not trading_symbol:
            return _blocked(
                f"Trading symbol is missing: {candidate}"
            )

        if not isinstance(instrument_token, int) or instrument_token <= 0:
            return _blocked(
                f"Instrument token is invalid: {candidate}"
            )

        execution_candidates.append(
            {
                "Candidate": candidate,
                "Priority": priority,
                "Trading Symbol": trading_symbol,
                "Instrument Token": instrument_token,
                "Entry Price": item.get("Entry Price"),
                "Lot Size": lot_size,
                "Reconciled Lots": lots,
                "Reconciled Quantity": quantity,
                "Allocated Capital": float(
                    allocated_capital
                ),
                "Required Capital": float(
                    required_capital
                ),
                "Contract Identity Valid": True,
                "Validated": True,
                "Execution Ready": True,
                "Order Placement Permitted": False,
            }
        )

    return {
        "Status": "EXECUTION_READINESS_VALIDATED",
        "Execution Ready Candidates": len(
            execution_candidates
        ),
        "Blocked Candidates": blocked_candidates,
        "Execution Candidates": execution_candidates,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Order Placement Permitted": False,
        "Wisdom Before Wealth": True,
    }