"""
JKJ AI Trader
V17.7.2 — Quantity-to-Contract Validation

Purpose:
    Validate the quantity produced by V17.7.1 against the
    exact contract validated by V17.5 Stage 2.

Important:
    This module does NOT:
    - change the reconciled quantity
    - change capital allocation
    - rank candidates
    - qualify trades
    - place orders
    - connect to Zerodha
    - modify V17.5
    - modify main.py

Wisdom Before Wealth.
"""


def validate_quantity_against_contract(
    reconciliation_result,
    contract_validation,
):
    """
    Validate reconciled quantity against a validated contract.

    Returns:
        QUANTITY_CONTRACT_VALIDATED
        or
        QUANTITY_CONTRACT_BLOCKED
    """

    # ---------------------------------------------------------
    # 1. Validate reconciliation input
    # ---------------------------------------------------------

    if not isinstance(
        reconciliation_result,
        dict
    ):
        return _blocked(
            "Invalid reconciliation result"
        )

    if (
        reconciliation_result.get("Status")
        != "RECONCILIATION_COMPLETE"
    ):
        return _blocked(
            "Capital-to-quantity reconciliation is not complete"
        )

    quantity = reconciliation_result.get(
        "Reconciled Quantity"
    )

    if not isinstance(quantity, int):
        return _blocked(
            "Reconciled quantity must be an integer"
        )

    if quantity <= 0:
        return _blocked(
            "Reconciled quantity must be greater than zero"
        )

    # ---------------------------------------------------------
    # 2. Validate contract input
    # ---------------------------------------------------------

    if not isinstance(
        contract_validation,
        dict
    ):
        return _blocked(
            "Invalid contract validation result"
        )

    if (
        contract_validation.get("Status")
        != "CONTRACT_VALIDATED"
    ):
        return _blocked(
            "Zerodha contract is not validated"
        )

    lot_size = contract_validation.get(
        "Lot Size"
    )

    if not isinstance(lot_size, int):
        return _blocked(
            "Validated contract lot size must be an integer"
        )

    if lot_size <= 0:
        return _blocked(
            "Validated contract lot size must be greater than zero"
        )

    # ---------------------------------------------------------
    # 3. Validate quantity against contract lot size
    # ---------------------------------------------------------

    if quantity % lot_size != 0:
        return _blocked(
            "Reconciled quantity is not a valid multiple "
            "of the validated contract lot size"
        )

    validated_lots = quantity // lot_size

    # ---------------------------------------------------------
    # 4. Return successful validation
    # ---------------------------------------------------------

    return {
        "Status":
            "QUANTITY_CONTRACT_VALIDATED",

        "Trading Symbol":
            contract_validation.get(
                "Trading Symbol"
            ),

        "Instrument Token":
            contract_validation.get(
                "Instrument Token"
            ),

        "Expiry":
            contract_validation.get(
                "Expiry"
            ),

        "Strike":
            contract_validation.get(
                "Strike"
            ),

        "Option Type":
            contract_validation.get(
                "Option Type"
            ),

        "Lot Size":
            lot_size,

        "Validated Quantity":
            quantity,

        "Validated Lots":
            validated_lots,

        "Quantity Matches Contract":
            True,

        "Contract Identity Valid":
            True,

        "Order Placement Permitted":
            False,

        "Wisdom Before Wealth":
            True,
    }


def _blocked(reason):
    """
    Safe quantity-contract blocked result.
    """

    return {
        "Status":
            "QUANTITY_CONTRACT_BLOCKED",

        "Validated Quantity":
            0,

        "Validated Lots":
            0,

        "Quantity Matches Contract":
            False,

        "Contract Identity Valid":
            False,

        "Order Placement Permitted":
            False,

        "Reason":
            reason,

        "Wisdom Before Wealth":
            True,
    }