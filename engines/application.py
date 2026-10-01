# ============================================================
# AI GLUE — APPLICATION ENGINE
# ============================================================
# Create, submit, track applications
# ============================================================

from sqlalchemy.orm import Session
from core.database import Application, Case, db
from core.audit import audit
import uuid

class ApplicationEngine:
    @staticmethod
    def create_application(candidate_id: str, opportunity_id: str, broker_id: str = None, session: Session = None):
        if session is None:
            session = db.get_session()
        
        app = Application(
            id=str(uuid.uuid4()),
            candidate_id=candidate_id,
            opportunity_id=opportunity_id,
            broker_id=broker_id,
            status="DRAFT"
        )
        session.add(app)
        session.commit()
        
        audit.log_event(
            actor_id=candidate_id,
            action="APPLICATION_CREATED",
            target_type="Application",
            target_id=app.id,
            after={"status": "DRAFT"}
        )
        return app

    @staticmethod
    def submit_application(application_id: str, session: Session = None):
        if session is None:
            session = db.get_session()
        
        app = session.query(Application).filter(Application.id == application_id).first()
        if not app:
            raise ValueError("Application not found")
        if app.status != "DRAFT":
            raise ValueError("Application already submitted")
        
        app.status = "SUBMITTED"
        app.submitted_at = db.now_utc()
        session.commit()
        
        audit.log_event(
            actor_id=app.candidate_id,
            action="APPLICATION_SUBMITTED",
            target_type="Application",
            target_id=app.id,
            before={"status": "DRAFT"},
            after={"status": "SUBMITTED"}
        )
        return app

    @staticmethod
    def get_application_status(application_id: str, session: Session = None):
        if session is None:
            session = db.get_session()
        app = session.query(Application).filter(Application.id == application_id).first()
        return app

application = ApplicationEngine()