# ============================================================
# AI GLUE v8.0 — HOUSING ENGINE (Corrected, Imports Fixed)
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

from core.database import db, User, StudentLife  # ✅ StudentLife Import Added
from auth.session import verify_token
from sqlalchemy.orm.attributes import flag_modified

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ---------- Pydantic Models ----------
class HousingCreate(BaseModel):
    location: str
    housing_type: str   # SHARED, PRIVATE, DORMITORY, PG
    monthly_rent: float
    currency: str = "EUR"
    available_from: datetime
    amenities: Optional[List[str]] = []
    description: Optional[str] = None
    landlord_name: Optional[str] = None
    landlord_contact: Optional[str] = None

class HousingStatusUpdate(BaseModel):
    housing_id: str
    status: str  # SEARCHING, VIEWED, APPLIED, BOOKED, MOVED_IN

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

# ---------- Import get_or_create_student_life from student_life ----------
from student_life import get_or_create_student_life

@router.post("/add", response_model=dict)
def add_housing(housing_data: HousingCreate, token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    student_life = get_or_create_student_life(session, user.id)
    
    prefs = student_life.preferences or {}
    if "housing" not in prefs:
        prefs["housing"] = []
    
    housing_dict = housing_data.dict()
    housing_dict["id"] = str(uuid.uuid4())
    housing_dict["status"] = "SEARCHING"
    housing_dict["created_at"] = datetime.utcnow().isoformat()
    # ✅ Convert available_from datetime to ISO string
    if housing_dict.get("available_from"):
        housing_dict["available_from"] = housing_dict["available_from"].isoformat()
    
    prefs["housing"].append(housing_dict)
    
    student_life.preferences = prefs
    flag_modified(student_life, "preferences")
    session.commit()
    session.close()
    
    return {"message": "Housing added", "housing": housing_dict}

@router.get("/my", response_model=list)
def get_my_housing(token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    student_life = session.query(StudentLife).filter(StudentLife.user_id == user.id).first()
    session.close()
    
    if not student_life:
        return []
    
    preferences = student_life.preferences
    if not preferences or "housing" not in preferences:
        return []
    
    housing_list = preferences.get("housing", [])
    
    # ✅ Ensure all datetime objects are converted to strings
    def safe_serialize(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: safe_serialize(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [safe_serialize(item) for item in obj]
        else:
            return obj
    
    return safe_serialize(housing_list)

@router.put("/{housing_id}/status", response_model=dict)
def update_housing_status(housing_id: str, status_data: HousingStatusUpdate, token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    student_life = get_or_create_student_life(session, user.id)
    
    prefs = student_life.preferences or {}
    housing_list = prefs.get("housing", [])
    for h in housing_list:
        if h.get("id") == housing_id:
            h["status"] = status_data.status
            student_life.preferences = prefs
            flag_modified(student_life, "preferences")
            session.commit()
            session.close()
            return {"message": f"Housing status updated to {status_data.status}", "housing": h}
    session.close()
    raise HTTPException(status_code=404, detail="Housing not found")

@router.get("/search", response_model=dict)
def search_housing(location: str, max_rent: Optional[float] = None):
    # Mock: In production, integrate with external API
    results = [
        {"id": "mock-1", "location": location, "housing_type": "SHARED", "monthly_rent": 450, "available_from": "2025-02-01"},
        {"id": "mock-2", "location": location, "housing_type": "DORMITORY", "monthly_rent": 350, "available_from": "2025-01-15"}
    ]
    if max_rent:
        results = [r for r in results if r["monthly_rent"] <= max_rent]
    return {"results": results}