# ============================================================
# AI GLUE v8.0 — ORGANIZATION & OPPORTUNITY ROUTER
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from core.dependencies import get_current_user, require_permission

from core.database import db, Organization, Opportunity, User
from auth.session import verify_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ---------- Pydantic Models ----------
class OrganizationCreate(BaseModel):
    name: str
    type: str   # e.g., "RECRUITER", "AGENCY", "COMPANY"
    tenant_id: Optional[str] = None

class OpportunityCreate(BaseModel):
    organization_id: str
    type: str           # e.g., "JOB", "INTERNSHIP", "SCHOLARSHIP"
    title: str
    description: Optional[str] = None
    requirements: Optional[Dict[str, Any]] = {}
    fees: Optional[Dict[str, Any]] = {}
    capacity: Optional[int] = None
    deadline: Optional[datetime] = None

class OpportunityStatusUpdate(BaseModel):
    opportunity_id: str
    status: str   # DRAFT, PUBLISHED, CLOSED

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

# ---------- Organization Endpoints ----------
@router.post("/organizations/create", response_model=dict)
def create_organization(org_data: OrganizationCreate, token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    
    new_org = Organization(
        name=org_data.name,
        type=org_data.type,
        tenant_id=org_data.tenant_id,
        verification_status="PENDING"
    )
    session.add(new_org)
    session.commit()
    session.refresh(new_org)
    session.close()
    
    return {"id": new_org.id, "name": new_org.name, "message": "Organization created"}

@router.get("/organizations", response_model=list)
def get_organizations(token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    orgs = session.query(Organization).all()
    session.close()
    return [{"id": o.id, "name": o.name, "type": o.type, "verification_status": o.verification_status} for o in orgs]

# ---------- Opportunity Endpoints ----------
@router.post("/vacancy", response_model=dict)
def create_opportunity(opp_data: OpportunityCreate, token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    
    # Check organization exists and user has permission (optional)
    org = session.query(Organization).filter(Organization.id == opp_data.organization_id).first()
    if not org:
        session.close()
        raise HTTPException(status_code=404, detail="Organization not found")
    
    new_opp = Opportunity(
        organization_id=opp_data.organization_id,
        type=opp_data.type,
        title=opp_data.title,
        description=opp_data.description,
        requirements=opp_data.requirements,
        fees=opp_data.fees,
        capacity=opp_data.capacity,
        deadline=opp_data.deadline,
        status="DRAFT",
        filled_count=0
    )
    session.add(new_opp)
    session.commit()
    session.refresh(new_opp)
    session.close()
    
    return {"id": new_opp.id, "title": new_opp.title, "message": "Opportunity created"}

@router.put("/vacancy/status", response_model=dict)
def update_opportunity_status(status_data: OpportunityStatusUpdate, token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    
    opp = session.query(Opportunity).filter(Opportunity.id == status_data.opportunity_id).first()
    if not opp:
        session.close()
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    opp.status = status_data.status
    session.commit()
    session.close()
    
    return {"id": opp.id, "status": opp.status, "message": "Opportunity status updated"}

@router.get("/vacancy", response_model=list)
def get_vacancies(
    session: Session = Depends(db.get_session),
    current_user: User = Depends(require_permission("OPPORTUNITY", "READ", "TENANT"))
):
    """Get all active opportunities."""
    opportunities = session.query(Opportunity).filter(
        Opportunity.status.in_(["ACTIVE", "PUBLISHED", "OPEN"])
    ).all()
    
    return [{
        "id": o.id,
        "title": o.title,
        "type": o.type,
        "status": o.status,
        "organization_id": o.organization_id,
        "description": (o.description or "")[:100],
        "deadline": str(o.deadline) if o.deadline else None,
    } for o in opportunities]
