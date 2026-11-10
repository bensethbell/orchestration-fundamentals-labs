"""Who is making this request? A stand-in for real login, for the labs only.

API calls (curl) identify the user with an X-User-Id header. The browser
identifies the user with a session cookie set by visiting /login/<user_id>.
The header wins if both are present.
"""
from flask import request, session


def get_current_user_id():
    """Return the current user's id as an int, or None if nobody is identified."""
    header_value = request.headers.get("X-User-Id")
    if header_value is not None:
        try:
            return int(header_value)
        except ValueError:
            return None
    session_value = session.get("user_id")
    if session_value is not None:
        return int(session_value)
    return None


def set_current_user_id(user_id):
    session["user_id"] = user_id
