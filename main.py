# ========== FORCE CREATE TABLES ==========
import core.database
from core.database import Base, db as database_instance
Base.metadata.create_all(bind=database_instance.engine)
print("✅ Tables created successfully!")
# ==========================================


"""" 
AI GLUE — Main FastAPI App (Blueprint Section 6.3)
With Complete RBAC Enforcement + Audit + Multi-Tenant Middleware 
+ Security Hardening (Rate Limiting, Secure Headers)
+ MFA + Notification Engine
+ Workflow Engine + Document Lifecycle + Reconciliation  
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from core.database import db
from core.dependencies import get_current_user, require_permission
from core.tenant import set_current_tenant, clear_tenant
from auth.auth import register_user, login_user, refresh_access_token, logout_user
from auth.session import verify_token
from fastapi import Request
from core.database import User
from education import router as education_router
from student_life import router as student_life_router
from documents import router as documents_router
from deals import router as deals_router
from housing_engine import router as housing_router
from vendor_registry import router as vendor_router
from student_journey import router as journey_router
from recommendation_engine import router as recommendation_router
from auth.auth import oauth2_scheme
from auth.forgot import router as forgot_router



# ========== ENGINE IMPORTS (Direct Routes) ==========
from engines.search import search
from engines.application import application
from engines.offer import offer
from engines.payment import payment_engine
from engines.visa import visa
from engines.agent import agent
from engines.broker import broker
from engines.company import company
from engines.admin import admin
from engines.notification import notification_engine
from engines.workflow import workflow
from engines.document_lifecycle import document_lifecycle
from engines.reconciliation import reconciliation
from engines.referral import referral
from engines.subscription import subscription
from engines.scheduler import scheduler
from engines.reporting import reporting
from engines.bulk import bulk
from auth.mfa import mfa          # ✅ MFA Engine

# ========== ROUTER IMPORTS ==========
from auth.auth import router as auth_router
from profile import router as profile_router
from applications import router as applications_router
from offers import router as offers_router
from visa import router as visa_router
from organizations import router as org_router
from payments import router as payments_router
from admin import router as admin_router
from referral import router as referral_router

# ========== SECURITY IMPORTS ==========
from core.security import limiter, SecureHeadersMiddleware, RateLimitExceeded
from core.event_triggers import trigger_application_submitted, trigger_offer_created, trigger_visa_status_update, trigger_payment_success

# ========== APP INSTANCE ==========
app = FastAPI(title="AI Glue API", version="1.0")


# ========== SESSION DEPENDENCY ==========
def get_session():
    session = db.get_session()
    try:
        yield session
    finally:
        session.close()

# ========== PROFILE ME ENDPOINT ==========

@app.get("/profile/me")
def get_my_profile(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    from core.database import User
    from auth.session import verify_token
    payload = verify_token(token)
    if "error" in payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = payload.get("sub")
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "email": user.email, "full_name": user.full_name, "phone": user.phone}

# ========== CORS ==========

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "https://ai-glue-frontend.vercel.app",
    "*",
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== SECURITY MIDDLEWARE ==========
app.add_middleware(SecureHeadersMiddleware)
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return JSONResponse(status_code=429, content={"detail": "Too many requests. Please try later."})

# ========== MULTI-TENANT MIDDLEWARE ==========
@app.middleware("http")
async def tenant_middleware(request: Request, call_next):
    tenant_id = None
    org_id = None
    
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        payload = verify_token(token)
        if "error" not in payload:
            user_id = payload.get("sub")
            if user_id:
                session = db.get_session()
                user = session.query(User).filter(User.id == user_id).first()
                if user:
                    tenant_id = user.tenant_id
                session.close()
    
    set_current_tenant(tenant_id, org_id)
    response = await call_next(request)
    clear_tenant()
    return response

# ========== SESSION DEPENDENCY ==========
def get_session():
    session = db.get_session()
    try:
        yield session
    finally:
        session.close()

# ============================================================
# ROUTERS (Core Features — Routers में Shift)
# ============================================================
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(profile_router, prefix="/profile", tags=["Profile"])
app.include_router(applications_router, prefix="/applications", tags=["Applications"])
app.include_router(offers_router, prefix="/offers", tags=["Offers"])
app.include_router(visa_router, prefix="/visa", tags=["Visa"])
app.include_router(org_router, prefix="/company", tags=["Company"])
app.include_router(payments_router, prefix="/payments", tags=["Payments"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])
app.include_router(referral_router, prefix="/referral", tags=["Referral"])
app.include_router(education_router, prefix="/education", tags=["Education"])
app.include_router(student_life_router, prefix="/student-life", tags=["Student Life"])
app.include_router(documents_router, prefix="/documents", tags=["Documents"])
app.include_router(deals_router, prefix="/deals", tags=["Deals"])
app.include_router(housing_router, prefix="/housing", tags=["Housing"])
app.include_router(vendor_router, prefix="/vendors", tags=["Vendors"])
app.include_router(forgot_router)
app.include_router(journey_router, prefix="/journey", tags=["Student Journey"])
app.include_router(recommendation_router, prefix="/recommendations", tags=["Recommendations"])
from engines.communication import router as communication_router
app.include_router(communication_router, prefix="/communication", tags=["Communication"])


# ============================================================
# DIRECT ROUTES (बिना Routers के)
# ============================================================

# ---------- MFA (MISSING FROM PREVIOUS) ----------
@app.post("/auth/mfa/setup")
def setup_mfa(user_id: str, session: Session = Depends(get_session)):
    return mfa.setup_mfa(user_id, session)

@app.post("/auth/mfa/verify")
def verify_mfa(user_id: str, token: str, session: Session = Depends(get_session)):
    return mfa.verify_mfa(user_id, token, session)

@app.post("/auth/mfa/disable")
def disable_mfa(user_id: str, session: Session = Depends(get_session)):
    return mfa.disable_mfa(user_id, session)

# ---------- SEARCH ----------
@app.get("/search/opportunities")
def search_opportunities(
    q: str,
    type: str = None,
    status: str = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_permission("OPPORTUNITY", "READ", "TENANT"))
):
    filters = {}
    if type:
        filters['type'] = type
    if status:
        filters['status'] = status
    results = search.search_opportunities(q, filters, session)
    return {"count": len(results), "results": [{"id": r.id, "title": r.title, "type": r.type} for r in results]}

# ---------- AGENT ----------
@app.get("/agent/candidates")
def get_agent_candidates(
    agent_id: str = "demo_agent",
    session: Session = Depends(get_session),
    current_user: User = Depends(require_permission("APPLICATION", "READ", "CASE"))
):
    return agent.get_candidates(agent_id, session)
@app.get("/visa/cases")
def get_visa_cases(
    session: Session = Depends(db.get_session_dep),
    user=Depends(get_current_user),
):
    return visa.get_all_visa_cases(session)
@app.get("/agent/funnel")
def get_agent_funnel(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_permission("APPLICATION", "READ", "TEAM"))
):
    return agent.get_funnel(session)

# ---------- BROKER ----------
@app.get("/broker/dashboard/{broker_id}")
def get_broker_kpi(
    broker_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_permission("APPLICATION", "READ", "ORGANIZATION"))
):
    return broker.get_broker_kpi(broker_id, session)

@app.get("/broker/agents/performance")
def get_broker_agent_performance(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_permission("USER_ADMIN", "READ", "ORGANIZATION"))
):
    return broker.get_agent_performance(session)

@app.get("/broker/clients")
def get_broker_client_distribution(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_permission("APPLICATION", "READ", "ORGANIZATION"))
):
    return broker.get_client_distribution(session)

# ---------- ADMIN (NEW — Added Endpoints) ----------
@app.get("/admin/dashboard/metrics")
def admin_live_metrics(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_permission("USER_ADMIN", "READ", "SYSTEM"))
):
    return admin.get_live_metrics(session)

@app.get("/admin/users")
def admin_get_users(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_permission("USER_ADMIN", "READ", "SYSTEM"))
):
    print("=== NEW ADMIN_USERS CODE RUNNING ===", flush=True)
    from core.database import UserRole
    users = session.query(User).all()
    result = []
    for u in users:
        roles = session.query(UserRole).filter(UserRole.user_id == u.id).all()
        role_codes = [r.role_code for r in roles if r.revoked_at is None]
        result.append({
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "phone": u.phone,
            "status": u.status,
            "created_at": str(u.created_at) if u.created_at else None,
            "roles": role_codes,
            "role": role_codes[0] if role_codes else None,
         })
    return {"_debug_v2": True, "users": result}
@app.get("/admin/organizations")
def admin_get_orgs(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_permission("ORGANIZATION", "READ", "SYSTEM"))
):
    return admin.get_organizations(session)

@app.get("/admin/connectors")
def admin_get_connectors(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_permission("CONNECTOR", "READ", "SYSTEM"))
):
    return admin.get_connectors(session)

@app.get("/admin/audit")
def admin_get_audit_logs(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_permission("AUDIT_EVENT", "READ", "SYSTEM"))
):
    return admin.get_audit_logs(session)

@app.get("/admin/payments/summary")
def admin_payment_summary(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_permission("PAYMENT", "READ", "SYSTEM"))
):
    return admin.get_payment_summary(session)
# ---------- COMPANY (All Applicants for Employer Dashboard) ----------
@app.get("/company/applicants/all")
def get_all_company_applicants(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_permission("APPLICATION", "READ", "ORGANIZATION"))
):
    from core.database import Application, Opportunity
    apps = session.query(Application).all()
    return [{
        "id": str(a.id),
        "candidate_id": str(a.candidate_id),
        "opportunity_id": str(a.opportunity_id),
        "status": a.status,
        "match_score": a.match_score or 0,
        "submitted_at": str(a.submitted_at) if a.submitted_at else None,
    } for a in apps]

# ---------- COMPANY (Applicants - MISSING) ----------
@app.get("/company/applicants/{vacancy_id}")
def get_company_applicants(
    vacancy_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_permission("APPLICATION", "READ", "ORGANIZATION"))
):
    return company.get_applicants(vacancy_id, session)

@app.put("/company/applicants/{application_id}/status")
def update_company_applicant_status(
    application_id: str,
    status: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_permission("APPLICATION", "UPDATE", "ORGANIZATION"))
):
    return company.update_applicant_status(application_id, status, session)

# ---------- CONTRACTS (MISSING) ----------
@app.post("/contracts/create")
def create_contract(
    offer_id: str,
    candidate_signature: str = None,
    organization_signature: str = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_permission("CONTRACT", "CREATE", "SELF"))
):
    return offer.create_contract(offer_id, candidate_signature, organization_signature, session)

@app.put("/contracts/{contract_id}/sign")
def sign_contract(
    contract_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_permission("CONTRACT", "UPDATE", "SELF"))
):
    return offer.sign_contract(contract_id, session)

# ---------- VISA FUNNEL (MISSING) ----------
@app.get("/visa/funnel")
def get_visa_funnel(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_permission("VISA", "READ", "SYSTEM"))
):
    return visa.get_visa_funnel(session)

# ---------- NOTIFICATIONS ----------
@app.get("/notifications")
def get_notifications(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    return notification_engine.get_user_notifications(current_user.id, session)

@app.put("/notifications/{notification_id}/read")
def mark_notification_read(
    notification_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    return notification_engine.mark_as_read(notification_id, session)

# ---------- WORKFLOW ----------
@app.get("/workflow/definition/{entity_type}")
def get_workflow_definition(
    entity_type: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_permission("APPLICATION", "READ", "SELF"))
):
    return workflow.get_workflow_definition(entity_type)

@app.post("/workflow/transition")
def transition_state(
    entity_type: str,
    entity_id: str,
    target_state: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_permission("APPLICATION", "UPDATE", "SELF"))
):
    return workflow.transition(entity_type, entity_id, target_state, current_user.id, session)

# ---------- DOCUMENT LIFECYCLE ----------
@app.get("/documents/expiry/{document_id}")
def check_document_expiry(
    document_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_permission("DOCUMENT", "READ", "SELF"))
):
    return document_lifecycle.check_expiry(document_id, session)

@app.post("/documents/expiry/{document_id}")
def set_document_expiry(
    document_id: str,
    expiry_date: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_permission("DOCUMENT", "UPDATE", "SELF"))
):
    return document_lifecycle.set_expiry(document_id, expiry_date, session)

@app.get("/documents/expiring")
def get_expiring_documents(
    days: int = 30,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_permission("DOCUMENT", "READ", "TENANT"))
):
    return document_lifecycle.get_expiring_documents(days, session)

# ---------- RECONCILIATION ----------
@app.get("/reconciliation/calculate")
def calculate_commission(
    amount: float,
    agent_rate: float = 0.10,
    broker_rate: float = 0.05,
    platform_rate: float = 0.02,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_permission("PAYMENT", "READ", "SYSTEM"))
):
    return reconciliation.calculate_commission(amount, agent_rate, broker_rate, platform_rate)

@app.post("/reconciliation/commission")
def create_commission_event(
    application_id: str,
    amount: float,
    agent_id: str,
    broker_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_permission("PAYMENT", "CREATE", "SYSTEM"))
):
    return reconciliation.create_commission_event(application_id, amount, agent_id, broker_id, session)

@app.get("/reconciliation/summary")
def get_reconciliation_summary(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_permission("PAYMENT", "READ", "SYSTEM"))
):
    return reconciliation.get_reconciliation_summary(session)

# ---------- SUBSCRIPTION ----------
@app.post("/subscription/plan")
def create_plan(
    name: str,
    price_monthly: float,
    price_yearly: float,
    features: dict,
    session: Session = Depends(get_session)
):
    return subscription.create_plan(name, price_monthly, price_yearly, features, session)

@app.post("/subscription/assign")
def assign_plan(
    user_id: str,
    plan_id: str,
    duration: str = "monthly",
    session: Session = Depends(get_session)
):
    return subscription.assign_plan(user_id, plan_id, duration, session)

@app.get("/subscription/{user_id}")
def get_user_plan(
    user_id: str,
    session: Session = Depends(get_session)
):
    return subscription.get_user_plan(user_id, session)

# ---------- SCHEDULER ----------
@app.post("/scheduler/job")
def schedule_job(
    job_type: str,
    target_id: str,
    scheduled_at: str,
    payload: dict = None,
    session: Session = Depends(get_session)
):
    from datetime import datetime
    dt = datetime.fromisoformat(scheduled_at.replace('Z', '+00:00'))
    return scheduler.schedule_job(job_type, target_id, dt, payload, session)

@app.post("/scheduler/run")
def execute_pending_jobs(
    session: Session = Depends(get_session)
):
    return scheduler.execute_pending_jobs(session)

@app.get("/scheduler/pending")
def get_pending_jobs(
    session: Session = Depends(get_session)
):
    return scheduler.get_pending_jobs(session)

# ---------- REPORTING ----------
@app.get("/reporting/funnel")
def get_funnel(
    session: Session = Depends(get_session)
):
    return reporting.get_funnel_data(session)

@app.get("/reporting/conversion")
def get_conversion(
    session: Session = Depends(get_session)
):
    return reporting.get_conversion_rates(session)

@app.get("/reporting/revenue")
def get_revenue(
    session: Session = Depends(get_session)
):
    return reporting.get_revenue_summary(session)

@app.get("/reporting/activity")
def get_activity(
    session: Session = Depends(get_session)
):
    return reporting.get_user_activity_summary(session)

# ---------- BULK ----------
@app.get("/bulk/users/export")
def export_users(
    session: Session = Depends(get_session)
):
    return bulk.export_users_csv(session)

@app.get("/bulk/applications/export")
def export_applications(
    session: Session = Depends(get_session)
):
    return bulk.export_applications_csv(session)

@app.post("/bulk/opportunities/import")
def import_opportunities(
    csv_data: str,
    session: Session = Depends(get_session)
):
    return bulk.import_opportunities_csv(csv_data, session)

# ========== ROOT ==========
@app.get("/")
def root():
    return {"message": "AI Glue API is running"}



# ============================================================
# AGENT GRADE SYSTEM — Routes
# ============================================================
from engines.grade import grade_engine


@app.get("/agents/{agent_id}/grade")
def get_agent_grade(
    agent_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get current grade for an agent"""
    return grade_engine.get_grade(agent_id, session)


