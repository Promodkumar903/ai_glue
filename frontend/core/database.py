# ============================================================
# AI GLUE v8.0 — DATABASE SCHEMA (ZERO-GAP FINAL)
# ============================================================
# Based on FINAL MASTER BLUEPRINT v4.0
# 27 Canonical Tables — Identity, Profile, Opportunity, Application,
# Document, Evidence, Connector, Offer, Contract, Financial, Visa,
# Communication, Governance, Audit, Learning.
# SQLAlchemy ORM — PostgreSQL Compatible (with SQLite fallback for tests).
# ============================================================

import os
import uuid
from datetime import datetime, timedelta
from sqlalchemy import (
    create_engine, Column, String, Boolean, DateTime, Float, Integer,
    JSON, ForeignKey, Text, Enum, DECIMAL, TIMESTAMP, BigInteger, Index,
    UniqueConstraint, CheckConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Query, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

# ---------- Helper Functions ----------
def generate_uuid():
    return str(uuid.uuid4())

def now_utc():
    return datetime.utcnow()

# ---------- Tenant-Aware Query (Auto-Filter) ----------
class TenantAwareQuery(Query):
    """Automatically filters queries by tenant/org if applicable."""
    def __iter__(self):
        self._apply_tenant_filters()
        return super().__iter__()

    def _apply_tenant_filters(self):
        if hasattr(self, '_tenant_filters_applied'):
            return self
        # In production, get_current_tenant() from request context
        from core.tenant import get_current_tenant, get_current_org
        if self._entities:
            entity = self._entities[0]
            if hasattr(entity, 'entity_zero'):
                model = entity.entity_zero.class_
                if hasattr(model, 'tenant_id'):
                    tenant_id = get_current_tenant()
                    if tenant_id:
                        self = self.filter(model.tenant_id == tenant_id)
                if hasattr(model, 'organization_id'):
                    org_id = get_current_org()
                    if org_id:
                        self = self.filter(model.organization_id == org_id)
        self._tenant_filters_applied = True
        return self

# ---------- Database Engine ----------
class DatabaseEngine:
    def __init__(self, db_url=None):
        self.db_url = db_url or os.getenv('DATABASE_URL', 'sqlite:///./ai_glue.db')
        connect_args = {"check_same_thread": False} if self.db_url.startswith('sqlite') else {}
        self.engine = create_engine(self.db_url, connect_args=connect_args, pool_pre_ping=True)
        self.Session = sessionmaker(bind=self.engine, query_cls=TenantAwareQuery)

    def create_tables(self):
        Base.metadata.create_all(self.engine)

    def get_session(self):
        return self.Session()

    def drop_tables(self):
        Base.metadata.drop_all(self.engine)

db = DatabaseEngine()

# ============================================================
# MODELS (All tables — 27 tables)
# ============================================================

# ---------- 1. TENANT ----------
class Tenant(Base):
    __tablename__ = 'tenants'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # BROKER_FIRM, EMPLOYER, UNIVERSITY
    plan = Column(String(50), default='FREE')  # FREE, BASIC, PRO, ENTERPRISE
    config = Column(JSON, default={})
    status = Column(String(20), default='ACTIVE')
    created_at = Column(TIMESTAMP, default=now_utc)
    updated_at = Column(TIMESTAMP, default=now_utc, onupdate=now_utc)

# ---------- 2. USER ----------
class User(Base):
    __tablename__ = 'users'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(200))
    phone = Column(String(20))
    status = Column(String(20), default='PENDING')  # PENDING, ACTIVE, LOCKED, DELETED
    tenant_id = Column(String(36), ForeignKey('tenants.id'), nullable=True)
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255), nullable=True)
    login_attempts = Column(Integer, default=0)
    locked_until = Column(TIMESTAMP, nullable=True)
    referral_code = Column(String(50), nullable=True)
    created_at = Column(TIMESTAMP, default=now_utc)
    updated_at = Column(TIMESTAMP, default=now_utc, onupdate=now_utc)

