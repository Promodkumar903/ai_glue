# ============================================================
# AI GLUE — TENANT CONTEXT (Request-scoped)
# ============================================================
# Provides current tenant and organization IDs from request context.
# Used by TenantAwareQuery to auto-filter queries.
# ============================================================

from threading import local

_thread_local = local()

def set_current_tenant(tenant_id: str):
    _thread_local.tenant_id = tenant_id

def get_current_tenant() -> str:
    return getattr(_thread_local, 'tenant_id', None)

def set_current_org(org_id: str):
    _thread_local.org_id = org_id

def get_current_org() -> str:
    return getattr(_thread_local, 'org_id', None)

def clear_tenant_context():
    _thread_local.tenant_id = None
    _thread_local.org_id = None