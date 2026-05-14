"""
Tiện ích cho Google OAuth2 + Gmail API.
Thiết lập biến môi trường: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, FRONTEND_URL (ví dụ: http://localhost:3000).
"""
import os
from urllib.parse import urlencode

# Google may return a broader scope set when the user has previously consented to
# additional permissions (e.g. Gmail access). Relax scope validation so login
# still succeeds when the returned scope is a superset of the requested scopes.
os.environ.setdefault("OAUTHLIB_RELAX_TOKEN_SCOPE", "1")

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/auth/google/callback")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Login uses only basic profile/email scopes.
# Gmail read access is requested separately when using the Gmail scan feature.
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]


def get_google_login_url(state: str = "") -> str:
    """Build Google OAuth2 authorization URL."""
    base = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "select_account consent",
        "include_granted_scopes": "true",
    }
    if state:
        params["state"] = state
    return f"{base}?{urlencode(params)}"


def is_google_configured() -> bool:
    return bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)
