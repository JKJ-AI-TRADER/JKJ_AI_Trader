"""
JKJ AI Trader
V16.2 — Zerodha Authentication Bridge

Purpose:
Provide a controlled browser-login handoff for V16.2.

This module does NOT:
- place live orders
- make BUY/SELL decisions
- fetch market data
- modify V12 modules
- modify V13-V15 modules
- modify main.py
"""

import os
from urllib.parse import urlparse, parse_qs

from kiteconnect import KiteConnect

from modules.intraday_zerodha_session_manager import (
    save_session,
    validate_kite_session,
)


def get_authenticated_kite():
    """
    Reuse today's valid session when possible.

    If no valid session exists, perform a fresh browser
    authentication and save the new session locally.
    """

    api_key = os.getenv("JKJ_KITE_API_KEY")
    api_secret = os.getenv("JKJ_KITE_API_SECRET")

    if not api_key:
        return {
            "Status": "FAILED",
            "Reason": "JKJ_KITE_API_KEY is not available.",
        }

    if not api_secret:
        return {
            "Status": "FAILED",
            "Reason": "JKJ_KITE_API_SECRET is not available.",
        }

    kite = KiteConnect(api_key=api_key)

    print("\nPlease authenticate with a fresh Zerodha session.")
    print("Open the following Kite Login URL:\n")
    print(kite.login_url())

    callback_url = input(
        "\nPaste the fresh Zerodha callback URL: "
    ).strip()

    if not callback_url:
        return {
            "Status": "FAILED",
            "Reason": "No callback URL was provided.",
        }

    parsed_url = urlparse(callback_url)
    query_params = parse_qs(parsed_url.query)

    request_token = query_params.get(
        "request_token",
        [None],
    )[0]

    if not request_token:
        return {
            "Status": "FAILED",
            "Reason": "Request token was not found in callback URL.",
        }

    try:

        session_data = kite.generate_session(
            request_token,
            api_secret=api_secret,
        )

        access_token = session_data.get(
            "access_token"
        )

        if not access_token:
            return {
                "Status": "FAILED",
                "Reason": "Zerodha did not return an access token.",
            }

        kite.set_access_token(
            access_token
        )

        if not validate_kite_session(kite):
            return {
                "Status": "FAILED",
                "Reason": "Fresh Zerodha session failed validation.",
            }

        if not save_session(access_token):
            return {
                "Status": "FAILED",
                "Reason": "Fresh Zerodha session could not be saved.",
            }

        return {
            "Status": "AUTHENTICATED",
            "Kite": kite,
        }

    except Exception as error:

        return {
            "Status": "FAILED",
            "Reason": str(error),
        }
