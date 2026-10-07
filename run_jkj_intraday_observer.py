from modules.jkj_daily_zerodha_auth import authenticate_today
from modules.nifty_option_v21_2_19_persistent_observer import run_persistent_observer

print("=" * 70)
print("JKJ V21.2.19 INTRADAY PERSISTENT OBSERVER")
print("=" * 70)

auth = authenticate_today()

print("Zerodha Status:", auth.get("Status"))
print("Reason:", auth.get("Reason"))

kite = auth.get("Kite")

if kite is None:
    print("ERROR: Authenticated Kite session not available.")
    raise SystemExit(1)

print("Kite session: READY")
print("Live Order: False")
print("Paper Trade: False")
print()

result = run_persistent_observer(
    kite,
    interval_seconds=15,
    max_observations=4,
    strikes_each_side=10,
)

print()
print("=" * 70)
print("JKJ V21.2.19 OBSERVER RESULT")
print("=" * 70)

print("Status:", result.get("Status"))
print("NIFTY Spot:", result.get("NIFTY Spot"))
print("Expiry:", result.get("Expiry"))
print("Universe Count:", result.get("Universe Count"))
print("Observation Count:", result.get("Observation Count"))
print("Interval Seconds:", result.get("Interval Seconds"))
print("Live Order:", result.get("Live Order"))
print("Paper Trade:", result.get("Paper Trade"))

print()
print("Store Summary:")
print(result.get("Store Summary"))

print()
print("Candidate Lifecycle:")
lifecycle = result.get("Candidate Lifecycle", {})

for symbol, record in lifecycle.items():
    print(
        symbol,
        "| State:", record.get("State"),
        "| Movement:", record.get("Recent Movement %"),
        "| Velocity:", record.get("Latest Velocity %/sec"),
        "| Acceleration:", record.get("Latest Acceleration %/sec2"),
    )
