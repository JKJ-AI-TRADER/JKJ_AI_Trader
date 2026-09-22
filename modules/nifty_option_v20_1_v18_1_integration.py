"""
JKJ AI Trader
V20.1 -> V18.1 Paper Target Exit Synchronization Integration

Purpose:
    Connect a successfully lifecycle-ready V20.1/V17.8 paper
    trade to the existing V18.1 target-exit synchronization
    layer when an actual V11 exit event and V17.2 target-stage
    execution record are available.

Authority:
    V11    = actual position quantity
    V17.2  = target-stage execution state
    V18.1  = reconciliation between the two

This module does NOT:
    - generate exit quantities
    - generate target stages
    - modify V11
    - modify V17.2
    - modify V15.4
    - place real orders
    - communicate with Zerodha
    - modify main.py

Wisdom Before Wealth.
"""

try:
    from nifty_option_v18_1_paper_target_exit_synchronization import (
        synchronize_target_exit,
    )
except ModuleNotFoundError:
    from modules.nifty_option_v18_1_paper_target_exit_synchronization import (
        synchronize_target_exit,
    )


def _blocked(reason):
    return {
        "Status": "V20_1_V18_1_INTEGRATION_BLOCKED",
        "Reason": reason,
        "Synchronization Confirmed": False,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Automatic Ranking": False,
        "Capital Reassignment": False,
        "Wisdom Before Wealth": True,
    }


def integrate_v20_1_to_v18_1(
    v20_1_v17_8_8_result,
    v11_exit_result,
    execution_record,
    global_original_quantity,
    previous_cumulative_filled=0,
):
    """
    Integrate a lifecycle-ready V20.1 paper trade with V18.1.

    V18.1 receives actual V11 exit information and an existing
    V17.2 target-stage execution record.

    No exit quantity or target stage is generated here.
    """

    # ---------------------------------------------------------
    # 1. Validate V20.1 -> V17.8.8 integration
    # ---------------------------------------------------------

    if not isinstance(v20_1_v17_8_8_result, dict):
        return _blocked(
            "V20.1 -> V17.8.8 result must be a dictionary"
        )

    if (
        v20_1_v17_8_8_result.get("Status")
        != "V20_1_V17_8_8_INTEGRATION_COMPLETE"
    ):
        return _blocked(
            "V20.1 -> V17.8.8 integration is not complete"
        )

    if v20_1_v17_8_8_result.get("Lifecycle Ready") is not True:
        return _blocked(
            "Lifecycle is not ready"
        )

    if (
        v20_1_v17_8_8_result.get("Lifecycle Owner")
        != "V15.4 / V11"
    ):
        return _blocked(
            "Lifecycle owner must remain V15.4 / V11"
        )

    # ---------------------------------------------------------
    # 2. Preserve upstream safeguards
    # ---------------------------------------------------------

    if v20_1_v17_8_8_result.get("Paper Execution") is not True:
        return _blocked(
            "Paper execution flag must remain True"
        )

    if (
        v20_1_v17_8_8_result.get("Broker Communication")
        is not False
    ):
        return _blocked(
            "Broker communication must remain False"
        )

    if (
        v20_1_v17_8_8_result.get("Order Placement Permitted")
        is not False
    ):
        return _blocked(
            "Order placement must remain False"
        )

    if (
        v20_1_v17_8_8_result.get("Capital Reassignment")
        is not False
    ):
        return _blocked(
            "Capital reassignment must remain False"
        )

    if (
        v20_1_v17_8_8_result.get("Automatic Ranking")
        is not False
    ):
        return _blocked(
            "Automatic ranking must remain False"
        )

    if (
        v20_1_v17_8_8_result.get("Priority Source")
        != "DECISION_RISK_LAYER"
    ):
        return _blocked(
            "Priority source must remain DECISION_RISK_LAYER"
        )

    # ---------------------------------------------------------
    # 3. Validate actual V11 exit event
    # ---------------------------------------------------------

    if not isinstance(v11_exit_result, dict):
        return _blocked(
            "V11 exit result must be a dictionary"
        )

    if "Exit Quantity" not in v11_exit_result:
        return _blocked(
            "V11 exit result must contain actual Exit Quantity"
        )

    if "Remaining Quantity" not in v11_exit_result:
        return _blocked(
            "V11 exit result must contain Remaining Quantity"
        )

    # ---------------------------------------------------------
    # 4. Validate V17.2 execution record
    # ---------------------------------------------------------

    if not isinstance(execution_record, dict):
        return _blocked(
            "V17.2 execution record must be a dictionary"
        )

    if execution_record.get("Status") != "PLANNED":
        return _blocked(
            "V17.2 execution record must have Status PLANNED"
        )

    if "Target Stage" not in execution_record:
        return _blocked(
            "V17.2 target stage is missing"
        )

    if "Planned Quantity" not in execution_record:
        return _blocked(
            "V17.2 planned quantity is missing"
        )

    # ---------------------------------------------------------
    # 5. V18.1 performs the actual reconciliation
    # ---------------------------------------------------------

    synchronization_result = synchronize_target_exit(
        v11_exit_result=v11_exit_result,
        execution_record=execution_record,
        global_original_quantity=global_original_quantity,
        previous_cumulative_filled=previous_cumulative_filled,
    )

    if (
        synchronization_result.get("Status")
        != "SYNCHRONIZED"
    ):
        return {
            "Status": "V20_1_V18_1_INTEGRATION_BLOCKED",
            "Reason": synchronization_result.get(
                "Reason",
                "V18.1 synchronization failed",
            ),
            "V18.1 Result": synchronization_result,
            "Synchronization Confirmed": False,
            "Paper Execution": True,
            "Broker Communication": False,
            "Order Placement Permitted": False,
            "Automatic Ranking": False,
            "Capital Reassignment": False,
            "Wisdom Before Wealth": True,
        }

    # ---------------------------------------------------------
    # 6. Successful synchronization
    # ---------------------------------------------------------

    return {
        "Status": "V20_1_V18_1_INTEGRATION_COMPLETE",
        "V20.1 -> V17.8.8 Result": v20_1_v17_8_8_result,
        "V11 Exit Result": v11_exit_result,
        "V17.2 Execution Record": execution_record,
        "V18.1 Result": synchronization_result,
        "Target Stage": synchronization_result["Target Stage"],
        "Original Quantity": synchronization_result[
            "Original Quantity"
        ],
        "Planned Quantity": synchronization_result[
            "Planned Quantity"
        ],
        "V11 Event Exit Quantity": synchronization_result[
            "V11 Event Exit Quantity"
        ],
        "Previous Cumulative Filled": synchronization_result[
            "Previous Cumulative Filled"
        ],
        "Cumulative Filled Quantity": synchronization_result[
            "Cumulative Filled Quantity"
        ],
        "V11 Remaining Quantity": synchronization_result[
            "V11 Remaining Quantity"
        ],
        "Expected Remaining Quantity": synchronization_result[
            "Expected Remaining Quantity"
        ],
        "V17.2 Execution Status": synchronization_result[
            "V17.2 Execution Status"
        ],
        "Synchronization Confirmed": True,
        "Lifecycle Owner": "V15.4 / V11",
        "V11 Quantity Authority": True,
        "V17.2 Target Stage Authority": True,
        "Paper Execution": True,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Automatic Ranking": False,
        "Capital Reassignment": False,
        "Wisdom Before Wealth": True,
    }