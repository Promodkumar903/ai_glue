# ============================================================
# AI GLUE v8.0 — RECOMMENDATION ENGINE
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from core.database import db, User
from auth.session import verify_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

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
def get_recommendations(token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    from student_life import get_or_create_student_life
    student_life = get_or_create_student_life(session, user.id)
    
    prefs = student_life.preferences or {}
    journey = prefs.get("journey", {})
    current_status = journey.get("current_status", "ADMITTED")
    
    # ✅ Full Recommendations for every status
    recommendations_map = {
        "ADMITTED": [
            {"type": "VISA", "title": "Apply for Student Visa", "priority": "HIGH", "description": "Start visa application immediately."},
            {"type": "HOUSING", "title": "Find Accommodation", "priority": "MEDIUM", "description": "Search for housing near your university."}
        ],
        "VISA_APPLIED": [
            {"type": "VISA", "title": "Track Visa Status", "priority": "HIGH", "description": "Monitor your visa application progress."},
            {"type": "FLIGHT", "title": "Research Flights", "priority": "MEDIUM", "description": "Look for flight deals to Germany."}
        ],
        "VISA_APPROVED": [
            {"type": "FLIGHT", "title": "Book Flight Ticket", "priority": "HIGH", "description": "Book your flight to Germany."},
            {"type": "HOUSING", "title": "Finalize Accommodation", "priority": "HIGH", "description": "Confirm your housing arrangement."}
        ],
        "ARRIVED": [
            {"type": "REGISTRATION", "title": "City Registration", "priority": "HIGH", "description": "Register at the local citizen's office."},
            {"type": "SIM", "title": "Get German SIM Card", "priority": "HIGH", "description": "Get a local SIM card for communication."},
            {"type": "BANK", "title": "Open Bank Account", "priority": "HIGH", "description": "Open a German bank account."}
        ],
        "SEMESTER_STARTED": [
            {"type": "BOOKS", "title": "Buy University Books", "priority": "HIGH", "description": "Purchase required books for your courses."},
            {"type": "JOB", "title": "Find Part-Time Job", "priority": "MEDIUM", "description": "Start looking for part-time work."}
        ],
        "JOB_SEEKING": [
            {"type": "CAREER", "title": "Polish Your CV", "priority": "HIGH", "description": "Update your resume for German job market."},
            {"type": "NETWORK", "title": "Connect with Alumni", "priority": "MEDIUM", "description": "Reach out to alumni for referrals."}
        ]
    }
    
    recs = recommendations_map.get(current_status, [{"type": "SUPPORT", "title": "Contact Support", "priority": "LOW", "description": "Need guidance? Contact our support team."}])
    
    # Add need-based recommendation if any
    current_need = student_life.current_need
    if current_need:
        recs.append({
            "type": "NEED",
            "title": f"Action: {current_need}",
            "priority": "HIGH",
            "description": f"We noticed you need {current_need}. Here's how to proceed."
        })
    
    session.close()
    return {
        "user_id": user.id,
        "current_status": current_status,
        "recommendations": recs,
        "total": len(recs)
    }
    
    # Mock recommendations based on journey status
    recommendations = {
        "ADMITTED": [
            {"type": "VISA", "title": "Apply for Student Visa", "priority": "HIGH", "description": "Start your visa application process immediately."},
            {"type": "HOUSING", "title": "Find Accommodation", "priority": "MEDIUM", "description": "Search for housing near your university."}
        ],
        "VISA_APPROVED": [
            {"type": "FLIGHT", "title": "Book Flight Ticket", "priority": "HIGH", "description": "Book your flight to Germany."},
            {"type": "HOUSING", "title": "Confirm Accommodation", "priority": "HIGH", "description": "Finalize your housing arrangement."}
        ],
        "ARRIVED": [
            {"type": "SIM", "title": "Get German SIM Card", "priority": "HIGH", "description": "Get a local SIM card for communication."},
            {"type": "BANK", "title": "Open Bank Account", "priority": "HIGH", "description": "Open a German bank account."},
            {"type": "INSURANCE", "title": "Health Insurance", "priority": "HIGH", "description": "Get health insurance (mandatory in Germany)."}
        ],
        "SEMESTER_STARTED": [
            {"type": "BOOKS", "title": "Buy University Books", "priority": "HIGH", "description": "Purchase required books for your courses."},
            {"type": "JOB", "title": "Find Part-Time Job", "priority": "MEDIUM", "description": "Start looking for part-time work."},
            {"type": "GROCERY", "title": "Find Local Grocery Stores", "priority": "LOW", "description": "Discover nearby grocery stores."}
        ],
        "JOB_SEEKING": [
            {"type": "CAREER", "title": "Polish Your CV", "priority": "HIGH", "description": "Update your resume for German job market."},
            {"type": "NETWORK", "title": "Connect with Alumni", "priority": "MEDIUM", "description": "Reach out to alumni for referrals."}
        ]
    }
    
    recs = recommendations.get(current_status, [])
    
    # Add need-based recommendations
    current_need = student_life.current_need
    if current_need:
        recs.append({
            "type": "NEED",
            "title": f"Action: {current_need}",
            "priority": "HIGH",
            "description": f"We noticed you need {current_need}. Here's how to proceed."
        })
    
    session.close()
    return {
        "user_id": user.id,
        "current_status": current_status,
        "recommendations": recs,
        "total": len(recs)
    }

@router.get("/next-need", response_model=dict)
def get_next_need(token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    from student_life import get_or_create_student_life
    student_life = get_or_create_student_life(session, user.id)
    
    journey = student_life.preferences.get("journey", {}) if student_life.preferences else {}
    current_status = journey.get("current_status", "ADMITTED")
    
    # Smart recommendation for next step
    next_need_map = {
        "ADMITTED": {"need": "Visa Application", "urgency": "HIGH"},
        "VISA_APPLIED": {"need": "Wait for Decision", "urgency": "MEDIUM"},
        "VISA_APPROVED": {"need": "Housing and Travel", "urgency": "HIGH"},
        "ARRIVED": {"need": "Registration (City + University)", "urgency": "HIGH"},
        "SEMESTER_STARTED": {"need": "Books and Supplies", "urgency": "MEDIUM"},
        "JOB_SEEKING": {"need": "Job Search Strategy", "urgency": "HIGH"}
    }
    
    session.close()
    return {
        "user_id": user.id,
        "current_status": current_status,
        "next_need": next_need_map.get(current_status, {"need": "Contact Support", "urgency": "LOW"})
    }