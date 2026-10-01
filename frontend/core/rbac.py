# ============================================================
# AI GLUE — RBAC ENGINE (ABAC – Attribute-Based Access Control)
# ============================================================
# Enforces permissions based on Role, Resource, Action, Scope.
# Default = DENY (C-06).
# ============================================================

from typing import List, Optional
from core.actors import RoleCode, ActorType, get_actor_type

class PermissionEngine:
    """Centralized permission checker for all actions."""

    # Permission Matrix: Role → Resource → (Action, Scope)
    # This is a canonical mapping. In production, load from DB/YAML.
    PERMISSIONS = {
        # ---------- STUDENT ----------
        RoleCode.STUDENT: {
            "PROFILE": [("CREATE", "SELF"), ("READ", "SELF"), ("UPDATE", "SELF"), ("DELETE", "SELF")],
            "APPLICATION": [("CREATE", "SELF"), ("READ", "SELF"), ("UPDATE", "SELF"), ("SUBMIT", "SELF"), ("DELETE", "SELF")],
            "DOCUMENT": [("CREATE", "SELF"), ("READ", "SELF"), ("UPDATE", "SELF"), ("DELETE", "SELF")],
            "OFFER": [("READ", "SELF"), ("UPDATE", "SELF")],
            "PAYMENT": [("CREATE", "SELF"), ("READ", "SELF")],
            "VISA_CASE": [("READ", "SELF")],
            "MESSAGE": [("CREATE", "SELF"), ("READ", "SELF")],
        },
        # ---------- JOB_SEEKER (same as STUDENT) ----------
        RoleCode.JOB_SEEKER: {
            "PROFILE": [("CREATE", "SELF"), ("READ", "SELF"), ("UPDATE", "SELF"), ("DELETE", "SELF")],
            "APPLICATION": [("CREATE", "SELF"), ("READ", "SELF"), ("UPDATE", "SELF"), ("SUBMIT", "SELF"), ("DELETE", "SELF")],
            "DOCUMENT": [("CREATE", "SELF"), ("READ", "SELF"), ("UPDATE", "SELF"), ("DELETE", "SELF")],
            "OFFER": [("READ", "SELF"), ("UPDATE", "SELF")],
            "PAYMENT": [("CREATE", "SELF"), ("READ", "SELF")],
            "VISA_CASE": [("READ", "SELF")],
            "MESSAGE": [("CREATE", "SELF"), ("READ", "SELF")],
        },
        # ---------- BROKER_AGENT ----------
        RoleCode.BROKER_AGENT: {
            "CANDIDATE_PROFILE": [("READ", "CASE")],  # requires consent
            "APPLICATION": [("CREATE", "CASE"), ("READ", "CASE"), ("UPDATE", "CASE"), ("SUBMIT", "CASE")],
            "DOCUMENT": [("READ", "CASE"), ("UPLOAD", "CASE")],
            "MESSAGE": [("CREATE", "CASE"), ("READ", "CASE")],
            "COMMISSION_EVENT": [("READ", "CASE")],
        },
        # ---------- BROKER_MANAGER ----------
        RoleCode.BROKER_MANAGER: {
            "APPLICATION": [("READ", "TEAM"), ("UPDATE", "TEAM"), ("SUBMIT", "TEAM"), ("REJECT", "TEAM")],
            "AGENT": [("CREATE", "TEAM"), ("READ", "TEAM"), ("UPDATE", "TEAM"), ("DEACTIVATE", "TEAM")],
            "COMMISSION_EVENT": [("READ", "TEAM"), ("EXPORT", "TEAM")],
            "CLIENT_DISTRIBUTION": [("READ", "TEAM")],
        },
        # ---------- BROKER_OWNER ----------
        RoleCode.BROKER_OWNER: {
            "APPLICATION": [("READ", "ORGANIZATION"), ("UPDATE", "ORGANIZATION"), ("SUBMIT", "ORGANIZATION"), ("REJECT", "ORGANIZATION"), ("APPROVE", "ORGANIZATION")],
            "AGENT": [("CREATE", "ORGANIZATION"), ("READ", "ORGANIZATION"), ("UPDATE", "ORGANIZATION"), ("DEACTIVATE", "ORGANIZATION")],
            "COMMISSION_EVENT": [("READ", "ORGANIZATION"), ("EXPORT", "ORGANIZATION")],
            "CLIENT_DISTRIBUTION": [("READ", "ORGANIZATION")],
            "FINANCIAL": [("READ", "ORGANIZATION")],
        },
        # ---------- RECRUITER ----------
        RoleCode.RECRUITER: {
            "VACANCY": [("CREATE", "ORGANIZATION"), ("READ", "ORGANIZATION"), ("UPDATE", "ORGANIZATION"), ("PUBLISH", "ORGANIZATION"), ("REVOKE", "ORGANIZATION")],
            "APPLICATION": [("READ", "ORGANIZATION"), ("UPDATE", "ORGANIZATION"), ("APPROVE", "ORGANIZATION"), ("REJECT", "ORGANIZATION")],
            "OFFER": [("CREATE", "ORGANIZATION"), ("READ", "ORGANIZATION"), ("UPDATE", "ORGANIZATION"), ("SEND", "ORGANIZATION")],
            "CANDIDATE_SEARCH": [("EXECUTE", "ORGANIZATION")],
        },
        # ---------- ADMISSIONS_OFFICER ----------
        RoleCode.ADMISSIONS_OFFICER: {
            "PROGRAMME": [("CREATE", "ORGANIZATION"), ("READ", "ORGANIZATION"), ("UPDATE", "ORGANIZATION"), ("PUBLISH", "ORGANIZATION"), ("REVOKE", "ORGANIZATION")],
            "APPLICATION": [("READ", "ORGANIZATION"), ("UPDATE", "ORGANIZATION"), ("APPROVE", "ORGANIZATION"), ("REJECT", "ORGANIZATION")],
            "OFFER": [("CREATE", "ORGANIZATION"), ("READ", "ORGANIZATION"), ("UPDATE", "ORGANIZATION"), ("SEND", "ORGANIZATION")],
        },
        # ---------- ORG_ADMIN ----------
        RoleCode.ORG_ADMIN: {
            "ORGANIZATION": [("READ", "ORGANIZATION"), ("UPDATE", "ORGANIZATION"), ("VERIFY", "ORGANIZATION")],
            "ORGANIZATION_MEMBER": [("CREATE", "ORGANIZATION"), ("READ", "ORGANIZATION"), ("UPDATE", "ORGANIZATION"), ("DEACTIVATE", "ORGANIZATION")],
            "VACANCY": [("READ", "ORGANIZATION")],
            "PROGRAMME": [("READ", "ORGANIZATION")],
            "APPLICATION": [("READ", "ORGANIZATION")],
        },
        # ---------- ORG_OWNER ----------
        RoleCode.ORG_OWNER: {
            "ORGANIZATION": [("CREATE", "ORGANIZATION"), ("READ", "ORGANIZATION"), ("UPDATE", "ORGANIZATION"), ("DELETE", "ORGANIZATION"), ("VERIFY", "ORGANIZATION")],
            "ORGANIZATION_MEMBER": [("CREATE", "ORGANIZATION"), ("READ", "ORGANIZATION"), ("UPDATE", "ORGANIZATION"), ("DEACTIVATE", "ORGANIZATION")],
            "FINANCIAL": [("READ", "ORGANIZATION"), ("CREATE", "ORGANIZATION"), ("EXECUTE", "ORGANIZATION")],
            "CONTRACT": [("APPROVE", "ORGANIZATION"), ("SIGN", "ORGANIZATION")],
        },
        # ---------- MASTER ADMIN ROLES ----------
        RoleCode.SYSTEM_OWNER: {
            "TENANT": [("CREATE", "SYSTEM"), ("READ", "SYSTEM"), ("UPDATE", "SYSTEM"), ("DELETE", "SYSTEM")],
            "BILLING": [("READ", "SYSTEM"), ("EXECUTE", "SYSTEM")],
            "PLATFORM_CONFIG": [("READ", "SYSTEM"), ("UPDATE", "SYSTEM")],
        },
        RoleCode.GOVERNANCE_ADMIN: {
            "EVIDENCE": [("READ", "TENANT"), ("VERIFY", "TENANT"), ("REVOKE", "TENANT")],
            "SOURCE": [("CREATE", "TENANT"), ("READ", "TENANT"), ("UPDATE", "TENANT"), ("VERIFY", "TENANT")],
            "CONSTITUTION_AMENDMENT": [("REVIEW", "TENANT"), ("APPROVE", "TENANT"), ("REJECT", "TENANT")],
            "MODEL_REGISTRY": [("APPROVE", "TENANT"), ("KILL", "TENANT")],
        },
        RoleCode.OPERATIONS_ADMIN: {
            "CONNECTOR": [("READ", "SYSTEM"), ("UPDATE", "SYSTEM"), ("CONFIGURE", "SYSTEM")],
            "ORGANIZATION_VERIFICATION": [("APPROVE", "SYSTEM"), ("REJECT", "SYSTEM")],
            "SUPPORT_TICKET": [("READ", "SYSTEM"), ("UPDATE", "SYSTEM"), ("RESOLVE", "SYSTEM")],
        },
        RoleCode.FINANCE_ADMIN: {
            "INVOICE": [("READ", "SYSTEM"), ("CREATE", "SYSTEM"), ("EXPORT", "SYSTEM")],
            "REFUND": [("APPROVE", "SYSTEM")],
            "RECONCILIATION": [("EXECUTE", "SYSTEM"), ("READ", "SYSTEM")],
        },
        RoleCode.SECURITY_ADMIN: {
            "SECURITY_EVENT": [("READ", "SYSTEM"), ("RESOLVE", "SYSTEM")],
            "MFA_CONFIG": [("UPDATE", "SYSTEM")],
            "IP_WHITELIST": [("CREATE", "SYSTEM"), ("READ", "SYSTEM"), ("UPDATE", "SYSTEM"), ("DELETE", "SYSTEM")],
        },
        RoleCode.SUPPORT_ADMIN: {
            "SUPPORT_TICKET": [("READ", "CASE"), ("UPDATE", "CASE"), ("RESOLVE", "CASE")],
            "CASE": [("READ", "CASE")],
        },
    }

    # Scope hierarchy for containment checks
    SCOPE_HIERARCHY = {
        "SELF": 1,
        "CASE": 2,
        "TEAM": 3,
        "ORGANIZATION": 4,
        "TENANT": 5,
        "SYSTEM": 6,
    }

    @classmethod
    def has_permission(cls, role: RoleCode, resource: str, action: str, required_scope: str = "SELF") -> bool:
        """Check if a given role has permission to perform action on resource."""
        if role not in cls.PERMISSIONS:
            return False
        resource_actions = cls.PERMISSIONS[role].get(resource)
        if not resource_actions:
            return False
        for allowed_action, allowed_scope in resource_actions:
            if allowed_action == action:
                # Check if allowed_scope encompasses required_scope
                if cls.SCOPE_HIERARCHY.get(allowed_scope, 0) >= cls.SCOPE_HIERARCHY.get(required_scope, 0):
                    return True
        return False

    @classmethod
    def get_permissions_for_role(cls, role: RoleCode) -> dict:
        """Get full permission map for a role."""
        return cls.PERMISSIONS.get(role, {})