"""
JKJ AI Trader
V12.4 Real Market Movement Test

Flow:
Zerodha
    ↓
Dynamic NIFTY Option Selection
    ↓
Real Quote #1
    ↓
V12.3 Movement Recorder
    ↓
Real Quote #2
    ↓
V12.3 Movement Recorder
    ↓
V12.4 Movement Analyzer

This test does NOT:
- place orders
- make BUY decisions
- make SELL/EXIT decisions
- calculate opportunity scores
- modify main.py
"""

import os
import time

from kiteconnect import KiteConnect

from modules.nifty_option_contract_selector import (
    select_nearby_contracts,
)
from modules.intraday_zerodha_option_adapter import (
    adapt_zerodha_option_quote,
)
from modules.intraday_option_real_market_observer import (
    observe_option_market,
)
from modules.nifty_option_movement_recorder import (
    record_option_observation,
)
from modules.nifty_option_movement_analyzer import (
    analyze_option_movement,
)


print("=" * 70)
print("JKJ AI Trader — V12.4 Real Market Movement Test")
print("=" * 70)

print()
print("Please authenticate with a fresh Zerodha session.")
print()

api_key = os.environ.get("JKJ_KITE_API_KEY")
api_secret = os.environ.get("JKJ_KITE_API_SECRET")

if not api_key or not api_secret:
    raise RuntimeError(
        "JKJ_KITE_API_KEY or JKJ_KITE_API_SECRET is missing."
    )

kite = KiteConnect(api_key=api_key)

print("Kite Login URL:")
print(kite.login_url())
print()

callback_url = input(
    "Paste fresh callback URL: "
).strip()

from urllib.parse import urlparse, parse_qs

parsed_url = urlparse(callback_url)
query_params = parse_qs(parsed_url.query)

request_token = query_params.get(
    "request_token",
    [None],
)[0]

if not request_token:
    raise RuntimeError(
        "Request token not found in callback URL."
    )

session_data = kite.generate_session(
    request_token,
    api_secret=api_secret,
)

access_token = session_data.get("access_token")

if not access_token:
    raise RuntimeError(
        "Zerodha access token was not generated."
    )

kite.set_access_token(access_token)

print("Zerodha authentication: SUCCESS")
print()


# ------------------------------------------------------------
# Dynamic NIFTY contract selection
# ------------------------------------------------------------

instruments = kite.instruments("NFO")

nifty_ltp = kite.ltp("NSE:NIFTY 50")

nifty_spot = nifty_ltp["NSE:NIFTY 50"]["last_price"]

nifty_options = [
    instrument
    for instrument in instruments
    if instrument.get("name") == "NIFTY"
    and instrument.get("instrument_type") in ("CE", "PE")
]

expiries = sorted(
    {
        instrument.get("expiry")
        for instrument in nifty_options
        if instrument.get("expiry") is not None
    }
)

if not expiries:
    raise RuntimeError(
        "No NIFTY option expiries found."
    )

selected_expiry = expiries[0]

selection_result = select_nearby_contracts(
    nifty_options,
    nifty_spot,
    selected_expiry,
    contracts_per_side=1,
)

if selection_result.get("Status") != "SELECTED":
    raise RuntimeError(
        f"No nearby NIFTY option contracts selected: "
        f"{selection_result}"
    )

contracts = selection_result.get("Contracts", [])

if not contracts:
    raise RuntimeError(
        "No contracts were returned by the selector."
    )

selected_contract = contracts[0]

trading_symbol = selected_contract["tradingsymbol"]
instrument_token = selected_contract["instrument_token"]
strike = selected_contract["strike"]
option_type = selected_contract["instrument_type"]
expiry = selected_contract["expiry"]

expiry_string = str(expiry)

print("Dynamic NIFTY contract selected:")
print(f"Trading Symbol: {trading_symbol}")
print(f"Instrument Token: {instrument_token}")
print(f"Strike: {strike}")
print(f"Option Type: {option_type}")
print(f"Expiry: {expiry}")
print()


# ------------------------------------------------------------
# Helper: capture one real market observation
# ------------------------------------------------------------

def capture_observation():
    quote_response = kite.quote(
        [
            f"NFO:{trading_symbol}",
            "NSE:NIFTY 50",
        ]
    )

    adapted_option = adapt_zerodha_option_quote(
        quote_response=quote_response,
        trading_symbol=trading_symbol,
        instrument_token=instrument_token,
        underlying="NIFTY",
    )

    observed_option = observe_option_market(
        adapted_option
    )

    if observed_option.get("Status") != "READY":
        raise RuntimeError(
            f"Option observation failed: {observed_option}"
        )

    option_price = observed_option["Current Price"]
    volume = observed_option["Volume"]
    open_interest = observed_option["Open Interest"]

    nifty_quote = quote_response["NSE:NIFTY 50"]
    fresh_nifty_spot = nifty_quote["last_price"]

    observation = record_option_observation(
        trading_symbol=trading_symbol,
        underlying="NIFTY",
        expiry=expiry_string,
        strike=strike,
        option_type=option_type,
        current_price=option_price,
        volume=volume,
        open_interest=open_interest,
        nifty_spot_price=fresh_nifty_spot,
        timestamp=observed_option[
            "Observation Timestamp"
        ],
    )

    if observation.get("Status") != "RECORDED":
        raise RuntimeError(
            f"Movement record failed: {observation}"
        )

    return observation


# ------------------------------------------------------------
# Observation 1
# ------------------------------------------------------------

print("Capturing real market observation #1...")
observation_1 = capture_observation()

print()
print("Observation #1:")
print(observation_1)
print()


# ------------------------------------------------------------
# Wait before observation 2
# ------------------------------------------------------------

print("Waiting 10 seconds for market movement...")
time.sleep(10)


# ------------------------------------------------------------
# Observation 2
# ------------------------------------------------------------

print()
print("Capturing real market observation #2...")
observation_2 = capture_observation()

print()
print("Observation #2:")
print(observation_2)
print()


# ------------------------------------------------------------
# V12.4 Movement Analysis
# ------------------------------------------------------------

movement = analyze_option_movement(
    observation_1,
    observation_2,
)

print("V12.4 Movement Analysis:")
print(movement)
print()


if movement.get("Status") != "ANALYZED":
    raise RuntimeError(
        f"Movement analysis failed: {movement}"
    )


print("=" * 70)
print("V12.4 REAL MARKET → MOVEMENT ANALYSIS: PASS")
print("=" * 70)