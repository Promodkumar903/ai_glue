# ============================================================
# AI GLUE v8.0 — ADMIN ROUTER (Fixed)
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

from core.database import db, User, UserRole, Organization, Connector, AuditEvent, Payment
from auth.session import verify_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ---------- Dependencies ----------
def get_current_user(token: str = Depends(oauth2_scheme)):
    """Extract current user from Bearer token."""
    payload = verify_token(token)
    if "error" in payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    session = db.get_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    finally:
        session.close()


def require_admin(user: User = Depends(get_current_user)):
    """Check if user has ADMIN role."""
    session = db.get_session()
    try:
        roles = session.query(UserRole.role_code).filter(UserRole.user_id == user.id).all()
        role_codes = [r[0] for r in roles]
        if "ADMIN" not in role_codes:
            raise HTTPException(status_code=403, detail="Admin access required")
        return user
    finally:
        session.close()


# ---------- Endpoints ----------
@router.get("/users", response_model=list)
def admin_get_users(admin: User = Depends(require_admin)):
    session = db.get_session()
    try:
        users = session.query(User).all()
        return [
            {"id": u.id, "email": u.email, "full_name": u.full_name,
             "status": u.status, "created_at": str(u.created_at) if u.created_at else None}
            for u in users
        ]
    finally:
        session.close()


@router.get("/organizations", response_model=list)
def admin_get_orgs(admin: User = Depends(require_admin)):
    session = db.get_session()
    try:
        orgs = session.query(Organization).all()
        return [
            {"id": o.id, "name": o.name, "type": o.type,
             "verification_status": o.verification_status}
            for o in orgs
        ]
    finally:
        session.close()


@router.get("/connectors", response_model=list)
def admin_get_connectors(admin: User = Depends(require_admin)):
    """Get all connectors — with demo fallback."""
    session = db.get_session()
    try:
        conns = session.query(Connector).all()
        if not conns:
            return [
                {"id": "1", "name": "Germany Visa API", "status": "DOWN", "country": "Germany"},
                {"id": "2", "name": "Canada IRCC", "status": "HEALTHY", "country": "Canada"},
                {"id": "3", "name": "UK Visa Portal", "status": "HEALTHY", "country": "UK"},
                {"id": "4", "name": "AI Model API", "status": "HEALTHY", "country": None},
                {"id": "5", "name": "Payment Gateway", "status": "DEGRADED", "country": None},
            ]
        return [
            {"id": c.id, "name": c.name, "type": c.type, "status": c.status}
            for c in conns
        ]
    finally:
        session.close()


@router.get("/audit", response_model=list)
def admin_audit_logs(admin: User = Depends(require_admin)):
    session = db.get_session()
    try:
        logs = session.query(AuditEvent).order_by(AuditEvent.timestamp.desc()).limit(100).all()
        return [
            {
                "id": l.id,
                "actor_id": l.actor_id,
                "action": l.action,
                "target_type": l.target_type,
                "target_id": l.target_id,
                "timestamp": str(l.timestamp) if l.timestamp else None,
                "reason": l.reason
            }
            for l in logs
        ]
    finally:
        session.close()