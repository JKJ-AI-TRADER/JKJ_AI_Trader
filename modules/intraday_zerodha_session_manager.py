"""
JKJ AI Trader
V12.5 — Secure Daily Zerodha Session Manager

Purpose:
Manage a local daily Kite session without exposing
credentials or access tokens in source code or GitHub.

This stage does NOT:
- place live orders
- modify main.py
- modify frozen V1–V12 modules
- make trading decisions
"""

import os
from datetime import datetime
from zoneinfo import ZoneInfo


SESSION_FILE = ".kite_session"
INDIA_TIMEZONE = ZoneInfo("Asia/Kolkata")


def _today_ist():
    """
    Return today's date according to India Standard Time.
    """

    return datetime.now(INDIA_TIMEZONE).date().isoformat()


def session_file_exists():
    """
    Check whether a local Kite session file exists.
    """

    return os.path.isfile(SESSION_FILE)


def session_file_date():
    """
    Return the date stored in the local session file.

    Returns None if the file does not exist or cannot
    be read safely.
    """

    if not session_file_exists():
        return None

    try:

        with open(
            SESSION_FILE,
            "r",
            encoding="utf-8",
        ) as file:

            stored_date = file.readline().strip()

        if not stored_date:
            return None

        return stored_date

    except Exception:

        return None


def session_is_from_today():
    """
    Check whether the local session file belongs to
    today according to India Standard Time.
    """

    stored_date = session_file_date()

    if not stored_date:
        return False

    return stored_date == _today_ist()


def save_session(access_token):
    """
    Save an authenticated Kite access token locally
    together with today's India date.

    The token is never printed.
    """

    if not isinstance(access_token, str):
        return False

    access_token = access_token.strip()

    if not access_token:
        return False

    try:

        with open(
            SESSION_FILE,
            "w",
            encoding="utf-8",
        ) as file:

            file.write(
                _today_ist()
                + "\n"
            )

            file.write(
                access_token
            )

        return True

    except Exception:

        return False


def read_session_token():
    """
    Read today's locally stored access token.

    Returns None if the session does not belong to today.
    """

    if not session_is_from_today():
        return None

    try:

        with open(
            SESSION_FILE,
            "r",
            encoding="utf-8",
        ) as file:

            stored_date = file.readline().strip()
            access_token = file.read().strip()

        if stored_date != _today_ist():
            return None

        if not access_token:
            return None

        return access_token

    except Exception:

        return None


def delete_session():
    """
    Delete the locally stored Kite session.
    """

    try:

        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)

        return True

    except Exception:

        return False


def validate_kite_session(kite):
    """
    Validate an existing Kite session using a read-only
    authenticated API call.

    Returns True if the session is accepted by Zerodha.
    Returns False if the session is invalid or unavailable.

    This function does not place orders.
    """

    if kite is None:
        return False

    try:

        kite.profile()

        return True

    except Exception:

        return False


def _build_kite_from_token(access_token):
    """
    Build and validate a Kite session from a saved token.

    Returns
    -------
    KiteConnect object or None
    """

    if not access_token:
        return None

    try:

        from kiteconnect import KiteConnect

        api_key = os.getenv(
            "JKJ_KITE_API_KEY"
        )

        if not api_key:
            return None

        kite = KiteConnect(
            api_key=api_key
        )

        kite.set_access_token(
            access_token
        )

        if not validate_kite_session(kite):
            return None

        return kite

    except Exception:

        return None


def get_kite_session():
    """
    Return an authenticated Kite session.

    If a valid session for today exists, validate and reuse it.

    If today's session is invalid or no session exists,
    use the existing Zerodha authentication helper.

    A newly authenticated session is saved, read back,
    and validated again before being returned.

    Returns
    -------
    dict
        Session result containing the Kite object when
        authentication succeeds.
    """

    existing_token = read_session_token()

    if existing_token:

        kite = _build_kite_from_token(
            existing_token
        )

        if kite is not None:

            return {
                "Status": "SESSION_REUSED",
                "Kite": kite,
            }

        # Existing session is no longer valid.
        # Remove only the invalid local session and
        # continue to fresh authentication.
        delete_session()

    from modules.intraday_zerodha_auth import (
        create_zerodha_session,
    )

    try:

        authentication_result = (
            create_zerodha_session()
        )

    except Exception as error:

        return {
            "Status": "FAILED",
            "Reason": (
                "Zerodha authentication helper failed: "
                + str(error)
            ),
        }

    if authentication_result.get(
        "Status"
    ) != "AUTHENTICATED":

        return authentication_result

    kite = authentication_result.get(
        "Kite"
    )

    if kite is None:

        return {
            "Status": "FAILED",
            "Reason": (
                "Authenticated Kite session "
                "was not returned."
            ),
        }

    access_token = getattr(
        kite,
        "access_token",
        None
    )

    if not access_token:

        return {
            "Status": "FAILED",
            "Reason": (
                "Authenticated access token "
                "was not available."
            ),
        }

    if not save_session(
        access_token
    ):

        return {
            "Status": "FAILED",
            "Reason": (
                "Authenticated session "
                "could not be saved."
            ),
        }

    # Re-read the saved token and validate it.
    saved_token = read_session_token()

    if not saved_token:

        return {
            "Status": "FAILED",
            "Reason": (
                "Saved Zerodha session "
                "could not be read back."
            ),
        }

    verified_kite = _build_kite_from_token(
        saved_token
    )

    if verified_kite is None:

        return {
            "Status": "FAILED",
            "Reason": (
                "Saved Zerodha session "
                "could not be revalidated."
            ),
        }

    return {
        "Status": "AUTHENTICATED_AND_VERIFIED",
        "Kite": verified_kite,
    }


def authenticate_and_save_session():
    """
    Authenticate with Zerodha using the existing V12.4
    authentication helper and save the resulting access
    token for reuse during the current day.

    The saved token is read back and validated before
    the function reports success.

    The access token is never printed.
    """

    from modules.intraday_zerodha_auth import (
        create_zerodha_session,
    )

    try:

        authentication_result = (
            create_zerodha_session()
        )

    except Exception as error:

        return {
            "Status": "FAILED",
            "Reason": (
                "Zerodha authentication helper failed: "
                + str(error)
            ),
        }

    if authentication_result.get(
        "Status"
    ) != "AUTHENTICATED":

        return authentication_result

    kite = authentication_result.get(
        "Kite"
    )

    if kite is None:

        return {
            "Status": "FAILED",
            "Reason": (
                "Authenticated Kite session "
                "was not returned."
            ),
        }

    access_token = getattr(
        kite,
        "access_token",
        None
    )

    if not access_token:

        return {
            "Status": "FAILED",
            "Reason": (
                "Authenticated access token "
                "was not available."
            ),
        }

    if not save_session(
        access_token
    ):

        return {
            "Status": "FAILED",
            "Reason": (
                "Authenticated session "
                "could not be saved."
            ),
        }

    saved_token = read_session_token()

    if not saved_token:

        return {
            "Status": "FAILED",
            "Reason": (
                "Saved Zerodha session "
                "could not be read back."
            ),
        }

    verified_kite = _build_kite_from_token(
        saved_token
    )

    if verified_kite is None:

        return {
            "Status": "FAILED",
            "Reason": (
                "Saved Zerodha session "
                "could not be revalidated."
            ),
        }

    return {
        "Status": "AUTHENTICATED_AND_VERIFIED",
        "Kite": verified_kite,
    }