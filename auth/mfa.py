# ============================================================
# AI GLUE v8.0 — MFA (Multi-Factor Authentication) Engine
# ============================================================
# Purpose: TOTP-based MFA for user accounts
# ============================================================

import pyotp
import base64
import os
from typing import Optional, Tuple

class MFAEngine:
    """Handles TOTP generation, verification, and secret management."""

    @staticmethod
    def generate_secret() -> str:
        """Generate a new TOTP secret key (base32 encoded)."""
        return pyotp.random_base32()

    @staticmethod
    def get_otp_uri(secret: str, email: str, issuer: str = "AI Glue") -> str:
        """Generate provisioning URI for QR code."""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=email, issuer_name=issuer)

    @staticmethod
    def verify_code(secret: str, code: str) -> bool:
        """Verify a TOTP code against the secret."""
        totp = pyotp.TOTP(secret)
        return totp.verify(code)

    @staticmethod
    def get_current_code(secret: str) -> str:
        """Get current TOTP code (for testing)."""
        totp = pyotp.TOTP(secret)
        return totp.now()

# Singleton instance
mfa = MFAEngine()