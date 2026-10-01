# ============================================================
# AI GLUE v8.0 — VENDOR REGISTRY (Local Marketplace)
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

from core.database import db, User, PartnerRegistry
from auth.session import verify_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ---------- Pydantic Models ----------
class VendorCreate(BaseModel):
    name: str
    category: str  # GROCERY, BOOKS, LAPTOP, FURNITURE, SIM, INSURANCE, CLOTHING
    location: str
    address: Optional[str] = None
    phone: str
    website: Optional[str] = None
    rating: Optional[float] = 0.0
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class VendorUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    rating: Optional[float] = None
    status: Optional[str] = None  # PENDING, ACTIVE, INACTIVE

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

@router.post("/create", response_model=dict)
def create_vendor(vendor_data: VendorCreate, admin: User = Depends(require_admin)):
    session = db.get_session()
    new_vendor = PartnerRegistry(
        name=vendor_data.name,
        category=vendor_data.category,
        location=vendor_data.location,
        phone=vendor_data.phone,
        website=vendor_data.website,
        trust_score=vendor_data.rating or 0.0,
        status="PENDING",
        source={"latitude": vendor_data.latitude, "longitude": vendor_data.longitude, "address": vendor_data.address}
    )
    session.add(new_vendor)
    session.commit()
    session.refresh(new_vendor)
    vendor_id = new_vendor.id
    session.close()
    return {"id": vendor_id, "name": vendor_data.name, "message": "Vendor created"}

@router.get("/vendors", response_model=list)
def get_vendors(category: Optional[str] = None):
    session = db.get_session()
    query = session.query(PartnerRegistry)
    if category:
        query = query.filter(PartnerRegistry.category == category)
    vendors = query.filter(PartnerRegistry.status == "ACTIVE").all()
    session.close()
    return [
        {
            "id": v.id,
            "name": v.name,
            "category": v.category,
            "location": v.location,
            "phone": v.phone,
            "trust_score": v.trust_score,
            "website": v.website
        }
        for v in vendors
    ]

@router.get("/vendors/{vendor_id}", response_model=dict)
def get_vendor(vendor_id: str):
    session = db.get_session()
    vendor = session.query(PartnerRegistry).filter(PartnerRegistry.id == vendor_id).first()
    session.close()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return {
        "id": vendor.id,
        "name": vendor.name,
        "category": vendor.category,
        "location": vendor.location,
        "phone": vendor.phone,
        "website": vendor.website,
        "trust_score": vendor.trust_score,
        "status": vendor.status,
        "source": vendor.source
    }

@router.get("/categories", response_model=list)
def get_categories():
    return ["GROCERY", "BOOKS", "LAPTOP", "FURNITURE", "SIM", "INSURANCE", "CLOTHING", "TRANSPORT"]

@router.get("/nearby", response_model=list)
def get_nearby_vendors(latitude: float, longitude: float, radius_km: float = 5):
    # Mock: In production, use geospatial queries
    session = db.get_session()
    vendors = session.query(PartnerRegistry).filter(PartnerRegistry.status == "ACTIVE").limit(10).all()
    session.close()
    return [
        {
            "id": v.id,
            "name": v.name,
            "category": v.category,
            "location": v.location,
            "distance": round(2.5 + (hash(v.id) % 5), 1),  # Mock distance
            "trust_score": v.trust_score
        }
        for v in vendors
    ]