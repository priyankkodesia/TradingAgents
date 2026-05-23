"""Session management via signed cookies (itsdangerous)."""

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from fastapi import Request

import os
SECRET_KEY = os.environ.get("HILLTRADE_SECRET_KEY", "hilltrade-web-secret-2026-change-in-prod")
SESSION_COOKIE = "ht_session"
SESSION_MAX_AGE = 8 * 3600  # 8 hours

_signer = URLSafeTimedSerializer(SECRET_KEY)


def make_session_token(user_id: int, username: str) -> str:
    return _signer.dumps({"uid": user_id, "uname": username})


def get_session(request: Request) -> dict | None:
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        return None
    try:
        return _signer.loads(token, max_age=SESSION_MAX_AGE)
    except (BadSignature, SignatureExpired):
        return None
