# ============================================================
# AI GLUE v8.0 — REFERRAL & REWARDS ROUTER
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from core.database import db, User, ReferralEvent, Reward
from auth.session import verify_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ---------- Pydantic Models ----------
class ReferralTrack(BaseModel):
    referrer_id: str
    referee_id: str
    action_type: str   # REGISTER, APPLICATION_SUBMIT, OFFER_ACCEPT

class RewardCreate(BaseModel):
    user_id: str
    type: str   # SIGNUP_BONUS, REFERRAL_BONUS, APPLICATION_BONUS
    amount: float
    reason: Optional[str] = None

# ---------- Helper ----------
def get_current_user(token: str):
    payload = verify_token(token)
    if "error" in payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    session = db.get_session()
    user = session.query(User).filter(User.id == user_id).first()
    session.close()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ---------- Endpoints ----------
@router.get("/link/{user_id}", response_model=dict)
def get_referral_link(user_id: str, token: str = Depends(oauth2_scheme)):
    # Generate a referral link (just a mock)
    link = f"http://localhost:8000/ref?ref={user_id}"
    return {"referral_link": link, "user_id": user_id}

@router.post("/track", response_model=dict)
def track_referral(track_data: ReferralTrack, token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    
    # Check if referee exists
    referee = session.query(User).filter(User.id == track_data.referee_id).first()
    if not referee:
        session.close()
        raise HTTPException(status_code=404, detail="Referee not found")
    
    # Check if referral already tracked
    existing = session.query(ReferralEvent).filter(
        ReferralEvent.referrer_id == track_data.referrer_id,
        ReferralEvent.referee_id == track_data.referee_id,
        ReferralEvent.action_type == track_data.action_type
    ).first()
    if existing:
        session.close()
        raise HTTPException(status_code=400, detail="Referral already tracked for this action")
    
    new_event = ReferralEvent(
        referrer_id=track_data.referrer_id,
        referee_id=track_data.referee_id,
        action_type=track_data.action_type,
        status="PENDING"
    )
    session.add(new_event)
    session.commit()
    session.refresh(new_event)
    
    # Optionally, create a reward for referrer
    reward = Reward(
        user_id=track_data.referrer_id,
        type="REFERRAL_BONUS",
        amount=10.0,   # Mock amount
        reason=f"Referral {track_data.action_type} by {track_data.referee_id}",
        status="PENDING"
    )
    session.add(reward)
    session.commit()
    
    session.close()
    return {"id": new_event.id, "message": "Referral tracked successfully"}

@router.get("/stats/{user_id}", response_model=dict)
def get_referral_stats(user_id: str, token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    
    referrals = session.query(ReferralEvent).filter(ReferralEvent.referrer_id == user_id).all()
    total = len(referrals)
    pending = len([r for r in referrals if r.status == "PENDING"])
    completed = len([r for r in referrals if r.status == "COMPLETED"])
    
    rewards = session.query(Reward).filter(Reward.user_id == user_id).all()
    total_rewards = sum(r.amount for r in rewards if r.status == "GRANTED")
    
    session.close()
    return {
        "user_id": user_id,
        "total_referrals": total,
        "pending_referrals": pending,
        "completed_referrals": completed,
        "total_rewards": total_rewards
    }

@router.get("/leaderboard", response_model=list)
def get_leaderboard(token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    
    # Get users with referral counts
    results = session.query(
        User.id,
        User.full_name,
        User.email,
        ReferralEvent.referrer_id
    ).join(ReferralEvent, User.id == ReferralEvent.referrer_id).group_by(User.id).all()
    
    # Simple aggregation
    leaderboard = []
    for user_id, full_name, email, _ in results:
        count = session.query(ReferralEvent).filter(ReferralEvent.referrer_id == user_id).count()
        leaderboard.append({
            "user_id": user_id,
            "name": full_name or email,
            "referral_count": count
        })
    leaderboard.sort(key=lambda x: x["referral_count"], reverse=True)
    session.close()
    return leaderboard[:10]  # Top 10