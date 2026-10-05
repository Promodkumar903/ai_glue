# ============================================================
# AI GLUE v8.1 — AUTH ENGINE (STRICT RBAC + SECURE REGISTER)
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
    role: Optional[str] = "STUDENT"

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: Optional[str] = "STUDENT"

# ---------- Helpers ----------
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))

SIGNUP_ROLES = ["STUDENT", "JOB_SEEKER", "AGENT", "BROKER", "EMPLOYER"]

VALID_ROLES = [
    "STUDENT", "JOB_SEEKER", "AGENT", "BROKER", "RECRUITER", "EMPLOYER",
    "ADMIN", "SUB_ADMIN",
    "BROKER_OWNER", "BROKER_MANAGER", "BROKER_AGENT",
    "ORG_OWNER", "ORG_ADMIN", "ADMISSIONS_OFFICER",
    "SYSTEM_OWNER", "GOVERNANCE_ADMIN", "OPERATIONS_ADMIN",
    "SECURITY_ADMIN", "FINANCE_ADMIN", "SUPPORT_ADMIN",
    "VENDOR_ADMIN", "EDU_ADMIN", "JOB_ADMIN"
]

# ---------- Register (Signup Whitelist) ----------
@router.post("/register", response_model=dict)
def register_user(
    user_data: UserCreate,
    role: str = "STUDENT",
    session: Session = Depends(db.get_session)
):
    """Register — only public roles. Admin signup BLOCKED."""
    selected_role = (role or "STUDENT").upper().strip()
    if selected_role not in SIGNUP_ROLES:
        selected_role = "STUDENT"

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

    user_role = UserRole(user_id=new_user.id, role_code=selected_role)
    session.add(user_role)
    session.commit()

    return {
        "id": new_user.id,
        "email": new_user.email,
        "role": selected_role,
        "message": "User registered successfully"
    }

# ---------- Login (Strict Role Check) ----------
@router.post("/login", response_model=TokenResponse)
async def login_user(request: Request, session: Session = Depends(db.get_session)):
    """Login — user ke paas selected role HONA chahiye."""
    try:
        body = await request.json()
        email = body.get('email')
        password = body.get('password')
        role = body.get('role', 'STUDENT')
    except Exception:
        email = None
        password = None
        role = 'STUDENT'

    if not email:
        email = request.query_params.get('email')
    if not password:
        password = request.query_params.get('password')
    if not role:
        role = request.query_params.get('role', 'STUDENT')

    if not email or not password:
        raise HTTPException(status_code=422, detail="Email and password required")

    role = (role or 'STUDENT').upper()
    if role not in VALID_ROLES:
        role = 'STUDENT'

    user = session.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if user.status != 'ACTIVE':
        raise HTTPException(status_code=403, detail="Account is not active")

    # STRICT ROLE CHECK
    has_role = session.query(UserRole).filter(
        UserRole.user_id == user.id,
        UserRole.role_code == role
    ).first()

    if not has_role:
        all_roles = session.query(UserRole).filter(UserRole.user_id == user.id).all()
        assigned = [r.role_code for r in all_roles]
        raise HTTPException(
            status_code=403,
            detail=f"Aapka account '{role}' role ke liye register nahi hai. "
                   f"Aap ye roles use kar sakte ho: {', '.join(assigned) if assigned else 'None'}. "
                   f"Sahi role select karo ya naya account banao."
        )

    access_token = create_access_token(data={"sub": user.id, "active_role": role})
    refresh_token = create_refresh_token(data={"sub": user.id, "active_role": role})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "role": role
    }

# ---------- Refresh ----------
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

    new_access = create_access_token(data={"sub": user_id, "active_role": active_role})
    return {
        "access_token": new_access,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "role": active_role
    }

# ---------- Logout ----------
@router.post("/logout")
def logout_user():
    return {"message": "Logged out successfully"}