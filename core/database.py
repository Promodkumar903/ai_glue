# ============================================================
# AI GLUE v8.0 — DATABASE SCHEMA (FINAL)
# ============================================================
# Based on Blueprint v8.0 — 35 Tables + 34 Invariants
# Engine: E-01 Foundation
# SQLAlchemy ORM, SQLite Compatible (PostgreSQL ready)
# ============================================================

import os
import uuid
from datetime import datetime, timedelta
from sqlalchemy import (
    create_engine, Column, String, Boolean, DateTime, Float, Integer,
    JSON, ForeignKey, Text, Enum, DECIMAL, TIMESTAMP, BigInteger, Index
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
        from sqlalchemy.pool import NullPool

        self.engine = create_engine(
            self.db_url,
            connect_args=connect_args,
            poolclass=NullPool,
        )
        self.Session = sessionmaker(bind=self.engine, query_cls=TenantAwareQuery)

    def create_tables(self):
        Base.metadata.create_all(self.engine)

    def get_session(self):
        return self.Session()

    def get_session_dep(self):
        session = self.Session()
        try:
            yield session
        finally:
            session.close()

    def drop_tables(self):
        Base.metadata.drop_all(self.engine)


db = DatabaseEngine()


# ============================================================
# MODELS (All tables — 35 tables)
# ============================================================

# ---------- 1. TENANT ----------
class Tenant(Base):
    __tablename__ = 'tenants'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    plan = Column(String(50), default='FREE')
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
    status = Column(String(20), default='PENDING')
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
    role_code = Column(String(50), nullable=False)
    granted_at = Column(TIMESTAMP, default=now_utc)
    granted_by = Column(String(36), ForeignKey('users.id'), nullable=True)
    revoked_at = Column(TIMESTAMP, nullable=True)


# ---------- 4. ORGANIZATION ----------
class Organization(Base):
    __tablename__ = 'organizations'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)
    tenant_id = Column(String(36), ForeignKey('tenants.id'), nullable=True)
    verification_status = Column(String(20), default='PENDING')
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
    role_code = Column(String(50), nullable=False)
    added_at = Column(TIMESTAMP, default=now_utc)
    removed_at = Column(TIMESTAMP, nullable=True)


# ---------- 6. COUNTRY ----------
class Country(Base):
    __tablename__ = 'countries'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    iso_code = Column(String(2), unique=True, nullable=False)
    visa_difficulty = Column(Float, default=0.0)
    cost_of_living_index = Column(Float, default=0.0)


# ---------- 7. UNIVERSITY ----------
class University(Base):
    __tablename__ = 'universities'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    country_id = Column(String(36), ForeignKey('countries.id'), nullable=False)
    name = Column(String(255), nullable=False)
    website = Column(String(500))
    ranking_global = Column(Integer)
    ranking_national = Column(Integer)
    accreditation = Column(Text)
    domain = Column(String(255))


# ---------- 8. CITY ----------
class City(Base):
    __tablename__ = 'cities'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    country_id = Column(String(36), ForeignKey('countries.id'), nullable=False)
    name = Column(String(100), nullable=False)
    state = Column(String(100))


# ---------- 9. CAMPUS ----------
class Campus(Base):
    __tablename__ = 'campuses'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    university_id = Column(String(36), ForeignKey('universities.id'), nullable=False)
    city_id = Column(String(36), ForeignKey('cities.id'), nullable=False)
    name = Column(String(255))
    address = Column(Text)
    established_year = Column(Integer)


# ---------- 10. DEPARTMENT ----------
class Department(Base):
    __tablename__ = 'departments'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    campus_id = Column(String(36), ForeignKey('campuses.id'), nullable=False)
    name = Column(String(255), nullable=False)


# ---------- 11. COURSE ----------
class Course(Base):
    __tablename__ = 'courses'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    department_id = Column(String(36), ForeignKey('departments.id'), nullable=False)
    name = Column(String(255), nullable=False)
    level = Column(String(50))
    duration_months = Column(Integer)
    tuition_fee = Column(DECIMAL(15, 2))
    currency = Column(String(3), default='USD')
    admission_requirements = Column(JSON)
    course_url = Column(String(500))


# ---------- 12. INTAKE_SEATS ----------
class IntakeSeat(Base):
    __tablename__ = 'intake_seats'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    course_id = Column(String(36), ForeignKey('courses.id'), nullable=False)
    academic_year = Column(String(9))
    total_seats = Column(Integer)
    filled_seats = Column(Integer, default=0)
    waiting_seats = Column(Integer, default=0)
    last_updated = Column(TIMESTAMP, default=now_utc)


