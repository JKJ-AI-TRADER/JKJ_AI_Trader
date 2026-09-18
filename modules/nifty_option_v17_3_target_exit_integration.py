"""
JKJ AI Trader
V17.3 Target Progression + Exit Plan Integration

Purpose:
    Connect a V15.5 target progression event to the
    V17.1 target exit plan and V17.2 execution state.

Architecture:
    V15.5 determines WHAT target has been reached.
    V17.1 determines the PLANNED quantity for each target.
    V17.2 records WHAT ACTUALLY happened.

Important:
    This module does NOT:
    - place orders
    - connect to Zerodha
    - assume an exit was filled
    - modify V11
    - modify V14
    - modify V15.5
    - modify V17.1
    - modify V17.2
    - modify main.py

Target condition and target execution remain separate.

Wisdom Before Wealth.
"""

from modules.nifty_option_target_exit_plan import (
    create_target_exit_plan,
)

from modules.nifty_option_target_exit_execution import (
    create_target_exit_execution,
    update_target_exit_execution,
)


VALID_TARGET_STAGES = {
    "TARGET 1",
    "TARGET 2",
    "TARGET 3",
}


def create_target_exit_integration(
    target_progression,
    total_quantity,
):
    """
    Create a target-exit integration state.

    V15.5 supplies the target event.

    V17.1 supplies the planned target allocation.

    V17.2 creates the initial execution state.

    No execution is assumed.
    """

    # ---------------------------------------------------------
    # 1. Validate V15.5 target progression
    # ---------------------------------------------------------

    if not isinstance(target_progression, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Invalid target progression data",
        }

    if target_progression.get("Status") != "TARGET_REACHED":
        return {
            "Status": "REJECTED",
            "Reason": (
                "Target progression must have "
                "Status TARGET_REACHED"
            ),
        }

    target_stage = target_progression.get("Target Event")

    if target_stage not in VALID_TARGET_STAGES:
        return {
            "Status": "REJECTED",
            "Reason": "Invalid target event",
        }

    # ---------------------------------------------------------
    # 2. Create V17.1 target exit plan
    # ---------------------------------------------------------

    exit_plan = create_target_exit_plan(
        total_quantity
    )

    if exit_plan.get("Status") != "VALIDATED":
        return {
            "Status": "REJECTED",
            "Reason": "Target exit plan rejected",
            "Target Stage": target_stage,
            "Target Exit Plan": exit_plan,
        }

    # ---------------------------------------------------------
    # 3. Select planned quantity for reached target
    # ---------------------------------------------------------

    quantity_key = {
        "TARGET 1": "Target 1 Quantity",
        "TARGET 2": "Target 2 Quantity",
        "TARGET 3": "Target 3 Quantity",
    }[target_stage]

    planned_quantity = exit_plan.get(quantity_key)

    if planned_quantity is None:
        return {
            "Status": "REJECTED",
            "Reason": "Planned target quantity unavailable",
            "Target Stage": target_stage,
            "Target Exit Plan": exit_plan,
        }

    # ---------------------------------------------------------
    # 4. Create V17.2 execution state
    # ---------------------------------------------------------

    execution = create_target_exit_execution(
        target_stage=target_stage,
        original_quantity=total_quantity,
        planned_quantity=planned_quantity,
    )

    if execution.get("Status") != "PLANNED":
        return {
            "Status": "REJECTED",
            "Reason": "Target exit execution state rejected",
            "Target Stage": target_stage,
            "Target Exit Plan": exit_plan,
            "Execution": execution,
        }

    # ---------------------------------------------------------
    # 5. Return integrated state
    # ---------------------------------------------------------

    return {
        "Status": "PLANNED",
        "Target Stage": target_stage,

        "Target Price": target_progression.get(
            "Target Price"
        ),

        "Current Price": target_progression.get(
            "Current Price"
        ),

        "Final Target": target_progression.get(
            "Final Target"
        ),

        "Targets Reached": target_progression.get(
            "Targets Reached"
        ),

        "Target Exit Plan": exit_plan,

        "Planned Exit Quantity": planned_quantity,

        "Execution": execution,

        "Execution Confirmed": False,
    }


def record_target_exit_execution(
    integration_state,
    execution_status,
    filled_quantity=0,
    submitted_quantity=None,
):
    """
    Record the actual execution result for the
    integrated target exit.

    This function does not communicate with a broker.

    The supplied filled quantity represents the actual
    execution result.

    Actual remaining quantity is taken from V17.2.
    """

    # ---------------------------------------------------------
    # 1. Validate integration state
    # ---------------------------------------------------------

    if not isinstance(integration_state, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Invalid integration state",
        }

    if integration_state.get("Status") != "PLANNED":
        return {
            "Status": "REJECTED",
            "Reason": (
                "Integration state must have Status PLANNED"
            ),
        }

    execution = integration_state.get("Execution")

    if not isinstance(execution, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Execution state is missing",
        }

    # ---------------------------------------------------------
    # 2. Update V17.2 execution state
    # ---------------------------------------------------------

    updated_execution = update_target_exit_execution(
        execution_record=execution,
        execution_status=execution_status,
        filled_quantity=filled_quantity,
        submitted_quantity=submitted_quantity,
    )

    if updated_execution.get("Status") != "UPDATED":
        return {
            "Status": "REJECTED",
            "Reason": "Execution update rejected",
            "Target Stage": integration_state.get(
                "Target Stage"
            ),
            "Execution": updated_execution,
        }

    # ---------------------------------------------------------
    # 3. Return reconciled integration state
    # ---------------------------------------------------------

    return {
        "Status": "EXECUTION_UPDATED",

        "Target Stage": integration_state.get(
            "Target Stage"
        ),

        "Target Price": integration_state.get(
            "Target Price"
        ),

        "Current Price": integration_state.get(
            "Current Price"
        ),

        "Final Target": integration_state.get(
            "Final Target"
        ),

        "Targets Reached": integration_state.get(
            "Targets Reached"
        ),

        "Target Exit Plan": integration_state.get(
            "Target Exit Plan"
        ),

        "Planned Exit Quantity": integration_state.get(
            "Planned Exit Quantity"
        ),

        "Execution": updated_execution,

        "Execution Confirmed": updated_execution.get(
            "Execution Confirmed"
        ),

        "Actual Remaining Quantity": updated_execution.get(
            "Actual Remaining Quantity"
        ),
    }
