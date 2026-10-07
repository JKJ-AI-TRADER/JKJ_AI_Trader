from modules.nifty_option_v21_2_22_d_final_evidence_gate import (
    evaluate_final_evidence,
)

print("=" * 70)
print("V21.2.22-D REAL-MARKET REGRESSION TEST")
print("2026-10-06 EVIDENCE-CONFLICT CASE")
print("=" * 70)

candidates = [
    {
        "Trading Symbol": "NIFTY26O0622250PE",
        "Lifecycle": "PERSISTING",
        "Qualification": "DEVELOPING_CANDIDATE",
        "V12.6 Persistence": "PERSISTENT",
        "V12.6 Direction": "DOWN",
        "V12.6 Confirmation": "CONFIRMED",
        "Overall Movement %": -10.0,
        "Latest Movement %": -4.545454545,
    },
    {
        "Trading Symbol": "NIFTY26O0622400PE",
        "Lifecycle": "STRENGTHENING",
        "Qualification": "STRONG_DEVELOPING_CANDIDATE",
        "V12.6 Persistence": "PERSISTENT",
        "V12.6 Direction": "DOWN",
        "V12.6 Confirmation": "CONFIRMED",
        "Overall Movement %": -12.173913043,
        "Latest Movement %": -7.762557078,
    },
    {
        "Trading Symbol": "NIFTY26O0622450PE",
        "Lifecycle": "STRENGTHENING",
        "Qualification": "STRONG_DEVELOPING_CANDIDATE",
        "V12.6 Persistence": "PERSISTENT",
        "V12.6 Direction": "DOWN",
        "V12.6 Confirmation": "CONFIRMED",
        "Overall Movement %": -13.687150838,
        "Latest Movement %": -8.035714286,
    },
]

for candidate in candidates:
    result = evaluate_final_evidence(candidate)

    print(
        candidate["Trading Symbol"],
        "| Result:",
        result["Status"],
        "| Expected: FINAL_EVIDENCE_REJECTED",
    )

    if result["Status"] != "FINAL_EVIDENCE_REJECTED":
        print("FAILED")
        print("Failed Checks:", result["Failed Checks"])
        raise SystemExit(1)

print()
print("=" * 70)
print("V21.2.22-D REAL-MARKET REGRESSION TEST PASS")
print("=" * 70)
print("All three 2026-10-06 candidates correctly rejected.")
print("Live Order: False")
print("Paper Trade: False")
