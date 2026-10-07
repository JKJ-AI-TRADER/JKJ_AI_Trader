"""
JKJ AI Trader

V21.2.22-D.1 → B.1 → V21.2.16 Positive-Path Integration Test

Purpose:
    Prove that a candidate explicitly accepted by D.1 is the ONLY
    candidate permitted through the B.1 restriction and into the
    existing V21.2.20 → V21.2.16 adapter.

Safety:
    - Synthetic data only
    - No Zerodha market data
    - No orders
    - No paper trades
    - No BUY/SELL
    - No position sizing
    - No stop/target execution
"""

from modules.nifty_option_v21_2_22_d1_to_b1_authorization import (
    build_d1_authorized_b1_result,
)

from modules.nifty_option_v21_2_22_b1_to_v21_2_16_adapter import (
    build_selected_qualification_result,
)


LIVE_ORDER = False
PAPER_TRADE = False


print("=" * 72)
print("V21.2.22-D.1 → B.1 → V21.2.16 POSITIVE-PATH TEST")
print("=" * 72)
print("Safety: Live Order=False")
print("Safety: Paper Trade=False")
print()


# ---------------------------------------------------------
# 1. Synthetic B.1 selected result
# ---------------------------------------------------------

b1_result = {
    "Status": "CANDIDATE_QUALIFICATION_COMPLETE",

    "Candidates": {},

    "Qualified Candidates": [
        {
            "Trading Symbol": "NIFTY26O0622900CE",
            "Qualification": "STRONG_DEVELOPING_CANDIDATE",
        },
        {
            "Trading Symbol": "NIFTY26O0622850CE",
            "Qualification": "DEVELOPING_CANDIDATE",
        },
        {
            "Trading Symbol": "NIFTY26O0622800CE",
            "Qualification": "DEVELOPING_CANDIDATE",
        },
    ],

    "Selection Applied": True,

    "Selection Source": (
        "V21.2.22-B.1 Candidate Selection"
    ),

    "Original Qualification Source": (
        "V21.2.20 Candidate Qualification"
    ),

    "Live Order": False,
    "Paper Trade": False,
}


# ---------------------------------------------------------
# 2. Synthetic D.1 result
#
# Only 2900CE passes D.1.
# ---------------------------------------------------------

d1_result = {
    "Status": "EVIDENCE_GATED_ENTRY_BRIDGE_COMPLETE",

    "Accepted Candidates": [
        {
            "Trading Symbol": "NIFTY26O0622900CE",
            "Lifecycle": "STRENGTHENING",
            "Qualification": "STRONG_DEVELOPING_CANDIDATE",
            "V12.6 Persistence": "PERSISTENT",
            "V12.6 Direction": "UP",
            "V12.6 Confirmation": "CONFIRMED",
            "Evidence Gate": "PASSED",
            "Entry Evaluation": "PENDING",
            "Live Order": False,
            "Paper Trade": False,
        }
    ],

    "Rejected Candidates": [
        {
            "Trading Symbol": "NIFTY26O0622850CE",
        },
        {
            "Trading Symbol": "NIFTY26O0622800CE",
        },
    ],

    "Accepted Candidate Count": 1,
    "Rejected Candidate Count": 2,

    "Next Stage": "EXISTING_ENTRY_QUALIFICATION",

    "Live Order": False,
    "Paper Trade": False,
}


# ---------------------------------------------------------
# 3. D.1 authorization
# ---------------------------------------------------------

authorized_result = build_d1_authorized_b1_result(
    b1_result,
    d1_result,
)

print("D.1 Authorization Status:",
      authorized_result.get("Status"))

print(
    "B.1 Original Candidates:",
    authorized_result.get(
        "Original B1 Qualified Candidate Count"
    ),
)

print(
    "D.1 Accepted:",
    authorized_result.get(
        "D1 Accepted Candidate Count"
    ),
)

print(
    "Authorized:",
    authorized_result.get(
        "Authorized Candidate Count"
    ),
)

print(
    "Blocked:",
    authorized_result.get(
        "Rejected By D1 Count"
    ),
)

for candidate in authorized_result.get(
    "Qualified Candidates",
    [],
):
    print(
        "  AUTHORIZED:",
        candidate.get("Trading Symbol"),
    )

for candidate in authorized_result.get(
    "Rejected By D1 Candidates",
    [],
):
    print(
        "  BLOCKED:",
        candidate.get("Trading Symbol"),
    )

print()


# ---------------------------------------------------------
# 4. Existing B.1 → V21.2.16 adapter
# ---------------------------------------------------------

# Build a synthetic selection result containing only the
# candidates authorized by D.1.

authorized_candidates = authorized_result.get(
    "Qualified Candidates",
    [],
)

selection_for_existing_adapter = {
    "Status": "CANDIDATE_SELECTION_COMPLETE",

    "Selected Candidates": authorized_candidates,

    "Selection Source": (
        "V21.2.22-D.1 Authorization"
    ),

    "Live Order": False,
    "Paper Trade": False,
}


# The existing adapter expects the original V21.2.20
# qualification result plus the selected candidates.

handoff_result = build_selected_qualification_result(
    b1_result,
    selection_for_existing_adapter,
)


print("Existing B.1 → V21.2.16 Adapter Status:",
      handoff_result.get("Status"))

print(
    "Handoff Qualified Candidates:",
    handoff_result.get(
        "Qualified Candidate Count"
    ),
)

for candidate in handoff_result.get(
    "Qualified Candidates",
    [],
):
    print(
        "  V21.2.16 AUTHORIZED:",
        candidate.get("Trading Symbol"),
    )

print()


# ---------------------------------------------------------
# 5. Assertions
# ---------------------------------------------------------

assert authorized_result.get("Status") == (
    "D1_AUTHORIZED_B1_RESULT_COMPLETE"
)

assert authorized_result.get(
    "Authorized Candidate Count"
) == 1

assert authorized_result.get(
    "D1 Accepted Candidate Count"
) == 1

assert authorized_result.get(
    "Rejected By D1 Count"
) == 2

assert handoff_result.get("Status") == (
    "CANDIDATE_QUALIFICATION_COMPLETE"
)

assert handoff_result.get(
    "Qualified Candidate Count"
) == 1

final_candidates = handoff_result.get(
    "Qualified Candidates",
    [],
)

assert len(final_candidates) == 1

assert final_candidates[0].get(
    "Trading Symbol"
) == "NIFTY26O0622900CE"

assert (
    final_candidates[0].get("Trading Symbol")
    != "NIFTY26O0622850CE"
)

assert (
    final_candidates[0].get("Trading Symbol")
    != "NIFTY26O0622800CE"
)

assert handoff_result.get("Live Order") is False
assert handoff_result.get("Paper Trade") is False


print("=" * 72)
print("POSITIVE-PATH TEST PASS")
print("=" * 72)
print("D.1 Accepted:              1")
print("D.1 Blocked:               2")
print("Authorized for V21.2.16:  1")
print("Final handoff candidates: 1")
print("Authorized symbol:         NIFTY26O0622900CE")
print("Live Order:                False")
print("Paper Trade:               False")
print("BUY/SELL:                  NOT EXECUTED")
print("=" * 72)
