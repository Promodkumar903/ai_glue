# ============================================================
# AI GLUE v8.0 — VISA ROUTER (FIXED, SESSION-SAFE)
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

from core.database import db, VisaCase, VisaAppointment, User
from auth.session import verify_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ---------- Pydantic Models ----------
class VisaCreate(BaseModel):
    country: str
    visa_type: str

class VisaStatusUpdate(BaseModel):
    visa_case_id: str
    status: str

class VisaAppointmentCreate(BaseModel):
    visa_case_id: str
    scheduled_at: datetime
    location: str

class VisaStatusResponse(BaseModel):
    id: str
    candidate_id: str
    country: str
    visa_type: str
    status: str
    applied_at: Optional[datetime]
    decision_at: Optional[datetime]

class ChecklistResponse(BaseModel):
    country: str
    visa_type: str
    checklist: Dict[str, Any]

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
def create_visa_case(visa_data: VisaCreate, token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    
    new_visa = VisaCase(
        candidate_id=user.id,
        country=visa_data.country,
        visa_type=visa_data.visa_type,
        status="NOT_STARTED"
    )
    session.add(new_visa)
    session.commit()
    session.refresh(new_visa)
    visa_id = new_visa.id
    session.close()
    return {"id": visa_id, "message": "Visa case created successfully"}

@router.put("/{visa_case_id}/status", response_model=dict)
def update_visa_status(visa_case_id: str, status_update: VisaStatusUpdate, token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    
    visa = session.query(VisaCase).filter(VisaCase.id == visa_case_id).first()
    if not visa:
        session.close()
        raise HTTPException(status_code=404, detail="Visa case not found")
    if visa.candidate_id != user.id:
        session.close()
        raise HTTPException(status_code=403, detail="Not authorized")
    
    visa.status = status_update.status
    if status_update.status in ["APPROVED", "REJECTED"]:
        visa.decision_at = datetime.utcnow()
    if status_update.status == "APPLIED":
        visa.applied_at = datetime.utcnow()
    session.commit()
    
    visa_id = visa.id
    visa_status = visa.status
    session.close()
    return {"id": visa_id, "status": visa_status, "message": "Visa status updated"}

@router.get("/{visa_case_id}", response_model=VisaStatusResponse)
def get_visa_status(visa_case_id: str, token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    
    visa = session.query(VisaCase).filter(VisaCase.id == visa_case_id).first()
    if not visa:
        session.close()
        raise HTTPException(status_code=404, detail="Visa case not found")
    if visa.candidate_id != user.id:
        session.close()
        raise HTTPException(status_code=403, detail="Not authorized")
    
    visa_data = {
        "id": visa.id,
        "candidate_id": visa.candidate_id,
        "country": visa.country,
        "visa_type": visa.visa_type,
        "status": visa.status,
        "applied_at": visa.applied_at,
        "decision_at": visa.decision_at
    }
    session.close()
    return VisaStatusResponse(**visa_data)

@router.get("/checklist/{country}/{visa_type}", response_model=ChecklistResponse)
def get_checklist(country: str, visa_type: str, token: str = Depends(oauth2_scheme)):
    # Mock checklist
    checklist = {
        "USA": {
            "STUDENT": ["I-20", "Passport", "DS-160", "SEVIS Fee Receipt", "Financial Proof"],
            "TOURIST": ["Passport", "DS-160", "Travel Itinerary", "Financial Proof"]
        },
        "UK": {
            "STUDENT": ["CAS", "Passport", "Visa Application Form", "Financial Proof", "English Test"]
        },
        "CANADA": {
            "STUDENT": ["Acceptance Letter", "Passport", "Study Permit Application", "Financial Proof"]
        }
    }
    items = checklist.get(country, {}).get(visa_type, ["Passport", "Visa Application Form"])
    return ChecklistResponse(country=country, visa_type=visa_type, checklist={"items": items})

@router.post("/appointment", response_model=dict)
def create_visa_appointment(appointment_data: VisaAppointmentCreate, token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    
    visa = session.query(VisaCase).filter(VisaCase.id == appointment_data.visa_case_id).first()
    if not visa:
        session.close()
        raise HTTPException(status_code=404, detail="Visa case not found")
    if visa.candidate_id != user.id:
        session.close()
        raise HTTPException(status_code=403, detail="Not authorized")
    
    new_appointment = VisaAppointment(
        visa_case_id=appointment_data.visa_case_id,
        scheduled_at=appointment_data.scheduled_at,
        location=appointment_data.location,
        status="SCHEDULED"
    )
    session.add(new_appointment)
    session.commit()
    session.refresh(new_appointment)
    app_id = new_appointment.id
    session.close()
    return {"id": app_id, "message": "Appointment created successfully"}

@router.get("/cases", response_model=list)
def get_all_visa_cases(token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    
    visas = session.query(VisaCase).filter(VisaCase.candidate_id == user.id).all()
    session.close()
    
    return [
        {
            "id": v.id,
            "country": v.country,
            "visa_type": v.visa_type,
            "status": v.status
        }
        for v in visas
    ]