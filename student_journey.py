# ============================================================
# AI GLUE v8.0 — STUDENT JOURNEY ENGINE (Germany Lifecycle)
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

from core.database import db, User
from auth.session import verify_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ---------- Pydantic Models ----------
class JourneyStatusUpdate(BaseModel):
    status: str  # ADMITTED, VISA_APPLIED, VISA_APPROVED, ARRIVED, SEMESTER_STARTED, JOB_SEEKING, COMPLETED

# ---------- Journey States ----------
JOURNEY_STATES = {
    "ADMITTED": {"next": ["VISA_APPLIED"], "display": "Admitted to University"},
    "VISA_APPLIED": {"next": ["VISA_APPROVED", "VISA_REJECTED"], "display": "Visa Applied"},
    "VISA_APPROVED": {"next": ["ARRIVED"], "display": "Visa Approved"},
    "VISA_REJECTED": {"next": [], "display": "Visa Rejected"},
    "ARRIVED": {"next": ["SEMESTER_STARTED"], "display": "Arrived in Germany"},
    "SEMESTER_STARTED": {"next": ["JOB_SEEKING"], "display": "Semester Started"},
    "JOB_SEEKING": {"next": ["COMPLETED"], "display": "Job Seeking"},
    "COMPLETED": {"next": [], "display": "Journey Complete"}
}

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

@router.get("/me", response_model=dict)
def get_my_journey(token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    from student_life import get_or_create_student_life
    student_life = get_or_create_student_life(session, user.id)
    
    prefs = student_life.preferences or {}
    journey = prefs.get("journey", {})
    current_status = journey.get("current_status", "ADMITTED")
    history = journey.get("history", [])
    next_states = JOURNEY_STATES.get(current_status, {}).get("next", [])
    
    session.close()
    return {
        "user_id": user.id,
        "current_status": current_status,
        "display_status": JOURNEY_STATES.get(current_status, {}).get("display", current_status),
        "next_possible_states": next_states,
        "history": history,
        "progress": len(history) / len(JOURNEY_STATES) * 100 if len(JOURNEY_STATES) > 0 else 0
    }

@router.post("/update", response_model=dict)
def update_journey_status(status_data: JourneyStatusUpdate, token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    from student_life import get_or_create_student_life
    student_life = get_or_create_student_life(session, user.id)
    
    prefs = student_life.preferences or {}
    journey = prefs.get("journey", {})
    current_status = journey.get("current_status", "ADMITTED")
    
    # Validate transition
    valid_transitions = JOURNEY_STATES.get(current_status, {}).get("next", [])
    if status_data.status not in valid_transitions and status_data.status != "VISA_REJECTED":
        raise HTTPException(status_code=400, detail=f"Invalid transition from {current_status} to {status_data.status}")
    
    # Update history
    history = journey.get("history", [])
    history.append({
        "from_status": current_status,
        "to_status": status_data.status,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    journey["current_status"] = status_data.status
    journey["history"] = history
    prefs["journey"] = journey
    
    student_life.preferences = prefs
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(student_life, "preferences")
    session.commit()
    session.close()
    
    return {
        "user_id": user.id,
        "previous_status": current_status,
        "new_status": status_data.status,
        "message": f"Journey updated from {current_status} to {status_data.status}"
    }

@router.get("/states", response_model=dict)
def get_journey_states():
    return {"states": JOURNEY_STATES}

@router.get("/next-steps", response_model=list)
def get_next_steps(token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    from student_life import get_or_create_student_life
    student_life = get_or_create_student_life(session, user.id)
    
    prefs = student_life.preferences or {}
    journey = prefs.get("journey", {})
    current_status = journey.get("current_status", "ADMITTED")
    session.close()
    
    # Return next steps based on current status
    next_steps_map = {
        "ADMITTED": [{"action": "Apply for Visa", "endpoint": "/visa/create"}],
        "VISA_APPLIED": [{"action": "Wait for Visa Decision", "endpoint": "/visa/{visa_case_id}"}],
        "VISA_APPROVED": [{"action": "Book Flight & Find Housing", "endpoint": "/housing/search"}],
        "ARRIVED": [{"action": "Get SIM Card", "endpoint": "/vendors?category=SIM"}, {"action": "Open Bank Account", "endpoint": "/vendors?category=BANK"}],
        "SEMESTER_STARTED": [{"action": "Find Part-Time Job", "endpoint": "/student-life/jobs"}],
        "JOB_SEEKING": [{"action": "Apply for Jobs", "endpoint": "/search/opportunities"}]
    }
    return next_steps_map.get(current_status, [{"action": "Contact Support", "endpoint": "/support"}])