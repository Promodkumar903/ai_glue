# ============================================================
# AI GLUE v8.0 — PAYMENTS ROUTER
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

from core.database import db, Payment, User
from auth.session import verify_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ---------- Pydantic Models ----------
class PaymentInitiate(BaseModel):
    amount: float
    currency: str = "USD"
    payee_type: str   # PLATFORM, ORGANIZATION, AGENT, BROKER
    payee_id: Optional[str] = None
    payment_meta: Optional[Dict[str, Any]] = {}

class PaymentStatusResponse(BaseModel):
    id: str
    amount: float
    currency: str
    status: str
    gateway_ref: Optional[str]
    created_at: datetime
    updated_at: datetime

class PaymentSimulate(BaseModel):
    payment_id: str

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
@router.post("/initiate", response_model=dict)
def initiate_payment(payment_data: PaymentInitiate, token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    
    new_payment = Payment(
        payer_id=user.id,
        payee_type=payment_data.payee_type,
        payee_id=payment_data.payee_id,
        amount=payment_data.amount,
        currency=payment_data.currency,
        status="PENDING",
        payment_meta=payment_data.payment_meta,
        idempotency_key=str(uuid.uuid4())
    )
    session.add(new_payment)
    session.commit()
    session.refresh(new_payment)
    
    payment_id = new_payment.id
    session.close()
    return {"id": payment_id, "status": "PENDING", "message": "Payment initiated"}

@router.get("/{payment_id}/status", response_model=PaymentStatusResponse)
def get_payment_status(payment_id: str, token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    
    payment = session.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        session.close()
        raise HTTPException(status_code=404, detail="Payment not found")
    if payment.payer_id != user.id:
        session.close()
        raise HTTPException(status_code=403, detail="Not authorized")
    
    payment_data = {
        "id": payment.id,
        "amount": payment.amount,
        "currency": payment.currency,
        "status": payment.status,
        "gateway_ref": payment.gateway_ref,
        "created_at": payment.created_at,
        "updated_at": payment.updated_at
    }
    session.close()
    return PaymentStatusResponse(**payment_data)

@router.post("/simulate/{payment_id}/success", response_model=dict)
def simulate_success(payment_id: str, token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    
    payment = session.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        session.close()
        raise HTTPException(status_code=404, detail="Payment not found")
    if payment.payer_id != user.id:
        session.close()
        raise HTTPException(status_code=403, detail="Not authorized")
    
    payment.status = "SUCCESS"
    payment.gateway_ref = f"sim_{uuid.uuid4().hex[:8]}"
    session.commit()
    
    payment_id = payment.id
    payment_status = payment.status
    session.close()
    return {"id": payment_id, "status": payment_status, "message": "Payment simulated as SUCCESS"}

@router.post("/simulate/{payment_id}/failure", response_model=dict)
def simulate_failure(payment_id: str, token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    
    payment = session.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        session.close()
        raise HTTPException(status_code=404, detail="Payment not found")
    if payment.payer_id != user.id:
        session.close()
        raise HTTPException(status_code=403, detail="Not authorized")
    
    payment.status = "FAILED"
    payment.gateway_ref = None
    session.commit()
    
    payment_id = payment.id
    payment_status = payment.status
    session.close()
    return {"id": payment_id, "status": payment_status, "message": "Payment simulated as FAILURE"}