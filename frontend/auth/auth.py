# ============================================================
# AI GLUE — AUTHENTICATION ENGINE
# ============================================================
# Registration, Login, JWT Generation/Verification,
# Password Hashing (bcrypt), Email Verification Status.
# ============================================================

import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict
from sqlalchemy.orm import Session

from core.database import User, db
from core.tenant import set_current_tenant
from core.audit import audit
from core.constitution import Constitution

# Load JWT Secret from Environment
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = 7

class AuthEngine:
    """Handles authentication and token lifecycle."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against a hashed password."""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    @classmethod
    def register_user(cls, email: str, password: str, full_name: str, session: Optional[Session] = None) -> Dict:
        """Register a new user (status = PENDING until email verified)."""
        if session is None:
            session = db.get_session()

        # Check if user already exists
        existing = session.query(User).filter(User.email == email).first()
        if existing:
            raise ValueError("User with this email already exists")

        # Hash password
        hashed = cls.hash_password(password)

        # Create user
        user = User(
            email=email,
            password_hash=hashed,
            full_name=full_name,
            status="PENDING"  # Email verification pending
        )
        session.add(user)
        session.commit()

        # Audit log (I-10: every signup is audited)
        audit.log_event(
            actor_id=user.id,
            action="USER_REGISTERED",
            target_type="User",
            target_id=user.id,
            after={"email": email, "status": "PENDING"},
            session=session
        )

        return {
            "user_id": user.id,
            "email": user.email,
            "status": user.status,
            "message": "Registration successful. Please verify your email."
        }

    @classmethod
    def login_user(cls, email: str, password: str, session: Optional[Session] = None) -> Dict:
        """Authenticate user and return access/refresh tokens."""
        if session is None:
            session = db.get_session()

        # Find user
        user = session.query(User).filter(User.email == email).first()
        if not user:
            raise ValueError("Invalid email or password")

        # Check account status
        if user.status == "LOCKED":
            raise ValueError("Account is locked. Contact support.")
        if user.status == "DELETED":
            raise ValueError("Account has been deleted.")
        if user.status == "PENDING":
            raise ValueError("Email not verified. Please verify your email first.")

        # Verify password
        if not cls.verify_password(password, user.password_hash):
            # Increment login attempts (I-01: security)
            user.login_attempts += 1
            if user.login_attempts >= 5:
                user.status = "LOCKED"
                user.locked_until = datetime.utcnow() + timedelta(minutes=15)
                session.commit()
                raise ValueError("Too many failed attempts. Account locked for 15 minutes.")
            session.commit()
            raise ValueError("Invalid email or password")

        # Reset login attempts on success
        user.login_attempts = 0
        user.last_login = datetime.utcnow()
        session.commit()

        # Generate tokens
        access_token = cls._create_token(user.id, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        refresh_token = cls._create_token(user.id, expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))

        # Audit log
        audit.log_event(
            actor_id=user.id,
            action="USER_LOGIN",
            target_type="User",
            target_id=user.id,
            after={"email": user.email, "login_time": datetime.utcnow().isoformat()},
            session=session
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "status": user.status
            }
        }

    @classmethod
    def _create_token(cls, user_id: str, expires_delta: timedelta) -> str:
        """Generate a JWT token."""
        payload = {
            "sub": user_id,
            "exp": datetime.utcnow() + expires_delta,
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    @classmethod
    def verify_token(cls, token: str) -> Optional[str]:
        """Verify JWT and return user_id if valid."""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload.get("sub")
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")

    @classmethod
    def refresh_access_token(cls, refresh_token: str, session: Optional[Session] = None) -> Dict:
        """Generate a new access token using a valid refresh token."""
        user_id = cls.verify_token(refresh_token)
        if not user_id:
            raise ValueError("Invalid refresh token")

        # Check if user still active
        if session is None:
            session = db.get_session()
        user = session.query(User).filter(User.id == user_id).first()
        if not user or user.status in ("LOCKED", "DELETED"):
            raise ValueError("User account is not active")

        new_access_token = cls._create_token(user_id, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        return {
            "access_token": new_access_token,
            "token_type": "Bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }

    @classmethod
    def logout_user(cls, user_id: str, session: Optional[Session] = None) -> None:
        """Logout (audit only – client discards tokens)."""
        if session is None:
            session = db.get_session()
        audit.log_event(
            actor_id=user_id,
            action="USER_LOGOUT",
            target_type="User",
            target_id=user_id,
            session=session
        )

    @classmethod
    def verify_email(cls, user_id: str, session: Optional[Session] = None) -> Dict:
        """Mark user as ACTIVE after email verification."""
        if session is None:
            session = db.get_session()
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        if user.status != "PENDING":
            raise ValueError("Email already verified or account not in pending state")
        user.status = "ACTIVE"
        session.commit()
        audit.log_event(
            actor_id=user_id,
            action="EMAIL_VERIFIED",
            target_type="User",
            target_id=user_id,
            after={"status": "ACTIVE"},
            session=session
        )
        return {"message": "Email verified successfully. You can now log in."}