"""
JKJ AI Trader
V17.1 Target Exit Plan Test

Purpose:
    Validate deterministic three-stage target allocation.

Tests:
    - 60 quantity
    - 61 quantity
    - 62 quantity
    - 65 quantity
    - invalid quantity
    - zero quantity
    - quantity conservation
    - no zero-sized slices

Wisdom Before Wealth.
"""

from modules.nifty_option_target_exit_plan import (
    create_target_exit_plan,
)


def run_valid_case(quantity, expected):
    result = create_target_exit_plan(quantity)

    assert result["Status"] == "VALIDATED"
    assert result["Allocation Valid"] is True

    assert result["Target 1 Quantity"] == expected[0]
    assert result["Target 2 Quantity"] == expected[1]
    assert result["Target 3 Quantity"] == expected[2]

    total = (
        result["Target 1 Quantity"]
        + result["Target 2 Quantity"]
        + result["Target 3 Quantity"]
    )

    assert total == quantity
    assert result["Planned Exit Quantity"] == quantity

    assert result["Target 1 Quantity"] > 0
    assert result["Target 2 Quantity"] > 0
    assert result["Target 3 Quantity"] > 0

    print(
        f"PASS | {quantity} -> "
        f"{result['Target 1 Quantity']} / "
        f"{result['Target 2 Quantity']} / "
        f"{result['Target 3 Quantity']}"
    )


def run_invalid_case(quantity, description):
    result = create_target_exit_plan(quantity)

    assert result["Status"] == "REJECTED"
    assert result["Allocation Valid"] is False

    print(f"PASS | {description}")


def main():

    print("\nJKJ AI Trader")
    print("V17.1 Target Exit Plan Test")
    print("=" * 50)

    # ---------------------------------------------------------
    # 1. Standard allocation tests
    # ---------------------------------------------------------

    run_valid_case(60, (20, 20, 20))
    run_valid_case(61, (21, 20, 20))
    run_valid_case(62, (21, 21, 20))
    run_valid_case(65, (22, 22, 21))

    # ---------------------------------------------------------
    # 2. Invalid quantity tests
    # ---------------------------------------------------------

    run_invalid_case(0, "Zero quantity rejected")
    run_invalid_case(-10, "Negative quantity rejected")
    run_invalid_case(None, "Missing quantity rejected")
    run_invalid_case("ABC", "Non-numeric quantity rejected")

    # ---------------------------------------------------------
    # 3. Final validation
    # ---------------------------------------------------------

    print("=" * 50)
    print("V17.1 TARGET EXIT PLAN TEST: PASS")
    print("Three-stage allocation validated.")
    print("No live orders.")
    print("No Zerodha connection.")
    print("No V11 modification.")
    print("Wisdom Before Wealth.")
    print("=" * 50)


if __name__ == "__main__":
    main()