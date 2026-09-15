"""
JKJ AI Trader
Zerodha Authentication Helper — Stage 1

Purpose:
Provide a small local mechanism for receiving a Zerodha
request token from the browser callback.

This stage does NOT:
- authenticate with Zerodha
- create an access token
- place orders
- modify main.py
- modify frozen JKJ modules
"""

import os
import time


TOKEN_FILE = ".kite_request_token"


def clear_request_token():
    """
    Remove any previous request token.
    """

    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)

    return True


def save_request_token(request_token):
    """
    Save a fresh request token locally.

    The token is never printed or returned.
    """

    if not isinstance(request_token, str):
        return False

    request_token = request_token.strip()

    if not request_token:
        return False

    with open(
        TOKEN_FILE,
        "w",
        encoding="utf-8",
    ) as file:
        file.write(request_token)

    return True


def request_token_available():
    """
    Check whether a request token has been received.
    """

    return os.path.isfile(TOKEN_FILE)


def read_request_token(timeout_seconds=60):
    """
    Wait for a request token to appear.

    The token itself is returned to the caller but is never
    printed by this module.
    """

    start_time = time.time()

    while time.time() - start_time < timeout_seconds:

        if request_token_available():

            with open(
                TOKEN_FILE,
                "r",
                encoding="utf-8",
            ) as file:
                request_token = file.read().strip()

            if request_token:
                return request_token

        time.sleep(1)

    return None


def delete_request_token():
    """
    Delete the locally stored request token.
    """

    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)

    return True
def create_zerodha_session():
    """
    Create a Zerodha authenticated Kite session
    using the saved request token.

    Returns
    -------
    dict
        Authentication result containing the Kite
        connection when successful.

    Credentials and tokens are never printed.
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

    request_token = read_request_token(
        timeout_seconds=60
    )

    if not request_token:
        return {
            "Status": "FAILED",
            "Reason": "No request token was received.",
        }

    try:

        from kiteconnect import KiteConnect

        kite = KiteConnect(
            api_key=api_key
        )

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

        delete_request_token()

        return {
            "Status": "AUTHENTICATED",
            "Kite": kite,
        }

    except Exception as error:

        return {
            "Status": "FAILED",
            "Reason": str(error),
        }