# ============================================================
# AI GLUE v8.0 — PROFILE ROUTER (No Session Dependency Issue)
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from core.database import db, CandidateProfile, User
from auth.session import verify_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ---------- Pydantic Models ----------
class ProfileCreate(BaseModel):
    education: List[Dict[str, Any]] = []
    experience: List[Dict[str, Any]] = []
    skills: List[str] = []
    languages: List[str] = []
    preferences: Dict[str, Any] = {}

class ProfileUpdate(BaseModel):
    education: Optional[List[Dict[str, Any]]] = None
    experience: Optional[List[Dict[str, Any]]] = None
    skills: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    preferences: Optional[Dict[str, Any]] = None

# ---------- Helper: Get Current User ----------
def get_current_user_from_token(token: str):
    payload = verify_token(token)
    if "error" in payload:
        print(f"❌ Token error: {payload['error']}")   # Debug
        raise HTTPException(status_code=401, detail=f"Invalid token: {payload['error']}")
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
def create_profile(profile_data: ProfileCreate, token: str = Depends(oauth2_scheme)):
    """Create candidate profile."""
    user = get_current_user_from_token(token)
    session = db.get_session()
    
    existing = session.query(CandidateProfile).filter(CandidateProfile.user_id == user.id).first()
    if existing:
        session.close()
        raise HTTPException(status_code=400, detail="Profile already exists")
    
    new_profile = CandidateProfile(
        user_id=user.id,
        education=profile_data.education,
        experience=profile_data.experience,
        skills=profile_data.skills,
        languages=profile_data.languages,
        preferences=profile_data.preferences,
        completeness_pct=0
    )
    session.add(new_profile)
    session.commit()
    session.refresh(new_profile)
    session.close()
    
    return {"id": new_profile.id, "user_id": user.id, "message": "Profile created successfully"}

@router.put("/update", response_model=dict)
def update_profile(profile_data: ProfileUpdate, token: str = Depends(oauth2_scheme)):
    user = get_current_user_from_token(token)
    session = db.get_session()
    profile = session.query(CandidateProfile).filter(CandidateProfile.user_id == user.id).first()
    if not profile:
        session.close()
        raise HTTPException(status_code=404, detail="Profile not found")
    
    if profile_data.education is not None:
        profile.education = profile_data.education
    if profile_data.experience is not None:
        profile.experience = profile_data.experience
    if profile_data.skills is not None:
        profile.skills = profile_data.skills
    if profile_data.languages is not None:
        profile.languages = profile_data.languages
    if profile_data.preferences is not None:
        profile.preferences = profile_data.preferences
    
    session.commit()
    session.close()
    return {"id": profile.id, "message": "Profile updated successfully"}

@router.get("/{user_id}", response_model=dict)
def get_profile(user_id: str, token: str = Depends(oauth2_scheme)):
    # Optional: check permissions
    session = db.get_session()
    profile = session.query(CandidateProfile).filter(CandidateProfile.user_id == user_id).first()
    session.close()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {
        "id": profile.id,
        "user_id": profile.user_id,
        "education": profile.education,
        "experience": profile.experience,
        "skills": profile.skills,
        "languages": profile.languages,
        "preferences": profile.preferences,
        "completeness_pct": profile.completeness_pct
    }