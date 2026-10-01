# ============================================================
# AI GLUE v8.0 — OFFER ROUTER (FIXED, SESSION-SAFE)
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

from core.database import db, Offer, Application, Organization, User
from auth.session import verify_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ---------- Pydantic Models ----------
class OfferCreate(BaseModel):
    application_id: str
    organization_id: str
    terms: Dict[str, Any]
    scholarship_amount: Optional[float] = 0.0
    deadline: Optional[datetime] = None

class OfferSend(BaseModel):
    offer_id: str

class OfferAction(BaseModel):
    offer_id: str

class OfferStatusResponse(BaseModel):
    id: str
    status: str
    sent_at: Optional[datetime]
    deadline: Optional[datetime]
    scholarship_amount: float
    application_id: str
    organization_id: str

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
@router.post("/create", response_model=dict)
def create_offer(offer_data: OfferCreate, token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    
    app = session.query(Application).filter(Application.id == offer_data.application_id).first()
    if not app:
        session.close()
        raise HTTPException(status_code=404, detail="Application not found")
    
    org = session.query(Organization).filter(Organization.id == offer_data.organization_id).first()
    if not org:
        session.close()
        raise HTTPException(status_code=404, detail="Organization not found")
    
    new_offer = Offer(
        application_id=offer_data.application_id,
        organization_id=offer_data.organization_id,
        terms=offer_data.terms,
        scholarship_amount=offer_data.scholarship_amount,
        status="DRAFT",
        deadline=offer_data.deadline
    )
    session.add(new_offer)
    session.commit()
    session.refresh(new_offer)
    
    offer_id = new_offer.id
    session.close()
    return {"id": offer_id, "message": "Offer created successfully"}

@router.post("/send", response_model=dict)
def send_offer(send_data: OfferSend, token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    
    offer = session.query(Offer).filter(Offer.id == send_data.offer_id).first()
    if not offer:
        session.close()
        raise HTTPException(status_code=404, detail="Offer not found")
    
    app = session.query(Application).filter(Application.id == offer.application_id).first()
    if not app or (app.candidate_id != user.id):
        session.close()
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if offer.status != "DRAFT":
        session.close()
        raise HTTPException(status_code=400, detail="Offer already sent or processed")
    
    offer.status = "SENT"
    offer.sent_at = datetime.utcnow()
    session.commit()
    
    offer_id = offer.id
    offer_status = offer.status
    session.close()
    return {"id": offer_id, "status": offer_status, "message": "Offer sent successfully"}

@router.post("/accept", response_model=dict)
def accept_offer(action_data: OfferAction, token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    
    offer = session.query(Offer).filter(Offer.id == action_data.offer_id).first()
    if not offer:
        session.close()
        raise HTTPException(status_code=404, detail="Offer not found")
    
    app = session.query(Application).filter(Application.id == offer.application_id).first()
    if not app or (app.candidate_id != user.id):
        session.close()
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if offer.status != "SENT":
        session.close()
        raise HTTPException(status_code=400, detail=f"Offer not in sent state (current: {offer.status})")
    
    offer.status = "ACCEPTED"
    app.status = "OFFER_ACCEPTED"
    session.commit()
    
    offer_id = offer.id
    offer_status = offer.status
    session.close()
    return {"id": offer_id, "status": offer_status, "message": "Offer accepted successfully"}

@router.post("/decline", response_model=dict)
def decline_offer(action_data: OfferAction, token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    
    offer = session.query(Offer).filter(Offer.id == action_data.offer_id).first()
    if not offer:
        session.close()
        raise HTTPException(status_code=404, detail="Offer not found")
    
    app = session.query(Application).filter(Application.id == offer.application_id).first()
    if not app or (app.candidate_id != user.id):
        session.close()
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if offer.status != "SENT":
        session.close()
        raise HTTPException(status_code=400, detail=f"Offer not in sent state (current: {offer.status})")
    
    offer.status = "DECLINED"
    app.status = "OFFER_DECLINED"
    session.commit()
    
    offer_id = offer.id
    offer_status = offer.status
    session.close()
    return {"id": offer_id, "status": offer_status, "message": "Offer declined successfully"}

@router.get("/{offer_id}/status", response_model=OfferStatusResponse)
def get_offer_status(offer_id: str, token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    
    offer = session.query(Offer).filter(Offer.id == offer_id).first()
    if not offer:
        session.close()
        raise HTTPException(status_code=404, detail="Offer not found")
    
    app = session.query(Application).filter(Application.id == offer.application_id).first()
    if not app or (app.candidate_id != user.id):
        session.close()
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Store data before closing
    offer_data = {
        "id": offer.id,
        "status": offer.status,
        "sent_at": offer.sent_at,
        "deadline": offer.deadline,
        "scholarship_amount": offer.scholarship_amount,
        "application_id": offer.application_id,
        "organization_id": offer.organization_id
    }
    session.close()
    return OfferStatusResponse(**offer_data)