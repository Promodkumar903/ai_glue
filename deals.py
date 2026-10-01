# ============================================================
# AI GLUE v8.0 — DEAL ROUTER
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from core.database import db, Deal, User, Organization, Opportunity, Payment
from auth.session import verify_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ---------- Pydantic Models ----------
class DealCreate(BaseModel):
    agent_id: str
    broker_id: Optional[str] = None
    company_id: str
    candidate_id: str
    opportunity_id: str
    deal_fee: float
    platform_cut: float = 0.0
    agent_commission: float = 0.0
    broker_commission: Optional[float] = 0.0

class DealUpdate(BaseModel):
    status: str  # PENDING, COMPLETED, CANCELLED
    payment_id: Optional[str] = None

class CommissionCalculate(BaseModel):
    deal_fee: float
    platform_rate: float = 0.02
    agent_rate: float = 0.10
    broker_rate: float = 0.05

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

def require_admin(user: User = Depends(get_current_user)):
    session = db.get_session()
    from core.database import UserRole
    roles = session.query(UserRole.role_code).filter(UserRole.user_id == user.id).all()
    session.close()
    role_codes = [r[0] for r in roles]
    if "ADMIN" not in role_codes:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

# ---------- Endpoints ----------
@router.post("/create", response_model=dict)
def create_deal(deal_data: DealCreate, token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    
    # Validate all referenced entities exist
    agent = session.query(User).filter(User.id == deal_data.agent_id).first()
    if not agent:
        session.close()
        raise HTTPException(status_code=404, detail="Agent not found")
    
    if deal_data.broker_id:
        broker = session.query(User).filter(User.id == deal_data.broker_id).first()
        if not broker:
            session.close()
            raise HTTPException(status_code=404, detail="Broker not found")
    
    company = session.query(Organization).filter(Organization.id == deal_data.company_id).first()
    if not company:
        session.close()
        raise HTTPException(status_code=404, detail="Company not found")
    
    candidate = session.query(User).filter(User.id == deal_data.candidate_id).first()
    if not candidate:
        session.close()
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    opportunity = session.query(Opportunity).filter(Opportunity.id == deal_data.opportunity_id).first()
    if not opportunity:
        session.close()
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    # Calculate commissions if not provided
    platform_cut = deal_data.platform_cut or (deal_data.deal_fee * 0.02)
    agent_commission = deal_data.agent_commission or (deal_data.deal_fee * 0.10)
    broker_commission = deal_data.broker_commission or (deal_data.deal_fee * 0.05)
    
    new_deal = Deal(
        agent_id=deal_data.agent_id,
        broker_id=deal_data.broker_id,
        company_id=deal_data.company_id,
        candidate_id=deal_data.candidate_id,
        opportunity_id=deal_data.opportunity_id,
        status="PENDING",
        deal_fee=deal_data.deal_fee,
        platform_cut=platform_cut,
        agent_commission=agent_commission,
        broker_commission=broker_commission
    )
    session.add(new_deal)
    session.commit()
    session.refresh(new_deal)
    deal_id = new_deal.id
    session.close()
    
    return {
        "id": deal_id,
        "deal_fee": deal_data.deal_fee,
        "platform_cut": platform_cut,
        "agent_commission": agent_commission,
        "broker_commission": broker_commission,
        "message": "Deal created successfully"
    }

@router.get("/{deal_id}", response_model=dict)
def get_deal(deal_id: str, token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    deal = session.query(Deal).filter(Deal.id == deal_id).first()
    session.close()
    
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    return {
        "id": deal.id,
        "agent_id": deal.agent_id,
        "broker_id": deal.broker_id,
        "company_id": deal.company_id,
        "candidate_id": deal.candidate_id,
        "opportunity_id": deal.opportunity_id,
        "status": deal.status,
        "deal_fee": deal.deal_fee,
        "platform_cut": deal.platform_cut,
        "agent_commission": deal.agent_commission,
        "broker_commission": deal.broker_commission,
        "payment_id": deal.payment_id,
        "created_at": deal.created_at,
        "updated_at": deal.updated_at
    }

@router.put("/{deal_id}/status", response_model=dict)
def update_deal_status(deal_id: str, status: str, token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    deal = session.query(Deal).filter(Deal.id == deal_id).first()
    
    if not deal:
        session.close()
        raise HTTPException(status_code=404, detail="Deal not found")
    
    if deal.agent_id != user.id:
        # Allow company or admin to update too
        pass
    
    deal.status = status
    session.commit()
    session.close()
    return {"id": deal_id, "status": status, "message": "Deal status updated"}

@router.put("/{deal_id}/payment", response_model=dict)
def link_payment(deal_id: str, payment_id: str, token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    deal = session.query(Deal).filter(Deal.id == deal_id).first()
    
    if not deal:
        session.close()
        raise HTTPException(status_code=404, detail="Deal not found")
    
    payment = session.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        session.close()
        raise HTTPException(status_code=404, detail="Payment not found")
    
    deal.payment_id = payment_id
    if payment.status == "SUCCESS":
        deal.status = "COMPLETED"
    session.commit()
    session.close()
    return {"id": deal_id, "payment_id": payment_id, "status": deal.status, "message": "Payment linked"}

@router.get("/my/deals", response_model=list)
def get_my_deals(token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    deals = session.query(Deal).filter(
        (Deal.agent_id == user.id) | (Deal.broker_id == user.id) | (Deal.candidate_id == user.id)
    ).all()
    session.close()
    
    return [
        {
            "id": d.id,
            "deal_fee": d.deal_fee,
            "status": d.status,
            "created_at": d.created_at,
            "company_id": d.company_id,
            "opportunity_id": d.opportunity_id
        }
        for d in deals
    ]

@router.post("/commission/calculate", response_model=dict)
def calculate_commission(calc_data: CommissionCalculate):
    platform_cut = calc_data.deal_fee * calc_data.platform_rate
    agent_commission = calc_data.deal_fee * calc_data.agent_rate
    broker_commission = calc_data.deal_fee * calc_data.broker_rate
    total = platform_cut + agent_commission + broker_commission
    
    return {
        "deal_fee": calc_data.deal_fee,
        "platform_cut": platform_cut,
        "agent_commission": agent_commission,
        "broker_commission": broker_commission,
        "total_commission": total,
        "net_company_revenue": calc_data.deal_fee - total
    }