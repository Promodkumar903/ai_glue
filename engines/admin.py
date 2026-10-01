"""
AI GLUE — Admin Engine (Blueprint Section 3.4)
War Room: System Health, Metrics, Governance, Audit
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from core.database import (
    db, User, Organization, Application, Offer, AuditEvent, Connector,
    UserRole, Payment
)
from core.audit import log_audit


class AdminEngine:

    @staticmethod
    def get_users(session=None):
        _auto_close = session is None
        if session is None:
            session = db.get_session()
        try:
            users = session.query(User).all()
            result = []
            for u in users:
                roles = session.query(UserRole).filter(UserRole.user_id == u.id).all()
                role_codes = [r.role_code for r in roles if r.revoked_at is None]
                result.append({
                    "id": u.id,
                    "email": u.email,
                    "full_name": u.full_name,
                    "phone": u.phone,
                    "status": u.status,
                    "created_at": str(u.created_at) if u.created_at else None,
                    "roles": role_codes,
                    "role": role_codes[0] if role_codes else None,
                })
            return result
        finally:
            if _auto_close:
                session.close()

    @staticmethod
    def update_user_status(user_id: str, status: str, session: Session = None):
        _auto_close = session is None
        if session is None:
            session = db.get_session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return {"error": "User not found"}
            user.status = status
            session.commit()
            log_audit(session, user_id, "UPDATE_STATUS", "USER", user_id, after={"status": status})
            return {"message": f"User status updated to {status}"}
        finally:
            if _auto_close:
                session.close()

    @staticmethod
    def assign_role(user_id: str, role_code: str, session: Session = None):
        _auto_close = session is None
        if session is None:
            session = db.get_session()
        try:
            existing = session.query(UserRole).filter(
                UserRole.user_id == user_id,
                UserRole.role_code == role_code,
                UserRole.revoked_at == None
            ).first()
            if existing:
                return {"message": "Role already assigned"}

            ur = UserRole(user_id=user_id, role_code=role_code)
            session.add(ur)
            session.commit()
            log_audit(session, user_id, "ASSIGN_ROLE", "USER", user_id, after={"role_code": role_code})
            return {"message": f"Role {role_code} assigned"}
        finally:
            if _auto_close:
                session.close()

    @staticmethod
    def get_organizations(session: Session = None):
        _auto_close = session is None
        if session is None:
            session = db.get_session()
        try:
            orgs = session.query(Organization).all()
            return [
                {
                    "id": o.id,
                    "name": o.name,
                    "type": o.type,
                    "verification_status": o.verification_status,
                    "created_at": str(o.created_at) if o.created_at else None,
                }
                for o in orgs
            ]
        finally:
            if _auto_close:
                session.close()

    @staticmethod
    def verify_organization(org_id: str, status: str, session: Session = None):
        _auto_close = session is None
        if session is None:
            session = db.get_session()
        try:
            org = session.query(Organization).filter(Organization.id == org_id).first()
            if not org:
                return {"error": "Organization not found"}
            org.verification_status = status
            session.commit()
            log_audit(session, None, "VERIFY_ORG", "ORGANIZATION", org_id, after={"status": status})
            return {"message": f"Organization {status}"}
        finally:
            if _auto_close:
                session.close()

    @staticmethod
    def get_connectors(session: Session = None):
        _auto_close = session is None
        if session is None:
            session = db.get_session()
        try:
            connectors = session.query(Connector).all()
            return [
                {
                    "id": c.id,
                    "name": c.name,
                    "type": c.type,
                    "created_at": str(c.created_at) if c.created_at else None,
                }
                for c in connectors
            ]
        finally:
            if _auto_close:
                session.close()

    @staticmethod
    def update_connector_status(connector_id: str, status: str, session: Session = None):
        _auto_close = session is None
        if session is None:
            session = db.get_session()
        try:
            connector = session.query(Connector).filter(Connector.id == connector_id).first()
            if not connector:
                return {"error": "Connector not found"}
            connector.config = status
            session.commit()
            return {"message": "Connector updated"}
        finally:
            if _auto_close:
                session.close()

    @staticmethod
    def get_payment_summary(session: Session = None):
        _auto_close = session is None
        if session is None:
            session = db.get_session()
        try:
            total = session.query(func.sum(Payment.amount)).scalar() or 0
            count = session.query(Payment).count()
            return {
                "total_revenue": float(total),
                "total_transactions": count,
            }
        finally:
            if _auto_close:
                session.close()

    @staticmethod
    def get_audit_logs(session: Session = None):
        _auto_close = session is None
        if session is None:
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
                }
                for l in logs
            ]
        finally:
            if _auto_close:
                session.close()

    @staticmethod
    def get_live_metrics(session: Session = None):
        _auto_close = session is None
        if session is None:
            session = db.get_session()
        try:
            total_users = session.query(User).count()
            active_users = session.query(User).filter(User.status == 'ACTIVE').count()
            total_orgs = session.query(Organization).count()
            total_apps = session.query(Application).count()
            total_offers = session.query(Offer).count()

            revenue = session.query(func.sum(Payment.amount)).scalar() or 0

            return {
                "total_users": total_users,
                "active_users": active_users,
                "total_organizations": total_orgs,
                "total_applications": total_apps,
                "total_offers": total_offers,
                "total_revenue": float(revenue),
                "placements": total_offers,
            }
        finally:
            if _auto_close:
                session.close()


admin = AdminEngine()