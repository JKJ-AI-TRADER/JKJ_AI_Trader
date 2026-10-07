from modules.nifty_option_v21_2_22_d_final_evidence_gate import (
    evaluate_final_evidence,
)


def make_candidate(
    symbol,
    lifecycle,
    qualification,
    persistence,
    direction,
    confirmation,
    overall,
    latest,
):
    return {
        "Trading Symbol": symbol,
        "Lifecycle": lifecycle,
        "Qualification": qualification,
        "V12.6 Persistence": persistence,
        "V12.6 Direction": direction,
        "V12.6 Confirmation": confirmation,
        "Overall Movement %": overall,
        "Latest Movement %": latest,
    }


def check(name, candidate, expected):
    result = evaluate_final_evidence(candidate)

    actual = result["Status"]

    print(
        f"{name}: "
        f"{actual} "
        f"| Expected: {expected}"
    )

    if actual != expected:
        print("FAILED")
        print("Failed Checks:", result.get("Failed Checks"))
        raise SystemExit(1)


print("=" * 70)
print("V21.2.22-D SYNTHETIC VALIDATION")
print("=" * 70)

# ------------------------------------------------------------
# 1. Genuine positive case
# ------------------------------------------------------------
check(
    "POSITIVE DEVELOPING",
    make_candidate(
        "NIFTY_TEST_22500CE",
        "PERSISTING",
        "DEVELOPING_CANDIDATE",
        "PERSISTENT",
        "UP",
        "CONFIRMED",
        5.50,
        1.80,
    ),
    "FINAL_EVIDENCE_ACCEPTED",
)


# ------------------------------------------------------------
# 2. Negative price movement
# ------------------------------------------------------------
check(
    "NEGATIVE PRICE",
    make_candidate(
        "NIFTY_TEST_22400PE",
        "STRENGTHENING",
        "STRONG_DEVELOPING_CANDIDATE",
        "PERSISTENT",
        "DOWN",
        "CONFIRMED",
        -10.00,
        -4.00,
    ),
    "FINAL_EVIDENCE_REJECTED",
)


# ------------------------------------------------------------
# 3. Positive price but non-persistent momentum
# ------------------------------------------------------------
check(
    "NOT PERSISTENT",
    make_candidate(
        "NIFTY_TEST_22300CE",
        "PERSISTING",
        "DEVELOPING_CANDIDATE",
        "NOT_PERSISTENT",
        "UP",
        "CONFIRMED",
        4.00,
        2.00,
    ),
    "FINAL_EVIDENCE_REJECTED",
)


# ------------------------------------------------------------
# 4. Positive price but lifecycle retreat
# ------------------------------------------------------------
check(
    "RETREAT",
    make_candidate(
        "NIFTY_TEST_22200CE",
        "RETREAT",
        "DEVELOPING_CANDIDATE",
        "PERSISTENT",
        "UP",
        "CONFIRMED",
        4.00,
        1.00,
    ),
    "FINAL_EVIDENCE_REJECTED",
)


# ------------------------------------------------------------
# 5. Positive price but no confirmation
# ------------------------------------------------------------
check(
    "NOT CONFIRMED",
    make_candidate(
        "NIFTY_TEST_22100CE",
        "PERSISTING",
        "DEVELOPING_CANDIDATE",
        "PERSISTENT",
        "UP",
        "NOT_CONFIRMED",
        4.00,
        1.00,
    ),
    "FINAL_EVIDENCE_REJECTED",
)


print()
print("=" * 70)
print("V21.2.22-D SYNTHETIC TEST PASS")
print("=" * 70)
print("Positive case accepted: PASS")
print("Negative price rejected: PASS")
print("Non-persistent rejected: PASS")
print("Retreat rejected: PASS")
print("Unconfirmed rejected: PASS")
print("Live Order: False")
print("Paper Trade: False")
