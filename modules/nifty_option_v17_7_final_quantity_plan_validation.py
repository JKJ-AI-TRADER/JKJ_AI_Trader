"""
JKJ AI Trader
V17.7.4 — Final Quantity Plan Validation

Purpose:
Validate the final multi-candidate quantity reconciliation produced by V17.7.3.

This module:
- Validates the integrity of successful candidate quantities.
- Confirms quantity matches validated contract lot size.
- Confirms required capital does not exceed allocated capital.
- Preserves Decision/Risk priority.
- Preserves contract identity.
- Tracks blocked and uncommitted capital.
- Does NOT rank candidates.
- Does NOT reallocate capital.
- Does NOT modify quantity.
- Does NOT modify entry, stop-loss, or targets.
- Does NOT place orders.
"""

from typing import Any, Dict, List


def _blocked(reason: str) -> Dict[str, Any]:
    """Return a safely blocked final-plan result."""
    return {
        "Status": "FINAL_QUANTITY_PLAN_BLOCKED",
        "Reason": reason,
        "Validated Candidates": 0,
        "Blocked Candidates": 0,
        "Total Allocated Capital": 0.0,
        "Total Required Capital": 0.0,
        "Total Uncommitted Capital": 0.0,
        "Validation Results": [],
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Order Placement Permitted": False,
        "Wisdom Before Wealth": True,
    }