# ---------- 3. USER_ROLE ----------
class UserRole(Base):
    __tablename__ = 'user_roles'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    role_code = Column(String(50), nullable=False)  # STUDENT, JOB_SEEKER, BROKER_AGENT, BROKER_MANAGER, BROKER_OWNER, RECRUITER, ADMISSIONS_OFFICER, ORG_ADMIN, ORG_OWNER, SYSTEM_OWNER, GOVERNANCE_ADMIN, OPERATIONS_ADMIN, SECURITY_ADMIN, FINANCE_ADMIN, SUPPORT_ADMIN
    granted_at = Column(TIMESTAMP, default=now_utc)
    granted_by = Column(String(36), ForeignKey('users.id'), nullable=True)
    revoked_at = Column(TIMESTAMP, nullable=True)

# ---------- 4. ORGANIZATION ----------
class Organization(Base):
    __tablename__ = 'organizations'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # COMPANY, INSTITUTION
    tenant_id = Column(String(36), ForeignKey('tenants.id'), nullable=True)
    verification_status = Column(String(20), default='PENDING')  # PENDING, VERIFIED, REJECTED
    verified_by = Column(String(36), ForeignKey('users.id'), nullable=True)
    verified_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, default=now_utc)
    updated_at = Column(TIMESTAMP, default=now_utc, onupdate=now_utc)

# ---------- 5. ORGANIZATION_MEMBER ----------
class OrganizationMember(Base):
    __tablename__ = 'organization_members'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey('organizations.id'), nullable=False)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    role_code = Column(String(50), nullable=False)  # RECRUITER, ADMISSIONS_OFFICER, ORG_ADMIN, ORG_OWNER
    added_at = Column(TIMESTAMP, default=now_utc)
    removed_at = Column(TIMESTAMP, nullable=True)

# ---------- 6. BROKER_FIRM ----------
class BrokerFirm(Base):
    __tablename__ = 'broker_firms'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    owner_user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    tenant_id = Column(String(36), ForeignKey('tenants.id'), nullable=True)
    verification_status = Column(String(20), default='PENDING')
    created_at = Column(TIMESTAMP, default=now_utc)
    updated_at = Column(TIMESTAMP, default=now_utc, onupdate=now_utc)

# ---------- 7. BROKER_AGENT ----------
class BrokerAgent(Base):
    __tablename__ = 'broker_agents'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    broker_firm_id = Column(String(36), ForeignKey('broker_firms.id'), nullable=False)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    role_code = Column(String(50), nullable=False)  # BROKER_OWNER, BROKER_MANAGER, BROKER_AGENT
    added_at = Column(TIMESTAMP, default=now_utc)
    removed_at = Column(TIMESTAMP, nullable=True)

# ---------- 8. CANDIDATE_PROFILE ----------
class CandidateProfile(Base):
    __tablename__ = 'candidate_profiles'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey('users.id'), unique=True, nullable=False)
    education = Column(JSON, default=[])
    experience = Column(JSON, default=[])
    skills = Column(JSON, default=[])
    languages = Column(JSON, default=[])
    preferences = Column(JSON, default={})
    completeness_pct = Column(Integer, default=0)
    updated_at = Column(TIMESTAMP, default=now_utc, onupdate=now_utc)

# ---------- 9. CANDIDATE_CONSENT ----------
class CandidateConsent(Base):
    __tablename__ = 'candidate_consent'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    candidate_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    broker_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    status = Column(String(20), default='ACTIVE')  # ACTIVE, REVOKED
    granted_at = Column(TIMESTAMP, default=now_utc)
    revoked_at = Column(TIMESTAMP, nullable=True)

