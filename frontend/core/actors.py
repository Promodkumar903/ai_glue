# ============================================================
# AI GLUE — ACTOR REGISTRY (Canonical Actors & Roles)
# ============================================================
# 8 Actors, 15+ Roles, Hierarchy defined.
# Used for permission checks and audit logging.
# ============================================================

from enum import Enum

class ActorType(str, Enum):
    ENDUSER = "EndUser"
    BROKER = "Broker"
    COMPANY = "Company"
    INSTITUTION = "Institution"
    GOVERNMENT = "Government"
    AIGLUE = "AIGlue"
    MASTERADMIN = "MasterAdmin"
    SERVICEACTOR = "ServiceActor"

class RoleCode(str, Enum):
    # EndUser Roles
    STUDENT = "STUDENT"
    JOB_SEEKER = "JOB_SEEKER"
    # Broker Roles
    BROKER_OWNER = "BROKER_OWNER"
    BROKER_MANAGER = "BROKER_MANAGER"
    BROKER_AGENT = "BROKER_AGENT"
    # Company/Institution Roles
    ORG_OWNER = "ORG_OWNER"
    ORG_ADMIN = "ORG_ADMIN"
    RECRUITER = "RECRUITER"
    ADMISSIONS_OFFICER = "ADMISSIONS_OFFICER"
    # Master Admin Roles
    SYSTEM_OWNER = "SYSTEM_OWNER"
    GOVERNANCE_ADMIN = "GOVERNANCE_ADMIN"
    OPERATIONS_ADMIN = "OPERATIONS_ADMIN"
    SECURITY_ADMIN = "SECURITY_ADMIN"
    FINANCE_ADMIN = "FINANCE_ADMIN"
    SUPPORT_ADMIN = "SUPPORT_ADMIN"

# Mapping: Actor Type → Allowed Roles
ACTOR_ROLES = {
    ActorType.ENDUSER: [RoleCode.STUDENT, RoleCode.JOB_SEEKER],
    ActorType.BROKER: [RoleCode.BROKER_OWNER, RoleCode.BROKER_MANAGER, RoleCode.BROKER_AGENT],
    ActorType.COMPANY: [RoleCode.ORG_OWNER, RoleCode.ORG_ADMIN, RoleCode.RECRUITER],
    ActorType.INSTITUTION: [RoleCode.ORG_OWNER, RoleCode.ORG_ADMIN, RoleCode.ADMISSIONS_OFFICER],
    ActorType.GOVERNMENT: [],
    ActorType.AIGLUE: [],
    ActorType.MASTERADMIN: [RoleCode.SYSTEM_OWNER, RoleCode.GOVERNANCE_ADMIN, RoleCode.OPERATIONS_ADMIN,
                           RoleCode.SECURITY_ADMIN, RoleCode.FINANCE_ADMIN, RoleCode.SUPPORT_ADMIN],
    ActorType.SERVICEACTOR: [],
}

# Role Hierarchy (for escalation checks)
ROLE_HIERARCHY = {
    RoleCode.BROKER_AGENT: RoleCode.BROKER_MANAGER,
    RoleCode.BROKER_MANAGER: RoleCode.BROKER_OWNER,
    RoleCode.RECRUITER: RoleCode.ORG_ADMIN,
    RoleCode.ADMISSIONS_OFFICER: RoleCode.ORG_ADMIN,
    RoleCode.ORG_ADMIN: RoleCode.ORG_OWNER,
    # MasterAdmin roles are independent (no upward escalation)
}

def get_actor_type(role_code: str) -> ActorType:
    """Return the Actor type that owns a given role."""
    for actor, roles in ACTOR_ROLES.items():
        if role_code in roles:
            return actor
    return None

def is_role_higher(role1: str, role2: str) -> bool:
    """Check if role1 is higher/equal in hierarchy than role2."""
    if role1 == role2:
        return True
    current = role2
    while current in ROLE_HIERARCHY:
        parent = ROLE_HIERARCHY[current]
        if parent == role1:
            return True
        current = parent
    return False