# ============================================================
# AI GLUE v8.0 — COMMUNICATION ENGINE (Walled Garden)
# ============================================================
# Platform-Only Messaging for Agent ↔ Agent, Broker ↔ Broker
# Auto-Redaction of Contact Info + Mute Terms
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import re
import uuid

from core.database import db, User, UserRole, Message, ContactShare
from auth.session import verify_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ---------- Privacy Filter ----------
class PrivacyFilter:
    CONTACT_PATTERNS = {
        'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
        'phone': re.compile(r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'),
        'whatsapp': re.compile(r'(whatsapp|wa\.me|wa\.me/)[\d\+\-\s]+', re.IGNORECASE),
        'social': re.compile(r'(instagram|fb\.me|facebook|linkedin\.com/in/|twitter\.com/|x\.com/)[a-zA-Z0-9_\.]+', re.IGNORECASE),
        'url': re.compile(r'(http://|https://)[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}(/\S*)?'),
    }

    MUTE_TERMS = [
    'contract', 'agreement', 'deal',
    'payment', 'invoice', 'bill', 'commission',
    'call me', 'contact me',
    'meet me', 'meeting', 'appointment',
    'whatsapp', 'viber', 'telegram',
    'facebook', 'instagram', 'linkedin'
]

    @classmethod
    def redact(cls, message: str) -> str:
        redacted = message
        for pattern in cls.CONTACT_PATTERNS.values():
            redacted = pattern.sub('[REDACTED]', redacted)
        return redacted

    @classmethod
    def check_mute_terms(cls, message: str) -> bool:
        msg_lower = message.lower()
        for term in cls.MUTE_TERMS:
            if term in msg_lower:
                return True
        return False

    @classmethod
    def sanitize(cls, message: str) -> tuple:
        is_muted = cls.check_mute_terms(message)
        redacted = cls.redact(message)
        return redacted, is_muted


# ---------- Helper Functions ----------
def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if "error" in payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = payload.get("sub")
    session = db.get_session()
    user = session.query(User).filter(User.id == user_id).first()
    session.close()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ---------- Pydantic Models ----------
class MessageCreate(BaseModel):
    receiver_id: str
    message: str
    context_type: Optional[str] = None
    context_id: Optional[str] = None


# ---------- Endpoints ----------
@router.post("/messages/send")
def send_message(
    msg_data: MessageCreate,
    current_user: User = Depends(get_current_user),
):
    session = db.get_session()
    try:
        receiver = session.query(User).filter(User.id == msg_data.receiver_id).first()
        if not receiver:
            raise HTTPException(status_code=404, detail="Receiver not found")

        sanitized, is_muted = PrivacyFilter.sanitize(msg_data.message)

        new_msg = Message(
            id=str(uuid.uuid4()),
            sender_id=current_user.id,
            receiver_id=msg_data.receiver_id,
            message=sanitized if not is_muted else "[MUTED]",
            is_muted=is_muted,
            context_type=msg_data.context_type,
            context_id=msg_data.context_id,
        )
        session.add(new_msg)
        session.commit()
        session.refresh(new_msg)

        return {
            "id": new_msg.id,
            "sender_id": new_msg.sender_id,
            "receiver_id": new_msg.receiver_id,
            "message": new_msg.message,
            "is_muted": new_msg.is_muted,
            "created_at": str(new_msg.created_at)
        }
    finally:
        session.close()


@router.get("/messages/inbox")
def get_inbox(current_user: User = Depends(get_current_user)):
    session = db.get_session()
    try:
        messages = session.query(Message).filter(
            Message.receiver_id == current_user.id
        ).order_by(Message.created_at.desc()).all()
        return [{
            "id": m.id,
            "sender_id": m.sender_id,
            "message": m.message,
            "is_read": m.is_read,
            "is_muted": m.is_muted,
            "created_at": str(m.created_at)
        } for m in messages]
    finally:
        session.close()


@router.get("/policy")
def get_policy():
    return {
        "platform_only": True,
        "blocked": ["email", "phone", "whatsapp", "social_media", "urls"],
        "mute_terms": PrivacyFilter.MUTE_TERMS,
        "contact_sharing": "Only after offer acceptance",
    }