# ---------- 13. OPPORTUNITY ----------
class Opportunity(Base):
    __tablename__ = 'opportunities'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey('organizations.id'), nullable=False)
    type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    requirements = Column(JSON, default={})
    status = Column(String(20), default='DRAFT')
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


# ---------- 14. APPLICATION ----------
class Application(Base):
    __tablename__ = 'applications'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    case_id = Column(String(36), ForeignKey('cases.id'), nullable=False)
    candidate_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    opportunity_id = Column(String(36), ForeignKey('opportunities.id'), nullable=False)
    broker_id = Column(String(36), ForeignKey('users.id'), nullable=True)
    status = Column(String(50), default='DRAFT')
    segment = Column(String(50), nullable=True)
    match_score = Column(Float)
    submitted_at = Column(TIMESTAMP, nullable=True)
    plan_hash = Column(String(64))
    idempotency_key = Column(String(255), unique=True, nullable=True)
    created_at = Column(TIMESTAMP, default=now_utc)
    updated_at = Column(TIMESTAMP, default=now_utc, onupdate=now_utc)


# ---------- 15. OFFER ----------
class Offer(Base):
    __tablename__ = 'offers'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    application_id = Column(String(36), ForeignKey('applications.id'), nullable=False)
    organization_id = Column(String(36), ForeignKey('organizations.id'), nullable=False)
    terms = Column(JSON, default={})
    scholarship_amount = Column(DECIMAL(15, 2), default=0)
    status = Column(String(20), default='DRAFT')
    deadline = Column(TIMESTAMP, nullable=True)
    sent_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, default=now_utc)
    updated_at = Column(TIMESTAMP, default=now_utc, onupdate=now_utc)


# ---------- 16. CONTRACT ----------
class Contract(Base):
    __tablename__ = 'contracts'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    offer_id = Column(String(36), ForeignKey('offers.id'), nullable=False)
    candidate_signature_at = Column(TIMESTAMP, nullable=True)
    organization_signature_at = Column(TIMESTAMP, nullable=True)
    status = Column(String(20), default='PENDING')
    document_id = Column(String(36), nullable=True)


# ---------- 17. PAYMENT ----------
class Payment(Base):
    __tablename__ = 'payments'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    payer_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    payee_type = Column(String(50), nullable=False)
    payee_id = Column(String(36), nullable=True)
    amount = Column(DECIMAL(15, 2), nullable=False)
    currency = Column(String(3), default='USD')
    idempotency_key = Column(String(255), unique=True, nullable=True)
    status = Column(String(20), default='PENDING')
    gateway_ref = Column(String(255), nullable=True)
    payment_meta = Column(JSON, default={})
    created_at = Column(TIMESTAMP, default=now_utc)
    updated_at = Column(TIMESTAMP, default=now_utc, onupdate=now_utc)


# ---------- 18. VISA_CASE ----------
class VisaCase(Base):
    __tablename__ = 'visa_cases'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    candidate_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    country = Column(String(50), nullable=False)
    visa_type = Column(String(50), nullable=False)
    status = Column(String(20), default='NOT_STARTED')
    applied_at = Column(TIMESTAMP, nullable=True)
    decision_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, default=now_utc)
    updated_at = Column(TIMESTAMP, default=now_utc, onupdate=now_utc)


# ---------- 19. VISA_APPOINTMENT ----------
class VisaAppointment(Base):
    __tablename__ = 'visa_appointments'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    visa_case_id = Column(String(36), ForeignKey('visa_cases.id'), nullable=False)
    scheduled_at = Column(TIMESTAMP, nullable=False)
    location = Column(String(255))
    status = Column(String(20), default='SCHEDULED')


# ---------- 20. VISA_RULE ----------
class VisaRule(Base):
    __tablename__ = 'visa_rules'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    country = Column(String(50), nullable=False)
    visa_type = Column(String(50), nullable=False)
    rules = Column(JSON, nullable=False)
    effective_from = Column(TIMESTAMP, nullable=False)
    source_id = Column(String(36), nullable=True)
    version = Column(Integer, default=1)
    content_hash = Column(String(64))


