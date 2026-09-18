"""
JKJ AI Trader
V17.6.5 — Policy-Based Multi-Candidate Capital Allocation

Purpose:
Allocate usable capital across already-qualified candidates
according to explicit Decision/Risk priority and configured
capital-management policy.

This module does NOT:
- rank candidates automatically
- qualify opportunities
- change entry/stop/target decisions
- place orders
"""

def allocate_with_policy(
    usable_capital,
    candidates,
    max_positions,
    max_capital_per_candidate,
    minimum_candidate_allocation,
):
    # ---------------------------------------------------------
    # Basic validation
    # ---------------------------------------------------------
    if not isinstance(usable_capital, (int, float)):
        return {
            "Status": "POLICY_ALLOCATION_BLOCKED",
            "Reason": "Invalid usable capital",
        }

    if usable_capital < 0:
        return {
            "Status": "POLICY_ALLOCATION_BLOCKED",
            "Reason": "Usable capital cannot be negative",
        }

    if not isinstance(candidates, list):
        return {
            "Status": "POLICY_ALLOCATION_BLOCKED",
            "Reason": "Candidates must be a list",
        }

    if not isinstance(max_positions, int) or max_positions <= 0:
        return {
            "Status": "POLICY_ALLOCATION_BLOCKED",
            "Reason": "Invalid maximum positions",
        }

    if (
        not isinstance(max_capital_per_candidate, (int, float))
        or max_capital_per_candidate <= 0
    ):
        return {
            "Status": "POLICY_ALLOCATION_BLOCKED",
            "Reason": "Invalid maximum capital per candidate",
        }

    if (
        not isinstance(minimum_candidate_allocation, (int, float))
        or minimum_candidate_allocation <= 0
    ):
        return {
            "Status": "POLICY_ALLOCATION_BLOCKED",
            "Reason": "Invalid minimum candidate allocation",
        }

    if minimum_candidate_allocation > max_capital_per_candidate:
        return {
            "Status": "POLICY_ALLOCATION_BLOCKED",
            "Reason": "Minimum allocation exceeds maximum allocation",
        }

    # ---------------------------------------------------------
    # Validate candidates
    # ---------------------------------------------------------
    required_fields = {
        "Candidate",
        "Priority",
        "Requested Allocation",
    }

    seen_priorities = set()

    for candidate in candidates:
        if not isinstance(candidate, dict):
            return {
                "Status": "POLICY_ALLOCATION_BLOCKED",
                "Reason": "Each candidate must be a dictionary",
            }

        if not required_fields.issubset(candidate.keys()):
            return {
                "Status": "POLICY_ALLOCATION_BLOCKED",
                "Reason": "Candidate missing required fields",
            }

        priority = candidate["Priority"]
        requested = candidate["Requested Allocation"]

        if not isinstance(priority, int) or priority <= 0:
            return {
                "Status": "POLICY_ALLOCATION_BLOCKED",
                "Reason": "Priority must be a positive integer",
            }

        if priority in seen_priorities:
            return {
                "Status": "POLICY_ALLOCATION_BLOCKED",
                "Reason": "Duplicate candidate priority",
            }

        seen_priorities.add(priority)

        if (
            not isinstance(requested, (int, float))
            or requested < 0
        ):
            return {
                "Status": "POLICY_ALLOCATION_BLOCKED",
                "Reason": "Requested allocation must be non-negative",
            }

    # ---------------------------------------------------------
    # Explicit Decision/Risk priority only
    # Lower number = higher priority
    # ---------------------------------------------------------
    ordered_candidates = sorted(
        candidates,
        key=lambda candidate: candidate["Priority"]
    )

    remaining_capital = float(usable_capital)
    allocations = []
    positions_allocated = 0

    # ---------------------------------------------------------
    # Apply allocation policy
    # ---------------------------------------------------------
    for candidate in ordered_candidates:

        if positions_allocated >= max_positions:
            allocations.append({
                "Candidate": candidate["Candidate"],
                "Priority": candidate["Priority"],
                "Requested Allocation": candidate["Requested Allocation"],
                "Allocated Capital": 0,
                "Allocation Status": "UNALLOCATED_MAX_POSITIONS",
            })
            continue

        requested = candidate["Requested Allocation"]

        candidate_limit = min(
            requested,
            max_capital_per_candidate
        )

        if candidate_limit < minimum_candidate_allocation:
            allocations.append({
                "Candidate": candidate["Candidate"],
                "Priority": candidate["Priority"],
                "Requested Allocation": requested,
                "Allocated Capital": 0,
                "Allocation Status": "UNALLOCATED_BELOW_MINIMUM",
            })
            continue

        if remaining_capital < minimum_candidate_allocation:
            allocations.append({
                "Candidate": candidate["Candidate"],
                "Priority": candidate["Priority"],
                "Requested Allocation": requested,
                "Allocated Capital": 0,
                "Allocation Status": "UNALLOCATED_INSUFFICIENT_CAPITAL",
            })
            continue

        allocation = min(
            candidate_limit,
            remaining_capital
        )

        if allocation < minimum_candidate_allocation:
            allocation = 0

        if allocation > 0:
            positions_allocated += 1
            remaining_capital -= allocation

        allocations.append({
            "Candidate": candidate["Candidate"],
            "Priority": candidate["Priority"],
            "Requested Allocation": requested,
            "Allocated Capital": allocation,
            "Allocation Status": (
                "ALLOCATED"
                if allocation > 0
                else "UNALLOCATED"
            ),
        })

    # ---------------------------------------------------------
    # Final result
    # ---------------------------------------------------------
    return {
        "Status": "POLICY_ALLOCATION_COMPLETE",
        "Usable Capital": usable_capital,
        "Maximum Positions": max_positions,
        "Maximum Capital Per Candidate": max_capital_per_candidate,
        "Minimum Candidate Allocation": minimum_candidate_allocation,
        "Allocations": allocations,
        "Positions Allocated": positions_allocated,
        "Remaining Capital": remaining_capital,
        "Priority Source": "DECISION_RISK_LAYER",
        "Automatic Ranking": False,
    }