# ============================================================
# AI GLUE v8.0 — AUTH ENGINE (FINAL WORKING WITH ROLE)
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
import bcrypt
from datetime import timedelta

from core.database import db, User, UserRole
from core.security import PasswordPolicy
from auth.session import create_access_token, create_refresh_token, verify_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ---------- Pydantic Models ----------
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    role: Optional[str] = "STUDENT"   # ✅ Frontend से Role आएगा

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

# ---------- Helper Functions ----------
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))

# Valid Roles List
VALID_ROLES = ["STUDENT", "JOB_SEEKER", "AGENT", "BROKER", "RECRUITER", "EMPLOYER", "ADMIN",
               "BROKER_OWNER", "BROKER_MANAGER", "BROKER_AGENT",
               "ORG_OWNER", "ORG_ADMIN", "ADMISSIONS_OFFICER",
               "SYSTEM_OWNER", "GOVERNANCE_ADMIN", "OPERATIONS_ADMIN",
               "SECURITY_ADMIN", "FINANCE_ADMIN", "SUPPORT_ADMIN"]

# ---------- Register Endpoint ----------
@router.post("/register", response_model=dict)
def register_user(user_data: UserCreate, session: Session = Depends(db.get_session)):
    """Register a new user."""
    existing = session.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    is_valid, msg = PasswordPolicy.validate(user_data.password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=msg)

    hashed = hash_password(user_data.password)
    new_user = User(
        email=user_data.email,
        password_hash=hashed,
        full_name=user_data.full_name,
        phone=user_data.phone,
        status='ACTIVE'
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    # Default role — STUDENT
    default_role = UserRole(user_id=new_user.id, role_code='STUDENT')
    session.add(default_role)
    session.commit()

    return {"id": new_user.id, "email": new_user.email, "message": "User registered successfully"}

# ---------- Login Endpoint (with Role) ----------
@router.post("/login", response_model=TokenResponse)
async def login_user(request: Request, session: Session = Depends(db.get_session)):
    """
    Login with email + password + optional role.
    The selected role is embedded in the JWT as 'active_role'.
    RBAC will use this role for permission checks.
    """
    # Parse Body — JSON या Query Params
    try:
        body = await request.json()
        email = body.get('email')
        password = body.get('password')
        role = body.get('role', 'STUDENT')
    except:
        email = None
        password = None
        role = 'STUDENT'

    # Fallback to query parameters
    if not email:
        email = request.query_params.get('email')
    if not password:
        password = request.query_params.get('password')
    if not role:
        role = request.query_params.get('role', 'STUDENT')

    if not email or not password:
        raise HTTPException(status_code=422, detail="Email and password required")

    # Validate role
    role = role.upper()
    if role not in VALID_ROLES:
        role = 'STUDENT'   # Fallback to STUDENT if invalid role

    user = session.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if user.status != 'ACTIVE':
        raise HTTPException(status_code=403, detail="Account is not active")

    # ✅ JWT में active_role Embed करो
    access_token = create_access_token(data={"sub": user.id, "active_role": role})
    refresh_token = create_refresh_token(data={"sub": user.id, "active_role": role})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

# ---------- Refresh & Logout ----------
@router.post("/refresh", response_model=TokenResponse)
def refresh_access_token(refresh_token: str, session: Session = Depends(db.get_session)):
    payload = verify_token(refresh_token)
    if "error" in payload:
        raise HTTPException(status_code=401, detail=payload["error"])
    user_id = payload.get("sub")
    active_role = payload.get("active_role", "STUDENT")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # ✅ Role Preserve करो
    new_access = create_access_token(data={"sub": user_id, "active_role": active_role})
    return {"access_token": new_access, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/logout")
def logout_user():
    return {"message": "Logged out successfully"}