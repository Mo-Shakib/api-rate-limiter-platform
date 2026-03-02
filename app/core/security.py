import hmac
import secrets
from hashlib import sha256

from app.core.config import settings


def generate_api_key() -> str:
    # plaintext key returned to user ONCE
    # ak_live_ + 40 url-safe chars ~= strong enough for MVP
    return "ak_live_" + secrets.token_urlsafe(30)


def api_key_prefix(key: str, n: int = 12) -> str:
    # store a short prefix for display/search (never enough to recreate the key)
    return key[:n]


def hash_api_key(key: str) -> str:
    # HMAC with app secret ("pepper") so DB leak doesn't reveal keys
    digest = hmac.new(settings.APP_SECRET.encode("utf-8"), key.encode("utf-8"), sha256).hexdigest()
    return digest