# ---------- 21. DOCUMENT ----------
class Document(Base):
    __tablename__ = 'documents'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    owner_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    type = Column(String(50), nullable=False)
    country_format = Column(String(50))
    version = Column(Integer, default=1)
    file_hash = Column(String(128))
    storage_url = Column(String(500))
    uploaded_at = Column(TIMESTAMP, default=now_utc)
    expiry_date = Column(TIMESTAMP, nullable=True)
    translation_status = Column(String(20), default='NOT_REQUIRED')
    attestation_status = Column(String(20), default='NOT_REQUIRED')
    verified = Column(Boolean, default=False)


# ---------- 22. EVIDENCE ----------
class Evidence(Base):
    __tablename__ = 'evidence'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    claim_id = Column(String(36), nullable=False)
    source_id = Column(String(36), nullable=False)
    captured_at = Column(TIMESTAMP, default=now_utc)
    hash = Column(String(128))
    confidence = Column(Float, default=0.0)
    freshness_days = Column(Integer)
    valid_until = Column(TIMESTAMP, nullable=True)
    source_url = Column(String(500))
    source_domain = Column(String(255))
    content = Column(JSON, default={})


# ---------- 23. SOURCE_REGISTRY ----------
class SourceRegistry(Base):
    __tablename__ = 'source_registry'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    authority_level = Column(String(20), nullable=False)
    url = Column(String(500))
    status = Column(String(20), default='HEALTHY')
    last_success = Column(TIMESTAMP, nullable=True)
    last_failure = Column(TIMESTAMP, nullable=True)
    error_count = Column(Integer, default=0)
    type = Column(String(50), nullable=False)


# ---------- 24. TRUST_SCORE ----------
class TrustScore(Base):
    __tablename__ = 'trust_scores'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(36), nullable=False)
    score = Column(Float, default=0.0)
    confidence = Column(Float, default=0.0)
    last_updated = Column(TIMESTAMP, default=now_utc)
    evidence_ids = Column(JSON, default=[])
    status = Column(String(20), default='PENDING')


# ---------- 25. TTL_RECORD ----------
class TTLRecord(Base):
    __tablename__ = 'ttl_records'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(36), nullable=False)
    ttl_days = Column(Integer, default=30)
    last_verified_at = Column(TIMESTAMP, default=now_utc)
    expires_at = Column(TIMESTAMP, default=now_utc)
    status = Column(String(20), default='ACTIVE')


# ---------- 26. STUDENT_LIFE ----------
class StudentLife(Base):
    __tablename__ = 'student_life'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    country = Column(String(50), nullable=False)
    city = Column(String(100))
    university = Column(String(255))
    semester = Column(Integer)
    last_location_update = Column(TIMESTAMP)
    preferences = Column(JSON, default={})
    current_need = Column(String(50), nullable=True)
    need_detected_at = Column(TIMESTAMP, nullable=True)


# ---------- 27. PARTNER_REGISTRY ----------
class PartnerRegistry(Base):
    __tablename__ = 'partner_registry'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False)
    location = Column(String(500))
    latitude = Column(Float)
    longitude = Column(Float)
    phone = Column(String(20))
    website = Column(String(500))
    trust_score = Column(Float, default=0.0)
    status = Column(String(20), default='PENDING')
    source = Column(JSON, default={})


# ---------- 28. AUDIT_EVENT ----------
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


# ---------- 29. CONSTITUTION_ITEM ----------
class ConstitutionItem(Base):
    __tablename__ = 'constitution_items'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(JSON, nullable=False)
    version = Column(Integer, default=1)
    approved_by = Column(String(36), ForeignKey('users.id'), nullable=True)
    effective_from = Column(TIMESTAMP, default=now_utc)


# ---------- 30. AI_COST_LOG ----------
class AICostLog(Base):
    __tablename__ = 'ai_cost_logs'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=True)
    model = Column(String(50), nullable=False)
    tokens = Column(Integer, default=0)
    cost = Column(DECIMAL(15, 6), default=0)
    purpose = Column(String(50))
    created_at = Column(TIMESTAMP, default=now_utc)


# ---------- 31. FRAUD_FLAG ----------
class FraudFlag(Base):
    __tablename__ = 'fraud_flags'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(36), nullable=False)
    reason = Column(Text)
    evidence = Column(JSON)
    status = Column(String(20), default='PENDING')
    reported_by = Column(String(36), ForeignKey('users.id'), nullable=True)
    created_at = Column(TIMESTAMP, default=now_utc)
    resolved_at = Column(TIMESTAMP, nullable=True)


