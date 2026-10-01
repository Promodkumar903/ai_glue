# ============================================================
# AI GLUE v8.0 — DOCUMENT MANAGEMENT ROUTER
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import hashlib
import uuid


from core.database import db, Document, User
from auth.session import verify_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ---------- Pydantic Models ----------
class DocumentCreate(BaseModel):
    type: str  # PASSPORT, VISA, DEGREE, TRANSCRIPT, ID_PROOF, etc.
    country_format: Optional[str] = None
    expiry_date: Optional[datetime] = None

class DocumentUpdate(BaseModel):
    expiry_date: Optional[datetime] = None
    translation_status: Optional[str] = None  # NOT_REQUIRED, PENDING, COMPLETED
    attestation_status: Optional[str] = None
    verified: Optional[bool] = None

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
@router.post("/upload", response_model=dict)
def upload_document(
    doc_data: DocumentCreate,
    file: UploadFile = File(...),
    token: str = Depends(oauth2_scheme)
):
    user = get_current_user(token)
    session = db.get_session()
    
    # Read file content for hash
    file_content = file.file.read()
    file_hash = hashlib.sha256(file_content).hexdigest()
    
    # Generate storage URL (mock - in production, upload to S3 or local storage)
    storage_url = f"/uploads/{user.id}/{file.filename}"
    
    new_doc = Document(
        owner_id=user.id,
        type=doc_data.type,
        country_format=doc_data.country_format,
        version=1,
        file_hash=file_hash,
        storage_url=storage_url,
        uploaded_at=datetime.utcnow(),
        expiry_date=doc_data.expiry_date,
        translation_status="NOT_REQUIRED",
        attestation_status="NOT_REQUIRED",
        verified=False
    )
    session.add(new_doc)
    session.commit()
    session.refresh(new_doc)
    doc_id = new_doc.id
    session.close()
    
    return {"id": doc_id, "storage_url": storage_url, "message": "Document uploaded successfully"}

@router.get("/my", response_model=list)
def get_my_documents(token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    docs = session.query(Document).filter(Document.owner_id == user.id).all()
    session.close()
    
    return [
        {
            "id": d.id,
            "type": d.type,
            "country_format": d.country_format,
            "version": d.version,
            "storage_url": d.storage_url,
            "uploaded_at": d.uploaded_at,
            "expiry_date": d.expiry_date,
            "translation_status": d.translation_status,
            "attestation_status": d.attestation_status,
            "verified": d.verified
        }
        for d in docs
    ]

@router.get("/{document_id}", response_model=dict)
def get_document(document_id: str, token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    doc = session.query(Document).filter(Document.id == document_id).first()
    session.close()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return {
        "id": doc.id,
        "type": doc.type,
        "country_format": doc.country_format,
        "version": doc.version,
        "storage_url": doc.storage_url,
        "uploaded_at": doc.uploaded_at,
        "expiry_date": doc.expiry_date,
        "translation_status": doc.translation_status,
        "attestation_status": doc.attestation_status,
        "verified": doc.verified
    }

@router.put("/{document_id}", response_model=dict)
def update_document(document_id: str, doc_update: DocumentUpdate, token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    doc = session.query(Document).filter(Document.id == document_id).first()
    
    if not doc:
        session.close()
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.owner_id != user.id:
        session.close()
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if doc_update.expiry_date is not None:
        doc.expiry_date = doc_update.expiry_date
    if doc_update.translation_status is not None:
        doc.translation_status = doc_update.translation_status
    if doc_update.attestation_status is not None:
        doc.attestation_status = doc_update.attestation_status
    if doc_update.verified is not None:
        doc.verified = doc_update.verified
    
    doc.version += 1
    session.commit()
    session.close()
    
    return {"id": document_id, "version": doc.version, "message": "Document updated"}

@router.get("/expiring/soon", response_model=list)
def get_expiring_soon(token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    
    thirty_days_later = datetime.utcnow() + timedelta(days=30)
    docs = session.query(Document).filter(
        Document.owner_id == user.id,
        Document.expiry_date.isnot(None),
        Document.expiry_date <= thirty_days_later
    ).all()
    session.close()
    
    return [
        {
            "id": d.id,
            "type": d.type,
            "expiry_date": d.expiry_date,
            "days_remaining": (d.expiry_date - datetime.utcnow()).days
        }
        for d in docs
        if d.expiry_date
    ]

@router.post("/verify/{document_id}", response_model=dict)
def verify_document(document_id: str, token: str = Depends(oauth2_scheme)):
    user = get_current_user(token)
    session = db.get_session()
    doc = session.query(Document).filter(Document.id == document_id).first()
    
    if not doc:
        session.close()
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.owner_id != user.id:
        session.close()
        raise HTTPException(status_code=403, detail="Not authorized")
    
    doc.verified = True
    session.commit()
    session.close()
    return {"id": document_id, "verified": True, "message": "Document verified"}