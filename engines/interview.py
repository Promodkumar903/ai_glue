"""
Interview Engine — Invite-only video interviews
Room IDs are random and share-only (no cold calling)
"""
import os, uuid, secrets, string, smtplib, sqlite3
from datetime import datetime, timedelta
from email.message import EmailMessage
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional

DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ai_glue.db")
BASE_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ═══════════════════════════════════════════
# Room ID Generator — Random, unguessable
# ═══════════════════════════════════════════
def generate_room_id(app_id: str = "") -> str:
    """Format: aiglueXivX{8-random} (no hyphens — Jitsi treats them as spaces)"""
    alphabet = string.ascii_lowercase + string.digits
    random_part = ''.join(secrets.choice(alphabet) for _ in range(10))
    return f"aiglueiv{random_part}"


# ═══════════════════════════════════════════
# DB Init
# ═══════════════════════════════════════════
def init_interview_table():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS interviews (
        id TEXT PRIMARY KEY,
        room_id TEXT UNIQUE NOT NULL,
        title TEXT,
        candidate_id TEXT NOT NULL,
        candidate_email TEXT,
        candidate_name TEXT,
        interviewer_id TEXT NOT NULL,
        interviewer_name TEXT,
        interviewer_role TEXT,
        scheduled_at TEXT,
        duration_minutes INTEGER DEFAULT 30,
        status TEXT DEFAULT 'SCHEDULED',
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        started_at TIMESTAMP,
        ended_at TIMESTAMP
    )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_iv_candidate ON interviews(candidate_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_iv_interviewer ON interviews(interviewer_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_iv_room ON interviews(room_id)")
    conn.commit()
    conn.close()


# ═══════════════════════════════════════════
# Models
# ═══════════════════════════════════════════
class CreateInterviewReq(BaseModel):
    title: str = "Interview"
    candidate_id: str
    candidate_email: str = ""
    candidate_name: str = ""
    scheduled_at: str = ""  # ISO format
    duration_minutes: int = 30
    notes: str = ""


class UpdateStatusReq(BaseModel):
    status: str  # SCHEDULED | COMPLETED | CANCELLED


# ═══════════════════════════════════════════
# Email invite
# ═══════════════════════════════════════════
def send_interview_invite(to_email, candidate_name, interviewer_name, title, room_id, scheduled_at):
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASS = os.getenv("SMTP_PASS", "")
    
    link = f"{BASE_URL}/video-call/{room_id}"
    
    subject = f"📹 Interview Scheduled — {title}"
    
    html = f"""<!DOCTYPE html>
<html><body style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px;">
  <div style="background: #6366f1; color: white; padding: 20px; border-radius: 12px 12px 0 0; text-align: center;">
    <h1 style="margin: 0; font-size: 22px;">📹 Interview Scheduled</h1>
  </div>
  <div style="background: white; padding: 24px; border: 1px solid #e5e7eb;">
    <p>Hi <b>{candidate_name or 'there'}</b>,</p>
    <p>An interview has been scheduled with you.</p>
    
    <div style="background: #f9fafb; padding: 16px; border-radius: 8px; margin: 16px 0;">
      <p style="margin: 6px 0;"><b>Title:</b> {title}</p>
      <p style="margin: 6px 0;"><b>Interviewer:</b> {interviewer_name}</p>
      <p style="margin: 6px 0;"><b>Scheduled:</b> {scheduled_at or 'Flexible'}</p>
    </div>
    
    <div style="text-align: center; padding: 20px 0;">
      <a href="{link}" style="display: inline-block; padding: 14px 32px; background: #6366f1; color: white; text-decoration: none; border-radius: 8px; font-weight: bold;">
        🎥 Join Video Interview
      </a>
    </div>
    
    <p style="font-size: 12px; color: #6b7280;">
      🔒 This link is private and unique to you. Please don't share it.
    </p>
  </div>
  <div style="background: #1f2937; color: #9ca3af; padding: 20px; text-align: center; border-radius: 0 0 12px 12px; font-size: 12px;">
    AI Glue · Interview System
  </div>
</body></html>"""
    
    try:
        msg = EmailMessage()
        msg["From"] = SMTP_USER
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(f"Interview scheduled. Join: {link}")
        msg.add_alternative(html, subtype="html")
        
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            s.starttls()
            s.login(SMTP_USER, SMTP_PASS)
            s.send_message(msg)
        return True
    except Exception as e:
        print(f"Invite email failed: {e}")
        return False


# ═══════════════════════════════════════════
# API — Create interview
# ═══════════════════════════════════════════
@router.post("/interview/create")
def create_interview(
    req: CreateInterviewReq,
    interviewer_id: str,           # in production: from JWT
    interviewer_name: str = "",
    interviewer_role: str = "HR",
):
    init_interview_table()
    
    iv_id = str(uuid.uuid4())
    room_id = generate_room_id(iv_id)
    
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO interviews 
        (id, room_id, title, candidate_id, candidate_email, candidate_name,
         interviewer_id, interviewer_name, interviewer_role,
         scheduled_at, duration_minutes, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        iv_id, room_id, req.title, req.candidate_id, req.candidate_email,
        req.candidate_name, interviewer_id, interviewer_name, interviewer_role,
        req.scheduled_at, req.duration_minutes, req.notes
    ))
    conn.commit()
    conn.close()
    
    # Send invite email
    email_sent = False
    if req.candidate_email:
        email_sent = send_interview_invite(
            req.candidate_email, req.candidate_name, interviewer_name,
            req.title, room_id, req.scheduled_at
        )
    
    # Create notification for candidate
    try:
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute("""INSERT INTO notifications (id, user_id, title, message, is_read, created_at)
            VALUES (?, ?, ?, ?, 0, ?)""",
            (str(uuid.uuid4()), req.candidate_id,
             f"📹 Interview Scheduled",
             f"{req.title} with {interviewer_name or 'Interviewer'} — Join: /video-call/{room_id}",
             datetime.utcnow().isoformat()))
        conn.commit()
        conn.close()
    except:
        pass
    
    return {
        "id": iv_id,
        "room_id": room_id,
        "join_link": f"{BASE_URL}/video-call/{room_id}",
        "email_sent": email_sent,
    }


# ═══════════════════════════════════════════
# API — List interviews (for candidate)
# ═══════════════════════════════════════════
@router.get("/interview/my")
def my_interviews(user_id: str):
    """Get all interviews where user is candidate"""
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    rows = cur.execute("""
        SELECT id, room_id, title, interviewer_name, interviewer_role,
               scheduled_at, duration_minutes, status, notes, created_at
        FROM interviews
        WHERE candidate_id = ?
        ORDER BY scheduled_at DESC
    """, (user_id,)).fetchall()
    conn.close()
    return {"interviews": [dict(r) for r in rows]}


# ═══════════════════════════════════════════
# API — List interviews (for interviewer)
# ═══════════════════════════════════════════
@router.get("/interview/created")
def created_interviews(user_id: str):
    """Get all interviews this user created"""
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    rows = cur.execute("""
        SELECT id, room_id, title, candidate_name, scheduled_at,
               duration_minutes, status, created_at
        FROM interviews
        WHERE interviewer_id = ?
        ORDER BY created_at DESC
    """, (user_id,)).fetchall()
    conn.close()
    return {"interviews": [dict(r) for r in rows]}


# ═══════════════════════════════════════════
# API — Get single interview by room_id
# ═══════════════════════════════════════════
@router.get("/interview/room/{room_id}")
def get_interview_by_room(room_id: str):
    """Anyone with room_id can fetch minimal info (for video page)"""
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    row = cur.execute("""
        SELECT id, room_id, title, interviewer_name, interviewer_role,
               candidate_name, scheduled_at, duration_minutes, status
        FROM interviews WHERE room_id = ?
    """, (room_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Interview not found or expired")
    return dict(row)


# ═══════════════════════════════════════════
# API — Update status
# ═══════════════════════════════════════════
@router.put("/interview/{iv_id}/status")
def update_interview_status(iv_id: str, req: UpdateStatusReq):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("UPDATE interviews SET status=? WHERE id=?", (req.status, iv_id))
    conn.commit()
    conn.close()
    return {"status": req.status, "id": iv_id}


# ═══════════════════════════════════════════
# API — Cancel
# ═══════════════════════════════════════════
@router.delete("/interview/{iv_id}")
def cancel_interview(iv_id: str):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("UPDATE interviews SET status='CANCELLED' WHERE id=?", (iv_id,))
    conn.commit()
    conn.close()
    return {"status": "CANCELLED", "id": iv_id}