# ---------- 10. OPPORTUNITY ----------
class Opportunity(Base):
    __tablename__ = 'opportunities'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey('organizations.id'), nullable=False)
    type = Column(String(50), nullable=False)  # VACANCY, PROGRAMME, SCHOLARSHIP
    title = Column(String(255), nullable=False)
    description = Column(Text)
    requirements = Column(JSON, default={})
    status = Column(String(20), default='DRAFT')  # DRAFT, OPEN, CLOSED, EXPIRED
    deadline = Column(TIMESTAMP, nullable=True)
    fees = Column(JSON, default={})
    capacity = Column(Integer, nullable=True)
    filled_count = Column(Integer, default=0)
    first_seen = Column(TIMESTAMP, default=now_utc)
    last_seen = Column(TIMESTAMP, default=now_utc)
    last_verified = Column(TIMESTAMP, nullable=True)
    version = Column(Integer, default=1)
    created_at = Column(TIMESTAMP, default=now_utc)
    updated_at = Column(TIMESTAMP, default=now_utc, onupdate=now_utc)
    __table_args__ = (
        Index('idx_opp_org', 'organization_id'),
        Index('idx_opp_status', 'status'),
        Index('idx_opp_deadline', 'deadline'),
    )

# ---------- 11. ELIGIBILITY_RESULT ----------
class EligibilityResult(Base):
    __tablename__ = 'eligibility_results'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    candidate_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    opportunity_id = Column(String(36), ForeignKey('opportunities.id'), nullable=False)
    hard_requirements_pass = Column(Boolean, default=False)
    soft_score = Column(Float, default=0.0)
    explanation = Column(Text)
    computed_at = Column(TIMESTAMP, default=now_utc)
    model_version = Column(String(36), nullable=True)  # References model_registry.id

# ---------- 12. MATCH_SCORE ----------
class MatchScore(Base):
    __tablename__ = 'match_scores'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    candidate_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    opportunity_id = Column(String(36), ForeignKey('opportunities.id'), nullable=False)
    score = Column(Float, nullable=False)
    ranking_position = Column(Integer)
    alternative_type = Column(String(20))  # DREAM, TARGET, SAFE
    computed_at = Column(TIMESTAMP, default=now_utc)
    model_version = Column(String(36), nullable=True)

# ---------- 13. RECOMMENDATION ----------
class Recommendation(Base):
    __tablename__ = 'recommendations'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    recipient_actor_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    candidate_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    opportunity_id = Column(String(36), ForeignKey('opportunities.id'), nullable=False)
    confidence = Column(Float, default=0.0)
    status = Column(String(20), default='PENDING')  # PENDING, FORWARDED, DISMISSED
    human_override_by = Column(String(36), ForeignKey('users.id'), nullable=True)
    created_at = Column(TIMESTAMP, default=now_utc)

# ---------- 14. CASE ----------
class Case(Base):
    __tablename__ = 'cases'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    candidate_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    case_type = Column(String(50), nullable=False)  # ADMISSION, JOB, SCHOLARSHIP, VISA, INTERNSHIP
    status = Column(String(50), default='OPEN')
    created_at = Column(TIMESTAMP, default=now_utc)
    updated_at = Column(TIMESTAMP, default=now_utc, onupdate=now_utc)

# ---------- 15. APPLICATION ----------
class Application(Base):
    __tablename__ = 'applications'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    case_id = Column(String(36), ForeignKey('cases.id'), nullable=False)
    candidate_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    opportunity_id = Column(String(36), ForeignKey('opportunities.id'), nullable=False)
    broker_id = Column(String(36), ForeignKey('users.id'), nullable=True)
    status = Column(String(50), default='DRAFT')  # DRAFT, READY, SUBMITTED, RECEIVED, UNDER_REVIEW, SHORTLISTED, INTERVIEW, OFFERED, ACCEPTED, REJECTED, WITHDRAWN, EXPIRED, CLOSED
    segment = Column(String(50), nullable=True)  # For fairness monitoring
    match_score = Column(Float)
    submitted_at = Column(TIMESTAMP, nullable=True)
    plan_hash = Column(String(64))
    idempotency_key = Column(String(255), unique=True, nullable=True)
    created_at = Column(TIMESTAMP, default=now_utc)
    updated_at = Column(TIMESTAMP, default=now_utc, onupdate=now_utc)
    __table_args__ = (
        Index('idx_app_user', 'candidate_id'),
        Index('idx_app_opp', 'opportunity_id'),
        Index('idx_app_status', 'status'),
        Index('idx_app_broker', 'broker_id'),
        UniqueConstraint('idempotency_key', name='uq_app_idempotency'),
    )

