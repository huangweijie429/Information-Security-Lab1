"""Security primitives: password hashing, JWT issue/verify (Work 1)."""
import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

ALGORITHM = "HS256"
ISSUER = "hdu-is-lab1"
TOKEN_TTL = timedelta(minutes=int(os.getenv("TOKEN_TTL_MIN", "30")))


def _secret() -> str:
    # Demo default only (>= 32 bytes so PyJWT does not warn about a short HMAC key);
    # always override with JWT_SECRET outside local experiments.
    return os.getenv("JWT_SECRET", "dev-only-insecure-secret-change-me-0123456789abcdef")


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode()


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode())
    except ValueError:
        return False


def create_token(subject: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + TOKEN_TTL).timestamp()),
        "iss": ISSUER,
    }
    return jwt.encode(payload, _secret(), algorithm=ALGORITHM)


def verify_token(token: str) -> str:
    """Return the subject, or raise jwt.PyJWTError."""
    payload = jwt.decode(
        token,
        _secret(),
        algorithms=[ALGORITHM],
        issuer=ISSUER,
        options={"require": ["exp", "sub"]},
    )
    return str(payload["sub"])
