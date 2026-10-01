# ============================================================
# AI GLUE — USER APP (Authentication Routes)
# ============================================================
# Register, Login, Refresh, Logout, Email Verification.
# All endpoints use AuthEngine.
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, EmailStr
from typing import Optional

from core.database import db
from core.tenant import clear_tenant_context
from core.audit import audit
from auth.auth import AuthEngine
from auth.session import SessionManager

router = APIRouter()

# ---------- Pydantic Schemas ----------
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

class EmailVerifyRequest(BaseModel):
    user_id: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "Bearer"
    expires_in: int
    user: Optional[dict] = None

class MessageResponse(BaseModel):
    message: str

# ---------- Endpoints ----------
@router.post("/register", response_model=MessageResponse)
async def register(request: RegisterRequest):
    """Register a new user (status PENDING until email verification)."""
    try:
        result = AuthEngine.register_user(
            email=request.email,
            password=request.password,
            full_name=request.full_name
        )
        return MessageResponse(message=result["message"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Authenticate user and return JWT tokens."""
    try:
        result = AuthEngine.login_user(
            email=request.email,
            password=request.password
        )
        return TokenResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
            expires_in=result["expires_in"],
            user=result["user"]
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: RefreshRequest):
    """Get a new access token using refresh token."""
    try:
        result = AuthEngine.refresh_access_token(request.refresh_token)
        return TokenResponse(
            access_token=result["access_token"],
            expires_in=result["expires_in"]
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/logout", response_model=MessageResponse)
async def logout(request: Request, user=Depends(SessionManager.get_current_user)):
    """Logout (audit only, client discards tokens)."""
    AuthEngine.logout_user(user.id)
    clear_tenant_context()
    return MessageResponse(message="Logged out successfully")

@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(request: EmailVerifyRequest):
    """Verify user email and set status to ACTIVE."""
    try:
        result = AuthEngine.verify_email(request.user_id)
        return MessageResponse(message=result["message"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me", response_model=dict)
async def get_me(user=Depends(SessionManager.get_current_user)):
    """Get current user profile."""
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "status": user.status,
        "tenant_id": user.tenant_id,
        "created_at": user.created_at.isoformat() if user.created_at else None
    }