# ---------- 16. DOCUMENT ----------
class Document(Base):
    __tablename__ = 'documents'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    owner_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    type = Column(String(50), nullable=False)  # CV, PASSPORT, TRANSCRIPT, DEGREE, SOP, MEDICAL, FINANCIAL
    country_format = Column(String(50))
    version = Column(Integer, default=1)
    file_hash = Column(String(128))
    storage_url = Column(String(500))
    uploaded_at = Column(TIMESTAMP, default=now_utc)
    expiry_date = Column(TIMESTAMP, nullable=True)
    translation_status = Column(String(20), default='NOT_REQUIRED')
    attestation_status = Column(String(20), default='NOT_REQUIRED')
    verified = Column(Boolean, default=False)
    __table_args__ = (
        Index('idx_doc_owner', 'owner_id'),
        Index('idx_doc_type', 'type'),
    )

# ---------- 17. DOCUMENT_CHECKLIST ----------
class DocumentChecklist(Base):
    __tablename__ = 'document_checklists'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    application_id = Column(String(36), ForeignKey('applications.id'), nullable=False)
    document_type = Column(String(50), nullable=False)
    status = Column(String(20), default='MISSING')  # MISSING, UPLOADED, VERIFIED, EXPIRED

# ---------- 18. SOURCE ----------
class Source(Base):
    __tablename__ = 'sources'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    authority_level = Column(String(20), nullable=False)  # OFFICIAL, GOVERNMENT, UNIVERSITY, COMPANY, AGENCY, UNVERIFIED
    url = Column(String(500))
    status = Column(String(20), default='HEALTHY')  # HEALTHY, DEGRADED, DOWN
    last_crawled = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, default=now_utc)
    updated_at = Column(TIMESTAMP, default=now_utc, onupdate=now_utc)

# ---------- 19. EVIDENCE ----------
class Evidence(Base):
    __tablename__ = 'evidence'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    claim_id = Column(String(36), nullable=False)  # Polymorphic target
    source_id = Column(String(36), ForeignKey('sources.id'), nullable=False)
    captured_at = Column(TIMESTAMP, default=now_utc)
    hash = Column(String(128))
    confidence = Column(Float, default=0.0)
    freshness_days = Column(Integer)
    valid_until = Column(TIMESTAMP, nullable=True)
    source_url = Column(String(500))
    source_domain = Column(String(255))
    content = Column(JSON, default={})

# ---------- 20. CONNECTOR ----------
class Connector(Base):
    __tablename__ = 'connectors'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    country = Column(String(50), nullable=True)
    type = Column(String(50), nullable=False)  # VISA, UNIVERSITY, GOVT_PORTAL, PAYMENT_GATEWAY
    auth_method = Column(String(50))
    status = Column(String(20), default='HEALTHY')  # HEALTHY, DEGRADED, DOWN
    last_success_at = Column(TIMESTAMP, nullable=True)
    last_failure_at = Column(TIMESTAMP, nullable=True)
    error_count_24h = Column(Integer, default=0)
    rate_limit_per_min = Column(Integer, default=60)
    config = Column(JSON, default={})
    created_at = Column(TIMESTAMP, default=now_utc)
    updated_at = Column(TIMESTAMP, default=now_utc, onupdate=now_utc)

# ---------- 21. OFFER ----------
class Offer(Base):
    __tablename__ = 'offers'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    application_id = Column(String(36), ForeignKey('applications.id'), nullable=False)
    organization_id = Column(String(36), ForeignKey('organizations.id'), nullable=False)
    terms = Column(JSON, default={})
    scholarship_amount = Column(DECIMAL(15,2), default=0)
    status = Column(String(20), default='DRAFT')  # DRAFT, SENT, ACCEPTED, DECLINED, EXPIRED
    deadline = Column(TIMESTAMP, nullable=True)
    sent_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, default=now_utc)
    updated_at = Column(TIMESTAMP, default=now_utc, onupdate=now_utc)

