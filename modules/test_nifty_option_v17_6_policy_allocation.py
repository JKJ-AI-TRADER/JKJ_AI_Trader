"""
JKJ AI Trader
V17.6.5 — Policy-Based Multi-Candidate Capital Allocation Test
"""

from nifty_option_v17_6_policy_allocation import allocate_with_policy


print("\n==============================================")
print("JKJ V17.6.5 POLICY ALLOCATION TEST")
print("==============================================")


# ---------------------------------------------------------
# TEST 1
# Priority must determine allocation order
# ---------------------------------------------------------
print("\nTEST 1 — Priority-Based Allocation")

candidates = [
    {
        "Candidate": "NIFTY PE B",
        "Priority": 2,
        "Requested Allocation": 10000,
    },
    {
        "Candidate": "NIFTY CE A",
        "Priority": 1,
        "Requested Allocation": 20000,
    },
]

result = allocate_with_policy(
    usable_capital=30000,
    candidates=candidates,
    max_positions=6,
    max_capital_per_candidate=20000,
    minimum_candidate_allocation=5000,
)

print(result)

assert result["Status"] == "POLICY_ALLOCATION_COMPLETE"
assert result["Allocations"][0]["Candidate"] == "NIFTY CE A"
assert result["Allocations"][0]["Allocated Capital"] == 20000
assert result["Allocations"][1]["Candidate"] == "NIFTY PE B"
assert result["Allocations"][1]["Allocated Capital"] == 10000


# ---------------------------------------------------------
# TEST 2
# Maximum positions
# ---------------------------------------------------------
print("\nTEST 2 — Maximum Position Limit")

candidates = [
    {
        "Candidate": "A",
        "Priority": 1,
        "Requested Allocation": 5000,
    },
    {
        "Candidate": "B",
        "Priority": 2,
        "Requested Allocation": 5000,
    },
    {
        "Candidate": "C",
        "Priority": 3,
        "Requested Allocation": 5000,
    },
]

result = allocate_with_policy(
    usable_capital=20000,
    candidates=candidates,
    max_positions=2,
    max_capital_per_candidate=20000,
    minimum_candidate_allocation=5000,
)

print(result)

assert result["Positions Allocated"] == 2
assert result["Allocations"][0]["Allocated Capital"] == 5000
assert result["Allocations"][1]["Allocated Capital"] == 5000
assert result["Allocations"][2]["Allocated Capital"] == 0
assert (
    result["Allocations"][2]["Allocation Status"]
    == "UNALLOCATED_MAX_POSITIONS"
)


# ---------------------------------------------------------
# TEST 3
# Maximum capital per candidate
# ---------------------------------------------------------
print("\nTEST 3 — Maximum Capital Per Candidate")

candidates = [
    {
        "Candidate": "A",
        "Priority": 1,
        "Requested Allocation": 30000,
    },
]

result = allocate_with_policy(
    usable_capital=30000,
    candidates=candidates,
    max_positions=6,
    max_capital_per_candidate=20000,
    minimum_candidate_allocation=5000,
)

print(result)

assert result["Allocations"][0]["Allocated Capital"] == 20000
assert result["Remaining Capital"] == 10000


# ---------------------------------------------------------
# TEST 4
# Minimum allocation
# ---------------------------------------------------------
print("\nTEST 4 — Minimum Candidate Allocation")

candidates = [
    {
        "Candidate": "A",
        "Priority": 1,
        "Requested Allocation": 3000,
    },
]

result = allocate_with_policy(
    usable_capital=30000,
    candidates=candidates,
    max_positions=6,
    max_capital_per_candidate=20000,
    minimum_candidate_allocation=5000,
)

print(result)

assert result["Allocations"][0]["Allocated Capital"] == 0
assert (
    result["Allocations"][0]["Allocation Status"]
    == "UNALLOCATED_BELOW_MINIMUM"
)


# ---------------------------------------------------------
# TEST 5
# Partial allocation from remaining capital
# ---------------------------------------------------------
print("\nTEST 5 — Partial Allocation From Remaining Capital")

candidates = [
    {
        "Candidate": "A",
        "Priority": 1,
        "Requested Allocation": 20000,
    },
    {
        "Candidate": "B",
        "Priority": 2,
        "Requested Allocation": 10000,
    },
    {
        "Candidate": "C",
        "Priority": 3,
        "Requested Allocation": 10000,
    },
]

result = allocate_with_policy(
    usable_capital=25000,
    candidates=candidates,
    max_positions=6,
    max_capital_per_candidate=20000,
    minimum_candidate_allocation=5000,
)

print(result)

assert result["Allocations"][0]["Allocated Capital"] == 20000
assert result["Allocations"][1]["Allocated Capital"] == 5000
assert result["Allocations"][2]["Allocated Capital"] == 0
assert result["Remaining Capital"] == 0


# ---------------------------------------------------------
# TEST 6
# Duplicate priority must be blocked
# ---------------------------------------------------------
print("\nTEST 6 — Duplicate Priority")

candidates = [
    {
        "Candidate": "A",
        "Priority": 1,
        "Requested Allocation": 10000,
    },
    {
        "Candidate": "B",
        "Priority": 1,
        "Requested Allocation": 10000,
    },
]

result = allocate_with_policy(
    usable_capital=30000,
    candidates=candidates,
    max_positions=6,
    max_capital_per_candidate=20000,
    minimum_candidate_allocation=5000,
)

print(result)

assert result["Status"] == "POLICY_ALLOCATION_BLOCKED"


print("\n==============================================")
print("ALL V17.6.5 POLICY ALLOCATION TESTS PASSED")
print("==============================================")