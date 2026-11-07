"""
Token Utility — Token tạo và xác thực thuần Python stdlib (HMAC-SHA256)
"""
import base64
import hashlib
import hmac
import json
import time

SECRET_KEY = "libmaster_secret_key_change_in_production"
TOKEN_EXPIRY_SECONDS = 86400 * 7  # 7 days


def create_token(payload: dict) -> str:
    body = payload.copy()
    body["exp"] = int(time.time()) + TOKEN_EXPIRY_SECONDS
    encoded_payload = base64.urlsafe_b64encode(json.dumps(body).encode()).decode().rstrip("=")
    signature = hmac.new(SECRET_KEY.encode(), encoded_payload.encode(), hashlib.sha256).hexdigest()
    return f"{encoded_payload}.{signature}"


def verify_token(token: str) -> dict | None:
    # ponytail: upgrade to PyJWT/cryptography if asymmetric signing or public JWKS is needed
    try:
        parts = token.split(".")
        if len(parts) != 2:
            return None
        encoded_payload, signature = parts
        expected_sig = hmac.new(SECRET_KEY.encode(), encoded_payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected_sig):
            return None

        # Pad base64
        rem = len(encoded_payload) % 4
        if rem > 0:
            encoded_payload += "=" * (4 - rem)
        data = json.loads(base64.urlsafe_b64decode(encoded_payload.encode()).decode())
        if data.get("exp", 0) < time.time():
            return None
        return data
    except Exception:
        return None
