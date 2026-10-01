# ============================================================
# AI GLUE — SESSION MANAGEMENT
# ============================================================
# Token validation, user context loading, and permission checks.
# Used as middleware for all authenticated routes.
# ============================================================

from typing import Optional
from fastapi import Request, HTTPException, Depends
from sqlalchemy.orm import Session

from core.database import User, db
from core.tenant import set_current_tenant, get_current_tenant
from core.actors import RoleCode, get_actor_type
from core.rbac import PermissionEngine
from core.audit import audit
from auth.auth import AuthEngine

class SessionManager:
    """Manages the current user session from JWT token."""

    @staticmethod
    def get_current_user(request: Request, session: Optional[Session] = None) -> User:
        """Extract user from JWT in Authorization header."""
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

        token = auth_header.split(" ")[1]
        user_id = AuthEngine.verify_token(token)
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        if session is None:
            session = db.get_session()
        user = session.query(User).filter(User.id == user_id).first()
        if not user or user.status in ("LOCKED", "DELETED"):
            raise HTTPException(status_code=403, detail="User account is not active")

        # Set tenant context for auto-filtering (I-08: tenant isolation)
        if user.tenant_id:
            set_current_tenant(user.tenant_id)

        return user

    @staticmethod
    def require_permission(resource: str, action: str, scope: str = "SELF"):
        """Dependency to check permission for current user."""
        def dependency(user: User = Depends(SessionManager.get_current_user)):
            # Get user's roles (for simplicity, we assume user has one primary role)
            # In production, fetch from user_roles table.
            role_code = None  # Placeholder – to be implemented with DB fetch
            if not PermissionEngine.has_permission(role_code, resource, action, scope):
                audit.log_event(
                    actor_id=user.id,
                    action="PERMISSION_DENIED",
                    target_type=resource,
                    after={"requested_action": action, "scope": scope},
                )
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            return user
        return dependency

    @staticmethod
    def get_user_roles(user_id: str, session: Session) -> list:
        """Fetch all roles for a user from database."""
        # Implementation will query user_roles table
        # For now, stub
        return []