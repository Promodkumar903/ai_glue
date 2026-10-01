# ============================================================
# AI GLUE — FORGOT / RESET PASSWORD
# ============================================================

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets
import smtplib
import bcrypt
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

from core.database import db, User, PasswordResetToken

router = APIRouter(prefix="/auth", tags=["Auth"])

# ---------- Pydantic Schemas ----------
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

# ---------- Email Sender (SMTP) ----------
def send_reset_email(to_email: str, reset_link: str):
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")

    if not smtp_user or not smtp_pass:
        print("⚠️ SMTP credentials not set.")
        return

    subject = "AI Glue – Password Reset"
    body = f"""
    <p>Hello,</p>
    <p>You requested to reset your password. Click the link below:</p>
    <p><a href="{reset_link}">{reset_link}</a></p>
    <p>This link will expire in 1 hour.</p>
    <p>If you didn't request this, ignore this email.</p>
    """

    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, to_email, msg.as_string())
            print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Email send error: {e}")

# ---------- Endpoints ----------
@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest, session: Session = Depends(db.get_session)):
    """Generate reset token and send email."""
    user = session.query(User).filter(User.email == req.email).first()
    if not user:
        return {"message": "If this email exists, a reset link has been sent."}

    # Delete old tokens
    session.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.used == False
    ).delete()
    session.commit()

    # Generate new token
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=1)

    reset_token = PasswordResetToken(
        user_id=user.id,
        token=token,
        expires_at=expires_at
    )
    session.add(reset_token)
    session.commit()

    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
    reset_link = f"{frontend_url}/reset-password?token={token}"

    send_reset_email(user.email, reset_link)

    return {"message": "If this email exists, a reset link has been sent."}

@router.post("/reset-password")
def reset_password(req: ResetPasswordRequest, session: Session = Depends(db.get_session)):
    """Reset password using token."""
    token_record = session.query(PasswordResetToken).filter(
        PasswordResetToken.token == req.token,
        PasswordResetToken.used == False,
        PasswordResetToken.expires_at > datetime.utcnow()
    ).first()

    if not token_record:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = session.query(User).filter(User.id == token_record.user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    # Direct bcrypt — no AuthEngine dependency
    user.password_hash = bcrypt.hashpw(req.new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    token_record.used = True
    session.commit()

    return {"message": "Password reset successfully"}