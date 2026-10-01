"""
AI GLUE — Notification Engine (Fixed)
"""
from sqlalchemy.orm import Session
from core.database import db, Notification, User
from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class NotificationEngine:

    @staticmethod
    def _send_email(to_email: str, subject: str, body: str):
        print(f"Email to {to_email}: {subject}")
        smtp_host = os.getenv("SMTP_HOST", "")
        smtp_user = os.getenv("SMTP_USER", "")
        if not smtp_host or not smtp_user:
            return True
        try:
            smtp_port = int(os.getenv("SMTP_PORT", 587))
            smtp_pass = os.getenv("SMTP_PASS", "")
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))
            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            print(f"SMTP Error: {e}")
            return False

    @staticmethod
    def create_notification(user_id: str, title: str, message: str, session: Session = None):
        _auto_close = session is None
        if session is None:
            session = db.get_session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return {"error": "User not found"}

            notif = Notification(
                user_id=user_id,
                title=title,
                message=message,
                is_read=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(notif)
            session.commit()
            session.refresh(notif)

            if user.email:
                NotificationEngine._send_email(user.email, title, message)

            return {"notification_id": str(notif.id), "message": "Notification sent"}
        finally:
            if _auto_close:
                session.close()

    @staticmethod
    def get_user_notifications(user_id: str, session: Session = None):
        _auto_close = session is None
        if session is None:
            session = db.get_session()
        try:
            notifs = session.query(Notification).filter(
                Notification.user_id == user_id
            ).order_by(Notification.created_at.desc()).limit(20).all()

            return {
                "notifications": [
                    {
                        "id": str(n.id),
                        "title": n.title,
                        "message": n.message,
                        "is_read": n.is_read,
                        "created_at": str(n.created_at) if n.created_at else None,
                    }
                    for n in notifs
                ]
            }
        finally:
            if _auto_close:
                session.close()

    @staticmethod
    def mark_as_read(notification_id: str, session: Session = None):
        _auto_close = session is None
        if session is None:
            session = db.get_session()
        try:
            notif = session.query(Notification).filter(Notification.id == notification_id).first()
            if not notif:
                return {"error": "Notification not found"}
            notif.is_read = True
            notif.updated_at = datetime.utcnow()
            session.commit()
            return {"message": "Notification marked as read"}
        finally:
            if _auto_close:
                session.close()


notification_engine = NotificationEngine()