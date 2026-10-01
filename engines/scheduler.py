"""
AI GLUE — Scheduler / Background Jobs Engine
"""
from sqlalchemy.orm import Session
from core.database import db, ScheduledJob, Document, Application, VisaCase
from datetime import datetime, timedelta
from core.audit import log_audit

class SchedulerEngine:
    @staticmethod
    def schedule_job(job_type: str, target_id: str, scheduled_at: datetime, payload: dict = None, session: Session = None):
        if session is None:
            session = db.get_session()
        
        job = ScheduledJob(
            job_type=job_type,
            target_id=target_id,
            scheduled_at=scheduled_at,
            payload=payload or {},
            status="PENDING"
        )
        session.add(job)
        session.commit()
        session.refresh(job)
        return {"job_id": str(job.id), "scheduled_at": job.scheduled_at}

    @staticmethod
    def execute_pending_jobs(session: Session = None):
        """Run all pending jobs due now."""
        if session is None:
            session = db.get_session()
        
        now = datetime.utcnow()
        jobs = session.query(ScheduledJob).filter(
            ScheduledJob.status == "PENDING",
            ScheduledJob.scheduled_at <= now
        ).all()
        
        results = []
        for job in jobs:
            try:
                # Execute based on job_type
                if job.job_type == "DOCUMENT_EXPIRY":
                    doc = session.query(Document).filter(Document.id == job.target_id).first()
                    if doc and doc.expiry_date and doc.expiry_date < now:
                        # Notify user via notification engine
                        from engines.notification import notification_engine
                        notification_engine.create_notification(
                            user_id=doc.owner_id,
                            event_type="DOCUMENT_EXPIRED",
                            channel="EMAIL",
                            priority="HIGH",
                            content={"subject": "Document Expired", "body": f"Your document {doc.type} has expired."}
                        )
                
                elif job.job_type == "VISA_REMINDER":
                    visa = session.query(VisaCase).filter(VisaCase.id == job.target_id).first()
                    if visa:
                        from engines.notification import notification_engine
                        notification_engine.create_notification(
                            user_id=visa.candidate_id,
                            event_type="VISA_DEADLINE_REMINDER",
                            channel="SMS",
                            priority="HIGH",
                            content={"body": f"Your visa case {visa.id} needs attention."}
                        )
                
                job.status = "EXECUTED"
                job.executed_at = now
                session.commit()
                results.append({"job_id": str(job.id), "status": "EXECUTED"})
            except Exception as e:
                job.status = "FAILED"
                job.retry_count += 1
                session.commit()
                results.append({"job_id": str(job.id), "status": "FAILED", "error": str(e)})
        
        return {"executed": len(results), "results": results}

    @staticmethod
    def get_pending_jobs(session: Session = None, limit: int = 50):
        if session is None:
            session = db.get_session()
        
        jobs = session.query(ScheduledJob).filter(
            ScheduledJob.status == "PENDING"
        ).order_by(ScheduledJob.scheduled_at).limit(limit).all()
        
        return {"pending_jobs": [{"id": str(j.id), "type": j.job_type, "scheduled_at": j.scheduled_at} for j in jobs]}

scheduler = SchedulerEngine()