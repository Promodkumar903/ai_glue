"""
AI GLUE — Company Engine (Blueprint Section 3.3)
Manages Company/HR operations: Vacancy Post, Applicant Review
With Complete Audit Trail
"""
from sqlalchemy.orm import Session
from core.database import Opportunity, Application, Organization, User
from core.audit import log_audit

class CompanyEngine:
    @staticmethod
    def create_vacancy(organization_id: str, title: str, description: str, requirements: dict, session: Session = None):
        """Create a new vacancy (job/programme)"""
        if session is None:
            from core.database import db
            session = db.get_session()
        
        org = session.query(Organization).filter(Organization.id == organization_id).first()
        if not org:
            return {"error": "Organization not found"}
        
        vacancy = Opportunity(
            organization_id=organization_id,
            type="VACANCY",
            title=title,
            description=description,
            requirements=requirements,
            status="OPEN"
        )
        session.add(vacancy)
        session.commit()
        session.refresh(vacancy)
        
        # ✅ AUDIT LOG
        log_audit(
            actor_id=None,  # Will be set by caller
            action="VACANCY_CREATE",
            target_type="OPPORTUNITY",
            target_id=str(vacancy.id),
            after={"title": title, "status": "OPEN"},
            reason="Vacancy created by company"
        )
        
        return {"vacancy_id": str(vacancy.id), "title": vacancy.title, "status": vacancy.status, "message": "Vacancy created"}

    @staticmethod
    def get_applicants(vacancy_id: str, session: Session = None):
        """Get all applicants for a specific vacancy"""
        if session is None:
            from core.database import db
            session = db.get_session()
        
        apps = session.query(Application).filter(Application.opportunity_id == vacancy_id).all()
        result = []
        for app in apps:
            user = session.query(User).filter(User.id == app.candidate_id).first()
            result.append({
                "application_id": str(app.id),
                "candidate_id": str(app.candidate_id),
                "candidate_name": user.full_name if user else "Unknown",
                "email": user.email if user else "Unknown",
                "status": app.status,
                "submitted_at": app.submitted_at
            })
        return {"applicants": result}

    @staticmethod
    def update_applicant_status(application_id: str, new_status: str, session: Session = None):
        """Update applicant status (shortlist, interview, offer, reject)"""
        if session is None:
            from core.database import db
            session = db.get_session()
        
        app = session.query(Application).filter(Application.id == application_id).first()
        if not app:
            return {"error": "Application not found"}
        
        allowed = ["SHORTLISTED", "INTERVIEW", "OFFERED", "JOINED", "REJECTED"]
        if new_status not in allowed:
            return {"error": f"Invalid status. Allowed: {allowed}"}
        
        old_status = app.status
        app.status = new_status
        session.commit()
        
        # ✅ AUDIT LOG
        log_audit(
            actor_id=None,
            action="APPLICANT_STATUS_UPDATE",
            target_type="APPLICATION",
            target_id=str(app.id),
            before={"status": old_status},
            after={"status": new_status},
            reason=f"Applicant status updated by company to {new_status}"
        )
        
        return {
            "application_id": str(application_id),
            "candidate_id": str(app.candidate_id),
            "status": new_status,
            "message": f"Status updated to {new_status}"
        }

# Singleton
company = CompanyEngine()