# ---------- 22. CONTRACT ----------
class Contract(Base):
    __tablename__ = 'contracts'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    offer_id = Column(String(36), ForeignKey('offers.id'), nullable=False)
    candidate_signature_at = Column(TIMESTAMP, nullable=True)
    organization_signature_at = Column(TIMESTAMP, nullable=True)
    status = Column(String(20), default='PENDING')  # PENDING, SIGNED, VOID
    document_id = Column(String(36), nullable=True)  # references documents.id
    created_at = Column(TIMESTAMP, default=now_utc)
    updated_at = Column(TIMESTAMP, default=now_utc, onupdate=now_utc)

# ---------- 23. PAYMENT ----------
class Payment(Base):
    __tablename__ = 'payments'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    payer_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    payee_type = Column(String(50), nullable=False)  # PLATFORM, ORGANIZATION
    payee_id = Column(String(36), nullable=True)  # organization_id if applicable
    amount = Column(DECIMAL(15,2), nullable=False)
    currency = Column(String(3), default='USD')
    idempotency_key = Column(String(255), unique=True, nullable=False)
    status = Column(String(20), default='PENDING')  # PENDING, SUCCESS, FAILED, REFUNDED
    gateway_ref = Column(String(255), nullable=True)
    payment_meta = Column(JSON, default={})
    created_at = Column(TIMESTAMP, default=now_utc)
    updated_at = Column(TIMESTAMP, default=now_utc, onupdate=now_utc)

# ---------- 24. COMMISSION_RULE ----------
class CommissionRule(Base):
    __tablename__ = 'commission_rules'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    broker_firm_id = Column(String(36), ForeignKey('broker_firms.id'), nullable=False)
    opportunity_id = Column(String(36), ForeignKey('opportunities.id'), nullable=True)
    type = Column(String(20), nullable=False)  # SUCCESS_BASED, FIXED
    rate_or_amount = Column(DECIMAL(15,2), nullable=False)
    trigger_event = Column(String(50), nullable=False)  # PLACEMENT_CONFIRMED
    created_at = Column(TIMESTAMP, default=now_utc)
    updated_at = Column(TIMESTAMP, default=now_utc, onupdate=now_utc)

# ---------- 25. COMMISSION_EVENT ----------
class CommissionEvent(Base):
    __tablename__ = 'commission_events'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    commission_rule_id = Column(String(36), ForeignKey('commission_rules.id'), nullable=False)
    application_id = Column(String(36), ForeignKey('applications.id'), nullable=False)
    amount = Column(DECIMAL(15,2), nullable=False)
    status = Column(String(20), default='PENDING')  # PENDING, INVOICED, PAID, DISPUTED, REFUNDED
    created_at = Column(TIMESTAMP, default=now_utc)
    updated_at = Column(TIMESTAMP, default=now_utc, onupdate=now_utc)

# ---------- 26. VISA_CASE ----------
class VisaCase(Base):
    __tablename__ = 'visa_cases'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    candidate_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    country = Column(String(50), nullable=False)
    visa_type = Column(String(50), nullable=False)
    status = Column(String(20), default='NOT_STARTED')  # NOT_STARTED, DOCUMENTS_PENDING, APPLIED, INTERVIEW, APPROVED, REJECTED, APPEALING
    applied_at = Column(TIMESTAMP, nullable=True)
    decision_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, default=now_utc)
    updated_at = Column(TIMESTAMP, default=now_utc, onupdate=now_utc)

# ---------- 27. VISA_APPOINTMENT ----------
class VisaAppointment(Base):
    __tablename__ = 'visa_appointments'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    visa_case_id = Column(String(36), ForeignKey('visa_cases.id'), nullable=False)
    scheduled_at = Column(TIMESTAMP, nullable=False)
    location = Column(String(255))
    status = Column(String(20), default='SCHEDULED')  # SCHEDULED, CANCELLED, COMPLETED

