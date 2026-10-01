# ============================================================
# AI GLUE v8.0 — TENANT CONTEXT
# ============================================================
# Purpose: Store current tenant/organization per request
# ============================================================

import contextvars
from typing import Optional

_current_tenant_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar('current_tenant_id', default=None)
_current_org_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar('current_org_id', default=None)

def set_current_tenant(tenant_id: Optional[str], org_id: Optional[str] = None):
    _current_tenant_id.set(tenant_id)
    _current_org_id.set(org_id)

def get_current_tenant() -> Optional[str]:
    return _current_tenant_id.get()

def get_current_org() -> Optional[str]:
    return _current_org_id.get()

def clear_tenant():
    _current_tenant_id.set(None)
    _current_org_id.set(None)