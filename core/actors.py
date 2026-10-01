# ============================================================
# AI GLUE v8.0 — ACTOR & ROLE REGISTRY
# ============================================================
# Engine: E-04
# Purpose: Define all actors and roles
# ============================================================

from typing import List, Optional

# ---------- Actor IDs ----------
class ActorID:
    END_USER = "ACT-001"
    BROKER = "ACT-002"
    COMPANY = "ACT-003"
    INSTITUTION = "ACT-004"
    GOVERNMENT = "ACT-005"
    AI_GLUE = "ACT-006"
    MASTER_ADMIN = "ACT-007"
    SERVICE_ACTOR = "ACT-008"

# ---------- Actor Definition ----------
class Actor:
    def __init__(self, id: str, name: str, description: str, actor_type: str, allowed_apps: List[str], max_authority: int):
        self.id = id
        self.name = name
        self.description = description
        self.type = actor_type
        self.allowed_apps = allowed_apps
        self.max_authority = max_authority  # L0-L4 as int

ACTORS = [
    Actor(ActorID.END_USER, "EndUser", "Student or Job Seeker", "Human", ["User App"], 2),
    Actor(ActorID.BROKER, "Broker", "Recruitment/Education Agent", "Human", ["Broker App"], 3),
    Actor(ActorID.COMPANY, "Company", "Employer Organization", "Organization", ["Company App"], 4),
    Actor(ActorID.INSTITUTION, "Institution", "Educational Institution", "Organization", ["Company/Institution App"], 4),
    Actor(ActorID.GOVERNMENT, "Government", "Regulatory Body/Embassy", "Organization", ["Admin App (view)"], 1),
    Actor(ActorID.AI_GLUE, "AIGlue", "AI Glue System", "System", ["All (Backend)"], 4),
    Actor(ActorID.MASTER_ADMIN, "MasterAdmin", "Platform Admin", "Human", ["Master Admin App"], 4),
    Actor(ActorID.SERVICE_ACTOR, "ServiceActor", "Internal Services / Background Jobs", "System", ["Internal APIs"], 4),
]

# ---------- Role Codes ----------
class RoleCode:
    # EndUser
    STUDENT = "STUDENT"
    JOB_SEEKER = "JOB_SEEKER"
    # Broker
    BROKER_OWNER = "BROKER_OWNER"
    BROKER_MANAGER = "BROKER_MANAGER"
    BROKER_AGENT = "BROKER_AGENT"
    # Company
    ORG_OWNER = "ORG_OWNER"
    ORG_ADMIN = "ORG_ADMIN"
    RECRUITER = "RECRUITER"
    ADMISSIONS_OFFICER = "ADMISSIONS_OFFICER"
    # Master Admin
    SYSTEM_OWNER = "SYSTEM_OWNER"
    GOVERNANCE_ADMIN = "GOVERNANCE_ADMIN"
    OPERATIONS_ADMIN = "OPERATIONS_ADMIN"
    SECURITY_ADMIN = "SECURITY_ADMIN"
    FINANCE_ADMIN = "FINANCE_ADMIN"
    SUPPORT_ADMIN = "SUPPORT_ADMIN"

class Role:
    def __init__(self, code: str, name: str, description: str, actor_type: str, parent_role: Optional[str] = None):
        self.code = code
        self.name = name
        self.description = description
        self.actor_type = actor_type
        self.parent_role = parent_role

ROLES = [
    Role(RoleCode.STUDENT, "Student", "Educational Candidate", "EndUser"),
    Role(RoleCode.JOB_SEEKER, "Job Seeker", "Employment Candidate", "EndUser"),
    Role(RoleCode.BROKER_OWNER, "Broker Owner", "Brokerage Owner", "Broker"),
    Role(RoleCode.BROKER_MANAGER, "Broker Manager", "Manages Agents", "Broker", RoleCode.BROKER_OWNER),
    Role(RoleCode.BROKER_AGENT, "Broker Agent", "Frontline Agent", "Broker", RoleCode.BROKER_MANAGER),
    Role(RoleCode.ORG_OWNER, "Organization Owner", "Legal Owner", "Company/Institution"),
    Role(RoleCode.ORG_ADMIN, "Organization Admin", "Day-to-Day Ops", "Company/Institution", RoleCode.ORG_OWNER),
    Role(RoleCode.RECRUITER, "Recruiter", "Hiring Manager", "Company", RoleCode.ORG_ADMIN),
    Role(RoleCode.ADMISSIONS_OFFICER, "Admissions Officer", "Programme Admissions", "Institution", RoleCode.ORG_ADMIN),
    Role(RoleCode.SYSTEM_OWNER, "System Owner", "Billing, Platform Config, DR", "MasterAdmin"),
    Role(RoleCode.GOVERNANCE_ADMIN, "Governance Admin", "Source Verification, Audit", "MasterAdmin"),
    Role(RoleCode.OPERATIONS_ADMIN, "Operations Admin", "Monitoring, Connectors", "MasterAdmin"),
    Role(RoleCode.SECURITY_ADMIN, "Security Admin", "Security Events, MFA", "MasterAdmin"),
    Role(RoleCode.FINANCE_ADMIN, "Finance Admin", "Invoices, Refunds", "MasterAdmin"),
    Role(RoleCode.SUPPORT_ADMIN, "Support Admin", "Tickets", "MasterAdmin"),
]

class ActorRegistry:
    @staticmethod
    def get_actor(actor_id: str) -> Optional[Actor]:
        for actor in ACTORS:
            if actor.id == actor_id:
                return actor
        return None

    @staticmethod
    def get_role(role_code: str) -> Optional[Role]:
        for role in ROLES:
            if role.code == role_code:
                return role
        return None

    @staticmethod
    def get_roles_for_actor(actor_type: str) -> List[Role]:
        return [r for r in ROLES if r.actor_type == actor_type]

    @staticmethod
    def get_all_actors() -> List[dict]:
        return [{"id": a.id, "name": a.name, "description": a.description, "type": a.type, "max_authority": a.max_authority} for a in ACTORS]

    @staticmethod
    def get_all_roles() -> List[dict]:
        return [{"code": r.code, "name": r.name, "description": r.description, "actor_type": r.actor_type, "parent": r.parent_role} for r in ROLES]

actor_registry = ActorRegistry()