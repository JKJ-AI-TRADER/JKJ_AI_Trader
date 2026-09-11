from intraday_option_universe import (
    calculate_atm_strike,
    build_nifty_option_universe,
)


print("\n=========================================")
print("JKJ OPTION UNIVERSE ENGINE V1 TEST")
print("=========================================")


# ---------------------------------------------------------
# TEST 1 — ATM calculation
# ---------------------------------------------------------

atm = calculate_atm_strike(
    spot_price=23291.50,
    strike_step=50
)

print("\nTEST 1 — ATM STRIKE")
print("-----------------------------------------")
print("ATM Strike:", atm)

if atm == 23300:
    print("PASS")
else:
    print("FAIL")


# ---------------------------------------------------------
# TEST 2 — Build NIFTY option universe
# ---------------------------------------------------------

result = build_nifty_option_universe(
    spot_price=23291.50,
    strike_step=50,
    expiry="2026-09-15",
    strikes_each_side=2
)

print("\nTEST 2 — OPTION UNIVERSE")
print("-----------------------------------------")

print("Status:", result["Status"])
print("Spot Price:", result["Spot Price"])
print("ATM Strike:", result["ATM Strike"])
print("Strike Step:", result["Strike Step"])
print("Expiry:", result["Expiry"])
print("Strikes:", result["Strikes"])
print("Candidate Count:", result["Candidate Count"])

if (
    result["Status"] == "READY"
    and result["ATM Strike"] == 23300
    and result["Candidate Count"] == 10
):
    print("PASS")
else:
    print("FAIL")


# ---------------------------------------------------------
# TEST 3 — Candidate structure
# ---------------------------------------------------------

print("\nTEST 3 — CANDIDATE STRUCTURE")
print("-----------------------------------------")

for candidate in result["Candidates"]:
    print(candidate)

valid_structure = all(
    candidate["Underlying"] == "NIFTY"
    and candidate["Expiry"] == "2026-09-15"
    and candidate["Option Type"] in ("CE", "PE")
    for candidate in result["Candidates"]
)

if valid_structure:
    print("PASS")
else:
    print("FAIL")


# ---------------------------------------------------------
# TEST 4 — Invalid input
# ---------------------------------------------------------

invalid_result = build_nifty_option_universe(
    spot_price=0,
    strike_step=50,
    expiry="2026-09-15"
)

print("\nTEST 4 — INVALID INPUT")
print("-----------------------------------------")
print("Status:", invalid_result["Status"])
print("Reason:", invalid_result["Reasons"])

if invalid_result["Status"] == "INVALID":
    print("PASS")
else:
    print("FAIL")


print("\n=========================================")
print("JKJ OPTION UNIVERSE V1 TEST COMPLETE")
print("=========================================")