"""
AI GLUE — Document Lifecycle (Expiry Tracking)
"""
from sqlalchemy.orm import Session
from core.database import db, Document
from datetime import datetime, timedelta
from core.audit import log_audit

class DocumentLifecycle:
    @staticmethod
    def check_expiry(document_id: str, session: Session = None):
        """Check expiry status of a document."""
        if session is None:
            session = db.get_session()
        
        doc = session.query(Document).filter(Document.id == document_id).first()
        if not doc:
            return {"error": "Document not found"}
        
        if not doc.expiry_date:
            return {"document_id": str(doc.id), "expiry_date": None, "days_left": None, "expired": False}
        
        days_left = (doc.expiry_date - datetime.utcnow()).days
        expired = days_left < 0
        
        return {
            "document_id": str(doc.id),
            "expiry_date": doc.expiry_date,
            "days_left": days_left,
            "expired": expired
        }

    @staticmethod
    def set_expiry(document_id: str, expiry_date: str, session: Session = None):
        """Set expiry date for a document."""
        if session is None:
            session = db.get_session()
        
        doc = session.query(Document).filter(Document.id == document_id).first()
        if not doc:
            return {"error": "Document not found"}
        
        try:
            expiry_dt = datetime.fromisoformat(expiry_date.replace('Z', '+00:00'))
        except:
            return {"error": "Invalid date format. Use ISO format (e.g., 2027-12-31T00:00:00)"}
        
        old_expiry = doc.expiry_date
        doc.expiry_date = expiry_dt
        session.commit()
        
        log_audit(
            actor_id=None,
            action="DOCUMENT_EXPIRY_SET",
            target_type="DOCUMENT",
            target_id=str(doc.id),
            before={"expiry_date": old_expiry},
            after={"expiry_date": expiry_dt},
            reason="Document expiry set/updated"
        )
        
        return {
            "document_id": str(doc.id),
            "expiry_date": expiry_dt,
            "message": "Expiry date set successfully"
        }

    @staticmethod
    def get_expiring_documents(days_threshold: int = 30, session: Session = None):
        """Get all documents expiring within the next N days."""
        if session is None:
            session = db.get_session()
        
        threshold_date = datetime.utcnow() + timedelta(days=days_threshold)
        docs = session.query(Document).filter(
            Document.expiry_date.isnot(None),
            Document.expiry_date <= threshold_date
        ).all()
        
        return {"expiring_documents": [
            {
                "id": str(d.id),
                "type": d.type,
                "owner_id": str(d.owner_id),
                "expiry_date": d.expiry_date,
                "days_left": (d.expiry_date - datetime.utcnow()).days
            } for d in docs
        ]}

document_lifecycle = DocumentLifecycle()