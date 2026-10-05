# ============================================================
# AI GLUE v8.0 — APPLICATION ROUTER (FIXED)
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from core.database import db, Application, Case, Opportunity, User
from auth.session import verify_token
from core.database import Application

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ---------- Pydantic Models ----------
class ApplicationCreate(BaseModel):
    opportunity_id: str
    segment: Optional[str] = None

class ApplicationSubmit(BaseModel):
    application_id: str

class ApplicationStatusResponse(BaseModel):
    id: str
    status: str
    submitted_at: Optional[datetime]
    match_score: Optional[float]
    case_id: str
    opportunity_id: str

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
def create_application(app_data: ApplicationCreate, token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    
    # Check opportunity exists
    opportunity = session.query(Opportunity).filter(Opportunity.id == app_data.opportunity_id).first()
    if not opportunity:
        session.close()
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    # Create case
    new_case = Case(
        candidate_id=user.id,
        case_type="APPLICATION",
        status="OPEN"
    )
    session.add(new_case)
    session.commit()
    session.refresh(new_case)
    
    # Create application
    new_app = Application(
        case_id=new_case.id,
        candidate_id=user.id,
        opportunity_id=app_data.opportunity_id,
        status="DRAFT",
        segment=app_data.segment,
        match_score=0.0
    )
    session.add(new_app)
    session.commit()
    session.refresh(new_app)
    
    # Store IDs before closing session
    app_id = new_app.id
    case_id = new_case.id
    
    session.close()
    return {"id": app_id, "case_id": case_id, "message": "Application created successfully"}

@router.post("/submit", response_model=dict)
def submit_application(submit_data: ApplicationSubmit, token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    
    app = session.query(Application).filter(Application.id == submit_data.application_id).first()
    if not app:
        session.close()
        raise HTTPException(status_code=404, detail="Application not found")
    if app.candidate_id != user.id:
        session.close()
        raise HTTPException(status_code=403, detail="Not authorized")
    if app.status != "DRAFT":
        session.close()
        raise HTTPException(status_code=400, detail=f"Application already submitted (status: {app.status})")
    
    app.status = "SUBMITTED"
    app.submitted_at = datetime.utcnow()
    session.commit()
    
    # Store values before closing session
    app_id = app.id
    app_status = app.status
    
    session.close()
    return {"id": app_id, "status": app_status, "message": "Application submitted successfully"}
@router.get("/my")
def get_my_applications(token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    try:
        uid = user.get("id") if isinstance(user, dict) else getattr(user, "id", None)
        apps = session.query(Application).filter(Application.candidate_id == uid).all()
        result = [{
            "id": str(a.id),
            "status": getattr(a, "status", None),
        } for a in apps]
        return {"applications": result}
    except Exception as e:
        return {"applications": [], "error": str(e)}
    finally:
        session.close()


# ============================================================
# MY APPLICATIONS STATUS — /applications/me/status
# Frontend isko call karta hai saari applications ke liye
# ============================================================
@router.get("/me/status")
def get_my_applications_status(token: str = Depends(oauth2_scheme)):
    """Get all applications for the logged-in user with full details."""
    user = get_current_user(token)
    session = db.get_session()
    try:
        apps = session.query(Application).filter(
            Application.candidate_id == user.id
        ).order_by(Application.submitted_at.desc().nullslast()).all()

        result = []
        for a in apps:
            # Opportunity details
            opp = session.query(Opportunity).filter(
                Opportunity.id == a.opportunity_id
            ).first() if a.opportunity_id else None

            result.append({
                "id": str(a.id),
                "status": a.status or "applied",
                "opportunity_id": str(a.opportunity_id) if a.opportunity_id else None,
                "opportunity_title": opp.title if opp else None,
                "university_name": getattr(opp, 'organization_name', None) if opp else None,
                "organization_name": getattr(opp, 'organization_name', None) if opp else None,
                "match_score": a.match_score if a.match_score else 0,
                "submitted_at": a.submitted_at.isoformat() if a.submitted_at else None,
                "created_at": a.created_at.isoformat() if hasattr(a, 'created_at') and a.created_at else None,
                "case_id": str(a.case_id) if a.case_id else None,
            })

        return result
    except Exception as e:
        return []
    finally:
        session.close()

@router.get("/{app_id}/status", response_model=ApplicationStatusResponse)
def get_application_status(app_id: str, token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    
    app = session.query(Application).filter(Application.id == app_id).first()
    if not app:
        session.close()
        raise HTTPException(status_code=404, detail="Application not found")
    if app.candidate_id != user.id:
        session.close()
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Store all needed data before closing session
    app_data = {
        "id": app.id,
        "status": app.status,
        "submitted_at": app.submitted_at,
        "match_score": app.match_score,
        "case_id": app.case_id,
        "opportunity_id": app.opportunity_id
    }
    session.close()
    
    return ApplicationStatusResponse(**app_data)