# ---------- 32. WORKFLOW_STATE ----------
class WorkflowState(Base):
    __tablename__ = 'workflow_states'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    case_id = Column(String(36), nullable=False)
    state = Column(String(50), nullable=False)
    previous_state = Column(String(50))
    actor_id = Column(String(36), ForeignKey('users.id'), nullable=True)
    timestamp = Column(TIMESTAMP, default=now_utc)
    evidence_id = Column(String(36), nullable=True)


# ---------- 33. DEAL ----------
class Deal(Base):
    __tablename__ = 'deals'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    agent_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    broker_id = Column(String(36), ForeignKey('users.id'), nullable=True)
    company_id = Column(String(36), ForeignKey('organizations.id'), nullable=False)
    candidate_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    opportunity_id = Column(String(36), ForeignKey('opportunities.id'), nullable=False)
    status = Column(String(20), default='PENDING')
    deal_fee = Column(DECIMAL(15, 2), nullable=False)
    platform_cut = Column(DECIMAL(15, 2), nullable=False)
    agent_commission = Column(DECIMAL(15, 2), nullable=False)
    broker_commission = Column(DECIMAL(15, 2), nullable=True)
    payment_id = Column(String(36), ForeignKey('payments.id'), nullable=True)
    created_at = Column(TIMESTAMP, default=now_utc)
    updated_at = Column(TIMESTAMP, default=now_utc, onupdate=now_utc)


# ---------- 34. REFERRAL_EVENT ----------
class ReferralEvent(Base):
    __tablename__ = 'referral_events'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    referrer_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    referee_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    action_type = Column(String(50), nullable=False)
    reward_amount = Column(DECIMAL(15, 2), default=0)
    status = Column(String(20), default='PENDING')
    created_at = Column(TIMESTAMP, default=now_utc)
    updated_at = Column(TIMESTAMP, default=now_utc, onupdate=now_utc)


# ---------- 35. REWARD ----------
class Reward(Base):
    __tablename__ = 'rewards'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    type = Column(String(50), nullable=False)
    amount = Column(DECIMAL(15, 2), nullable=False)
    reason = Column(Text)
    status = Column(String(20), default='PENDING')
    granted_at = Column(TIMESTAMP, default=now_utc)


# ---------- CASE ----------
class Case(Base):
    __tablename__ = 'cases'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    candidate_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    case_type = Column(String(50), nullable=False)
    status = Column(String(50), default='OPEN')
    created_at = Column(TIMESTAMP, default=now_utc)
    updated_at = Column(TIMESTAMP, default=now_utc, onupdate=now_utc)


# ---------- APPLICATION TIMELINE ----------
class ApplicationTimeline(Base):
    __tablename__ = 'application_timeline'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    application_id = Column(String(36), ForeignKey('applications.id'), nullable=False)
    from_state = Column(String(50))
    to_state = Column(String(50))
    actor_id = Column(String(36), ForeignKey('users.id'), nullable=True)
    reason = Column(Text)
    timestamp = Column(TIMESTAMP, default=now_utc)
    evidence_hash = Column(String(64))


# ---------- TASK ----------
class Task(Base):
    __tablename__ = 'tasks'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    case_id = Column(String(36), ForeignKey('cases.id'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(20), default='PENDING')
    assignee_id = Column(String(36), ForeignKey('users.id'), nullable=True)
    due_date = Column(TIMESTAMP, nullable=True)
    dependencies = Column(JSON, default=[])
    created_at = Column(TIMESTAMP, default=now_utc)
    updated_at = Column(TIMESTAMP, default=now_utc, onupdate=now_utc)


# ---------- CANDIDATE PROFILE ----------
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


# ---------- CANDIDATE CONSENT ----------
class CandidateConsent(Base):
    __tablename__ = 'candidate_consent'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    candidate_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    broker_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    status = Column(String(20), default='ACTIVE')
    granted_at = Column(TIMESTAMP, default=now_utc)
    revoked_at = Column(TIMESTAMP, nullable=True)


# ---------- COMMISSION_EVENT ----------
class CommissionEvent(Base):
    __tablename__ = 'commission_events'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    deal_id = Column(String(36), ForeignKey('deals.id'), nullable=False)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    amount = Column(DECIMAL(15, 2), nullable=False)
    commission_type = Column(String(50), nullable=True)
    status = Column(String(20), default='PENDING')
    created_at = Column(TIMESTAMP, default=now_utc)
    updated_at = Column(TIMESTAMP, default=now_utc, onupdate=now_utc)


# ---------- CONNECTOR ----------
class Connector(Base):
    __tablename__ = 'connectors'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=True)
    config = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, default=now_utc)
    updated_at = Column(TIMESTAMP, default=now_utc, onupdate=now_utc)


