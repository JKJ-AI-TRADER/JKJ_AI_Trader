import os
from urllib.parse import urlparse, parse_qs

from kiteconnect import KiteConnect

from modules.intraday_zerodha_session_manager import (
    read_session_token,
    save_session,
    validate_kite_session,
    delete_session,
)


def authenticate_today():
    """
    JKJ Daily Zerodha Authentication

    Purpose:
    - Reuse a valid Zerodha session for today.
    - If unavailable/invalid, perform fresh browser authentication.
    - Save and validate the new session.
    - No trading orders.
    - No paper trading.
    - No API secrets stored in source code.
    """

    api_key = os.getenv("JKJ_KITE_API_KEY")
    api_secret = os.getenv("JKJ_KITE_API_SECRET")

    if not api_key or not api_secret:
        return {
            "Status": "FAILED",
            "Reason": "JKJ_KITE_API_KEY or JKJ_KITE_API_SECRET is missing."
        }

    # ---------------------------------------------------------
    # Step 1: Try today's saved session
    # ---------------------------------------------------------

    saved_token = read_session_token()

    if saved_token:
        try:
            kite = KiteConnect(api_key=api_key)
            kite.set_access_token(saved_token)

            validation = validate_kite_session(kite)

            if validation:
                return {
                    "Status": "SESSION_REUSED",
                    "Reason": "Today's Zerodha session is valid.",
                    "Kite": kite,
                }
        except Exception:
            pass

        # Invalid/expired session
        try:
            delete_session()
        except Exception:
            pass

    # ---------------------------------------------------------
    # Step 2: Fresh browser authentication
    # ---------------------------------------------------------

    kite = KiteConnect(api_key=api_key)

    login_url = kite.login_url()

    print()
    print("=" * 70)
    print("JKJ DAILY ZERODHA AUTHENTICATION")
    print("=" * 70)
    print()
    print("Open this Zerodha login URL in your browser:")
    print()
    print(login_url)
    print()
    print("After successful login, Zerodha will redirect to your")
    print("configured callback URL.")
    print()
    print("Paste the COMPLETE callback URL below.")
    print()

    callback_url = input("Paste the fresh Zerodha callback URL: ").strip()

    if not callback_url:
        return {
            "Status": "FAILED",
            "Reason": "No callback URL was provided."
        }

    # ---------------------------------------------------------
    # Step 3: Extract request token
    # ---------------------------------------------------------

    try:
        parsed_url = urlparse(callback_url)
        query = parse_qs(parsed_url.query)

        request_tokens = query.get("request_token", [])

        if not request_tokens:
            return {
                "Status": "FAILED",
                "Reason": "request_token was not found in callback URL."
            }

        request_token = request_tokens[0]

    except Exception as exc:
        return {
            "Status": "FAILED",
            "Reason": f"Unable to parse callback URL: {exc}"
        }

    # ---------------------------------------------------------
    # Step 4: Generate Zerodha session
    # ---------------------------------------------------------

    try:
        session_data = kite.generate_session(
            request_token,
            api_secret=api_secret
        )

        access_token = session_data.get("access_token")

        if not access_token:
            return {
                "Status": "FAILED",
                "Reason": "Zerodha did not return an access token."
            }

        kite.set_access_token(access_token)

    except Exception as exc:
        return {
            "Status": "FAILED",
            "Reason": f"Zerodha session generation failed: {exc}"
        }

    # ---------------------------------------------------------
    # Step 5: Validate session
    # ---------------------------------------------------------

    try:
        validation = validate_kite_session(kite)

        if not validation:
            return {
                "Status": "FAILED",
                "Reason": "New Zerodha session could not be validated."
            }

    except Exception as exc:
        return {
            "Status": "FAILED",
            "Reason": f"Session validation failed: {exc}"
        }

    # ---------------------------------------------------------
    # Step 6: Save today's session
    # ---------------------------------------------------------

    try:
        save_session(access_token)
    except Exception as exc:
        return {
            "Status": "FAILED",
            "Reason": f"Unable to save Zerodha session: {exc}"
        }

    return {
        "Status": "AUTHENTICATED_AND_SAVED",
        "Reason": "Fresh Zerodha session authenticated, validated and saved.",
        "Kite": kite,
    }


if __name__ == "__main__":

    result = authenticate_today()

    print()
    print("=" * 70)
    print("JKJ DAILY ZERODHA AUTH RESULT")
    print("=" * 70)
    print("Status:", result.get("Status"))
    print("Reason:", result.get("Reason"))
    print()

    if result.get("Kite"):
        print("Kite session: READY")
    else:
        print("Kite session: NOT READY")

    print()
    print("Safety: NO ORDERS / NO PAPER TRADE")
    print("=" * 70)

