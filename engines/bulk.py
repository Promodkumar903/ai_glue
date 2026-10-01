"""
AI GLUE — Bulk Operations (CSV Import/Export)
"""
import csv
import io
from sqlalchemy.orm import Session
from core.database import db, User, Application, Opportunity

class BulkEngine:
    @staticmethod
    def export_users_csv(session: Session = None):
        if session is None:
            session = db.get_session()
        
        users = session.query(User).all()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "email", "full_name", "status", "created_at"])
        for u in users:
            writer.writerow([u.id, u.email, u.full_name, u.status, u.created_at])
        return output.getvalue()

    @staticmethod
    def export_applications_csv(session: Session = None):
        if session is None:
            session = db.get_session()
        
        apps = session.query(Application).all()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "candidate_id", "opportunity_id", "status", "submitted_at"])
        for a in apps:
            writer.writerow([a.id, a.candidate_id, a.opportunity_id, a.status, a.submitted_at])
        return output.getvalue()

    @staticmethod
    def import_opportunities_csv(csv_data: str, session: Session = None):
        if session is None:
            session = db.get_session()
        
        reader = csv.DictReader(io.StringIO(csv_data))
        results = []
        for row in reader:
            try:
                opp = Opportunity(
                    organization_id=row.get("organization_id"),
                    type=row.get("type", "VACANCY"),
                    title=row.get("title"),
                    description=row.get("description", ""),
                    requirements={},
                    status=row.get("status", "OPEN")
                )
                session.add(opp)
                results.append({"title": row.get("title"), "status": "SUCCESS"})
            except Exception as e:
                results.append({"title": row.get("title"), "status": "FAILED", "error": str(e)})
        session.commit()
        return {"imported": len([r for r in results if r["status"] == "SUCCESS"]), "results": results}

bulk = BulkEngine()