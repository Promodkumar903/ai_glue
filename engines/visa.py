"""
AI GLUE — Visa Engine (Blueprint Section 6)
With Complete Audit Trail
"""
from sqlalchemy.orm import Session
from core.database import db, VisaCase, VisaAppointment, User, AuditEvent
from datetime import datetime
import uuid
from core.audit import log_audit

class VisaEngine:

    @staticmethod
    def create_visa_case(user_id: str, country: str, visa_type: str, application_id: str = None, session: Session = None):
        """Create a new visa case (status: NOT_STARTED)"""
        if session is None:
            session = db.get_session()
        
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "User not found"}
        
        visa_case = VisaCase(
            candidate_id=user_id,
            country=country,
            visa_type=visa_type,
            status="NOT_STARTED"
        )
        session.add(visa_case)
        session.commit()
        session.refresh(visa_case)
        
        log_audit(
            actor_id=user_id,
            action="VISA_CASE_CREATE",
            target_type="VISA_CASE",
            target_id=str(visa_case.id),
            after={"status": "NOT_STARTED", "country": country, "visa_type": visa_type},
            reason="Visa case created"
        )
        
        return {
            "visa_case_id": str(visa_case.id),
            "status": visa_case.status,
            "message": "Visa case created successfully"
        }

    @staticmethod
    def update_visa_status(visa_case_id: str, new_status: str, session: Session = None):
        """Update visa case status"""
        if session is None:
            session = db.get_session()
        
        visa_case = session.query(VisaCase).filter(VisaCase.id == visa_case_id).first()
        if not visa_case:
            return {"error": "Visa case not found"}
        
        allowed_statuses = [
            "NOT_STARTED", "DOCUMENTS_PENDING", "APPLIED",
            "INTERVIEW", "APPROVED", "REJECTED", "APPEALING"
        ]
        if new_status not in allowed_statuses:
            return {"error": f"Invalid status. Allowed: {allowed_statuses}"}
        
        old_status = visa_case.status
        visa_case.status = new_status
        if new_status == "APPLIED":
            visa_case.applied_at = datetime.utcnow()
        if new_status in ["APPROVED", "REJECTED"]:
            visa_case.decision_at = datetime.utcnow()
        session.commit()
        
        log_audit(
            actor_id=visa_case.candidate_id,
            action="VISA_STATUS_UPDATE",
            target_type="VISA_CASE",
            target_id=str(visa_case.id),
            before={"status": old_status},
            after={"status": new_status},
            reason=f"Visa status updated to {new_status}"
        )
        
        return {
            "visa_case_id": str(visa_case.id),
            "status": visa_case.status,
            "message": f"Status updated to {new_status}"
        }

    @staticmethod
    def get_visa_status(visa_case_id: str, session: Session = None):
        """Get visa case details"""
        if session is None:
            session = db.get_session()
        
        visa_case = session.query(VisaCase).filter(VisaCase.id == visa_case_id).first()
        if not visa_case:
            return {"error": "Visa case not found"}
        
        return {
            "visa_case_id": str(visa_case.id),
            "candidate_id": visa_case.candidate_id,
            "country": visa_case.country,
            "visa_type": visa_case.visa_type,
            "status": visa_case.status,
            "applied_at": visa_case.applied_at,
            "decision_at": visa_case.decision_at,
            "created_at": visa_case.created_at
        }

    @staticmethod
    def get_document_checklist(country: str, visa_type: str, session: Session = None):
        """Get document checklist for a specific country and visa type"""
        checklist = {
            "Germany": {
                "Student": ["Passport", "Admission Letter", "Financial Proof", "Health Insurance", "Visa Application Form"],
                "Work": ["Passport", "Employment Contract", "Financial Proof", "Health Insurance", "Visa Application Form"]
            },
            "Canada": {
                "Student": ["Passport", "Letter of Acceptance", "Proof of Funds", "Medical Exam", "Visa Application Form"],
                "Work": ["Passport", "Job Offer", "Proof of Funds", "Medical Exam", "Visa Application Form"]
            }
        }
        items = checklist.get(country, {}).get(visa_type, ["Passport", "Visa Application Form"])
        return {"country": country, "visa_type": visa_type, "checklist": items}

    @staticmethod
    def create_appointment(visa_case_id: str, scheduled_at: str, location: str, session: Session = None):
        """Create an appointment for a visa case"""
        if session is None:
            session = db.get_session()
        
        visa_case = session.query(VisaCase).filter(VisaCase.id == visa_case_id).first()
        if not visa_case:
            return {"error": "Visa case not found"}
        
        try:
            scheduled_dt = datetime.fromisoformat(scheduled_at.replace('Z', '+00:00'))
        except:
            return {"error": "Invalid datetime format. Use ISO format (e.g., 2026-09-15T10:00:00)"}
        
        appointment = VisaAppointment(
            visa_case_id=visa_case_id,
            scheduled_at=scheduled_dt,
            location=location,
            status="SCHEDULED"
        )
        session.add(appointment)
        session.commit()
        session.refresh(appointment)
        
        log_audit(
            actor_id=visa_case.candidate_id,
            action="VISA_APPOINTMENT_CREATE",
            target_type="VISA_APPOINTMENT",
            target_id=str(appointment.id),
            after={"scheduled_at": str(scheduled_dt), "location": location},
            reason="Visa appointment created"
        )
        
        return {
            "appointment_id": str(appointment.id),
            "visa_case_id": visa_case_id,
            "scheduled_at": appointment.scheduled_at,
            "location": appointment.location,
            "status": appointment.status,
            "message": "Appointment created successfully"
        }

    @staticmethod
    def get_visa_funnel(session: Session = None):
        """Get visa case status counts (funnel)"""
        if session is None:
            session = db.get_session()
        
        statuses = ["NOT_STARTED", "DOCUMENTS_PENDING", "APPLIED", "INTERVIEW", "APPROVED", "REJECTED", "APPEALING"]
        funnel = {}
        for status in statuses:
            count = session.query(VisaCase).filter(VisaCase.status == status).count()
            funnel[status] = count
        return {"visa_funnel": funnel, "total": sum(funnel.values())}

    @staticmethod
    def get_all_visa_cases(session: Session = None):
        """Get all visa cases for embassy officer view"""
        if session is None:
            session = db.get_session()
        
        try:
            cases = session.query(VisaCase).all()
            result = []
            for c in cases:
                user = session.query(User).filter(User.id == c.candidate_id).first()
                result.append({
                    "id": str(c.id),
                    "candidate_id": str(c.candidate_id),
                    "candidate_name": user.full_name if user else "Unknown",
                    "country": c.country,
                    "visa_type": c.visa_type,
                    "status": c.status,
                    "applied_at": c.applied_at,
                    "decision_at": c.decision_at
                })
            return {"visa_cases": result}
        except Exception as e:
            return {"error": str(e), "visa_cases": []}

# Singleton
visa = VisaEngine()