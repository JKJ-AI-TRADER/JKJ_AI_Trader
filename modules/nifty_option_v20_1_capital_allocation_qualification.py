"""
JKJ AI Trader V20.1
Decision/Risk Capital Allocation Qualification

Purpose:
    Validate an already-qualified opportunity before it enters
    the V17.6 capital allocation layer.

V20.1 does not:
    - create trading decisions
    - calculate option quantity
    - allocate capital
    - rank candidates
    - place orders
    - communicate with Zerodha
    - modify V16.1/V17.6/V17.7/V17.8/V18.1/V19.1
    - modify main.py

Wisdom Before Wealth.
"""


def qualify_capital_allocation(
    opportunity,
    priority,
    requested_allocation,
):
    """
    Validate Decision/Risk qualification for V17.6 capital allocation.

    Priority and Requested Allocation must be explicitly supplied.
    V20.1 does not invent either value.
    """

    if not isinstance(opportunity, dict):
        return {
            "Status": "CAPITAL_ALLOCATION_BLOCKED",
            "Capital Allocation Eligible": False,
            "Reason": "Invalid opportunity input.",
            "Wisdom Before Wealth": True,
        }

    required_fields = [
        "Trading Symbol",
        "Paper Trade Permission",
    ]

    for field in required_fields:
        if field not in opportunity:
            return {
                "Status": "CAPITAL_ALLOCATION_BLOCKED",
                "Capital Allocation Eligible": False,
                "Reason": f"Missing required field: {field}.",
                "Wisdom Before Wealth": True,
            }

    if opportunity["Paper Trade Permission"] != "PERMITTED":
        return {
            "Status": "CAPITAL_ALLOCATION_BLOCKED",
            "Capital Allocation Eligible": False,
            "Reason": "Paper Trade Permission is not PERMITTED.",
            "Wisdom Before Wealth": True,
        }

    if not isinstance(priority, int) or isinstance(priority, bool) or priority <= 0:
        return {
            "Status": "CAPITAL_ALLOCATION_BLOCKED",
            "Capital Allocation Eligible": False,
            "Reason": "Priority must be a positive integer.",
            "Wisdom Before Wealth": True,
        }

    if (
        not isinstance(requested_allocation, (int, float))
        or isinstance(requested_allocation, bool)
        or requested_allocation <= 0
    ):
        return {
            "Status": "CAPITAL_ALLOCATION_BLOCKED",
            "Capital Allocation Eligible": False,
            "Reason": "Requested Allocation must be a positive number.",
            "Wisdom Before Wealth": True,
        }

    risk_context = opportunity.get(
        "Entry Risk Context",
        opportunity.get("Risk Context", "NOT PROVIDED"),
    )

    reasons = [
        "Decision/Risk opportunity supplied.",
        "Paper Trade Permission is PERMITTED.",
        "Priority explicitly supplied and validated.",
        "Requested Allocation explicitly supplied and validated.",
    ]

    return {
        "Status": "CAPITAL_ALLOCATION_QUALIFIED",
        "Trading Symbol": opportunity["Trading Symbol"],
        "Priority": priority,
        "Priority Source": "DECISION_RISK_LAYER",
        "Requested Allocation": requested_allocation,
        "Capital Allocation Eligible": True,
        "Qualification Reasons": reasons,
        "Risk Context": risk_context,
        "Paper Trade Permission": opportunity["Paper Trade Permission"],
        "Automatic Ranking": False,
        "Broker Communication": False,
        "Order Placement Permitted": False,
        "Wisdom Before Wealth": True,
    }