@app.get("/agents/leaderboard")
def agents_leaderboard(
    limit: int = 20,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Top graded agents"""
    return {"leaderboard": grade_engine.leaderboard(session, limit)}


@app.post("/admin/recalculate-grades")
def recalculate_grades(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_permission("USER_ADMIN", "READ", "SYSTEM"))
):
    """Manually trigger grade recalculation for all agents"""
    return grade_engine.recalculate_all(session)


# ============================================================
# ADMIN USERS V2 — fresh endpoint, no collision
# ============================================================
@app.get("/admin/users-v2")
def admin_get_users_v2(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_permission("USER_ADMIN", "READ", "SYSTEM"))
):
    from core.database import UserRole, AgentGrade
    users = session.query(User).all()
    result = []
    for u in users:
        roles = session.query(UserRole).filter(UserRole.user_id == u.id).all()
        role_codes = [r.role_code for r in roles if r.revoked_at is None]
        # Get latest grade
        latest = session.query(AgentGrade).filter(
            AgentGrade.agent_id == u.id
        ).order_by(AgentGrade.calculated_at.desc()).first()
        result.append({
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "phone": u.phone,
            "status": u.status,
            "created_at": str(u.created_at) if u.created_at else None,
            "roles": role_codes,
            "role": role_codes[0] if role_codes else None,
            "grade": latest.grade if latest else None,
            "trend": latest.trend if latest else None,
            "score": latest.score if latest else None,
        })
    return result


# ============================================================
# PUBLIC DIRECTORY — anyone authenticated can access
# ============================================================
@app.get("/public/directory")
def public_directory(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    from core.database import UserRole, AgentGrade
    users = session.query(User).all()
    result = []
    for u in users:
        roles = session.query(UserRole).filter(UserRole.user_id == u.id).all()
        role_codes = [r.role_code for r in roles if r.revoked_at is None]
        if not any(r in ['AGENT', 'BROKER'] for r in role_codes):
            continue
        latest = session.query(AgentGrade).filter(
            AgentGrade.agent_id == u.id
        ).order_by(AgentGrade.calculated_at.desc()).first()
        result.append({
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "phone": u.phone,
            "status": u.status,
            "roles": role_codes,
            "role": role_codes[0] if role_codes else None,
            "grade": latest.grade if latest else None,
            "trend": latest.trend if latest else None,
            "score": latest.score if latest else None,
        })
    return result


@app.get("/public/jobs")
def public_jobs(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    from core.database import Opportunity
    jobs = session.query(Opportunity).filter(Opportunity.type == 'VACANCY').all()
    return [
        {
            "id": j.id,
            "title": j.title,
            "type": j.type,
            "country": getattr(j, 'country', None),
            "status": j.status,
            "organization_id": j.organization_id,
        }
        for j in jobs
    ]
