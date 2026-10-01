"""
AI GLUE — Referral & Reward System (Blueprint Section 8.3)
"""
from sqlalchemy.orm import Session
from core.database import db, User, ReferralEvent, Reward
from datetime import datetime
import uuid
from core.audit import log_audit

class ReferralEngine:
    @staticmethod
    def generate_referral_link(user_id: str, session: Session = None):
        if session is None:
            session = db.get_session()
        
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "User not found"}
        
        code = uuid.uuid4().hex[:8]
        user.referral_code = code
        session.commit()
        
        return {"referral_code": code, "referral_link": f"https://ai-glue.com/ref/{code}"}

    @staticmethod
    def track_referral(referrer_id: str, referee_id: str, action: str, session: Session = None):
        if session is None:
            session = db.get_session()
        
        existing = session.query(ReferralEvent).filter(
            ReferralEvent.referrer_id == referrer_id,
            ReferralEvent.referee_id == referee_id,
            ReferralEvent.action_type == action
        ).first()
        if existing:
            return {"error": "Referral already tracked", "event_id": existing.id}
        
        reward_map = {
            "SIGNUP": 50,
            "APPLICATION": 100,
            "PLACEMENT": 500,
            "ADMISSION": 300
        }
        reward_amount = reward_map.get(action, 0)
        
        event = ReferralEvent(
            referrer_id=referrer_id,
            referee_id=referee_id,
            action_type=action,
            reward_amount=reward_amount,
            status="PENDING"
        )
        session.add(event)
        session.commit()
        session.refresh(event)
        
        if reward_amount > 0:
            reward = Reward(
                user_id=referrer_id,
                type="REFERRAL_BONUS",
                amount=reward_amount,
                reason=f"Referral {action} by {referee_id}",
                status="PENDING"
            )
            session.add(reward)
            session.commit()
        
        log_audit(
            actor_id=referrer_id,
            action="REFERRAL_TRACK",
            target_type="REFERRAL_EVENT",
            target_id=str(event.id),
            after={"action": action, "reward": reward_amount},
            reason="Referral tracked"
        )
        
        return {
            "event_id": str(event.id),
            "referrer_id": referrer_id,
            "referee_id": referee_id,
            "action": action,
            "reward_amount": reward_amount,
            "status": "PENDING"
        }

    @staticmethod
    def get_referral_stats(user_id: str, session: Session = None):
        if session is None:
            session = db.get_session()
        
        events = session.query(ReferralEvent).filter(ReferralEvent.referrer_id == user_id).all()
        rewards = session.query(Reward).filter(Reward.user_id == user_id).all()
        
        return {
            "total_referrals": len(events),
            "pending": sum(1 for e in events if e.status == "PENDING"),
            "paid": sum(1 for e in events if e.status == "PAID"),
            "total_earned": sum(e.reward_amount for e in events if e.status == "PAID"),
            "pending_rewards": sum(r.amount for r in rewards if r.status == "PENDING"),
            "events": [{"referee_id": e.referee_id, "action": e.action_type, "amount": e.reward_amount, "status": e.status} for e in events]
        }

    @staticmethod
    def get_leaderboard(session: Session = None, limit: int = 10):
        if session is None:
            session = db.get_session()
        
        from sqlalchemy import func
        results = session.query(
            ReferralEvent.referrer_id,
            func.count(ReferralEvent.id).label('total_refs'),
            func.sum(ReferralEvent.reward_amount).label('total_earned')
        ).filter(ReferralEvent.status == "PAID").group_by(ReferralEvent.referrer_id).order_by(func.sum(ReferralEvent.reward_amount).desc()).limit(limit).all()
        
        leaderboard = []
        for r in results:
            user = session.query(User).filter(User.id == r.referrer_id).first()
            leaderboard.append({
                "user_id": r.referrer_id,
                "user_name": user.full_name if user else "Unknown",
                "total_referrals": r.total_refs,
                "total_earned": r.total_earned
            })
        return {"leaderboard": leaderboard}

referral = ReferralEngine()