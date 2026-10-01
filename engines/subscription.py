"""
AI GLUE — Subscription & Pricing Engine (Blueprint Section 5.9)
"""
from sqlalchemy.orm import Session
from core.database import db, SubscriptionPlan, UserSubscription, User
from datetime import datetime, timedelta
from core.audit import log_audit

class SubscriptionEngine:
    @staticmethod
    def create_plan(name: str, price_monthly: float, price_yearly: float, features: dict, session: Session = None):
        if session is None:
            session = db.get_session()
        
        plan = SubscriptionPlan(
            name=name,
            price_monthly=price_monthly,
            price_yearly=price_yearly,
            features=features
        )
        session.add(plan)
        session.commit()
        session.refresh(plan)
        return {"plan_id": str(plan.id), "name": plan.name, "message": "Plan created"}

    @staticmethod
    def assign_plan(user_id: str, plan_id: str, duration: str = "monthly", session: Session = None):
        if session is None:
            session = db.get_session()
        
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "User not found"}
        
        plan = session.query(SubscriptionPlan).filter(SubscriptionPlan.id == plan_id).first()
        if not plan:
            return {"error": "Plan not found"}
        
        # Deactivate old subscription
        old = session.query(UserSubscription).filter(UserSubscription.user_id == user_id, UserSubscription.status == "ACTIVE").first()
        if old:
            old.status = "EXPIRED"
        
        end_date = datetime.utcnow() + (timedelta(days=365) if duration == "yearly" else timedelta(days=30))
        sub = UserSubscription(
            user_id=user_id,
            plan_id=plan_id,
            status="ACTIVE",
            start_date=datetime.utcnow(),
            end_date=end_date,
            auto_renew=True
        )
        session.add(sub)
        session.commit()
        session.refresh(sub)
        
        log_audit(
            actor_id=user_id,
            action="SUBSCRIPTION_ASSIGN",
            target_type="USER_SUBSCRIPTION",
            target_id=str(sub.id),
            after={"plan": plan.name, "duration": duration},
            reason="Subscription assigned"
        )
        
        return {"subscription_id": str(sub.id), "plan": plan.name, "status": "ACTIVE", "end_date": end_date}

    @staticmethod
    def get_user_plan(user_id: str, session: Session = None):
        if session is None:
            session = db.get_session()
        
        sub = session.query(UserSubscription).filter(
            UserSubscription.user_id == user_id,
            UserSubscription.status == "ACTIVE"
        ).first()
        if not sub:
            return {"user_id": user_id, "plan": "FREE", "features": {"max_applications": 1, "ai_credits": 100}}
        
        plan = session.query(SubscriptionPlan).filter(SubscriptionPlan.id == sub.plan_id).first()
        return {
            "user_id": user_id,
            "plan": plan.name if plan else "FREE",
            "features": plan.features if plan else {"max_applications": 1, "ai_credits": 100},
            "end_date": sub.end_date,
            "auto_renew": sub.auto_renew
        }

subscription = SubscriptionEngine()