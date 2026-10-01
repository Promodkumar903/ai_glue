# ============================================================
# AI GLUE v8.0 — SESSION & JWT ENGINE (WITH ROLE SUPPORT)
# ============================================================
# Purpose: Create and verify JWT access/refresh tokens
# Note: JWT includes 'active_role' claim for RBAC permission checks
# ============================================================

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext

# ---------- Configuration ----------
SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 30))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', 7))

# ---------- Password Context (if needed) ----------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a new JWT access token.
    
    Expected data fields:
      - sub: User ID
      - active_role: Role selected during login (STUDENT/BROKER/ADMIN/etc.)
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a new JWT refresh token (longer expiry)."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
    """
    Verify and decode JWT token.
    
    Args:
        token: JWT string
        token_type: "access" or "refresh" — validate matching type
    
    Returns:
        payload dict with keys: sub, active_role, exp, type
        OR {'error': message} on failure
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Validate token type
        if payload.get("type") != token_type:
            return {"error": f"Invalid token type. Expected {token_type}, got {payload.get('type')}"}
        
        return payload
    except JWTError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Token verification failed: {str(e)}"}


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Alias for verify_token that returns None on error (deprecated)."""
    result = verify_token(token)
    if "error" in result:
        return None
    return result