# ---------- 28. VISA_RULE ----------
class VisaRule(Base):
    __tablename__ = 'visa_rules'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    country = Column(String(50), nullable=False)
    visa_type = Column(String(50), nullable=False)
    rules = Column(JSON, nullable=False)
    effective_from = Column(TIMESTAMP, nullable=False)
    source_id = Column(String(36), ForeignKey('sources.id'), nullable=True)
    version = Column(Integer, default=1)
    content_hash = Column(String(64))
    created_at = Column(TIMESTAMP, default=now_utc)
    updated_at = Column(TIMESTAMP, default=now_utc, onupdate=now_utc)

# ---------- 29. MESSAGE ----------
class Message(Base):
    __tablename__ = 'messages'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    sender_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    recipient_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    context_type = Column(String(50))  # APPLICATION, CASE
    context_id = Column(String(36), nullable=True)
    body = Column(Text)
    sent_at = Column(TIMESTAMP, default=now_utc)
    read_at = Column(TIMESTAMP, nullable=True)

# ---------- 30. NOTIFICATION ----------
class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    recipient_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    event_type = Column(String(50), nullable=False)
    channel = Column(String(20), nullable=False)  # EMAIL, SMS, IN_APP, PUSH
    status = Column(String(20), default='QUEUED')  # QUEUED, SENT, FAILED, READ
    priority = Column(String(20), default='MEDIUM')
    content = Column(JSON)
    created_at = Column(TIMESTAMP, default=now_utc)
    sent_at = Column(TIMESTAMP, nullable=True)

# ---------- 31. AUDIT_EVENT ----------
class AuditEvent(Base):
    __tablename__ = 'audit_events'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    actor_id = Column(String(36), nullable=True)
    action = Column(String(100), nullable=False)
    target_type = Column(String(50))
    target_id = Column(String(36), nullable=True)
    before = Column(JSON)
    after = Column(JSON)
    reason = Column(Text, nullable=True)
    source_ip = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    prev_hash = Column(String(64))
    entry_hash = Column(String(64))
    timestamp = Column(TIMESTAMP, default=now_utc)
    __table_args__ = (
        Index('idx_audit_actor', 'actor_id'),
        Index('idx_audit_target', 'target_type', 'target_id'),
        Index('idx_audit_time', 'timestamp'),
    )

# ---------- 32. CONSTITUTION_ITEM ----------
class ConstitutionItem(Base):
    __tablename__ = 'constitution_items'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(JSON, nullable=False)
    version = Column(Integer, default=1)
    approved_by = Column(String(36), ForeignKey('users.id'), nullable=True)
    effective_from = Column(TIMESTAMP, default=now_utc)

# ---------- 33. AMENDMENT_PROPOSAL ----------
class AmendmentProposal(Base):
    __tablename__ = 'amendment_proposals'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    constitution_key = Column(String(100), nullable=False)
    proposed_value = Column(JSON, nullable=False)
    proposed_by = Column(String(36), ForeignKey('users.id'), nullable=False)
    status = Column(String(20), default='PENDING')  # PENDING, APPROVED, REJECTED
    approved_by = Column(String(36), ForeignKey('users.id'), nullable=True)
    approved_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, default=now_utc)

# ---------- 34. MODEL_REGISTRY ----------
class ModelRegistry(Base):
    __tablename__ = 'model_registry'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    model_name = Column(String(100), nullable=False)
    version = Column(Integer, nullable=False)
    status = Column(String(20), default='SHADOW')  # SHADOW, ACTIVE, RETIRED, KILLED
    trained_by = Column(String(36), ForeignKey('users.id'), nullable=True)
    approved_by = Column(String(36), ForeignKey('users.id'), nullable=True)
    shadow_started_at = Column(TIMESTAMP, nullable=True)
    promoted_at = Column(TIMESTAMP, nullable=True)
    killed_at = Column(TIMESTAMP, nullable=True)
    kill_reason = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, default=now_utc)

# ---------- 35. FAIRNESS_CHECK ----------
class FairnessCheck(Base):
    __tablename__ = 'fairness_checks'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    model_version = Column(String(36), ForeignKey('model_registry.id'), nullable=False)
    segment = Column(String(50), nullable=False)
    approval_rate = Column(Float)
    four_fifths_ratio = Column(Float)
    flagged = Column(Boolean, default=False)
    checked_at = Column(TIMESTAMP, default=now_utc)