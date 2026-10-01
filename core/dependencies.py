# ============================================================
# AI GLUE v8.0 — DEPENDENCIES (Auth + RBAC with JWT Active Role)
# ============================================================
# Purpose: FastAPI dependencies for authentication and authorization.
# Uses JWT 'active_role' claim (set during login) for RBAC checks.
# ============================================================

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from core.database import db
from core.rbac import rbac
from auth.session import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(db.get_session_dep),
):
    """Extract current user from JWT token."""
    from core.database import User
    payload = verify_token(token)
    if "error" in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=payload["error"])

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


def get_current_user_roles(
    user=Depends(get_current_user),
    session: Session = Depends(db.get_session_dep),
):
    """Get roles for the current user (from database — for backward compatibility)."""
    from core.database import UserRole
    roles = session.query(UserRole.role_code).filter(UserRole.user_id == user.id).all()
    return [r[0] for r in roles]


def require_permission(resource: str, action: str, scope: str = "SELF"):
    """
    Dependency factory to check RBAC permissions.

    Uses 'active_role' from JWT (set during login by Frontend's selected Role).
    This allows one user to have multiple roles and switch between them.

    Usage: Depends(require_permission("USER_ADMIN", "READ", "SYSTEM"))
    """
    def permission_dependency(
        token: str = Depends(oauth2_scheme),
        session: Session = Depends(db.get_session_dep),
    ):
        from core.database import User

        # 1. Verify Token
        payload = verify_token(token)
        if "error" in payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=payload["error"],
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )

        # 2. JWT se 'active_role' nikaalo (Frontend's selected role)
        active_role = payload.get("active_role", "STUDENT")

        # 3. User fetch karo
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        # 4. RBAC Check — sirf Active Role ki Permission
        if not rbac.has_permission([active_role], resource, action, scope):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied for {action} on {resource} (scope: {scope}, role: {active_role})",
            )

        return user

    return permission_dependency