"""
AI GLUE — Reporting & Analytics Engine
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from core.database import db, Application, Offer, Payment, VisaCase, User, Organization
from datetime import datetime, timedelta

class ReportingEngine:
    @staticmethod
    def get_funnel_data(session: Session = None):
        if session is None:
            session = db.get_session()
        
        statuses = ['DRAFT', 'SUBMITTED', 'UNDER_REVIEW', 'SHORTLISTED', 'INTERVIEW', 'OFFERED', 'ACCEPTED', 'JOINED']
        data = {}
        for status in statuses:
            data[status] = session.query(Application).filter(Application.status == status).count()
        
        return {"funnel": data, "total": sum(data.values())}

    @staticmethod
    def get_conversion_rates(session: Session = None):
        if session is None:
            session = db.get_session()
        
        total = session.query(Application).count()
        if total == 0:
            return {"error": "No data"}
        
        submitted = session.query(Application).filter(Application.status == "SUBMITTED").count()
        shortlisted = session.query(Application).filter(Application.status == "SHORTLISTED").count()
        offered = session.query(Application).filter(Application.status == "OFFERED").count()
        accepted = session.query(Application).filter(Application.status == "ACCEPTED").count()
        joined = session.query(Application).filter(Application.status == "JOINED").count()
        
        return {
            "total_applications": total,
            "conversion_rates": {
                "submit_rate": round(submitted/total*100, 2) if total else 0,
                "shortlist_rate": round(shortlisted/total*100, 2) if total else 0,
                "offer_rate": round(offered/total*100, 2) if total else 0,
                "acceptance_rate": round(accepted/total*100, 2) if total else 0,
                "joining_rate": round(joined/total*100, 2) if total else 0
            }
        }

    @staticmethod
    def get_revenue_summary(session: Session = None):
        if session is None:
            session = db.get_session()
        
        total_payments = session.query(Payment).count()
        total_amount = session.query(func.sum(Payment.amount)).scalar() or 0
        success_payments = session.query(Payment).filter(Payment.status == "SUCCESS").count()
        success_amount = session.query(func.sum(Payment.amount)).filter(Payment.status == "SUCCESS").scalar() or 0
        
        return {
            "total_transactions": total_payments,
            "total_amount": total_amount,
            "success_transactions": success_payments,
            "success_amount": success_amount,
            "pending_transactions": session.query(Payment).filter(Payment.status == "PENDING").count(),
            "failed_transactions": session.query(Payment).filter(Payment.status == "FAILED").count()
        }

    @staticmethod
    def get_user_activity_summary(session: Session = None):
        if session is None:
            session = db.get_session()
        
        total_users = session.query(User).count()
        active_users = session.query(User).filter(User.status == "ACTIVE").count()
        total_orgs = session.query(Organization).count()
        total_apps = session.query(Application).count()
        total_offers = session.query(Offer).count()
        total_visas = session.query(VisaCase).count()
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "total_organizations": total_orgs,
            "total_applications": total_apps,
            "total_offers": total_offers,
            "total_visa_cases": total_visas,
            "application_to_offer_ratio": round(total_offers/total_apps, 2) if total_apps else 0
        }

reporting = ReportingEngine()