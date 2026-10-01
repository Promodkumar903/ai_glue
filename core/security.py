# ============================================================
# AI GLUE v8.0 — SECURITY ENGINE
# ============================================================
# Purpose: Password Policy, Rate Limiting, Security Headers
# ============================================================

import re
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# ---------- Rate Limiter ----------
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

# ---------- Password Policy ----------
class PasswordPolicy:
    @staticmethod
    def validate(password: str) -> tuple:
        if len(password) < 8:
            return False, "Password must be at least 8 characters long."
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter."
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter."
        if not re.search(r'[0-9]', password):
            return False, "Password must contain at least one digit."
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character."
        return True, "Password is valid."

# ---------- Secure Headers Middleware (Placeholder) ----------
class SecureHeadersMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # Minimal: just pass through
        await self.app(scope, receive, send)