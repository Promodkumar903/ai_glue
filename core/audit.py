# ============================================================
# AI GLUE v8.0 — AUDIT ENGINE (Immutable)
# ============================================================
# Engine: E-03
# Purpose: Hash-chained immutable audit log
# ============================================================

import hashlib
import json
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from core.database import AuditEvent, db

class AuditEngine:
    _last_hash: Optional[str] = None

    @classmethod
    def _compute_entry_hash(cls, prev_hash: Optional[str], after: Dict, timestamp: str) -> str:
        content = {
            "prev_hash": prev_hash or "GENESIS",
            "after": after,
            "timestamp": timestamp
        }
        content_str = json.dumps(content, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()

    @classmethod
    def log_event(
        cls,
        actor_id: str,
        action: str,
        target_type: str,
        target_id: str,
        before: Optional[Dict] = None,
        after: Optional[Dict] = None,
        reason: Optional[str] = None,
        source_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        session: Optional[Session] = None
    ) -> AuditEvent:
        if session is None:
            session = db.get_session()

        # Sanitize to remove secrets (I-11)
        if before:
            before = cls._sanitize(before)
        if after:
            after = cls._sanitize(after)

        timestamp = datetime.utcnow().isoformat()
        prev_hash = cls._last_hash
        entry_hash = cls._compute_entry_hash(prev_hash, after or {}, timestamp)
        cls._last_hash = entry_hash

        event = AuditEvent(
            actor_id=actor_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            before=before,
            after=after,
            reason=reason,
            source_ip=source_ip,
            user_agent=user_agent,
            prev_hash=prev_hash,
            entry_hash=entry_hash,
            timestamp=timestamp
        )
        session.add(event)
        session.commit()
        return event

    @staticmethod
    def _sanitize(data: Dict) -> Dict:
        sensitive_keys = {'password', 'password_hash', 'card', 'cvv', 'pan', 'aadhaar', 'secret', 'token', 'api_key'}
        sanitized = {}
        for k, v in data.items():
            if k.lower() in sensitive_keys:
                sanitized[k] = '***REDACTED***'
            elif isinstance(v, dict):
                sanitized[k] = AuditEngine._sanitize(v)
            else:
                sanitized[k] = v
        return sanitized

    @classmethod
    def verify_chain(cls, events: list) -> bool:
        if not events:
            return True
        prev_hash = None
        for event in events:
            computed = cls._compute_entry_hash(
                prev_hash,
                event.after or {},
                event.timestamp
            )
            if computed != event.entry_hash:
                return False
            prev_hash = event.entry_hash
        return True

# ---------- Singleton ----------
audit = AuditEngine()

# ---------- Alias for easy import (used by engines/application.py) ----------
def log_audit(*args, **kwargs):
    """Wrapper function for easy import from engines."""
    return AuditEngine.log_event(*args, **kwargs)