# ---------- NOTIFICATION ----------
class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=True)
    title = Column(String(200), nullable=True)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, default=now_utc)
    updated_at = Column(TIMESTAMP, default=now_utc, onupdate=now_utc)


# ---------- SUBSCRIPTION_PLAN ----------
class SubscriptionPlan(Base):
    __tablename__ = 'subscription_plans'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(DECIMAL(15, 2), nullable=False)
    currency = Column(String(3), default='USD')
    features = Column(JSON, default={})
    max_users = Column(Integer, default=1)
    max_opportunities = Column(Integer, default=10)
    duration_days = Column(Integer, default=30)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=now_utc)
    updated_at = Column(TIMESTAMP, default=now_utc, onupdate=now_utc)


# ---------- USER_SUBSCRIPTION ----------
class UserSubscription(Base):
    __tablename__ = 'user_subscriptions'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    plan_id = Column(String(36), ForeignKey('subscription_plans.id'), nullable=False)
    status = Column(String(20), default='ACTIVE')
    start_date = Column(TIMESTAMP, default=now_utc)
    end_date = Column(TIMESTAMP, nullable=True)
    auto_renew = Column(Boolean, default=False)
    payment_id = Column(String(36), ForeignKey('payments.id'), nullable=True)
    created_at = Column(TIMESTAMP, default=now_utc)
    updated_at = Column(TIMESTAMP, default=now_utc, onupdate=now_utc)


# ---------- SCHEDULED_JOB ----------
class ScheduledJob(Base):
    __tablename__ = 'scheduled_jobs'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_name = Column(String(255), nullable=False)
    job_type = Column(String(50), nullable=False)
    cron_expression = Column(String(100), nullable=True)
    payload = Column(JSON, default={})
    status = Column(String(20), default='ACTIVE')
    last_run_at = Column(TIMESTAMP, nullable=True)
    next_run_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, default=now_utc)
    updated_at = Column(TIMESTAMP, default=now_utc, onupdate=now_utc)


# ---------- PASSWORD RESET TOKEN ----------
class PasswordResetToken(Base):
    __tablename__ = 'password_reset_tokens'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(TIMESTAMP, nullable=False)
    created_at = Column(TIMESTAMP, default=now_utc)
    used = Column(Boolean, default=False)


# ---------- MESSAGE ----------
class Message(Base):
    __tablename__ = 'messages'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    sender_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    receiver_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    is_muted = Column(Boolean, default=False)
    context_type = Column(String(50), nullable=True)
    context_id = Column(String(36), nullable=True)
    created_at = Column(TIMESTAMP, default=now_utc)
    updated_at = Column(TIMESTAMP, default=now_utc, onupdate=now_utc)


# ---------- CONTACT SHARE ----------
class ContactShare(Base):
    __tablename__ = 'contact_shares'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    message_id = Column(String(36), ForeignKey('messages.id'), nullable=False)
    sender_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    receiver_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    contact_data = Column(JSON, nullable=False)
    shared_at = Column(TIMESTAMP, default=now_utc)



# ============================================================
# AGENT GRADE SYSTEM — Week-based rolling performance
# ============================================================
class AgentGrade(Base):
    __tablename__ = 'agent_grades'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    agent_id = Column(String(36))
    grade = Column(String(1))  # A/B/C/D/E
    score = Column(Float, default=0.0)
    trend = Column(String(2))  # up/down/stable
    week_start = Column(TIMESTAMP)
    demands_assigned = Column(Integer, default=0)
    demands_completed = Column(Integer, default=0)
    week_completion_rate = Column(Float, default=0.0)
    career_demands = Column(Integer, default=0)
    career_completed = Column(Integer, default=0)
    career_completion_rate = Column(Float, default=0.0)
    avg_response_min = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    disputes = Column(Integer, default=0)
    calculated_at = Column(TIMESTAMP, default=now_utc)
    valid_until = Column(TIMESTAMP)


class GradeHistory(Base):
    __tablename__ = 'grade_history'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    agent_id = Column(String(36))
    old_grade = Column(String(1))
    new_grade = Column(String(1))
    reason = Column(String)
    week_start = Column(TIMESTAMP)
    changed_at = Column(TIMESTAMP, default=now_utc)