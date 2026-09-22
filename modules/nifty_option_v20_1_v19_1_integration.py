"""
JKJ AI Trader
V20.1 -> V19.1 Paper Trade Closure Validation Integration

Purpose:
    Connect the completed V20.1 paper-trade lifecycle to the
    existing V19.1 read-only closure validation layer.

Authority:
    V11   = authoritative paper trade record
    V18.1 = authoritative target-exit synchronization
    V19.1 = final read-only closure validation

This module does NOT:
    - calculate P&L
    - calculate exit quantities
    - modify V11
    - modify V17.2
    - modify V18.1
    - close trades
    - place real orders
    - communicate with Zerodha
    - modify main.py

Wisdom Before Wealth.
"""

try:
    from nifty_option_v19_1_paper_trade_closure_validation import (
        validate_paper_trade_closure,
    )
except ModuleNotFoundError:
    from modules.nifty_option_v19_1_paper_trade_closure_validation import (
        validate_paper_trade_closure,
    )


def _blocked(reason):
    return {
        "Status": "V20_1_V19_1_INTEGRATION_BLOCKED",
        "Reason": reason,
        "Final Audit": False,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Automatic Ranking": False,
        "Capital Reassignment": False,
        "Wisdom Before Wealth": True,
    }


def integrate_v20_1_to_v19_1(
    v20_1_v18_1_result,
    trade,
):
    """
    Integrate a V20.1 lifecycle result with the existing
    V19.1 final closure validation.

    V19.1 remains read-only.

    The supplied trade must already be CLOSED.
    The supplied V18.1 result must already represent the
    final synchronized lifecycle state.
    """

    # ---------------------------------------------------------
    # 1. Validate V20.1 -> V18.1 integration
    # ---------------------------------------------------------

    if not isinstance(v20_1_v18_1_result, dict):
        return _blocked(
            "V20.1 -> V18.1 result must be a dictionary"
        )

    if (
        v20_1_v18_1_result.get("Status")
        != "V20_1_V18_1_INTEGRATION_COMPLETE"
    ):
        return _blocked(
            "V20.1 -> V18.1 integration is not complete"
        )

    if (
        v20_1_v18_1_result.get("Synchronization Confirmed")
        is not True
    ):
        return _blocked(
            "V18.1 synchronization must be confirmed"
        )

    # ---------------------------------------------------------
    # 2. Preserve paper-only safeguards
    # ---------------------------------------------------------

    if v20_1_v18_1_result.get("Paper Execution") is not True:
        return _blocked(
            "Paper execution flag must remain True"
        )

    if (
        v20_1_v18_1_result.get("Broker Communication")
        is not False
    ):
        return _blocked(
            "Broker communication must remain False"
        )

    if (
        v20_1_v18_1_result.get("Order Placement Permitted")
        is not False
    ):
        return _blocked(
            "Order placement must remain False"
        )

    if (
        v20_1_v18_1_result.get("Capital Reassignment")
        is not False
    ):
        return _blocked(
            "Capital reassignment must remain False"
        )

    if (
        v20_1_v18_1_result.get("Automatic Ranking")
        is not False
    ):
        return _blocked(
            "Automatic ranking must remain False"
        )

    # ---------------------------------------------------------
    # 3. Validate final V18.1 synchronization result
    # ---------------------------------------------------------

    v18_1_result = v20_1_v18_1_result.get(
        "V18.1 Result"
    )

    if not isinstance(v18_1_result, dict):
        return _blocked(
            "V18.1 synchronization result is missing"
        )

    if v18_1_result.get("Status") != "SYNCHRONIZED":
        return _blocked(
            "V18.1 result must have Status SYNCHRONIZED"
        )

    if (
        v18_1_result.get("Synchronization Confirmed")
        is not True
    ):
        return _blocked(
            "V18.1 synchronization must be confirmed"
        )

    # ---------------------------------------------------------
    # 4. Validate V11 trade input
    # ---------------------------------------------------------

    if not isinstance(trade, dict):
        return _blocked(
            "V11 trade must be a dictionary"
        )

    if trade.get("Status") != "CLOSED":
        return _blocked(
            "V11 trade must already be CLOSED"
        )

    # ---------------------------------------------------------
    # 5. Verify V11/V18.1 final identity and quantity
    # ---------------------------------------------------------

    if (
        trade.get("Trade ID")
        != v20_1_v18_1_result.get("Trade ID")
    ):
        return _blocked(
            "V11 Trade ID does not match V20.1 lifecycle"
        )

    if (
        trade.get("Symbol")
        != v20_1_v18_1_result.get("Symbol")
    ):
        return _blocked(
            "V11 Symbol does not match V20.1 lifecycle"
        )

    if (
        v20_1_v18_1_result.get(
            "V11 Remaining Quantity"
        )
        != 0
    ):
        return _blocked(
            "Final V11 remaining quantity must be zero"
        )

    if (
        v20_1_v18_1_result.get(
            "Expected Remaining Quantity"
        )
        != 0
    ):
        return _blocked(
            "Final expected remaining quantity must be zero"
        )

    if (
        v20_1_v18_1_result.get(
            "Cumulative Filled Quantity"
        )
        != trade.get("Original Quantity")
    ):
        return _blocked(
            "V18.1 cumulative filled quantity must match "
            "V11 original quantity"
        )

    closure_result = validate_paper_trade_closure(
        trade=trade,
        v18_1_final_sync=v18_1_result,
    )

    if (
        closure_result.get("Status")
        != "PAPER_TRADE_CLOSURE_VALIDATED"
    ):
        return {
            "Status": "V20_1_V19_1_INTEGRATION_BLOCKED",
            "Reason": closure_result.get(
                "Reason",
                "V19.1 closure validation failed",
            ),
            "V19.1 Result": closure_result,
            "Final Audit": False,
            "Paper Execution": True,
            "Broker Communication": False,
            "Order Placement Permitted": False,
            "Automatic Ranking": False,
            "Capital Reassignment": False,
            "Wisdom Before Wealth": True,
        }

    # ---------------------------------------------------------
    # 7. Successful final audit
    # ---------------------------------------------------------

    return {
        "Status": "V20_1_V19_1_INTEGRATION_COMPLETE",
        "V20.1 -> V18.1 Result": v20_1_v18_1_result,
        "V18.1 Result": v18_1_result,
        "V11 Trade": trade,
        "V19.1 Result": closure_result,
        "Closure Record": closure_result[
            "Closure Record"
        ],
        "Final Audit": True,
        "Read Only": True,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Automatic Ranking": False,
        "Capital Reassignment": False,
        "Wisdom Before Wealth": True,
    }