def validate_final_quantity_plan(
    reconciliation_result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Validate the final quantity plan produced by V17.7.3.

    Expected input:
        reconciliation_result from
        V17.7.3 multi-candidate quantity reconciliation.

    Returns:
        FINAL_QUANTITY_PLAN_VALIDATED
        or
        FINAL_QUANTITY_PLAN_BLOCKED
    """

    if not isinstance(reconciliation_result, dict):
        return _blocked("Reconciliation result must be a dictionary")

    if reconciliation_result.get("Status") != (
        "MULTI_CANDIDATE_RECONCILIATION_COMPLETE"
    ):
        return _blocked(
            "V17.7.3 reconciliation is not complete"
        )

    reconciliations = reconciliation_result.get("Reconciliations")

    if not isinstance(reconciliations, list):
        return _blocked(
            "Reconciliation list is missing or invalid"
        )

    if reconciliation_result.get("Capital Reassignment") is not False:
        return _blocked(
            "Capital reassignment must remain False"
        )

    if reconciliation_result.get("Automatic Ranking") is not False:
        return _blocked(
            "Automatic ranking must remain False"
        )

    if reconciliation_result.get("Priority Source") != (
        "DECISION_RISK_LAYER"
    ):
        return _blocked(
            "Priority source must remain DECISION_RISK_LAYER"
        )

    validation_results: List[Dict[str, Any]] = []

    total_allocated = 0.0
    total_required = 0.0
    total_uncommitted = 0.0

    validated_candidates = 0
    blocked_candidates = 0

    seen_candidates = set()

    for item in reconciliations:

        if not isinstance(item, dict):
            return _blocked(
                "Invalid reconciliation entry"
            )

        candidate = item.get("Candidate")

        if not candidate:
            return _blocked(
                "Candidate identity is missing"
            )

        if candidate in seen_candidates:
            return _blocked(
                f"Duplicate candidate in final quantity plan: {candidate}"
            )

        seen_candidates.add(candidate)

        allocation_status = item.get("Allocation Status")

        # ---------------------------------------------------------
        # NOT ALLOCATED CANDIDATE
        # ---------------------------------------------------------
        if item.get("Status") == "NOT_ALLOCATED":

            if allocation_status != "UNALLOCATED":
                return _blocked(
                    f"Invalid allocation status for {candidate}"
                )

            quantity = item.get("Reconciled Quantity", 0)
            lots = item.get("Reconciled Lots", 0)
            capital = float(
                item.get("Allocated Capital", 0.0)
            )

            if quantity != 0 or lots != 0 or capital != 0.0:
                return _blocked(
                    f"Unallocated candidate contains execution quantity or capital: {candidate}"
                )

            validation_results.append(
                {
                    "Candidate": candidate,
                    "Priority": item.get("Priority"),
                    "Status": "NOT_ALLOCATED",
                    "Validated": False,
                    "Execution Eligible": False,
                    "Reason": "Candidate was not allocated capital",
                    "Order Placement Permitted": False,
                }
            )

            continue

        # ---------------------------------------------------------
        # BLOCKED CANDIDATE
        # ---------------------------------------------------------
        if item.get("Status") == "RECONCILIATION_BLOCKED":

            blocked_candidates += 1

            uncommitted = float(
                item.get("Uncommitted Capital", 0.0)
            )

            allocated = float(
                item.get("Allocated Capital", 0.0)
            )

            if uncommitted != allocated:
                return _blocked(
                    f"Blocked candidate capital mismatch: {candidate}"
                )

            validation_results.append(
                {
                    "Candidate": candidate,
                    "Priority": item.get("Priority"),
                    "Status": "BLOCKED",
                    "Validated": False,
                    "Execution Eligible": False,
                    "Reason": item.get("Reason"),
                    "Uncommitted Capital": uncommitted,
                    "Order Placement Permitted": False,
                }
            )

            total_uncommitted += uncommitted
            continue

        # ---------------------------------------------------------
        # SUCCESSFUL CANDIDATE
        # ---------------------------------------------------------
        if item.get("Status") != "RECONCILIATION_COMPLETE":
            return _blocked(
                f"Unknown reconciliation status for {candidate}"
            )

        required_fields = [
            "Priority",
            "Allocated Capital",
            "Entry Price",
            "Lot Size",
            "Reconciled Lots",
            "Reconciled Quantity",
            "Estimated Capital Required",
            "Trading Symbol",
            "Instrument Token",
            "Contract Identity Valid",
        ]

        for field in required_fields:
            if field not in item:
                return _blocked(
                    f"Missing {field} for candidate {candidate}"
                )

        priority = item["Priority"]
        allocated_capital = item["Allocated Capital"]
        entry_price = item["Entry Price"]
        lot_size = item["Lot Size"]
        lots = item["Reconciled Lots"]
        quantity = item["Reconciled Quantity"]
        required_capital = item["Estimated Capital Required"]

        if not isinstance(priority, int) or priority <= 0:
            return _blocked(
                f"Invalid priority for candidate {candidate}"
            )

        if priority in {
            result.get("Priority")
            for result in validation_results
            if result.get("Priority") is not None
        }:
            return _blocked(
                f"Duplicate priority in final quantity plan: {candidate}"
            )

        if not isinstance(allocated_capital, (int, float)):
            return _blocked(
                f"Invalid allocated capital for {candidate}"
            )

        if allocated_capital <= 0:
            return _blocked(
                f"Allocated capital must be positive for {candidate}"
            )

        if not isinstance(entry_price, (int, float)) or entry_price <= 0:
            return _blocked(
                f"Invalid entry price for {candidate}"
            )

        if not isinstance(lot_size, int) or lot_size <= 0:
            return _blocked(
                f"Invalid contract lot size for {candidate}"
            )

        if not isinstance(lots, int) or lots <= 0:
            return _blocked(
                f"Invalid reconciled lots for {candidate}"
            )

        if not isinstance(quantity, int) or quantity <= 0:
            return _blocked(
                f"Invalid reconciled quantity for {candidate}"
            )

        if quantity != lots * lot_size:
            return _blocked(
                f"Quantity does not match lot size for {candidate}"
            )

        calculated_required_capital = (
            entry_price * quantity
        )

        if abs(
            calculated_required_capital - required_capital
        ) > 0.01:
            return _blocked(
                f"Required capital calculation mismatch for {candidate}"
            )

        if required_capital > allocated_capital + 0.01:
            return _blocked(
                f"Required capital exceeds allocation for {candidate}"
            )

        if item.get("Contract Identity Valid") is not True:
            return _blocked(
                f"Contract identity is not valid for {candidate}"
            )

        if item.get("Order Placement Permitted") is not False:
            return _blocked(
                f"Order placement flag must remain False for {candidate}"
            )

        unused_allocation = float(
            item.get("Unused Allocated Capital", 0.0)
        )

        expected_unused = (
            float(allocated_capital)
            - float(required_capital)
        )

        if abs(unused_allocation - expected_unused) > 0.01:
            return _blocked(
                f"Unused allocation mismatch for {candidate}"
            )

        total_allocated += float(allocated_capital)
        total_required += float(required_capital)

        validated_candidates += 1

        validation_results.append(
            {
                "Candidate": candidate,
                "Priority": priority,
                "Status": "FINAL_QUANTITY_VALIDATED",
                "Validated": True,
                "Execution Eligible": True,
                "Trading Symbol": item["Trading Symbol"],
                "Instrument Token": item["Instrument Token"],
                "Entry Price": entry_price,
                "Lot Size": lot_size,
                "Reconciled Lots": lots,
                "Reconciled Quantity": quantity,
                "Allocated Capital": float(allocated_capital),
                "Required Capital": float(required_capital),
                "Unused Allocated Capital": unused_allocation,
                "Contract Identity Valid": True,
                "Order Placement Permitted": False,
            }
        )

    # -------------------------------------------------------------
    # FINAL CAPITAL RECONCILIATION
    # -------------------------------------------------------------
    source_allocated = float(
        reconciliation_result.get(
            "Total Allocated Capital", 0.0
        )
    )

    source_uncommitted = float(
        reconciliation_result.get(
            "Total Uncommitted Capital", 0.0
        )
    )

    expected_uncommitted = (
        source_allocated - total_required
    )

    # V17.7.3's uncommitted capital includes unused allocation
    # from successful candidates plus blocked candidate allocation.
    if abs(
        expected_uncommitted - source_uncommitted
    ) > 0.01:
        return _blocked(
            "Final capital reconciliation mismatch"
        )

    total_uncommitted = source_uncommitted

    return {
        "Status": "FINAL_QUANTITY_PLAN_VALIDATED",
        "Validated Candidates": validated_candidates,
        "Blocked Candidates": blocked_candidates,
        "Total Allocated Capital": source_allocated,
        "Total Required Capital": total_required,
        "Total Uncommitted Capital": total_uncommitted,
        "Validation Results": validation_results,
        "Capital Reassignment": False,
        "Automatic Ranking": False,
        "Priority Source": "DECISION_RISK_LAYER",
        "Order Placement Permitted": False,
        "Wisdom Before Wealth": True,
    }