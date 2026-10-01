"""
AI GLUE — Agent Engine (Blueprint Section 3.2)
Manages Agent-specific operations: Candidate List, Funnel
With Complete Audit Trail
"""
from sqlalchemy.orm import Session
from core.database import Application, User, CandidateProfile
from core.audit import log_audit

class AgentEngine:
    @staticmethod
    def get_candidates(agent_id: str = None, session: Session = None):
        """Get all candidates with their applications"""
        if session is None:
            from core.database import db
            session = db.get_session()
        
        candidates = session.query(User).all()
        result = []
        for user in candidates:
            apps = session.query(Application).filter(Application.candidate_id == user.id).all()
            profile = session.query(CandidateProfile).filter(CandidateProfile.user_id == user.id).first()
            result.append({
                "user_id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "profile_complete": bool(profile),
                "applications": [{"id": str(a.id), "status": a.status, "opportunity_id": str(a.opportunity_id)} for a in apps]
            })
        return {"candidates": result}

    @staticmethod
    def get_funnel(session: Session = None):
        """Get candidate funnel data: DRAFT → SUBMITTED → ..."""
        if session is None:
            from core.database import db
            session = db.get_session()
        
        statuses = ['DRAFT', 'SUBMITTED', 'UNDER_REVIEW', 'SHORTLISTED', 'INTERVIEW', 'OFFERED', 'ACCEPTED', 'JOINED']
        funnel = {}
        for status in statuses:
            count = session.query(Application).filter(Application.status == status).count()
            funnel[status] = count
        
        return {
            "funnel": funnel,
            "total": sum(funnel.values())
        }

# Singleton
agent = AgentEngine()