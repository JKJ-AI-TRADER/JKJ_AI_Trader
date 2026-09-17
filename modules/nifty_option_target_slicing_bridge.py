"""
JKJ AI Trader
V15.6 Target-to-Slicing Bridge

Purpose:
    Connect a V15.5 target progression event to the
    existing V11 position slicing engine.

Architecture:
    V15.5 controls WHAT target stage has been reached.
    V11 controls HOW MUCH of the position is exited.

Important:
    This module does NOT:
    - calculate exit quantity
    - modify V11
    - modify V14
    - place real orders
    - connect to Zerodha
    - modify main.py

A target milestone creates an opportunity for V11
to evaluate profit protection. V11 may HOLD or
perform a partial/full exit according to its own rules.

Wisdom Before Wealth.
"""

from modules.intraday_position_slicing import calculate_slice_plan


def evaluate_target_slicing(
    target_progression,
    total_quantity,
    current_quantity,
    entry_price,
    current_price,
    peak_price,
    momentum_status="STRONG",
    volume_status="STRONG",
    underlying_status="SUPPORTIVE",
    structure_status="STRONG",
):
    """
    Evaluate V11 slicing after a V15.5 target milestone.

    V15.5 determines the target event.

    V11 determines the quantity, using its existing
    slicing rules.

    The target event is deliberately NOT passed to V11
    as an exit signal containing the word "TARGET",
    because V11 treats that signal as an immediate
    full exit.
    """

    # ---------------------------------------------------------
    # 1. Validate target progression
    # ---------------------------------------------------------

    if not isinstance(target_progression, dict):
        return {
            "Status": "REJECTED",
            "Reason": "Invalid target progression data",
        }

    if target_progression.get("Status") != "TARGET_REACHED":
        return {
            "Status": "REJECTED",
            "Reason": "Target progression must have Status TARGET_REACHED",
        }

    target_event = target_progression.get("Target Event")

    if target_event not in {
        "TARGET 1",
        "TARGET 2",
        "TARGET 3",
    }:
        return {
            "Status": "REJECTED",
            "Reason": "Invalid target event",
        }

    # ---------------------------------------------------------
    # 2. Preserve target-stage information
    # ---------------------------------------------------------

    target_stage = target_event

    # ---------------------------------------------------------
    # 3. Send a neutral profit-protection signal to V11
    # ---------------------------------------------------------
    #
    # IMPORTANT:
    # Do not include the word "TARGET" in this signal.
    #
    # V11 interprets "TARGET" as FULL EXIT.
    #
    # V15 therefore records the target separately while
    # V11 receives a neutral profit-protection signal.
    # ---------------------------------------------------------

    exit_signal = "PROFIT MILESTONE"

    # ---------------------------------------------------------
    # 4. Let V11 decide the quantity
    # ---------------------------------------------------------

    slice_plan = calculate_slice_plan(
        total_quantity=total_quantity,
        current_quantity=current_quantity,
        entry_price=entry_price,
        current_price=current_price,
        peak_price=peak_price,
        exit_signal=exit_signal,
        momentum_status=momentum_status,
        volume_status=volume_status,
        underlying_status=underlying_status,
        structure_status=structure_status,
    )

    # ---------------------------------------------------------
    # 5. Return combined interpretation
    # ---------------------------------------------------------

    return {
        "Status": "EVALUATED",
        "Target Stage": target_stage,
        "Target Price": target_progression.get("Target Price"),
        "Current Price": target_progression.get("Current Price"),
        "Final Target": target_progression.get("Final Target"),
        "Targets Reached": target_progression.get("Targets Reached"),
        "V11 Slice Plan": slice_plan,
    }
