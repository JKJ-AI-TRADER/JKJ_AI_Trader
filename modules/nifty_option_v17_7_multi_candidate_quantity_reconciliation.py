"""
JKJ AI Trader
V17.7.3 — Multi-Candidate Quantity Reconciliation

Purpose:
    Reconcile multiple V17.6.5 capital allocations against
    their actual entry prices, contract lot sizes, and validated
    contract identities.

Important:
    This module does NOT:
    - rank candidates
    - change Decision/Risk priority
    - change capital allocations
    - change entry/stop/target decisions
    - place orders
    - connect to Zerodha
    - modify V17.5
    - modify V17.6
    - modify main.py

Capital that cannot support a valid quantity remains
uncommitted. It is NOT automatically reassigned.

Wisdom Before Wealth.
"""

from nifty_option_v17_7_capital_quantity_reconciliation import (
    reconcile_capital_to_quantity
)

from nifty_option_v17_7_quantity_contract_validation import (
    validate_quantity_against_contract
)


def reconcile_multi_candidate_quantities(
    allocation_result,
    candidate_market_data,
):
    """
    Reconcile all allocated candidates.

    Parameters
    ----------
    allocation_result : dict
        Output from V17.6.5 policy allocation.

    candidate_market_data : list
        Candidate-specific market/contract information.

        Each item must contain:
            Candidate
            Entry Price
            Contract Validation

    Returns
    -------
    dict
        MULTI_CANDIDATE_RECONCILIATION_COMPLETE
        or
        MULTI_CANDIDATE_RECONCILIATION_BLOCKED
    """

    # ---------------------------------------------------------
    # 1. Validate allocation result
    # ---------------------------------------------------------

    if not isinstance(allocation_result, dict):
        return _blocked(
            "Invalid allocation result"
        )

    if (
        allocation_result.get("Status")
        != "POLICY_ALLOCATION_COMPLETE"
    ):
        return _blocked(
            "Policy allocation is not complete"
        )

    allocations = allocation_result.get(
        "Allocations"
    )

    if not isinstance(allocations, list):
        return _blocked(
            "Allocation result does not contain a valid allocation list"
        )

    # ---------------------------------------------------------
    # 2. Validate candidate market data
    # ---------------------------------------------------------

    if not isinstance(candidate_market_data, list):
        return _blocked(
            "Candidate market data must be a list"
        )

    market_data_map = {}

    for candidate in candidate_market_data:

        if not isinstance(candidate, dict):
            return _blocked(
                "Each candidate market-data item must be a dictionary"
            )

        required_fields = {
            "Candidate",
            "Entry Price",
            "Contract Validation",
        }

        if not required_fields.issubset(
            candidate.keys()
        ):
            return _blocked(
                "Candidate market data is missing required fields"
            )

        name = candidate["Candidate"]

        if name in market_data_map:
            return _blocked(
                f"Duplicate candidate market data: {name}"
            )

        market_data_map[name] = candidate

    # ---------------------------------------------------------
    # 3. Process each V17.6.5 allocation
    # ---------------------------------------------------------

    reconciliations = []

    total_allocated_capital = 0.0
    total_reconciled_capital = 0.0
    total_uncommitted_capital = 0.0

    successful_candidates = 0
    blocked_candidates = 0

    for allocation in allocations:

        if not isinstance(allocation, dict):
            return _blocked(
                "Invalid allocation entry"
            )

        candidate_name = allocation.get(
            "Candidate"
        )

        allocated_capital = allocation.get(
            "Allocated Capital"
        )

        allocation_status = allocation.get(
            "Allocation Status"
        )

        if not isinstance(
            allocated_capital,
            (int, float)
        ):
            return _blocked(
                f"Invalid allocated capital for {candidate_name}"
            )

        # -----------------------------------------------------
        # Candidates not allocated by V17.6.5
        # -----------------------------------------------------

        if allocated_capital <= 0:

            reconciliations.append({
                "Candidate": candidate_name,
                "Priority": allocation.get(
                    "Priority"
                ),
                "Allocated Capital": 0.0,
                "Status": "NOT_ALLOCATED",
                "Reconciled Quantity": 0,
                "Reconciled Lots": 0,
                "Estimated Capital Required": 0.0,
                "Uncommitted Capital": 0.0,
                "Allocation Status": allocation_status,
                "Order Placement Permitted": False,
            })

            continue

        total_allocated_capital += (
            float(allocated_capital)
        )

        # -----------------------------------------------------
        # Market/contract information required
        # -----------------------------------------------------

        if candidate_name not in market_data_map:

            reconciliations.append({
                "Candidate": candidate_name,
                "Priority": allocation.get(
                    "Priority"
                ),
                "Allocated Capital":
                    float(allocated_capital),
                "Status":
                    "RECONCILIATION_BLOCKED",
                "Reconciled Quantity": 0,
                "Reconciled Lots": 0,
                "Estimated Capital Required": 0.0,
                "Uncommitted Capital":
                    float(allocated_capital),
                "Reason":
                    "Candidate market data not provided",
                "Allocation Status":
                    allocation_status,
                "Order Placement Permitted": False,
            })

            blocked_candidates += 1
            total_uncommitted_capital += (
                float(allocated_capital)
            )

            continue

        market_data = market_data_map[
            candidate_name
        ]

        entry_price = market_data[
            "Entry Price"
        ]

        contract_validation = market_data[
            "Contract Validation"
        ]

        # -----------------------------------------------------
        # V17.7.1 — Capital to quantity
        # -----------------------------------------------------

        quantity_result = (
            reconcile_capital_to_quantity(
                allocated_capital=
                    allocated_capital,
                entry_price=
                    entry_price,
                lot_size=
                    contract_validation.get(
                        "Lot Size",
                        0
                    )
            )
        )

        if (
            quantity_result.get("Status")
            != "RECONCILIATION_COMPLETE"
        ):

            reconciliations.append({
                "Candidate": candidate_name,
                "Priority": allocation.get(
                    "Priority"
                ),
                "Allocated Capital":
                    float(allocated_capital),
                "Status":
                    "RECONCILIATION_BLOCKED",
                "Reconciled Quantity": 0,
                "Reconciled Lots": 0,
                "Estimated Capital Required": 0.0,
                "Uncommitted Capital":
                    float(allocated_capital),
                "Reason":
                    quantity_result.get(
                        "Reason",
                        "Capital-to-quantity reconciliation failed"
                    ),
                "Allocation Status":
                    allocation_status,
                "Order Placement Permitted": False,
            })

            blocked_candidates += 1
            total_uncommitted_capital += (
                float(allocated_capital)
            )

            continue

        # -----------------------------------------------------
        # V17.7.2 — Quantity to contract
        # -----------------------------------------------------

        contract_result = (
            validate_quantity_against_contract(
                quantity_result,
                contract_validation
            )
        )

        if (
            contract_result.get("Status")
            != "QUANTITY_CONTRACT_VALIDATED"
        ):

            reconciliations.append({
                "Candidate": candidate_name,
                "Priority": allocation.get(
                    "Priority"
                ),
                "Allocated Capital":
                    float(allocated_capital),
                "Status":
                    "RECONCILIATION_BLOCKED",
                "Reconciled Quantity":
                    quantity_result.get(
                        "Reconciled Quantity",
                        0
                    ),
                "Reconciled Lots":
                    quantity_result.get(
                        "Reconciled Lots",
                        0
                    ),
                "Estimated Capital Required":
                    quantity_result.get(
                        "Estimated Capital Required",
                        0.0
                    ),
                "Uncommitted Capital":
                    float(allocated_capital),
                "Reason":
                    contract_result.get(
                        "Reason",
                        "Quantity-contract validation failed"
                    ),
                "Allocation Status":
                    allocation_status,
                "Order Placement Permitted": False,
            })

            blocked_candidates += 1
            total_uncommitted_capital += (
                float(allocated_capital)
            )

            continue

        # -----------------------------------------------------
        # Successful candidate
        # -----------------------------------------------------

        estimated_capital = quantity_result[
            "Estimated Capital Required"
        ]

        unused_capital = quantity_result[
            "Unused Allocated Capital"
        ]

        total_reconciled_capital += (
            float(estimated_capital)
        )

        total_uncommitted_capital += (
            float(unused_capital)
        )

        successful_candidates += 1

        reconciliations.append({
            "Candidate": candidate_name,
            "Priority": allocation.get(
                "Priority"
            ),
            "Allocated Capital":
                float(allocated_capital),
            "Entry Price":
                quantity_result.get(
                    "Entry Price"
                ),
            "Lot Size":
                quantity_result.get(
                    "Lot Size"
                ),
            "Reconciled Lots":
                contract_result.get(
                    "Validated Lots"
                ),
            "Reconciled Quantity":
                contract_result.get(
                    "Validated Quantity"
                ),
            "Estimated Capital Required":
                float(estimated_capital),
            "Unused Allocated Capital":
                float(unused_capital),
            "Status":
                "RECONCILIATION_COMPLETE",
            "Trading Symbol":
                contract_result.get(
                    "Trading Symbol"
                ),
            "Instrument Token":
                contract_result.get(
                    "Instrument Token"
                ),
            "Contract Identity Valid":
                contract_result.get(
                    "Contract Identity Valid"
                ),
            "Order Placement Permitted":
                False,
        })

    # ---------------------------------------------------------
    # 4. Final result
    # ---------------------------------------------------------

    return {
        "Status":
            "MULTI_CANDIDATE_RECONCILIATION_COMPLETE",

        "Total Allocated Capital":
            total_allocated_capital,

        "Total Reconciled Capital":
            total_reconciled_capital,

        "Total Uncommitted Capital":
            total_uncommitted_capital,

        "Successful Candidates":
            successful_candidates,

        "Blocked Candidates":
            blocked_candidates,

        "Reconciliations":
            reconciliations,

        "Capital Reassignment":
            False,

        "Priority Source":
            "DECISION_RISK_LAYER",

        "Automatic Ranking":
            False,

        "Order Placement Permitted":
            False,

        "Wisdom Before Wealth":
            True,
    }


def _blocked(reason):
    """
    Safe multi-candidate reconciliation blocked result.
    """

    return {
        "Status":
            "MULTI_CANDIDATE_RECONCILIATION_BLOCKED",

        "Reason":
            reason,

        "Total Allocated Capital":
            0.0,

        "Total Reconciled Capital":
            0.0,

        "Total Uncommitted Capital":
            0.0,

        "Successful Candidates":
            0,

        "Blocked Candidates":
            0,

        "Reconciliations":
            [],

        "Capital Reassignment":
            False,

        "Priority Source":
            "DECISION_RISK_LAYER",

        "Automatic Ranking":
            False,

        "Order Placement Permitted":
            False,

        "Wisdom Before Wealth":
            True,
    }