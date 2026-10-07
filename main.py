# ========== FORCE CREATE TABLES ==========
import core.database
from core.database import Base, db as database_instance
Base.metadata.create_all(bind=database_instance.engine)
print("??? Tables created successfully!")
# ==========================================

"""
AI GLUE ??? Main FastAPI App (Blueprint Section 6.3)
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
from auth.mfa import mfa          # ??? MFA Engine

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

# ========== AI IMPORTS ==========
import os
import json
import io
from groq import Groq
try:
    from zai import ZaiClient
except ImportError:
    ZaiClient = None
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from fastapi import UploadFile, File, Form
from verifier import verify_documents, verify_job_documents

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

ZAI_API_KEY = os.getenv("ZAI_API_KEY")
zai_client = ZaiClient(api_key=ZAI_API_KEY) if (ZAI_API_KEY and ZaiClient) else None
# ==================================

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
        "http://localhost:5173",
        "http://localhost:3000",
        "https://ai-glue-frontend.vercel.app",
        "https://aiglueagent.com",
        "https://www.aiglueagent.com",
        "https://ai-glue.vercel.app",
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
# ROUTERS (Core Features ??? Routers ????????? Shift)
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
# DIRECT ROUTES (???????????? Routers ??????)
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

# ---------- ADMIN (NEW ??? Added Endpoints) ----------
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
    return admin.get_users(session)

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


# ========== DOCUMENT CHECKLIST ENDPOINTS ==========
@app.get("/education/documents-list/countries", tags=["Education"])
def get_document_countries():
    import core.db_compat as sqlite3
    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()
    cur.execute('SELECT DISTINCT country FROM country_documents ORDER BY country')
    rows = cur.fetchall()
    conn.close()
    return [r[0] for r in rows]

@app.get("/education/documents/{country}", tags=["Education"])
def get_country_documents(country: str):
    import core.db_compat as sqlite3
    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()
    cur.execute('SELECT id, document_name, is_mandatory, description, estimated_days, official_link FROM country_documents WHERE LOWER(country) = LOWER(?)', (country,))
    rows = cur.fetchall()
    conn.close()
    return [
        {
            "id": r[0],
            "document_name": r[1],
            "is_mandatory": bool(r[2]),
            "description": r[3],
            "estimated_days": r[4],
            "official_link": r[5],
        }
        for r in rows
    ]


# ========== DOCUMENT SERVICES ENDPOINTS ==========
@app.get("/education/document-services/{document_type}", tags=["Education"])
def get_document_services(document_type: str, country: str = None):
    import core.db_compat as sqlite3
    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()
    if country:
        cur.execute(
            'SELECT id, service_type, provider_name, city, website, phone, price_range, rating, verified '
            'FROM document_services WHERE document_type LIKE ? AND (country LIKE ? OR country = "All") '
            'ORDER BY rating DESC',
            (f'%{document_type}%', f'%{country}%')
        )
    else:
        cur.execute(
            'SELECT id, service_type, provider_name, city, website, phone, price_range, rating, verified '
            'FROM document_services WHERE document_type LIKE ? ORDER BY rating DESC',
            (f'%{document_type}%',)
        )
    rows = cur.fetchall()
    conn.close()

    if rows:
        return [
            {
                "id": r[0],
                "service_type": r[1],
                "provider_name": r[2],
                "city": r[3],
                "website": r[4],
                "phone": r[5],
                "price_range": r[6],
                "rating": r[7],
                "verified": bool(r[8]),
                "source": "database",
            }
            for r in rows
        ]

    # Fallback: AI suggestions
    if groq_client:
        try:
            prompt = f"""You are an expert study-abroad advisor.

A student from {country or 'India'} needs help with this document: "{document_type}".

IMPORTANT RULES:
1. Suggest services available IN {country or 'India'} or ONLINE.
2. If "{document_type}" is country-specific, suggest the OFFICIAL government body first.
3. Do NOT suggest embassies of OTHER countries.
4. Suggest REAL services ??? coaching centers, agents, translators, government offices.

Return ONLY JSON:
{{
  "services": [
    {{
      "provider_name": "...",
      "service_type": "Coaching/Agent/Translator/Bank/Government",
      "city": "...",
      "website": "https://...",
      "phone": "...",
      "price_range": "...",
      "rating": 4.5,
      "verified": false
    }}
  ]
}}

No markdown. Only JSON."""

            response = groq_client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1500,
            )
            content = response.choices[0].message.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            import json as json_lib
            data = json_lib.loads(content)
            services = data.get("services", [])
            for s in services:
                s["source"] = "ai"
            return services
        except Exception:
            return []

    return []

# ========== AI DOCUMENT TYPES ==========
@app.get("/ai/document-types/{country}", tags=["AI"])
def get_document_types(country: str):
    """Get document types, language, and format for a specific country."""
    country_config = {
        "Germany": {
            "documents": [
                {"id": "cover_letter", "name": "Anschreiben (Cover Letter)", "lang": "German + English", "required": True},
                {"id": "cv", "name": "Lebenslauf (CV)", "lang": "German + English", "required": True},
                {"id": "motivation_letter", "name": "Motivationsschreiben", "lang": "German + English", "required": True},
            ],
            "photo_required": True,
            "photo_spec": "Passport size 35x45mm, white background",
            "format": "Europass",
            "length": "2 pages",
            "language_instruction": "Use GERMAN section headings (Lebenslauf, Berufserfahrung, Ausbildung, Sprachkenntnisse, Digitale Kompetenzen) with ENGLISH content. Include photo placeholder."
        },
        "Portugal": {
            "documents": [
                {"id": "cover_letter", "name": "Carta de Apresenta????o", "lang": "Portuguese + English", "required": True},
                {"id": "cv", "name": "Curriculum Vitae", "lang": "Portuguese + English", "required": True},
                {"id": "motivation_letter", "name": "Carta de Motiva????o", "lang": "Portuguese + English", "required": True},
            ],
            "photo_required": True,
            "photo_spec": "Passport size, white background",
            "format": "Europass",
            "length": "2 pages",
            "language_instruction": "Use PORTUGUESE section headings (Dados Pessoais, Experi??ncia Profissional, Educa????o, Compet??ncias, L??nguas) with ENGLISH content. Include photo placeholder."
        },
        "USA": {
            "documents": [
                {"id": "sop", "name": "Statement of Purpose", "lang": "English", "required": True},
                {"id": "resume", "name": "Resume", "lang": "English", "required": True},
            ],
            "photo_required": False,
            "format": "American ATS-friendly",
            "length": "1 page",
            "language_instruction": "Use ENGLISH throughout. ATS-friendly format: single column, no photo, no personal info. Focus on achievements with metrics."
        },
        "UK": {
            "documents": [
                {"id": "personal_statement", "name": "Personal Statement", "lang": "English", "required": True},
                {"id": "cv", "name": "CV", "lang": "English", "required": True},
            ],
            "photo_required": False,
            "format": "British CV",
            "length": "2 pages",
            "language_instruction": "Use ENGLISH throughout. British CV format: 2 pages, personal statement at top, reverse chronological, references available on request. NO PHOTO. NO PERSONAL INFORMATION ??? do NOT include Date of Birth, Nationality, Passport Number, or Marital Status (GDPR compliance)."
        },
        "Canada": {
            "documents": [
                {"id": "letter_of_explanation", "name": "Letter of Explanation (SOP)", "lang": "English", "required": True},
                {"id": "resume", "name": "Resume", "lang": "English", "required": True},
            ],
            "photo_required": False,
            "format": "Canadian Resume",
            "length": "2 pages",
            "language_instruction": "Use ENGLISH throughout. Canadian format: NO photo, NO personal info. Focus on achievements, include volunteer work."
        },
        "Japan": {
            "documents": [
                {"id": "rirekisho", "name": "Rirekisho (?????????)", "lang": "Japanese + English", "required": True},
                {"id": "shokumu_keirekisho", "name": "Shokumu Keirekisho (???????????????)", "lang": "Japanese + English", "required": True},
            ],
            "photo_required": True,
            "photo_spec": "3x4 cm, formal attire, white background",
            "format": "Japanese Rirekisho",
            "length": "2 pages",
            "language_instruction": "Use JAPANESE section headings (??????, ??????, ??????, ??????PR) with Japanese content, and provide English translation below. Include photo placeholder (3x4 cm)."
        },
        "Korea": {
            "documents": [
                {"id": "jasoseo", "name": "Jasoseo (???????????????)", "lang": "Korean + English", "required": True},
                {"id": "resume", "name": "????????? (Resume)", "lang": "Korean + English", "required": True},
            ],
            "photo_required": True,
            "photo_spec": "3.5x4.5 cm, formal, white background",
            "format": "Korean Jasoseo",
            "length": "2 pages",
            "language_instruction": "Use KOREAN headings (????????????, ????????????, ????????? ?????????, ?????? ??? ??????) with English content. Include photo placeholder (3.5x4.5 cm)."
        },
        "Australia": {
            "documents": [
                {"id": "genuine_student", "name": "Genuine Student Statement", "lang": "English", "required": True},
                {"id": "resume", "name": "Resume", "lang": "English", "required": True},
            ],
            "photo_required": False,
            "format": "Australian CV",
            "length": "2 pages",
            "language_instruction": "Use ENGLISH throughout. Genuine Student Statement MUST be formatted as 4 SEPARATE sections with numbered headers: '1. Why do you want to study in Australia?', '2. Why have you chosen this particular program?', '3. What are your academic and career goals?', '4. How will you contribute to the Australian academic community?' ??? each ~150 words. Resume: NO PHOTO, 2-3 pages, NO personal info (no DOB, no Gender, no Nationality, no Marital Status, no Passport)."
        },
    }
    config = country_config.get(country, {
        "documents": [
            {"id": "resume", "name": "Resume", "lang": "English", "required": True},
            {"id": "cover_letter", "name": "Cover Letter", "lang": "English", "required": True},
        ],
        "photo_required": False,
        "format": "International",
        "length": "2 pages",
        "language_instruction": "Use ENGLISH throughout.",
    })
    return {"country": country, **config}


# ========== AI GENERATE DOCUMENTS ==========
@app.post("/ai/generate-documents", tags=["AI"])
async def generate_documents(
    country: str = Form(...),
    document_ids: str = Form(...),
    target_role: str = Form(""),
    file: UploadFile = File(...),
    photo: UploadFile = File(None),
):
    if not groq_client:
        raise HTTPException(status_code=500, detail="AI not configured")

    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 5MB)")

    nl = chr(10)
    resume_text = ""
    filename = (file.filename or "").lower()

    try:
        if filename.endswith(".txt"):
            resume_text = contents.decode("utf-8", errors="ignore")
        elif filename.endswith(".pdf"):
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(contents))
            resume_text = nl.join([p.extract_text() or "" for p in reader.pages])
        elif filename.endswith(".docx"):
            from docx import Document
            doc = Document(io.BytesIO(contents))
            para_text = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
            table_text = []
            for table in doc.tables:
                for row in table.rows:
                    seen_cells = set()
                    row_text = []
                    for cell in row.cells:
                        cell_str = cell.text.strip()
                        if cell_str and cell_str not in seen_cells and cell_str != "CURRICULUM VIATE" and cell_str != "CURRICULUM VITAE":
                            seen_cells.add(cell_str)
                            row_text.append(cell_str)
                    if row_text:
                        table_text.append(" | ".join(row_text))
            raw_text = nl.join(para_text) + nl + nl.join(table_text)
            lines = raw_text.split(nl)
            cleaned_lines = []
            prev_line = None
            for line in lines:
                line = line.strip()
                if line and line != prev_line:
                    cleaned_lines.append(line)
                    prev_line = line
            resume_text = nl.join(cleaned_lines)
        else:
            raise HTTPException(status_code=400, detail="Supported: PDF, DOCX, TXT")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"File parse error: {str(e)}")

    if not resume_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text")

    country_config = get_document_types(country)
    language_instruction = country_config.get("language_instruction", "Use ENGLISH throughout.")
    format_name = country_config.get("format", "International")
    length = country_config.get("length", "2 pages")
    photo_required = country_config.get("photo_required", False)
    photo_spec = country_config.get("photo_spec", "")

    doc_instructions = {
        "cover_letter": "A formal cover letter (1 page).",
        "cv": "A professional CV following the country format.",
        "resume": "A professional resume following the country format.",
        "motivation_letter": "A motivation letter explaining academic goals.",
        "sop": "A Statement of Purpose explaining academic goals.",
        "letter_of_explanation": "A Letter of Explanation for visa purposes.",
        "personal_statement": "A personal statement for university admission.",
        "rirekisho": "A Japanese Rirekisho with photo placeholder.",
        "shokumu_keirekisho": "A Japanese Shokumu Keirekisho.",
        "jasoseo": "A Korean Jasoseo with 4 sections.",
        "genuine_student": "An Australian Genuine Student Statement.",
    }

    selected_ids = [d.strip() for d in document_ids.split(",") if d.strip()]
    docs_to_generate = []
    for did in selected_ids:
        if did in doc_instructions:
            docs_to_generate.append(f"- {did}: {doc_instructions[did]}")

    docs_spec = nl.join(docs_to_generate)

    photo_instruction = ""
    if photo_required:
        photo_instruction = f"PHOTO: Include placeholder [PHOTO PLACEHOLDER â€” {photo_spec}]"

    doc_format_placeholders = nl.join([f"===DOCUMENT:{did}==={nl}[Content]" for did in selected_ids])

    prompt = f"""You are a RESUME FORMATTER â€” NOT a writer.

CRITICAL CONTEXT: This is a STUDY ABROAD application, NOT a job application.
- Cover Letter: Address to "Admissions Committee", NOT "Hiring Manager"
- Focus on academic goals, NOT employment
- Use the candidate's REAL NAME from resume (NOT [Your Name])

STUDENT-SPECIFIC RULES:
- DO NOT include JOB-related sections: Notice Period, Career Level, Target Industry, Desired Work Location, Employment Type
- Include ONLY: Education, Experience, Skills, Languages, Projects, Research Interests

GLOBAL RULES:
- For UK, Canada, Australia, USA: NO personal info (DOB, Gender, Nationality, Marital Status, Passport)
- For Germany, Portugal, Japan, Korea: INCLUDE personal info + photo placeholder
- For Australia: GS Statement MUST have 4 numbered question headers

CRITICAL RULES:
1. USE ONLY THE ORIGINAL DATA â€” same companies, dates, degrees, titles.
2. DO NOT INVENT â€” no fake companies, no fake numbers, no fake skills.
3. YOUR VALUE-ADD: Change FORMAT ({format_name}), LANGUAGE ({language_instruction}), STRUCTURE.
4. Add [X] placeholders for missing quantities.

TARGET COUNTRY: {country}
FORMAT: {format_name}
LENGTH: {length}
{photo_instruction}
TARGET PROGRAM: {target_role or 'Not specified'}

=== ORIGINAL RESUME (SOURCE OF TRUTH â€” USE THIS DATA) ===
{resume_text}

=== DOCUMENTS TO GENERATE ===
{docs_spec}

Return in EXACT format:
{doc_format_placeholders}

NO markdown code blocks. Only the documents."""

    try:
        photo_b64 = None
        if photo:
            try:
                photo_contents = await photo.read()
                import base64 as b64_lib
                photo_b64 = b64_lib.b64encode(photo_contents).decode("utf-8")
            except Exception:
                photo_b64 = None

        response = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=6000,
        )
        content = response.choices[0].message.content.strip()

        documents = {}
        parts = content.split("===DOCUMENT:")
        for part in parts[1:]:
            if "===" in part:
                doc_id, doc_content = part.split("===", 1)
                documents[doc_id.strip()] = doc_content.strip()

        verification = verify_documents(resume_text, documents)

        if verification['status'] == 'FAIL' and verification['errorCount'] > 0:
            error_summary = nl.join([
                f"- {i['claim']} ({i['reason']}): {i['repairAction']}"
                for i in verification['issues'][:10]
            ])
            retry_prompt = prompt + nl + nl + "PREVIOUS ATTEMPT FAILED. ERRORS:" + nl + error_summary + nl + "REGENERATE fixing these errors. Use ONLY facts from original."

            response2 = groq_client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[{"role": "user", "content": retry_prompt}],
                temperature=0.1,
                max_tokens=6000,
            )
            content2 = response2.choices[0].message.content.strip()
            documents2 = {}
            parts2 = content2.split("===DOCUMENT:")
            for part in parts2[1:]:
                if "===" in part:
                    doc_id, doc_content = part.split("===", 1)
                    documents2[doc_id.strip()] = doc_content.strip()

            if documents2:
                documents = documents2
                verification = verify_documents(resume_text, documents)

        return {
            "country": country,
            "format": format_name,
            "language": language_instruction,
            "documents": documents,
            "verification": verification,
            "photo_b64": photo_b64,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error: {str(e)}")



# ========== AI VERIFY DOCUMENT ==========
class DocumentVerifyRequest(BaseModel):
    document_type: str
    image_url: str

class DocumentVerifyResponse(BaseModel):
    document_type: str
    is_valid: bool
    extracted_data: Optional[Dict[str, Any]] = None
    issues: Optional[List[str]] = None
    ai_note: Optional[str] = None

@app.post("/ai/verify-document", tags=["AI"], response_model=DocumentVerifyResponse)
async def verify_document(body: DocumentVerifyRequest):
    if not zai_client:
        raise HTTPException(status_code=500, detail="AI not configured")

    prompt = f"""You are a document verification expert.

Analyze this {body.document_type} document image.

Extract and verify:
1. Document type
2. Name on document
3. Document number
4. Issue date
5. Expiry date
6. Is the document valid and readable?

Provide JSON:
{{
  "is_valid": true,
  "extracted_data": {{
    "name": "...",
    "document_number": "...",
    "issue_date": "...",
    "expiry_date": "...",
    "additional_info": "..."
  }},
  "issues": [],
  "ai_note": "..."
}}

Only return valid JSON, no markdown."""

    try:
        response = zai_client.chat.completions.create(
            model="glm-4.6v-flash",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": body.image_url}},
                    ],
                }
            ],
            temperature=0.2,
            max_tokens=1500,
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        import json as json_lib
        data = json_lib.loads(content)
        return DocumentVerifyResponse(
            document_type=body.document_type,
            is_valid=data.get("is_valid", False),
            extracted_data=data.get("extracted_data"),
            issues=data.get("issues", []),
            ai_note=data.get("ai_note", ""),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error: {str(e)}")


# ========== AI UNIVERSITY INFO ==========
class UniversityInfoRequest(BaseModel):
    country: str
    university: str
    course: str = ""

class UniversityInfoResponse(BaseModel):
    university_info: Optional[Dict[str, Any]] = None
    courses: Optional[List[Dict[str, Any]]] = None
    ai_insights: Optional[str] = None

@app.post("/ai/university-info", tags=["AI"], response_model=UniversityInfoResponse)
async def ai_university_info(body: UniversityInfoRequest):
    if not groq_client:
        raise HTTPException(status_code=500, detail="AI not configured")

    prompt = f"""You are an expert study-abroad advisor.

Country: {body.country}
University: {body.university}
Course: {body.course or 'Not specified'}

Provide detailed information in JSON format:
{{
  "university_info": {{
    "ranking": "...",
    "popularity": "...",
    "location": "...",
    "established": "..."
  }},
  "courses": [
    {{
      "name": "...",
      "branches": ["...", "..."],
      "duration": "...",
      "fees": "...",
      "seats": 0,
      "application_deadline": "..."
    }}
  ],
  "ai_insights": "..."
}}

Only return valid JSON, no markdown."""

    try:
        response = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2000,
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        import json as json_lib
        data = json_lib.loads(content)
        return UniversityInfoResponse(**data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error: {str(e)}")



# ========== DOCUMENT UPLOAD + AI VERIFY ==========
import base64 as _b64

@app.post("/documents/upload-and-verify", tags=["Documents"])
async def upload_and_verify(
    document_type: str = Form(...),
    file: UploadFile = File(...),
):
    if not zai_client:
        raise HTTPException(status_code=500, detail="AI not configured")

    contents = await file.read()

    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 5MB)")

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only images allowed")

    b64 = _b64.b64encode(contents).decode("utf-8")
    data_url = f"data:{file.content_type};base64,{b64}"

    prompt = f"""You are a document verification expert.

Analyze this {document_type} document image.

Extract and verify:
1. Document type
2. Name on document
3. Document number
4. Issue date
5. Expiry date
6. Is the document valid and readable?

Provide JSON:
{{
  "is_valid": true,
  "extracted_data": {{
    "name": "...",
    "document_number": "...",
    "issue_date": "...",
    "expiry_date": "...",
    "additional_info": "..."
  }},
  "issues": [],
  "ai_note": "..."
}}

Only return valid JSON, no markdown."""

    try:
        response = zai_client.chat.completions.create(
            model="glm-4.6v-flash",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                }
            ],
            temperature=0.2,
            max_tokens=1500,
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        import json as json_lib
        data = json_lib.loads(content)
        return {
            "document_type": document_type,
            "filename": file.filename,
            "is_valid": data.get("is_valid", False),
            "extracted_data": data.get("extracted_data"),
            "issues": data.get("issues", []),
            "ai_note": data.get("ai_note", ""),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error: {str(e)}")



# ========== JOB REGIONS & COUNTRIES ==========
JOB_REGIONS = {
    "Asia": {
        "flag": "ðŸŒ",
        "countries": ["India", "China", "Japan", "South Korea", "Singapore", "Malaysia", "Thailand", "Vietnam", "Philippines", "Indonesia", "Sri Lanka", "Bangladesh", "Nepal", "Pakistan"]
    },
    "Middle East": {
        "flag": "ðŸ•Œ",
        "countries": ["UAE", "Saudi Arabia", "Qatar", "Kuwait", "Bahrain", "Oman", "Israel", "Turkey", "Jordan", "Lebanon"]
    },
    "Europe": {
        "flag": "ðŸŒ",
        "countries": ["Germany", "United Kingdom", "France", "Netherlands", "Portugal", "Spain", "Italy", "Poland", "Czech Republic", "Sweden", "Norway", "Denmark", "Ireland", "Switzerland", "Austria", "Belgium"]
    },
    "North America": {
        "flag": "ðŸŒŽ",
        "countries": ["USA", "Canada", "Mexico"]
    },
    "Latin America": {
        "flag": "ðŸŒ´",
        "countries": ["Brazil", "Argentina", "Chile", "Colombia", "Peru", "Ecuador"]
    },
    "Africa": {
        "flag": "ðŸŒ",
        "countries": ["South Africa", "Nigeria", "Kenya", "Egypt", "Morocco", "Ghana", "Tanzania"]
    },
    "Oceania": {
        "flag": "ðŸï¸",
        "countries": ["Australia", "New Zealand"]
    },
}

@app.get("/jobs/regions", tags=["Jobs"])
def get_job_regions():
    return JOB_REGIONS



# ========== AI JOB SEARCH (REAL-TIME) ==========
class AIJobSearchRequest(BaseModel):
    query: str
    region: str = ""
    country: str = ""
    job_type: str = ""

class AIJobSearchResponse(BaseModel):
    jobs: Optional[List[Dict[str, Any]]] = None
    total: int = 0
    ai_note: Optional[str] = None

@app.post("/ai/job-search", tags=["AI"], response_model=AIJobSearchResponse)
async def ai_job_search(body: AIJobSearchRequest):
    if not groq_client:
        raise HTTPException(status_code=500, detail="AI not configured")

    location = body.country or body.region or "worldwide"
    job_type_filter = body.job_type or "all types"

    prompt = f"""You are a global job market expert with real-time knowledge.

USER SEARCH:
- Query: "{body.query}"
- Location: {location}
- Job Type: {job_type_filter}

TASK:
Find 10 REAL job openings matching this search. For each job, provide:
1. Job title
2. Company name
3. Company website (real URL)
4. Location (city, country)
5. Salary range (in local currency, realistic for that market)
6. Job type (Full-time / Part-time / Contract / Internship)
7. Experience level (Entry / Mid / Senior / Executive)
8. Key requirements (3-5 bullet points)
9. Posted date (within last 30 days)
10. Apply link (real company career page URL)

RULES:
- Use REAL companies that operate in this location
- Salaries must be REALISTIC for that market (e.g., Oman salaries differ from USA)
- Include diversity: labor, technical, management, executive roles if matching query
- If query is "labor" â€” include construction, warehouse, delivery, etc.
- If query is "software" â€” include developers, engineers, architects
- Company websites must be REAL (e.g., google.com/careers, tesla.com/careers)

Return ONLY JSON:
{{
  "jobs": [
    {{
      "title": "...",
      "company": "...",
      "company_website": "https://...",
      "company_careers_url": "https://.../careers",
      "location": "...",
      "country": "...",
      "salary": "...",
      "job_type": "Full-time",
      "experience_level": "Mid",
      "requirements": ["...", "..."],
      "posted_date": "2026-10-01",
      "apply_url": "https://...",
      "description": "..."
    }}
  ],
  "ai_note": "Summary of job market for this search"
}}

Only return valid JSON, no markdown."""

    try:
        response = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=4000,
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        import json as json_lib
        data = json_lib.loads(content)
        jobs = data.get("jobs", [])
        return AIJobSearchResponse(
            jobs=jobs,
            total=len(jobs),
            ai_note=data.get("ai_note", ""),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error: {str(e)}")


# ========== AI COMPANY INFO ==========
class CompanyInfoRequest(BaseModel):
    company_name: str
    country: str = ""

class CompanyInfoResponse(BaseModel):
    company_name: str
    overview: Optional[str] = None
    industry: Optional[str] = None
    founded: Optional[str] = None
    headquarters: Optional[str] = None
    employees: Optional[str] = None
    website: Optional[str] = None
    rating: Optional[str] = None
    pros: Optional[List[str]] = None
    cons: Optional[List[str]] = None
    culture: Optional[str] = None
    salary_insights: Optional[str] = None
    hiring_process: Optional[str] = None
    ai_note: Optional[str] = None

@app.post("/ai/company-info", tags=["AI"], response_model=CompanyInfoResponse)
async def ai_company_info(body: CompanyInfoRequest):
    if not groq_client:
        raise HTTPException(status_code=500, detail="AI not configured")

    prompt = f"""You are a company research expert.

COMPANY: {body.company_name}
COUNTRY: {body.country or 'Global'}

Provide detailed company information:

Return ONLY JSON:
{{
  "company_name": "{body.company_name}",
  "overview": "2-3 sentence summary of what the company does",
  "industry": "...",
  "founded": "...",
  "headquarters": "...",
  "employees": "...",
  "website": "https://...",
  "rating": "4.2/5 (based on employee reviews)",
  "pros": ["...", "...", "..."],
  "cons": ["...", "..."],
  "culture": "Work culture summary",
  "salary_insights": "How much they pay compared to industry",
  "hiring_process": "Steps in their hiring process",
  "ai_note": "Why you might want to work here"
}}

If company is not real/known, say so in ai_note.
Only return valid JSON, no markdown."""

    try:
        response = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2000,
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        import json as json_lib
        data = json_lib.loads(content)
        return CompanyInfoResponse(**data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error: {str(e)}")



# ========== AI JOB DOCUMENT TYPES ==========
@app.get("/ai/job-document-types/{country}", tags=["AI"])
def get_job_document_types(country: str):
    """Get job-specific document types for a country."""
    config = {
        "Germany": {
            "documents": [
                {"id": "cover_letter", "name": "Anschreiben (Cover Letter)", "lang": "German + English", "required": True},
                {"id": "cv", "name": "Lebenslauf (CV)", "lang": "German + English", "required": True},
            ],
            "photo_required": True,
            "format": "German CV (Lebenslauf)",
            "length": "2 pages",
            "language_instruction": "Use GERMAN headings (Lebenslauf, Berufserfahrung, Ausbildung, Sprachkenntnisse) with ENGLISH content. Include photo placeholder. Work experience FIRST. Include dates in MM/YYYY format. Add Quantified achievements."
        },
        "USA": {
            "documents": [
                {"id": "resume", "name": "American Resume", "lang": "English", "required": True},
                {"id": "cover_letter", "name": "Cover Letter", "lang": "English", "required": True},
            ],
            "photo_required": False,
            "format": "American ATS-Friendly Resume",
            "length": "1 page",
            "language_instruction": "Use ENGLISH. ATS-friendly: single column, NO photo, NO personal info. Work experience FIRST. Start bullets with action verbs. Quantify everything with numbers. Use [X]% placeholders."
        },
        "UK": {
            "documents": [
                {"id": "cv", "name": "British CV", "lang": "English", "required": True},
                {"id": "cover_letter", "name": "Cover Letter", "lang": "English", "required": True},
            ],
            "photo_required": False,
            "format": "British CV",
            "length": "2 pages",
            "language_instruction": "Use ENGLISH. British CV: 2 pages, NO photo, NO personal info. Personal statement at top. Work experience FIRST. References available on request. Quantified achievements."
        },
        "Canada": {
            "documents": [
                {"id": "resume", "name": "Canadian Resume", "lang": "English", "required": True},
                {"id": "cover_letter", "name": "Cover Letter", "lang": "English", "required": True},
            ],
            "photo_required": False,
            "format": "Canadian Resume",
            "length": "2 pages",
            "language_instruction": "Use ENGLISH. Canadian format: NO photo, NO personal info. Work experience FIRST. Include volunteer work. Quantify achievements."
        },
        "UAE": {
            "documents": [
                {"id": "cv", "name": "Gulf CV", "lang": "English", "required": True},
                {"id": "cover_letter", "name": "Cover Letter", "lang": "English", "required": True},
            ],
            "photo_required": True,
            "photo_spec": "Passport size, professional",
            "format": "Gulf/Middle East CV",
            "length": "2-3 pages",
            "language_instruction": "Use ENGLISH. Gulf CV: photo required, include nationality, visa status, marital status. Work experience FIRST. Include languages. Quantify achievements."
        },
        "Japan": {
            "documents": [
                {"id": "rirekisho", "name": "Rirekisho (å±¥æ­´æ›¸)", "lang": "Japanese + English", "required": True},
                {"id": "shokumu_keirekisho", "name": "Shokumu Keirekisho (è·å‹™çµŒæ­´æ›¸)", "lang": "Japanese + English", "required": True},
            ],
            "photo_required": True,
            "photo_spec": "3x4 cm, formal attire",
            "format": "Japanese Rirekisho",
            "length": "2 pages",
            "language_instruction": "Use JAPANESE headings with English translation. Include photo placeholder. Strict chronological."
        },
    }
    default_config = {
        "documents": [
            {"id": "resume", "name": "Resume", "lang": "English", "required": True},
            {"id": "cover_letter", "name": "Cover Letter", "lang": "English", "required": True},
        ],
        "photo_required": False,
        "format": "International",
        "length": "2 pages",
        "language_instruction": "Use ENGLISH. Work experience FIRST. Quantify achievements.",
    }
    cfg = config.get(country, default_config)
    return {"country": country, **cfg}


# ========== AI GENERATE JOB DOCUMENTS ==========
@app.post("/ai/generate-job-documents", tags=["AI"])
async def generate_job_documents(
    country: str = Form(...),
    document_ids: str = Form(...),
    target_role: str = Form(""),
    target_company: str = Form(""),
    file: UploadFile = File(...),
    photo: UploadFile = File(None),
):
    if not groq_client:
        raise HTTPException(status_code=500, detail="AI not configured")

    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 5MB)")

    nl = chr(10)
    resume_text = ""
    filename = (file.filename or "").lower()

    try:
        if filename.endswith(".txt"):
            resume_text = contents.decode("utf-8", errors="ignore")
        elif filename.endswith(".pdf"):
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(contents))
            resume_text = nl.join([p.extract_text() or "" for p in reader.pages])
        elif filename.endswith(".docx"):
            from docx import Document
            doc = Document(io.BytesIO(contents))
            para_text = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
            table_text = []
            for table in doc.tables:
                for row in table.rows:
                    seen = set()
                    row_text = []
                    for cell in row.cells:
                        cs = cell.text.strip()
                        if cs and cs not in seen and cs != "CURRICULUM VIATE" and cs != "CURRICULUM VITAE":
                            seen.add(cs)
                            row_text.append(cs)
                    if row_text:
                        table_text.append(" | ".join(row_text))
            raw_text = nl.join(para_text) + nl + nl.join(table_text)
            lines = raw_text.split(nl)
            cleaned = []
            prev = None
            for line in lines:
                line = line.strip()
                if line and line != prev:
                    cleaned.append(line)
                    prev = line
            resume_text = nl.join(cleaned)
        else:
            raise HTTPException(status_code=400, detail="Supported: PDF, DOCX, TXT")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"File parse error: {str(e)}")

    if not resume_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text")

    country_config = get_job_document_types(country)
    language_instruction = country_config.get("language_instruction", "Use ENGLISH throughout.")
    format_name = country_config.get("format", "International")
    length = country_config.get("length", "2 pages")
    photo_required = country_config.get("photo_required", False)
    photo_spec = country_config.get("photo_spec", "Passport size")

    doc_instructions = {
        "cover_letter": "A professional cover letter (1 page) tailored to the target company and role. Address to Hiring Manager.",
        "cv": "A professional CV following the country format. Work experience FIRST.",
        "resume": "A professional resume following the country format. Work experience FIRST. ATS-friendly.",
        "rirekisho": "A Japanese Rirekisho with photo placeholder.",
        "shokumu_keirekisho": "A Japanese Shokumu Keirekisho â€” detailed career summary.",
    }

    selected_ids = [d.strip() for d in document_ids.split(",") if d.strip()]
    docs_to_generate = []
    for did in selected_ids:
        if did in doc_instructions:
            docs_to_generate.append(f"- {did}: {doc_instructions[did]}")

    docs_spec = nl.join(docs_to_generate)

    photo_instruction = ""
    if photo_required:
        photo_instruction = f"PHOTO: Include placeholder [PHOTO PLACEHOLDER - {photo_spec}]"

    doc_format_placeholders = nl.join([f"===DOCUMENT:{did}==={nl}[Content]" for did in selected_ids])

    prompt = f"""You are a SENIOR professional resume writer for JOB APPLICATIONS (not academic).

CRITICAL CONTEXT: This is a JOB APPLICATION, not university admission.
- Cover Letter: Address to "Hiring Manager" or "Dear [Company] Team"
- Focus on CAREER achievements, not academic goals
- Use measurable IMPACT: revenue, savings, %, numbers
- WORK EXPERIENCE FIRST, education second

CRITICAL RULES:
1. USE ONLY THE ORIGINAL DATA - same companies, dates, degrees, titles.
2. DO NOT INVENT - no fake companies, no fake numbers, no fake skills.
3. Start bullets with ACTION VERBS: Led, Managed, Increased, Reduced, Delivered
4. Add [X] placeholders for missing quantities (e.g., "Increased sales by [X]%")
5. Make it ATS-friendly for {format_name}

TARGET COUNTRY: {country}
FORMAT: {format_name}
LENGTH: {length}
{photo_instruction}
TARGET ROLE: {target_role or 'Not specified'}
TARGET COMPANY: {target_company or 'Not specified'}

=== ORIGINAL RESUME (SOURCE OF TRUTH) ===
{resume_text}

=== DOCUMENTS TO GENERATE ===
{docs_spec}

Return in EXACT format:
{doc_format_placeholders}

NO markdown code blocks. Only the documents."""

    try:
        photo_b64 = None
        if photo:
            try:
                photo_contents = await photo.read()
                import base64 as b64_lib
                photo_b64 = b64_lib.b64encode(photo_contents).decode("utf-8")
            except Exception:
                photo_b64 = None

        response = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=6000,
        )
        content = response.choices[0].message.content.strip()

        documents = {}
        parts = content.split("===DOCUMENT:")
        for part in parts[1:]:
            if "===" in part:
                doc_id, doc_content = part.split("===", 1)
                documents[doc_id.strip()] = doc_content.strip()

        verification = verify_job_documents(resume_text, documents)

        return {
            "country": country,
            "format": format_name,
            "language": language_instruction,
            "documents": documents,
            "verification": verification,
            "photo_b64": photo_b64,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error: {str(e)}")



# ========== PUBLIC DIRECTORY (Agents & Brokers) ==========
@app.get("/public/directory", tags=["Public"])
def public_directory():
    """Public directory â€” agents and brokers with grades."""
    import core.db_compat as sqlite3
    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()

    # Get all users with AGENT or BROKER role
    cur.execute("""
        SELECT u.id, u.email, u.full_name, u.phone, u.status,
               GROUP_CONCAT(ur.role_code) as roles
        FROM users u
        LEFT JOIN user_roles ur ON ur.user_id = u.id AND ur.revoked_at IS NULL
        WHERE u.status = 'ACTIVE'
        GROUP BY u.id
        HAVING GROUP_CONCAT(ur.role_code) LIKE '%AGENT%' OR GROUP_CONCAT(ur.role_code) LIKE '%BROKER%'
    """)
    rows = cur.fetchall()

    result = []
    for r in rows:
        # Get grade if exists
        cur.execute("""
            SELECT grade, trend, score
            FROM agent_grades
            WHERE agent_id = ?
            ORDER BY calculated_at DESC LIMIT 1
        """, (r[0],))
        grade_row = cur.fetchone()

        roles = (r[5] or '').split(',') if r[5] else []

        result.append({
            "id": r[0],
            "email": r[1],
            "full_name": r[2],
            "phone": r[3],
            "status": r[4],
            "roles": roles,
            "role": roles[0] if roles else None,
            "grade": grade_row[0] if grade_row else 'C',
            "trend": grade_row[1] if grade_row else 'stable',
            "score": grade_row[2] if grade_row else 0,
        })

    conn.close()
    return result



# ========== UNIVERSAL SEARCH ==========
@app.get("/admin/search", tags=["Admin"])
def admin_universal_search(
    q: str = "",
    type: str = "all",
    country: str = "",
    limit: int = 50,
    offset: int = 0,
):
    """Search across users, organizations, opportunities, documents."""
    import core.db_compat as sqlite3
    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()

    results = []
    q_like = f"%{q.lower()}%"

    # Search Users
    if type in ("all", "user", "agent", "broker", "student", "job_seeker", "employer", "admin"):
        cur.execute("""
            SELECT u.id, u.email, u.full_name, u.phone, u.status,
                   GROUP_CONCAT(ur.role_code) as roles
            FROM users u
            LEFT JOIN user_roles ur ON ur.user_id = u.id AND ur.revoked_at IS NULL
            WHERE LOWER(u.full_name) LIKE ? OR LOWER(u.email) LIKE ? OR LOWER(u.phone) LIKE ?
            GROUP BY u.id
        """, (q_like, q_like, q_like))

        for r in cur.fetchall():
            roles = (r[5] or '').split(',') if r[5] else []
            role_match = (type == "all") or (type.upper() in roles)
            if not role_match:
                continue
            results.append({
                "entity_type": "user",
                "id": r[0],
                "title": r[2] or r[1],
                "subtitle": r[1],
                "meta": f"Roles: {', '.join(roles) if roles else 'None'} | Status: {r[4]}",
                "role": roles[0] if roles else None,
            })

    # Search Organizations
    if type in ("all", "organization"):
        cur.execute("""
            SELECT id, name, type, tenant_id FROM organizations
            WHERE LOWER(name) LIKE ?
        """, (q_like,))
        for r in cur.fetchall():
            results.append({
                "entity_type": "organization",
                "id": r[0],
                "title": r[1],
                "subtitle": r[2],
                "meta": f"Type: {r[2]}",
            })

    # Search Opportunities
    if type in ("all", "job", "opportunity"):
        cur.execute("""
            SELECT id, title, type, country, company, status FROM opportunities
            WHERE LOWER(title) LIKE ? OR LOWER(company) LIKE ?
        """, (q_like, q_like))
        for r in cur.fetchall():
            results.append({
                "entity_type": "opportunity",
                "id": r[0],
                "title": r[1],
                "subtitle": f"{r[4] or ''} â€” {r[3] or ''}",
                "meta": f"Type: {r[2]} | Status: {r[5]}",
            })

    conn.close()

    # Pagination
    total = len(results)
    paginated = results[offset:offset + limit]

    return {
        "query": q,
        "type": type,
        "country": country,
        "total": total,
        "limit": limit,
        "offset": offset,
        "results": paginated,
    }


# ========== SUB-ADMIN CREATION ==========
class SubAdminCreateRequest(BaseModel):
    email: str
    full_name: str
    phone: str = ""
    role: str = "SUB_ADMIN"
    password: str = ""
    country: str = ""
    permissions: Optional[List[str]] = None

@app.post("/admin/create-sub-admin", tags=["Admin"])
def create_sub_admin(body: SubAdminCreateRequest):
    """Create a sub-admin account with specific permissions."""
    import core.db_compat as sqlite3
    import uuid
    import bcrypt as bcrypt_lib
    from datetime import datetime

    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()

    # Check if email exists
    cur.execute("SELECT id FROM users WHERE LOWER(email) = LOWER(?)", (body.email,))
    if cur.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Email already registered")

    # Generate password if not provided
    password = body.password
    if not password:
        import secrets
        import string
        password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))

    # Hash password
    pwd_hash = bcrypt_lib.hashpw(password.encode('utf-8'), bcrypt_lib.gensalt()).decode('utf-8')

    # Create user
    user_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    cur.execute("""
        INSERT INTO users (id, email, password_hash, full_name, phone, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, 'ACTIVE', ?, ?)
    """, (user_id, body.email, pwd_hash, body.full_name, body.phone, now, now))

    # Add role
    valid_admin_roles = ["SUB_ADMIN", "VENDOR_ADMIN", "EDU_ADMIN", "JOB_ADMIN", "FINANCE_ADMIN"]
    role = body.role.upper() if body.role.upper() in valid_admin_roles else "SUB_ADMIN"

    cur.execute("""
        INSERT INTO user_roles (id, user_id, role_code, granted_at)
        VALUES (?, ?, ?, ?)
    """, (str(uuid.uuid4()), user_id, role, now))

    # Create notification for new user
    cur.execute("""
        INSERT INTO notifications (id, user_id, title, message, is_read, created_at, updated_at)
        VALUES (?, ?, ?, ?, 0, ?, ?)
    """, (
        str(uuid.uuid4()), user_id,
        "Welcome to AI Glue",
        f"Your account has been created with role: {role}. Password: {password}",
        now, now
    ))

    conn.commit()
    conn.close()

    # ===== EMAIL ALERTS =====
    method_label = {"upi": "UPI", "esewa": "eSewa", "paypal": "PayPal"}.get(body.method, body.method.upper())

    # 1. Admin alert
    try:
        admin_email = os.getenv("SMTP_USER", "pramod.rf@gmail.com")
        admin_body = f"""
        <html><body style="font-family: Arial, sans-serif;">
            <h2 style="color:#9333ea;">ðŸ”” Naya Payment Aaya</h2>
            <table style="border-collapse: collapse;">
                <tr><td style="padding:6px;"><b>User:</b></td><td>{body.user_email or body.user_id}</td></tr>
                <tr><td style="padding:6px;"><b>Plan:</b></td><td>{plan[1]} ({body.billing_cycle})</td></tr>
                <tr><td style="padding:6px;"><b>Amount:</b></td><td><b>{currency} {final_amount}</b></td></tr>
                <tr><td style="padding:6px;"><b>Method:</b></td><td>{method_label}</td></tr>
                <tr><td style="padding:6px;"><b>UTR:</b></td><td><code>{body.utr_number}</code></td></tr>
            </table>
            <p style="margin-top:20px;">
                <a href="http://localhost:5173/admin/pending-payments" style="background:#9333ea; color:white; padding:10px 20px; text-decoration:none; border-radius:6px;">Approve Karo â†’</a>
            </p>
            <p style="color:#666; font-size:12px;">Ref: {payment_id[:8]}</p>
        </body></html>
        """
        _send_email(admin_email, f"ðŸ”” Naya Payment: {currency} {final_amount} â€” {plan[1]}", admin_body)
        _log_email(admin_email, f"New payment: {plan[1]}", "", "admin_alert", "sent")
    except Exception as e:
        print(f"Admin email failed: {e}")

    # 2. Customer thank you
    try:
        if body.user_email:
            customer_body = f"""
            <html><body style="font-family: Arial, sans-serif;">
                <div style="max-width:600px; margin:auto;">
                    <h2 style="color:#9333ea;">ðŸ™ Thank you, {body.user_email.split('@')[0]}!</h2>
                    <p>Aapka payment humein mil gaya hai.</p>
                    <div style="background:#f3f4f6; padding:16px; border-radius:8px; margin:20px 0;">
                        <p style="margin:4px 0;"><b>Plan:</b> {plan[1]} ({body.billing_cycle})</p>
                        <p style="margin:4px 0;"><b>Amount:</b> {currency} {final_amount}</p>
                        <p style="margin:4px 0;"><b>Method:</b> {method_label}</p>
                        <p style="margin:4px 0;"><b>UTR:</b> {body.utr_number}</p>
                        <p style="margin:4px 0;"><b>Reference ID:</b> <code>{payment_id[:8]}</code></p>
                    </div>
                    <p>â³ <b>Next step:</b> Hamari team 24 ghante ke andar verify karegi. Verify hote hi aapko confirmation email aayega aur aapka {plan[1]} pack activate ho jaayega.</p>
                    <p style="color:#666; font-size:13px;">Agar 24 ghante mein confirmation na mile, toh reply karein is email pe.</p>
                    <p>â€” Team AI Glue</p>
                </div>
            </body></html>
            """
            _send_email(body.user_email, f"ðŸ™ Payment Received â€” {plan[1]} ({payment_id[:8]})", customer_body)
            _log_email(body.user_email, f"Payment received: {plan[1]}", "", "customer_ack", "sent")
    except Exception as e:
        print(f"Customer email failed: {e}")

    return {
        "status": "pending",
        "payment_id": payment_id,
        "amount": final_amount,
        "currency": currency,
        "method": body.method,
        "message": "Payment submitted. Admin will verify within 24 hours.",
    }


# ========== ANALYTICS & TRACKING ==========
class TrackEventRequest(BaseModel):
    event_type: str
    page: str = ""
    user_id: str = ""
    metadata: Optional[Dict[str, Any]] = None

@app.post("/analytics/track", tags=["Analytics"])
async def track_event(body: TrackEventRequest, request: Request):
    """Track user events: page_view, click, download, etc."""
    import core.db_compat as sqlite3
    import json as json_lib
    from datetime import datetime

    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()

    try:
        ip = request.client.host if request.client else None
        ua = request.headers.get("user-agent", "")[:500]
        meta_str = json_lib.dumps(body.metadata) if body.metadata else None

        cur.execute("""
            INSERT INTO analytics_events (event_type, user_id, page, metadata, ip_address, user_agent, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (body.event_type, body.user_id or None, body.page, meta_str, ip, ua, datetime.utcnow().isoformat()))

        conn.commit()
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
    finally:
        conn.close()


@app.get("/admin/analytics/summary", tags=["Admin"])
def admin_analytics_summary(days: int = 7):
    """Get analytics summary for last N days."""
    import core.db_compat as sqlite3
    from datetime import datetime, timedelta

    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()

    since = (datetime.utcnow() - timedelta(days=days)).isoformat()

    # Total events
    cur.execute("SELECT COUNT(*) FROM analytics_events WHERE created_at >= ?", (since,))
    total_events = cur.fetchone()[0]

    # Unique visitors (distinct IPs)
    cur.execute("SELECT COUNT(DISTINCT ip_address) FROM analytics_events WHERE created_at >= ?", (since,))
    unique_visitors = cur.fetchone()[0]

    # Events by type
    cur.execute("""
        SELECT event_type, COUNT(*) FROM analytics_events
        WHERE created_at >= ?
        GROUP BY event_type ORDER BY COUNT(*) DESC
    """, (since,))
    by_type = [{"event_type": r[0], "count": r[1]} for r in cur.fetchall()]

    # Daily trend
    cur.execute("""
        SELECT DATE(created_at) as day, COUNT(*) FROM analytics_events
        WHERE created_at >= ?
        GROUP BY DATE(created_at) ORDER BY day
    """, (since,))
    daily = [{"date": r[0], "count": r[1]} for r in cur.fetchall()]

    # Top pages
    cur.execute("""
        SELECT page, COUNT(*) FROM analytics_events
        WHERE created_at >= ? AND page IS NOT NULL AND page != ''
        GROUP BY page ORDER BY COUNT(*) DESC LIMIT 10
    """, (since,))
    top_pages = [{"page": r[0], "count": r[1]} for r in cur.fetchall()]

    conn.close()

    return {
        "period_days": days,
        "total_events": total_events,
        "unique_visitors": unique_visitors,
        "by_type": by_type,
        "daily_trend": daily,
        "top_pages": top_pages,
    }



# ========== AI MATCHING ENGINE ==========
class MatchRequest(BaseModel):
    user_id: str = ""
    organization_id: str = ""
    limit: int = 10

@app.post("/ai/match/job-seeker/{user_id}", tags=["AI"])
async def match_job_seeker(user_id: str):
    """AI matches job seeker with relevant jobs from opportunities."""
    import core.db_compat as sqlite3

    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()

    resume_row = None


    # Get all active opportunities
    cur.execute("""
        SELECT id, title, type, country, company, salary
        FROM opportunities WHERE status = 'open' LIMIT 50
    """)
    opps = cur.fetchall()
    conn.close()

    if not opps:
        return {"matches": [], "total": 0, "ai_note": "No active opportunities found"}

    # Build opportunities list for AI
    opp_list = "\n".join([f"{o[0]} | {o[1]} | {o[2]} | {o[3] or 'Global'} | {o[4] or ''} | {o[5] or ''}" for o in opps])

    prompt = f"""You are a job matching expert.

CANDIDATE:
Name: {user[2] or user[1]}
Resume: {resume_row[0] if resume_row else 'Not uploaded'}

AVAILABLE JOBS:
{opp_list}

TASK:
Select the TOP 10 jobs that match this candidate. For each, provide:
- Job ID (exact)
- Match score (0-100)
- Why this matches (1-2 sentences)

Return JSON:
{{
  "matches": [
    {{"job_id": "...", "match_score": 85, "reason": "..."}}
  ],
  "ai_note": "Summary of match quality"
}}

Only return valid JSON."""

    if not groq_client:
        raise HTTPException(status_code=500, detail="AI not configured")

    try:
        response = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2000,
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        import json as json_lib
        data = json_lib.loads(content)

        # Enrich with job details
        enriched = []
        for m in data.get("matches", []):
            for o in opps:
                if o[0] == m["job_id"]:
                    enriched.append({
                        **m,
                        "title": o[1],
                        "type": o[2],
                        "country": o[3],
                        "company": o[4],
                        "salary": o[5],
                    })
                    break

        # Send email to job seeker
        if enriched and user[1]:
            try:
                _send_email(
                    user[1],
                    f"ðŸŽ¯ {len(enriched)} jobs match your profile!",
                    f"""<html><body>
                        <h2>Hi {user[2] or 'there'},</h2>
                        <p>We found <strong>{len(enriched)} jobs</strong> matching your profile.</p>
                        <p><a href="https://ai-glue-frontend.vercel.app/jobseeker-new/search">View jobs now</a></p>
                        <p>â€” Team AI Glue</p>
                    </body></html>"""
                )
                _log_email(user[1], f"{len(enriched)} jobs match", "", "job_match", "sent")
            except Exception:
                pass

        return {
            "user": {"id": user[0], "name": user[2] or user[1]},
            "matches": enriched,
            "total": len(enriched),
            "ai_note": data.get("ai_note", ""),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error: {str(e)}")


@app.post("/ai/match/student/{user_id}", tags=["AI"])
async def match_student(user_id: str):
    """AI matches student with relevant courses/programmes."""
    import core.db_compat as sqlite3

    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()

    cur.execute("SELECT id, email, full_name FROM users WHERE id = ?", (user_id,))
    user = cur.fetchone()
    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")

    cur.execute("""
        SELECT id, title, type, country FROM opportunities
        WHERE type IN ('PROGRAMME', 'SCHOLARSHIP')
    """)
    opps = cur.fetchall()
    conn.close()

    if not opps:
        return {"matches": [], "total": 0, "ai_note": "No programmes found"}

    opp_list = "\n".join([f"{o[0]} | {o[1]} | {o[2]} | {o[3] or 'Global'}" for o in opps])

    prompt = f"""You are a study-abroad advisor.

STUDENT: {user[2] or user[1]}

AVAILABLE PROGRAMMES:
{opp_list}

TASK: Select TOP 10 best matches. Provide match score (0-100) and reason.

Return JSON:
{{
  "matches": [{{"job_id": "...", "match_score": 85, "reason": "..."}}],
  "ai_note": "..."
}}

Only valid JSON."""

    if not groq_client:
        raise HTTPException(status_code=500, detail="AI not configured")

    try:
        response = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2000,
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        import json as json_lib
        data = json_lib.loads(content)

        enriched = []
        for m in data.get("matches", []):
            for o in opps:
                if o[0] == m["job_id"]:
                    enriched.append({**m, "title": o[1], "type": o[2], "country": o[3]})
                    break

        return {
            "user": {"id": user[0], "name": user[2] or user[1]},
            "matches": enriched,
            "total": len(enriched),
            "ai_note": data.get("ai_note", ""),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error: {str(e)}")


@app.post("/ai/match/company/{org_id}", tags=["AI"])
async def match_company(org_id: str):
    """AI matches company with candidates from users."""
    import core.db_compat as sqlite3

    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()

    cur.execute("SELECT id, name FROM organizations WHERE id = ?", (org_id,))
    org = cur.fetchone()
    if not org:
        conn.close()
        raise HTTPException(status_code=404, detail="Organization not found")

    # Get job seekers and students
    cur.execute("""
        SELECT u.id, u.full_name, u.email,
               GROUP_CONCAT(ur.role_code) as roles
        FROM users u
        LEFT JOIN user_roles ur ON ur.user_id = u.id AND ur.revoked_at IS NULL
        WHERE u.status = 'ACTIVE'
        GROUP BY u.id
        HAVING roles LIKE '%JOB_SEEKER%' OR roles LIKE '%STUDENT%'
        LIMIT 30
    """)
    candidates = cur.fetchall()
    conn.close()

    if not candidates:
        return {"matches": [], "total": 0, "ai_note": "No candidates found"}

    cand_list = "\n".join([f"{c[0]} | {c[1] or c[2]} | {c[3]}" for c in candidates])

    prompt = f"""You are a recruitment expert.

COMPANY: {org[1]}

AVAILABLE CANDIDATES:
{cand_list}

TASK: Select TOP 10 candidates for this company. Match score (0-100) and reason.

Return JSON:
{{
  "matches": [{{"candidate_id": "...", "match_score": 85, "reason": "..."}}],
  "ai_note": "..."
}}

Only valid JSON."""

    if not groq_client:
        raise HTTPException(status_code=500, detail="AI not configured")

    try:
        response = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2000,
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        import json as json_lib
        data = json_lib.loads(content)

        enriched = []
        for m in data.get("matches", []):
            for c in candidates:
                if c[0] == m["candidate_id"]:
                    enriched.append({**m, "name": c[1] or c[2], "email": c[2], "roles": c[3]})
                    break

        return {
            "organization": {"id": org[0], "name": org[1]},
            "matches": enriched,
            "total": len(enriched),
            "ai_note": data.get("ai_note", ""),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error: {str(e)}")



# ========== ORCHESTRATION ENGINE ==========
class OrchestrationRunRequest(BaseModel):
    entity_type: str  # "jobs", "students", "agents", "companies", "vendors"
    country: str = ""
    query: str = ""
    limit: int = 10
    auto_notify: bool = True

@app.post("/orchestration/run", tags=["Orchestration"])
async def run_orchestration(body: OrchestrationRunRequest):
    """Master orchestration â€” find, verify, and connect entities."""
    if not groq_client:
        raise HTTPException(status_code=500, detail="AI not configured")

    results = {
        "entity_type": body.entity_type,
        "country": body.country,
        "found": [],
        "verified": [],
        "notified": [],
        "errors": [],
    }

    # Step 1: AI discovers entities
        # Entity-specific guidance
    entity_guidance = {
        "education_agents": "Study-abroad/education consultants who help students apply to universities abroad. Examples: IDP, Edwise, AECC, Chopras, SI-UK, Y-Axis. NOT travel agencies or generic classifieds.",
        "job_agents": "Recruitment agencies and staffing firms who connect job seekers with employers. Examples: Randstad, Adecco, ManpowerGroup, Michael Page, Hays, Robert Half. NOT logistics companies.",
        "education_brokers": "Companies that manage networks of education sub-agents. B2B education aggregators. Examples: Adventus.io, ApplyBoard, MKS, Crizac.",
        "job_brokers": "Companies that manage networks of recruitment sub-agents or franchise staffing networks.",
        "vendor_agents": "Local service providers for students/workers: student housing, book stores, furniture rental, SIM cards, banking, insurance for newcomers.",
        "visa_agents": "Immigration consultants and visa processing agencies. Examples: Fragomen, VFS Global, Y-Axis, Santa Fe Relocation.",
        "jobs": "Real job openings at companies. Include title, company, salary if known.",
        "students": "Student profiles looking for universities. Individual candidates.",
        "companies": "Real employers/companies that hire or sponsor visas.",
        "vendors": "Product/service vendors for hotels, books, furniture, grocery, transport.",
        "colleges": "Real universities/colleges offering programs to international students.",
    }

    guidance = entity_guidance.get(body.entity_type, "Find real, relevant entities.")

    prompt = f"""You are a market intelligence expert for a study-abroad + job platform.

TASK: Find 10 REAL {body.entity_type} in {body.country or 'worldwide'} related to: "{body.query or 'all'}"

IMPORTANT CATEGORY:
{guidance}

RULES:
1. ONLY return entities matching the specific category above
2. Do NOT return generic classifieds (Sulekha, JustDial), travel agencies (MakeMyTrip), logistics (DHL), or insurance (PolicyBazaar) unless they SPECIFICALLY match the category
3. Use REAL companies with REAL websites
4. Verify flag = true only if you're confident the entity exists and matches category
5. Contact email must be from official 'Contact Us' page or leave empty

Return JSON:
{{
  "entities": [
    {{
      "name": "...",
      "website": "...",
      "location": "...",
      "contact_email": "...",
      "description": "...",
      "verified": true
    }}
  ],
  "ai_note": "Summary of discovery"
}}

Only return valid JSON."""
    try:
        response = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2500,
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        import json as json_lib
        data = json_lib.loads(content)

        entities = data.get("entities", [])
        results["found"] = entities
        results["verified"] = [e for e in entities if e.get("verified")]
        results["ai_note"] = data.get("ai_note", "")

        # Step 2: Log to database
        import core.db_compat as sqlite3
        import uuid
        from datetime import datetime
        conn = sqlite3.connect('ai_glue.db')
        cur = conn.cursor()

        for e in entities:
            try:
                cur.execute("""
                    INSERT INTO analytics_events (event_type, page, metadata, created_at)
                    VALUES (?, ?, ?, ?)
                """, (
                    f"orchestration_{body.entity_type}",
                    f"/orchestration/{body.entity_type}",
                    json_lib.dumps({"name": e.get("name"), "country": body.country}),
                    datetime.utcnow().isoformat()
                ))
            except Exception as err:
                results["errors"].append(str(err))

        conn.commit()
        conn.close()

        # Step 3: Create notifications for verified entities
        if body.auto_notify and results["verified"]:
            for e in results["verified"][:5]:
                try:
                    notif_id = str(uuid.uuid4())
                    conn = sqlite3.connect('ai_glue.db')
                    cur = conn.cursor()
                    cur.execute("""
                        INSERT INTO notifications (id, user_id, title, message, is_read, created_at, updated_at)
                        VALUES (?, ?, ?, ?, 0, ?, ?)
                    """, (
                        notif_id,
                        "admin",
                        f"ðŸŽ¯ New {body.entity_type}: {e.get('name')}",
                        f"Location: {e.get('location')} | Website: {e.get('website')}",
                        datetime.utcnow().isoformat(),
                        datetime.utcnow().isoformat()
                    ))
                    conn.commit()
                    conn.close()
                    results["notified"].append(e.get("name"))

                    # Send invitation email
                    contact_email = e.get("contact_email")
                    if contact_email:
                        role_label = body.entity_type.replace("_", " ").title()
                        success, err = _send_email(
                            contact_email,
                            f"You're invited to AI Glue â€” {role_label}",
                            f"""<html><body>
                                <h2>Hi {e.get('name')},</h2>
                                <p>We found your profile and would love to have you on <strong>AI Glue</strong> â€” a global platform connecting {role_label.lower()} with opportunities.</p>
                                <p><a href="https://ai-glue-frontend.vercel.app/register">Join now â€” it's free</a></p>
                                <p>â€” Team AI Glue</p>
                            </body></html>"""
                        )
                        _log_email(contact_email, f"Invitation â€” {role_label}", "", "invitation", "sent" if success else "failed", err)
                except Exception as err:
                    results["errors"].append(str(err))

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Orchestration error: {str(e)}")


@app.get("/orchestration/history", tags=["Orchestration"])
def orchestration_history(limit: int = 20):
    """Get recent orchestration runs from analytics."""
    import core.db_compat as sqlite3
    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()

    cur.execute("""
        SELECT event_type, page, metadata, created_at
        FROM analytics_events
        WHERE event_type LIKE 'orchestration_%'
        ORDER BY created_at DESC LIMIT ?
    """, (limit,))

    rows = cur.fetchall()
    conn.close()

    import json as json_lib
    result = []
    for r in rows:
        try:
            meta = json_lib.loads(r[2]) if r[2] else {}
        except Exception:
            meta = {}
        result.append({
            "type": r[0].replace("orchestration_", ""),
            "page": r[1],
            "name": meta.get("name", ""),
            "country": meta.get("country", ""),
            "created_at": r[3],
        })

    return {"history": result, "total": len(result)}



# ========== ADMIN USERS V2 (with roles) ==========
@app.get("/admin/users-v2", tags=["Admin"])
def admin_users_v2():
    """Get all users with their roles â€” used by admin dashboard."""
    import core.db_compat as sqlite3
    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()

    cur.execute("""
        SELECT u.id, u.email, u.full_name, u.phone, u.status, u.created_at,
               GROUP_CONCAT(ur.role_code) as roles
        FROM users u
        LEFT JOIN user_roles ur ON ur.user_id = u.id AND ur.revoked_at IS NULL
        GROUP BY u.id
        ORDER BY u.created_at DESC
    """)

    rows = cur.fetchall()
    conn.close()

    result = []
    for r in rows:
        roles = (r[6] or '').split(',') if r[6] else []
        result.append({
            "id": r[0],
            "email": r[1],
            "full_name": r[2],
            "phone": r[3],
            "status": r[4],
            "created_at": r[5],
            "roles": roles,
            "role": roles[0] if roles else None,
        })

    return result



# ========== ADMIN USERS V2 ==========
@app.get("/admin/users-v2", tags=["Admin"])
def admin_users_v2():
    """Get all users with their roles."""
    import core.db_compat as sqlite3
    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()

    cur.execute("""
        SELECT u.id, u.email, u.full_name, u.phone, u.status, u.created_at,
               GROUP_CONCAT(ur.role_code) as roles
        FROM users u
        LEFT JOIN user_roles ur ON ur.user_id = u.id AND ur.revoked_at IS NULL
        GROUP BY u.id
        ORDER BY u.created_at DESC
    """)

    rows = cur.fetchall()
    conn.close()

    result = []
    for r in rows:
        roles = (r[6] or '').split(',') if r[6] else []
        result.append({
            "id": r[0],
            "email": r[1],
            "full_name": r[2],
            "phone": r[3],
            "status": r[4],
            "created_at": r[5],
            "roles": roles,
            "role": roles[0] if roles else None,
        })

    return result



# ========== EMAIL SYSTEM ==========
class EmailSendRequest(BaseModel):
    to_email: str
    subject: str
    body: str
    template: str = "custom"

class EmailTemplateRequest(BaseModel):
    to_email: str
    template: str
    data: Dict[str, Any] = {}

def _log_email(to_email: str, subject: str, body: str, template: str, status: str, error: str = "", sent_by: str = ""):
    import core.db_compat as sqlite3
    from datetime import datetime
    try:
        conn = sqlite3.connect('ai_glue.db')
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO email_logs (recipient, subject, body, template, status, error, sent_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (to_email, subject, body, template, status, error, sent_by, datetime.utcnow().isoformat()))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Email log error: {e}")

def _send_email(to_email: str, subject: str, body: str) -> tuple:
    """Send email via SMTP. Returns (success, error_message)."""
    import os
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_pass = os.getenv("SMTP_PASS", "")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))

    if not smtp_host or not smtp_user or not smtp_pass:
        return (False, "SMTP not configured")

    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP(smtp_host, smtp_port, timeout=15)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        return (True, "")
    except Exception as e:
        return (False, str(e))

@app.post("/email/send", tags=["Email"])
async def send_email_endpoint(body: EmailSendRequest):
    """Send a custom email."""
    success, error = _send_email(body.to_email, body.subject, body.body)
    _log_email(body.to_email, body.subject, body.body, "custom", "sent" if success else "failed", error)

    if not success:
        raise HTTPException(status_code=500, detail=f"Email failed: {error}")

    return {"status": "sent", "to": body.to_email, "subject": body.subject}

@app.get("/email/templates", tags=["Email"])
def get_email_templates():
    """List available email templates."""
    return {
        "templates": [
            {"id": "welcome", "name": "Welcome Email", "description": "Welcome new users"},
            {"id": "invitation", "name": "Invitation", "description": "Invite agents/companies to join"},
            {"id": "job_match", "name": "Job Match", "description": "Notify job seekers of matching jobs"},
            {"id": "student_match", "name": "Student Match", "description": "Notify students of matching programmes"},
            {"id": "hr_alert", "name": "HR Alert", "description": "Notify HR of matching candidates"},
            {"id": "custom", "name": "Custom", "description": "Write your own email"},
        ]
    }

@app.post("/email/send-template", tags=["Email"])
async def send_template_email(body: EmailTemplateRequest):
    """Send email using a template."""
    templates = {
        "welcome": {
            "subject": "Welcome to AI Glue!",
            "body": f"""<html><body>
                <h2>Welcome to AI Glue, {body.data.get('name', 'Friend')}!</h2>
                <p>Your account is ready. Explore your dashboard to get started.</p>
                <p>â€” Team AI Glue</p>
            </body></html>"""
        },
        "invitation": {
            "subject": f"You're invited to AI Glue â€” {body.data.get('role', 'Partner')}",
            "body": f"""<html><body>
                <h2>Hi {body.data.get('name', 'there')},</h2>
                <p>We found your profile on {body.data.get('source', 'LinkedIn')}.</p>
                <p>AI Glue is a platform connecting <strong>{body.data.get('role', 'partners')}</strong> with global opportunities.</p>
                <p><a href="https://ai-glue-frontend.vercel.app/register">Join now â€” it's free</a></p>
                <p>â€” Team AI Glue</p>
            </body></html>"""
        },
        "job_match": {
            "subject": f"ðŸŽ¯ {body.data.get('count', 0)} jobs match your profile!",
            "body": f"""<html><body>
                <h2>Hi {body.data.get('name', 'there')},</h2>
                <p>We found <strong>{body.data.get('count', 0)} new jobs</strong> matching your profile.</p>
                <p><a href="https://ai-glue-frontend.vercel.app/jobseeker-new/search">View jobs now</a></p>
                <p>â€” Team AI Glue</p>
            </body></html>"""
        },
        "student_match": {
            "subject": f"ðŸŽ“ {body.data.get('count', 0)} programmes match you!",
            "body": f"""<html><body>
                <h2>Hi {body.data.get('name', 'there')},</h2>
                <p>We found <strong>{body.data.get('count', 0)} programmes</strong> matching your profile.</p>
                <p><a href="https://ai-glue-frontend.vercel.app/student-new/apply">View programmes</a></p>
                <p>â€” Team AI Glue</p>
            </body></html>"""
        },
        "hr_alert": {
            "subject": f"ðŸ‘¥ {body.data.get('count', 0)} candidates match your job",
            "body": f"""<html><body>
                <h2>Hi {body.data.get('name', 'Hiring Manager')},</h2>
                <p><strong>{body.data.get('count', 0)} candidates</strong> match your job posting.</p>
                <p><a href="https://ai-glue-frontend.vercel.app/employer-new/applicants">View candidates</a></p>
                <p>â€” Team AI Glue</p>
            </body></html>"""
        },
    }

    if body.template not in templates:
        raise HTTPException(status_code=404, detail=f"Template '{body.template}' not found")

    tmpl = templates[body.template]
    success, error = _send_email(body.to_email, tmpl["subject"], tmpl["body"])
    _log_email(body.to_email, tmpl["subject"], tmpl["body"], body.template, "sent" if success else "failed", error)

    if not success:
        raise HTTPException(status_code=500, detail=f"Email failed: {error}")

    return {"status": "sent", "to": body.to_email, "template": body.template}

@app.get("/admin/email/logs", tags=["Admin"])
def get_email_logs(limit: int = 50):
    """Get recent email logs."""
    import core.db_compat as sqlite3
    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()
    cur.execute("""
        SELECT id, recipient, subject, template, status, error, created_at
        FROM email_logs ORDER BY created_at DESC LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    conn.close()

    return {
        "logs": [
            {
                "id": r[0],
                "recipient": r[1],
                "subject": r[2],
                "template": r[3],
                "status": r[4],
                "error": r[5],
                "created_at": r[6],
            }
            for r in rows
        ],
        "total": len(rows),
    }

# ========== PROMOTIONS SYSTEM ==========
from typing import List as ListType

class PromotionCreateRequest(BaseModel):
    title: str
    type: str  # promotion | free | paid
    discount_percent: int = 0
    duration_days: int = 0
    start_date: str = ""
    end_date: str = ""
    message: str = ""
    image_data: str = ""  # base64 data URI
    service_ids: ListType[str] = []

def _get_services_list():
    """Return list of all platform services for promotions."""
    return [
        {"id": "resume_builder", "name": "AI Resume Builder"},
        {"id": "doc_verify", "name": "Document Verification"},
        {"id": "job_match", "name": "AI Job Match"},
        {"id": "student_match", "name": "AI Student Match"},
        {"id": "university_apply", "name": "University Application"},
        {"id": "visa_assist", "name": "Visa Assistance"},
        {"id": "accommodation", "name": "Accommodation"},
        {"id": "part_time", "name": "Part-time Jobs"},
    ]

@app.get("/promotions/services", tags=["Promotions"])
def get_promotion_services():
    """List all services available for promotion."""
    return {"services": _get_services_list()}

@app.post("/admin/promotions/create", tags=["Promotions"])
async def create_promotion(body: PromotionCreateRequest):
    """Create a new promotion / free offer / paid offer."""
    import core.db_compat as sqlite3
    import uuid
    from datetime import datetime

    if body.type not in ("promotion", "free", "paid"):
        raise HTTPException(status_code=400, detail="type must be promotion | free | paid")

    promo_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO promotions (id, title, type, discount_percent, duration_days,
                                start_date, end_date, message, image_data, status,
                                created_by, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', 'admin', ?, ?)
    """, (promo_id, body.title, body.type, body.discount_percent, body.duration_days,
          body.start_date, body.end_date, body.message, body.image_data, now, now))

    for sid in body.service_ids:
        cur.execute(
            "INSERT INTO promotion_services (id, promotion_id, service_id) VALUES (?, ?, ?)",
            (str(uuid.uuid4()), promo_id, sid)
        )

    conn.commit()
    conn.close()
    return {"status": "created", "id": promo_id, "title": body.title}

@app.get("/admin/promotions", tags=["Promotions"])
def list_promotions():
    """List all promotions (admin view)."""
    import core.db_compat as sqlite3
    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()
    cur.execute("""
        SELECT id, title, type, discount_percent, duration_days, start_date,
               end_date, message, image_data, status, created_at
        FROM promotions ORDER BY created_at DESC
    """)
    rows = cur.fetchall()

    result = []
    for r in rows:
        cur.execute("SELECT service_id FROM promotion_services WHERE promotion_id = ?", (r[0],))
        svc_ids = [x[0] for x in cur.fetchall()]
        result.append({
            "id": r[0], "title": r[1], "type": r[2],
            "discount_percent": r[3], "duration_days": r[4],
            "start_date": r[5], "end_date": r[6],
            "message": r[7], "image_data": r[8],
            "status": r[9], "created_at": r[10],
            "service_ids": svc_ids,
        })
    conn.close()
    return {"promotions": result, "total": len(result)}

@app.put("/admin/promotions/{promo_id}", tags=["Promotions"])
async def update_promotion(promo_id: str, body: PromotionCreateRequest):
    """Update an existing promotion."""
    import core.db_compat as sqlite3
    from datetime import datetime
    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()
    cur.execute("""
        UPDATE promotions SET title=?, type=?, discount_percent=?, duration_days=?,
               start_date=?, end_date=?, message=?, image_data=?, updated_at=?
        WHERE id=?
    """, (body.title, body.type, body.discount_percent, body.duration_days,
          body.start_date, body.end_date, body.message, body.image_data,
          datetime.utcnow().isoformat(), promo_id))

    cur.execute("DELETE FROM promotion_services WHERE promotion_id=?", (promo_id,))
    for sid in body.service_ids:
        cur.execute(
            "INSERT INTO promotion_services (id, promotion_id, service_id) VALUES (?, ?, ?)",
            (str(uuid.uuid4()), promo_id, sid)
        )

    conn.commit()
    conn.close()
    return {"status": "updated", "id": promo_id}

@app.delete("/admin/promotions/{promo_id}", tags=["Promotions"])
def delete_promotion(promo_id: str):
    """Delete a promotion."""
    import core.db_compat as sqlite3
    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM promotions WHERE id=?", (promo_id,))
    cur.execute("DELETE FROM promotion_services WHERE promotion_id=?", (promo_id,))
    conn.commit()
    conn.close()
    return {"status": "deleted", "id": promo_id}

@app.patch("/admin/promotions/{promo_id}/status", tags=["Promotions"])
def toggle_promotion_status(promo_id: str, status: str = "active"):
    """Activate / pause a promotion."""
    import core.db_compat as sqlite3
    from datetime import datetime
    if status not in ("active", "paused", "expired"):
        raise HTTPException(status_code=400, detail="status must be active|paused|expired")
    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()
    cur.execute(
        "UPDATE promotions SET status=?, updated_at=? WHERE id=?",
        (status, datetime.utcnow().isoformat(), promo_id)
    )
    conn.commit()
    conn.close()
    return {"status": "updated", "id": promo_id, "new_status": status}

@app.get("/promotions/active", tags=["Promotions"])
def get_active_promotions():
    """Public: fetch promotions to show users (dashboard + login popup)."""
    import core.db_compat as sqlite3
    from datetime import datetime
    now = datetime.utcnow().isoformat()
    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()
    cur.execute("""
        SELECT id, title, type, discount_percent, duration_days, start_date,
               end_date, message, image_data
        FROM promotions
        WHERE status = 'active'
          AND (end_date = '' OR end_date IS NULL OR end_date >= ?)
        ORDER BY created_at DESC
    """, (now,))
    rows = cur.fetchall()
    conn.close()

    return {
        "promotions": [
            {
                "id": r[0], "title": r[1], "type": r[2],
                "discount_percent": r[3], "duration_days": r[4],
                "start_date": r[5], "end_date": r[6],
                "message": r[7], "image_data": r[8],
            }
            for r in rows
        ],
        "total": len(rows),
    }

# ========== ADS SYSTEM ==========
class AdCreateRequest(BaseModel):
    title: str
    banner_data: str = ""
    target_url: str = ""
    placement: str = "dashboard"  # dashboard | sidebar | popup
    start_date: str = ""
    end_date: str = ""

@app.post("/admin/ads/create", tags=["Ads"])
async def create_ad(body: AdCreateRequest):
    import core.db_compat as sqlite3
    import uuid
    from datetime import datetime
    ad_id = str(uuid.uuid4())
    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO ads (id, title, banner_data, target_url, placement, start_date, end_date, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'active', ?)
    """, (ad_id, body.title, body.banner_data, body.target_url, body.placement,
          body.start_date, body.end_date, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    return {"status": "created", "id": ad_id}

@app.get("/admin/ads", tags=["Ads"])
def list_ads():
    import core.db_compat as sqlite3
    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()
    cur.execute("SELECT id, title, banner_data, target_url, placement, start_date, end_date, status, created_at FROM ads ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return {"ads": [
        {"id": r[0], "title": r[1], "banner_data": r[2], "target_url": r[3],
         "placement": r[4], "start_date": r[5], "end_date": r[6],
         "status": r[7], "created_at": r[8]}
        for r in rows
    ]}

@app.delete("/admin/ads/{ad_id}", tags=["Ads"])
def delete_ad(ad_id: str):
    import core.db_compat as sqlite3
    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM ads WHERE id=?", (ad_id,))
    conn.commit()
    conn.close()
    return {"status": "deleted", "id": ad_id}

@app.get("/ads/active", tags=["Ads"])
def get_active_ads(placement: str = "dashboard"):
    import core.db_compat as sqlite3
    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()
    cur.execute("""
        SELECT id, title, banner_data, target_url, placement
        FROM ads WHERE status='active' AND placement=?
        ORDER BY created_at DESC
    """, (placement,))
    rows = cur.fetchall()
    conn.close()
    return {"ads": [
        {"id": r[0], "title": r[1], "banner_data": r[2],
         "target_url": r[3], "placement": r[4]}
        for r in rows
    ]}

# ========== REVENUE / SUBSCRIPTION SYSTEM ==========
import json as json_lib_rev

class SubscribeRequest(BaseModel):
    user_id: str
    plan_id: str
    billing_cycle: str = "monthly"  # monthly | yearly
    coupon_code: str = ""

def _generate_invoice_number():
    import random, string
    from datetime import datetime
    return f"INV-{datetime.utcnow().strftime('%Y%m')}-{''.join(random.choices(string.digits, k=6))}"

def _apply_promotion_discount(amount: float, user_id: str = "") -> tuple:
    """Check active promotions and apply best discount. Returns (final_amount, discount_pct, promo_title)."""
    import core.db_compat as sqlite3
    from datetime import datetime
    now = datetime.utcnow().isoformat()
    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()
    cur.execute("""
        SELECT title, discount_percent FROM promotions
        WHERE status='active' AND type='promotion' AND discount_percent > 0
          AND (end_date = '' OR end_date IS NULL OR end_date >= ?)
        ORDER BY discount_percent DESC LIMIT 1
    """, (now,))
    row = cur.fetchone()
    conn.close()
    if row:
        pct = float(row[1])
        final = round(amount * (1 - pct/100), 2)
        return (final, pct, row[0])
    return (amount, 0, "")

@app.get("/subscriptions/plans", tags=["Subscriptions"])
def list_plans():
    """Public: list all active subscription plans."""
    import core.db_compat as sqlite3
    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()
    cur.execute("""
        SELECT id, name, description, price_monthly, price_yearly, features
        FROM subscription_plans WHERE is_active = 1 ORDER BY price_monthly ASC
    """)
    rows = cur.fetchall()
    conn.close()
    result = []
    for r in rows:
        try:
            feats = json_lib_rev.loads(r[5]) if r[5] else []
        except Exception:
            feats = []
        result.append({
            "id": r[0], "name": r[1], "description": r[2],
            "price_monthly": float(r[3] or 0), "price_yearly": float(r[4] or 0),
            "features": feats,
        })
    return {"plans": result, "total": len(result)}

@app.post("/subscriptions/subscribe", tags=["Subscriptions"])
async def subscribe(body: SubscribeRequest):
    """Subscribe user to a plan (mock payment)."""
    import core.db_compat as sqlite3, uuid
    from datetime import datetime, timedelta

    if body.billing_cycle not in ("monthly", "yearly"):
        raise HTTPException(status_code=400, detail="billing_cycle must be monthly or yearly")

    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()

    # Get plan
    cur.execute("SELECT id, name, price_monthly, price_yearly FROM subscription_plans WHERE id = ? AND is_active = 1", (body.plan_id,))
    plan = cur.fetchone()
    if not plan:
        conn.close()
        raise HTTPException(status_code=404, detail="Plan not found or inactive")

    # Verify user
    cur.execute("SELECT id, email FROM users WHERE id = ?", (body.user_id,))
    user = cur.fetchone()
    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")

    base_amount = float(plan[2] if body.billing_cycle == "monthly" else plan[3])
    final_amount, discount_pct, promo_title = _apply_promotion_discount(base_amount, body.user_id)

    now = datetime.utcnow()
    duration_days = 30 if body.billing_cycle == "monthly" else 365
    end_date = now + timedelta(days=duration_days)

    payment_id = str(uuid.uuid4())
    subscription_id = str(uuid.uuid4())
    invoice_id = str(uuid.uuid4())

    # Free plan â€” no payment record needed
    is_free = final_amount == 0

    if not is_free:
        # Create payment record (mock)
        cur.execute("""
            INSERT INTO payments (id, payer_id, payee_type, payee_id, amount, currency, idempotency_key, status, gateway_ref, created_at, updated_at, payment_meta)
            VALUES (?, ?, 'platform', 'ai_glue', ?, 'INR', ?, 'success', ?, ?, ?, ?)
        """, (payment_id, body.user_id, final_amount, str(uuid.uuid4()),
              f"mock_{payment_id[:8]}", now.isoformat(), now.isoformat(),
              json_lib_rev.dumps({"plan": plan[1], "cycle": body.billing_cycle, "discount_pct": discount_pct})))

    # Create subscription
    cur.execute("""
        INSERT INTO user_subscriptions (id, user_id, plan_id, status, start_date, end_date, auto_renew, payment_id, created_at, updated_at)
        VALUES (?, ?, ?, 'active', ?, ?, 0, ?, ?, ?)
    """, (subscription_id, body.user_id, body.plan_id, now.isoformat(), end_date.isoformat(),
          None if is_free else payment_id, now.isoformat(), now.isoformat()))

    # Create invoice
    cur.execute("""
        INSERT INTO invoices (id, billed_to_id, amount, currency, status, issued_at, due_at,
                              subscription_id, payment_id, invoice_number, description, paid_at)
        VALUES (?, ?, ?, 'INR', ?, ?, ?, ?, ?, ?, ?, ?)
    """, (invoice_id, body.user_id, final_amount, 'paid' if not is_free else 'free',
          now.isoformat(), now.isoformat(),
          subscription_id, None if is_free else payment_id,
          _generate_invoice_number(),
          f"{plan[1]} â€” {body.billing_cycle}" + (f" ({discount_pct}% off)" if discount_pct > 0 else ""),
          now.isoformat()))

    conn.commit()
    conn.close()

    # ===== CUSTOMER ACTIVATION EMAIL =====
    try:
        cur2 = sqlite3.connect('ai_glue.db').cursor()
        cur2.execute("SELECT email FROM users WHERE id = ?", (user_id,))
        urow = cur2.fetchone()
        user_email = urow[0] if urow else None
        cur2.connection.close()

        if user_email:
            days_left = duration_days
            end_str = end_date.strftime("%d %b %Y")
            method_label = {"upi": "UPI", "esewa": "eSewa", "paypal": "PayPal"}.get(method, method.upper())

            act_body = f"""
            <html><body style="font-family: Arial, sans-serif;">
                <div style="max-width:600px; margin:auto;">
                    <h2 style="color:#16a34a;">ðŸŽ‰ Aapka {plan_name} Pack Active Ho Gaya!</h2>
                    <p>Shukriya! Aapka payment verify ho gaya aur subscription activate ho gayi.</p>
                    
                    <div style="background:#f0fdf4; border-left:4px solid #16a34a; padding:16px; border-radius:8px; margin:20px 0;">
                        <p style="margin:4px 0;"><b>Plan:</b> {plan_name}</p>
                        <p style="margin:4px 0;"><b>Billing:</b> {billing_cycle}</p>
                        <p style="margin:4px 0;"><b>Amount Paid:</b> {currency} {amount}</p>
                        <p style="margin:4px 0;"><b>Method:</b> {method_label}</p>
                        <p style="margin:4px 0;"><b>Started:</b> {now.strftime("%d %b %Y")}</p>
                        <p style="margin:4px 0;"><b>Valid Till:</b> <b style="color:#16a34a;">{end_str} ({days_left} days)</b></p>
                    </div>
                    
                    <p>âœ… Ab aap saare {plan_name} features use kar sakte ho â€” <a href="http://localhost:5173/my-subscription">My Subscription</a> dekho.</p>
                    
                    <p style="margin-top:20px;">
                        <a href="http://localhost:5173/my-subscription" style="background:#9333ea; color:white; padding:10px 20px; text-decoration:none; border-radius:6px;">View My Subscription â†’</a>
                    </p>
                    
                    <p style="color:#666; font-size:13px; margin-top:24px;">Koi bhi sawaal ho toh reply karein is email pe.</p>
                    <p>â€” Team AI Glue ðŸ’œ</p>
                </div>
            </body></html>
            """
            _send_email(user_email, f"ðŸŽ‰ {plan_name} Activated â€” Valid till {end_str}", act_body)
            _log_email(user_email, f"Activated: {plan_name}", "", "customer_activation", "sent")
    except Exception as e:
        print(f"Activation email failed: {e}")

    return {
        "status": "approved",
        "subscription_id": subscription_id,
        "user_id": user_id,
        "plan": plan_name,
        "ends_at": end_date.isoformat(),
    }

@app.get("/subscriptions/me/{user_id}", tags=["Subscriptions"])
def my_subscription(user_id: str):
    """Get current active subscription for a user."""
    import core.db_compat as sqlite3
    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()
    cur.execute("""
        SELECT s.id, s.status, s.start_date, s.end_date, s.auto_renew,
               p.name, p.description, p.price_monthly, p.price_yearly, p.features
        FROM user_subscriptions s
        JOIN subscription_plans p ON p.id = s.plan_id
        WHERE s.user_id = ? AND s.status = 'active'
        ORDER BY s.created_at DESC LIMIT 1
    """, (user_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return {"subscription": None, "message": "No active subscription"}
    try:
        feats = json_lib_rev.loads(row[9]) if row[9] else []
    except Exception:
        feats = []
    return {
        "subscription": {
            "id": row[0], "status": row[1],
            "start_date": row[2], "end_date": row[3], "auto_renew": bool(row[4]),
            "plan": {"name": row[5], "description": row[6],
                     "price_monthly": float(row[7] or 0), "price_yearly": float(row[8] or 0),
                     "features": feats},
        }
    }

@app.get("/subscriptions/invoices/{user_id}", tags=["Subscriptions"])
def my_invoices(user_id: str):
    """Get invoices for a user."""
    import core.db_compat as sqlite3
    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()
    cur.execute("""
        SELECT id, invoice_number, amount, currency, status, issued_at, paid_at, description
        FROM invoices WHERE billed_to_id = ? ORDER BY issued_at DESC LIMIT 50
    """, (user_id,))
    rows = cur.fetchall()
    conn.close()
    return {"invoices": [
        {"id": r[0], "invoice_number": r[1], "amount": float(r[2] or 0),
         "currency": r[3], "status": r[4], "issued_at": r[5],
         "paid_at": r[6], "description": r[7]}
        for r in rows
    ], "total": len(rows)}

@app.post("/subscriptions/cancel/{user_id}", tags=["Subscriptions"])
def cancel_subscription(user_id: str):
    """Cancel active subscription."""
    import core.db_compat as sqlite3
    from datetime import datetime
    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()
    cur.execute("""
        UPDATE user_subscriptions SET status='cancelled', auto_renew=0, updated_at=?
        WHERE user_id=? AND status='active'
    """, (datetime.utcnow().isoformat(), user_id))
    conn.commit()
    conn.close()
    return {"status": "cancelled", "user_id": user_id}

@app.get("/admin/revenue/dashboard", tags=["Admin"])
def revenue_dashboard():
    """Admin: revenue metrics."""
    import core.db_compat as sqlite3
    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM subscription_plans WHERE is_active=1")
    total_plans = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM user_subscriptions WHERE status='active'")
    active_subs = cur.fetchone()[0]

    cur.execute("SELECT COALESCE(SUM(amount), 0) FROM payments WHERE status='success'")
    total_revenue = float(cur.fetchone()[0] or 0)

    cur.execute("SELECT COALESCE(SUM(amount), 0) FROM payments WHERE status='success' AND created_at >= date('now','start of month')")
    month_revenue = float(cur.fetchone()[0] or 0)

    cur.execute("""
        SELECT p.name, COUNT(*) FROM user_subscriptions s
        JOIN subscription_plans p ON p.id = s.plan_id
        WHERE s.status='active' GROUP BY p.name
    """)
    by_plan = [{"plan": r[0], "count": r[1]} for r in cur.fetchall()]

    cur.execute("""
        SELECT id, payer_id, amount, currency, status, created_at
        FROM payments ORDER BY created_at DESC LIMIT 20
    """)
    recent = [{"id": r[0], "user_id": r[1], "amount": float(r[2] or 0),
               "currency": r[3], "status": r[4], "created_at": r[5]}
              for r in cur.fetchall()]

    conn.close()
    return {
        "total_plans": total_plans,
        "active_subscriptions": active_subs,
        "total_revenue": total_revenue,
        "month_revenue": month_revenue,
        "by_plan": by_plan,
        "recent_payments": recent,
    }

@app.get("/admin/subscriptions", tags=["Admin"])
def admin_subscriptions():
    """Admin: list all subscriptions."""
    import core.db_compat as sqlite3
    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()
    cur.execute("""
        SELECT s.id, s.user_id, u.email, p.name, s.status, s.start_date, s.end_date
        FROM user_subscriptions s
        JOIN subscription_plans p ON p.id = s.plan_id
        LEFT JOIN users u ON u.id = s.user_id
        ORDER BY s.created_at DESC LIMIT 100
    """)
    rows = cur.fetchall()
    conn.close()
    return {"subscriptions": [
        {"id": r[0], "user_id": r[1], "email": r[2], "plan": r[3],
         "status": r[4], "start_date": r[5], "end_date": r[6]}
        for r in rows
    ], "total": len(rows)}

# ========== RAZORPAY PAYMENT INTEGRATION ==========
import os as os_rzp
import hmac as hmac_rzp
import hashlib as hashlib_rzp

class RazorpayOrderRequest(BaseModel):
    user_id: str
    plan_id: str
    billing_cycle: str = "monthly"

class RazorpayVerifyRequest(BaseModel):
    user_id: str
    plan_id: str
    billing_cycle: str
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

def _get_razorpay_client():
    """Return Razorpay client if configured, else None."""
    key_id = os_rzp.getenv("RAZORPAY_KEY_ID", "")
    key_secret = os_rzp.getenv("RAZORPAY_KEY_SECRET", "")
    if not key_id or not key_secret or "xxxxx" in key_id:
        return None
    try:
        import razorpay
        return razorpay.Client(auth=(key_id, key_secret))
    except Exception as e:
        print(f"Razorpay init failed: {e}")
        return None

@app.get("/payments/razorpay/config", tags=["Payments"])
def razorpay_config():
    """Return public Razorpay key for frontend checkout."""
    key_id = os_rzp.getenv("RAZORPAY_KEY_ID", "")
    configured = bool(key_id and "xxxxx" not in key_id)
    return {"key_id": key_id if configured else "", "configured": configured}

@app.post("/payments/razorpay/create-order", tags=["Payments"])
async def create_razorpay_order(body: RazorpayOrderRequest):
    """Create a Razorpay order for a subscription."""
    import core.db_compat as sqlite3
    client = _get_razorpay_client()
    if not client:
        raise HTTPException(status_code=503, detail="Razorpay not configured. Add test keys in .env")

    if body.billing_cycle not in ("monthly", "yearly"):
        raise HTTPException(status_code=400, detail="billing_cycle must be monthly or yearly")

    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()
    cur.execute("SELECT id, name, price_monthly, price_yearly FROM subscription_plans WHERE id=? AND is_active=1", (body.plan_id,))
    plan = cur.fetchone()
    conn.close()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    base_amount = float(plan[2] if body.billing_cycle == "monthly" else plan[3])
    final_amount, discount_pct, promo_title = _apply_promotion_discount(base_amount, body.user_id)

    if final_amount <= 0:
        raise HTTPException(status_code=400, detail="Free plan â€” use /subscriptions/subscribe directly")

    amount_paise = int(round(final_amount * 100))

    try:
        order = client.order.create({
            "amount": amount_paise,
            "currency": "INR",
            "receipt": f"rcpt_{body.user_id[:8]}",
            "notes": {
                "user_id": body.user_id,
                "plan_id": body.plan_id,
                "plan_name": plan[1],
                "billing_cycle": body.billing_cycle,
                "discount_pct": str(discount_pct),
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Razorpay order failed: {str(e)}")

    return {
        "order_id": order["id"],
        "amount": final_amount,
        "amount_paise": amount_paise,
        "currency": "INR",
        "plan_name": plan[1],
        "billing_cycle": body.billing_cycle,
        "discount_pct": discount_pct,
        "promo_applied": promo_title,
        "key_id": os_rzp.getenv("RAZORPAY_KEY_ID", ""),
    }

@app.post("/payments/razorpay/verify", tags=["Payments"])
async def verify_razorpay_payment(body: RazorpayVerifyRequest):
    """Verify Razorpay signature and activate subscription."""
    import core.db_compat as sqlite3, uuid
    from datetime import datetime, timedelta

    key_secret = os_rzp.getenv("RAZORPAY_KEY_SECRET", "")
    if not key_secret or "xxxx" in key_secret:
        raise HTTPException(status_code=503, detail="Razorpay secret missing")

    msg = f"{body.razorpay_order_id}|{body.razorpay_payment_id}".encode()
    expected = hmac_rzp.new(key_secret.encode(), msg, hashlib_rzp.sha256).hexdigest()
    if expected != body.razorpay_signature:
        raise HTTPException(status_code=400, detail="Payment signature mismatch")

    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()

    cur.execute("SELECT id, name, price_monthly, price_yearly FROM subscription_plans WHERE id=? AND is_active=1", (body.plan_id,))
    plan = cur.fetchone()
    if not plan:
        conn.close()
        raise HTTPException(status_code=404, detail="Plan not found")

    base_amount = float(plan[2] if body.billing_cycle == "monthly" else plan[3])
    final_amount, discount_pct, promo_title = _apply_promotion_discount(base_amount, body.user_id)

    now = datetime.utcnow()
    duration_days = 30 if body.billing_cycle == "monthly" else 365
    end_date = now + timedelta(days=duration_days)

    payment_id = str(uuid.uuid4())
    subscription_id = str(uuid.uuid4())
    invoice_id = str(uuid.uuid4())

    cur.execute("""
        INSERT INTO payments (id, payer_id, payee_type, payee_id, amount, currency, idempotency_key, status, gateway_ref, created_at, updated_at, payment_meta)
        VALUES (?, ?, 'platform', 'ai_glue', ?, 'INR', ?, 'success', ?, ?, ?, ?)
    """, (payment_id, body.user_id, final_amount, body.razorpay_order_id,
          body.razorpay_payment_id, now.isoformat(), now.isoformat(),
          json_lib_rev.dumps({
              "gateway": "razorpay",
              "order_id": body.razorpay_order_id,
              "payment_id": body.razorpay_payment_id,
              "plan": plan[1], "cycle": body.billing_cycle, "discount_pct": discount_pct
          })))

    cur.execute("""
        INSERT INTO user_subscriptions (id, user_id, plan_id, status, start_date, end_date, auto_renew, payment_id, created_at, updated_at)
        VALUES (?, ?, ?, 'active', ?, ?, 0, ?, ?, ?)
    """, (subscription_id, body.user_id, body.plan_id, now.isoformat(), end_date.isoformat(),
          payment_id, now.isoformat(), now.isoformat()))

    cur.execute("""
        INSERT INTO invoices (id, billed_to_id, amount, currency, status, issued_at, due_at,
                              subscription_id, payment_id, invoice_number, description, paid_at)
        VALUES (?, ?, ?, 'INR', 'paid', ?, ?, ?, ?, ?, ?, ?)
    """, (invoice_id, body.user_id, final_amount, now.isoformat(), now.isoformat(),
          subscription_id, payment_id, _generate_invoice_number(),
          f"{plan[1]} â€” {body.billing_cycle}" + (f" ({discount_pct}% off)" if discount_pct > 0 else ""),
          now.isoformat()))

    conn.commit()
    conn.close()

    return {
        "status": "subscribed",
        "subscription_id": subscription_id,
        "plan": plan[1],
        "final_amount": final_amount,
        "discount_pct": discount_pct,
        "razorpay_payment_id": body.razorpay_payment_id,
        "starts_at": now.isoformat(),
        "ends_at": end_date.isoformat(),
    }

# ========== ESEWA PAYMENT INTEGRATION (NEPAL) ==========
import os as os_esewa
import hmac as hmac_esewa
import hashlib as hashlib_esewa
import base64 as base64_esewa

class EsewaOrderRequest(BaseModel):
    user_id: str
    plan_id: str
    billing_cycle: str = "monthly"

class EsewaVerifyRequest(BaseModel):
    user_id: str
    plan_id: str
    billing_cycle: str
    transaction_uuid: str
    total_amount: float

def _get_esewa_config():
    """Return eSewa config based on environment."""
    is_test = os_esewa.getenv("ESEWA_MODE", "test").lower() == "test"
    if is_test:
        return {
            "product_code": "EPAYTEST",
            "secret_key": "8gBm/:&EnhH.1/q",
            "payment_url": "https://rc-epay.esewa.com.np/api/epay/main/v2/form",
            "status_url": "https://rc.esewa.com.np/api/epay/transaction/status/",
            "is_test": True,
        }
    return {
        "product_code": os_esewa.getenv("ESEWA_PRODUCT_CODE", ""),
        "secret_key": os_esewa.getenv("ESEWA_SECRET_KEY", ""),
        "payment_url": "https://epay.esewa.com.np/api/epay/main/v2/form",
        "status_url": "https://esewa.com.np/api/epay/transaction/status/",
        "is_test": False,
    }

@app.get("/payments/esewa/config", tags=["Payments"])
def esewa_config():
    """Return eSewa config for frontend."""
    cfg = _get_esewa_config()
    return {
        "product_code": cfg["product_code"],
        "is_test": cfg["is_test"],
        "configured": True if cfg["is_test"] else bool(cfg["secret_key"]),
        "payment_url": cfg["payment_url"],
    }

@app.post("/payments/esewa/create-order", tags=["Payments"])
async def create_esewa_order(body: EsewaOrderRequest):
    """Create eSewa payment order (for Nepal)."""
    import core.db_compat as sqlite3, uuid
    from datetime import datetime

    cfg = _get_esewa_config()
    if not cfg["is_test"] and not cfg["secret_key"]:
        raise HTTPException(status_code=503, detail="eSewa not configured. Add production keys in .env")

    if body.billing_cycle not in ("monthly", "yearly"):
        raise HTTPException(status_code=400, detail="billing_cycle must be monthly or yearly")

    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()
    cur.execute("SELECT id, name, price_monthly, price_yearly FROM subscription_plans WHERE id=? AND is_active=1", (body.plan_id,))
    plan = cur.fetchone()
    conn.close()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Convert INR to NPR (rough rate: 1 INR = 1.6 NPR)
    INR_TO_NPR = 1.6
    base_inr = float(plan[2] if body.billing_cycle == "monthly" else plan[3])
    base_amount = round(base_inr * INR_TO_NPR, 2)

    final_amount, discount_pct, promo_title = _apply_promotion_discount(base_amount, body.user_id)

    if final_amount <= 0:
        raise HTTPException(status_code=400, detail="Free plan â€” use /subscriptions/subscribe directly")

    amount_str = f"{final_amount:.2f}"
    total_amount = amount_str
    transaction_uuid = str(uuid.uuid4())

    # Generate HMAC-SHA256 signature (base64 encoded)
    message = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={cfg['product_code']}"
    signature = base64_esewa.b64encode(
        hmac_esewa.new(cfg["secret_key"].encode(), message.encode(), hashlib_esewa.sha256).digest()
    ).decode()

    return {
        "transaction_uuid": transaction_uuid,
        "amount": amount_str,
        "tax_amount": "0",
        "product_service_charge": "0",
        "product_delivery_charge": "0",
        "total_amount": total_amount,
        "product_code": cfg["product_code"],
        "signature": signature,
        "signed_field_names": "total_amount,transaction_uuid,product_code",
        "payment_url": cfg["payment_url"],
        "plan_name": plan[1],
        "billing_cycle": body.billing_cycle,
        "discount_pct": discount_pct,
        "promo_applied": promo_title,
        "currency": "NPR",
    }

@app.post("/payments/esewa/verify", tags=["Payments"])
async def verify_esewa_payment(body: EsewaVerifyRequest):
    """Verify eSewa payment and activate subscription."""
    import core.db_compat as sqlite3, uuid
    from datetime import datetime, timedelta
    import requests as req_lib

    cfg = _get_esewa_config()

    # Check status via eSewa API
    try:
        status_resp = req_lib.get(cfg["status_url"], params={
            "product_code": cfg["product_code"],
            "total_amount": body.total_amount,
            "transaction_uuid": body.transaction_uuid,
        }, timeout=15)
        status_data = status_resp.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"eSewa status check failed: {str(e)}")

    if status_data.get("status") != "COMPLETE":
        raise HTTPException(status_code=400, detail=f"Payment not completed: {status_data.get('status', 'unknown')}")

    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()

    cur.execute("SELECT id, name, price_monthly, price_yearly FROM subscription_plans WHERE id=? AND is_active=1", (body.plan_id,))
    plan = cur.fetchone()
    if not plan:
        conn.close()
        raise HTTPException(status_code=404, detail="Plan not found")

    # Amount in NPR (already converted)
    INR_TO_NPR = 1.6
    base_inr = float(plan[2] if body.billing_cycle == "monthly" else plan[3])
    base_amount = round(base_inr * INR_TO_NPR, 2)
    final_amount, discount_pct, promo_title = _apply_promotion_discount(base_amount, body.user_id)

    now = datetime.utcnow()
    duration_days = 30 if body.billing_cycle == "monthly" else 365
    end_date = now + timedelta(days=duration_days)

    payment_id = str(uuid.uuid4())
    subscription_id = str(uuid.uuid4())
    invoice_id = str(uuid.uuid4())

    cur.execute("""
        INSERT INTO payments (id, payer_id, payee_type, payee_id, amount, currency, idempotency_key, status, gateway_ref, created_at, updated_at, payment_meta)
        VALUES (?, ?, 'platform', 'ai_glue', ?, 'NPR', ?, 'success', ?, ?, ?, ?)
    """, (payment_id, body.user_id, final_amount, body.transaction_uuid,
          body.transaction_uuid, now.isoformat(), now.isoformat(),
          json_lib_rev.dumps({
              "gateway": "esewa",
              "transaction_uuid": body.transaction_uuid,
              "plan": plan[1], "cycle": body.billing_cycle, "discount_pct": discount_pct,
              "currency": "NPR"
          })))

    cur.execute("""
        INSERT INTO user_subscriptions (id, user_id, plan_id, status, start_date, end_date, auto_renew, payment_id, created_at, updated_at)
        VALUES (?, ?, ?, 'active', ?, ?, 0, ?, ?, ?)
    """, (subscription_id, body.user_id, body.plan_id, now.isoformat(), end_date.isoformat(),
          payment_id, now.isoformat(), now.isoformat()))

    cur.execute("""
        INSERT INTO invoices (id, billed_to_id, amount, currency, status, issued_at, due_at,
                              subscription_id, payment_id, invoice_number, description, paid_at)
        VALUES (?, ?, ?, 'NPR', 'paid', ?, ?, ?, ?, ?, ?, ?)
    """, (invoice_id, body.user_id, final_amount, now.isoformat(), now.isoformat(),
          subscription_id, payment_id, _generate_invoice_number(),
          f"{plan[1]} â€” {body.billing_cycle}" + (f" ({discount_pct}% off)" if discount_pct > 0 else ""),
          now.isoformat()))

    conn.commit()
    conn.close()

    return {
        "status": "subscribed",
        "subscription_id": subscription_id,
        "plan": plan[1],
        "final_amount": final_amount,
        "currency": "NPR",
        "discount_pct": discount_pct,
        "esewa_transaction_uuid": body.transaction_uuid,
        "starts_at": now.isoformat(),
        "ends_at": end_date.isoformat(),
    }

# ========== PAYMENT SETTINGS & MANUAL PAYMENTS ==========
class PaymentSettingsRequest(BaseModel):
    upi_id_1: str = ""
    upi_id_2: str = ""
    upi_qr_image: str = ""
    esewa_id: str = ""
    esewa_name: str = ""
    esewa_qr_image: str = ""
    paypal_link: str = ""
    paypal_qr_image: str = ""

class ManualPaymentRequest(BaseModel):
    user_id: str
    user_email: str = ""
    plan_id: str
    billing_cycle: str = "monthly"
    method: str = "upi"  # upi | esewa | paypal
    utr_number: str = ""
    screenshot_data: str = ""

class ApprovalRequest(BaseModel):
    admin_note: str = ""
    reject_reason: str = ""

@app.get("/payments/settings", tags=["Payments"])
def get_payment_settings():
    """Public: get UPI/eSewa/PayPal QR and IDs."""
    import core.db_compat as sqlite3
    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()
    cur.execute("""
        SELECT upi_id_1, upi_id_2, upi_qr_image, esewa_id, esewa_name,
               esewa_qr_image, paypal_link, paypal_qr_image
        FROM payment_settings LIMIT 1
    """)
    row = cur.fetchone()
    conn.close()
    if not row:
        return {"settings": {}}
    return {
        "settings": {
            "upi_id_1": row[0], "upi_id_2": row[1], "upi_qr_image": row[2],
            "esewa_id": row[3], "esewa_name": row[4], "esewa_qr_image": row[5],
            "paypal_link": row[6], "paypal_qr_image": row[7],
        }
    }

@app.post("/admin/payments/settings", tags=["Admin"])
async def update_payment_settings(body: PaymentSettingsRequest):
    """Admin: update payment settings."""
    import core.db_compat as sqlite3, uuid
    from datetime import datetime
    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()
    cur.execute("SELECT id FROM payment_settings LIMIT 1")
    row = cur.fetchone()
    now = datetime.utcnow().isoformat()
    if row:
        cur.execute("""
            UPDATE payment_settings SET upi_id_1=?, upi_id_2=?, upi_qr_image=?,
                   esewa_id=?, esewa_name=?, esewa_qr_image=?,
                   paypal_link=?, paypal_qr_image=?, updated_at=?
            WHERE id=?
        """, (body.upi_id_1, body.upi_id_2, body.upi_qr_image,
              body.esewa_id, body.esewa_name, body.esewa_qr_image,
              body.paypal_link, body.paypal_qr_image, now, row[0]))
    else:
        cur.execute("""
            INSERT INTO payment_settings (id, upi_id_1, upi_id_2, upi_qr_image,
                   esewa_id, esewa_name, esewa_qr_image, paypal_link, paypal_qr_image, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (str(uuid.uuid4()), body.upi_id_1, body.upi_id_2, body.upi_qr_image,
              body.esewa_id, body.esewa_name, body.esewa_qr_image,
              body.paypal_link, body.paypal_qr_image, now))
    conn.commit()
    conn.close()
    return {"status": "updated"}

@app.post("/payments/manual/submit", tags=["Payments"])
async def submit_manual_payment(body: ManualPaymentRequest):
    """User: submit UTR after manual payment (UPI/eSewa/PayPal)."""
    import core.db_compat as sqlite3, uuid
    from datetime import datetime

    if body.method not in ("upi", "esewa", "paypal"):
        raise HTTPException(status_code=400, detail="method must be upi|esewa|paypal")

    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()

    cur.execute("SELECT id, name, price_monthly, price_yearly FROM subscription_plans WHERE id=? AND is_active=1", (body.plan_id,))
    plan = cur.fetchone()
    if not plan:
        conn.close()
        raise HTTPException(status_code=404, detail="Plan not found")

    base_amount = float(plan[2] if body.billing_cycle == "monthly" else plan[3])
    final_amount, discount_pct, promo_title = _apply_promotion_discount(base_amount, body.user_id)

    # Currency by method
    currency = "NPR" if body.method == "esewa" else "INR"
    if body.method == "esewa":
        final_amount = round(final_amount * 1.6, 2)  # INR â†’ NPR

    now = datetime.utcnow().isoformat()
    payment_id = str(uuid.uuid4())

    cur.execute("""
        INSERT INTO pending_payments (id, user_id, user_email, plan_id, plan_name,
              billing_cycle, amount, currency, method, utr_number, screenshot_data,
              status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?)
    """, (payment_id, body.user_id, body.user_email, body.plan_id, plan[1],
          body.billing_cycle, final_amount, currency, body.method,
          body.utr_number, body.screenshot_data, now, now))

    conn.commit()
    conn.close()

    # ===== EMAIL ALERTS =====
    method_label = {"upi": "UPI", "esewa": "eSewa", "paypal": "PayPal"}.get(body.method, body.method.upper())

    # 1. Admin alert
    try:
        admin_email = os.getenv("SMTP_USER", "pramod.rf@gmail.com")
        admin_body = f"""
        <html><body style="font-family: Arial, sans-serif;">
            <h2 style="color:#9333ea;">ðŸ”” Naya Payment Aaya</h2>
            <table style="border-collapse: collapse;">
                <tr><td style="padding:6px;"><b>User:</b></td><td>{body.user_email or body.user_id}</td></tr>
                <tr><td style="padding:6px;"><b>Plan:</b></td><td>{plan[1]} ({body.billing_cycle})</td></tr>
                <tr><td style="padding:6px;"><b>Amount:</b></td><td><b>{currency} {final_amount}</b></td></tr>
                <tr><td style="padding:6px;"><b>Method:</b></td><td>{method_label}</td></tr>
                <tr><td style="padding:6px;"><b>UTR:</b></td><td><code>{body.utr_number}</code></td></tr>
            </table>
            <p style="color:#666; font-size:12px;">Ref: {payment_id[:8]}</p>
        </body></html>
        """
        _send_email(admin_email, f"ðŸ”” Naya Payment: {currency} {final_amount} â€” {plan[1]}", admin_body)
        _log_email(admin_email, f"New payment: {plan[1]}", "", "admin_alert", "sent")
    except Exception as e:
        print(f"Admin email failed: {e}")

    # 2. Customer thank you
    try:
        if body.user_email:
            customer_body = f"""
            <html><body style="font-family: Arial, sans-serif;">
                <div style="max-width:600px; margin:auto;">
                    <h2 style="color:#9333ea;">ðŸ™ Thank you!</h2>
                    <p>Aapka payment humein mil gaya hai.</p>
                    <div style="background:#f3f4f6; padding:16px; border-radius:8px; margin:20px 0;">
                        <p style="margin:4px 0;"><b>Plan:</b> {plan[1]} ({body.billing_cycle})</p>
                        <p style="margin:4px 0;"><b>Amount:</b> {currency} {final_amount}</p>
                        <p style="margin:4px 0;"><b>Method:</b> {method_label}</p>
                        <p style="margin:4px 0;"><b>UTR:</b> {body.utr_number}</p>
                        <p style="margin:4px 0;"><b>Reference ID:</b> <code>{payment_id[:8]}</code></p>
                    </div>
                    <p>â³ <b>Next step:</b> Hamari team 24 ghante ke andar verify karegi.</p>
                    <p>â€” Team AI Glue</p>
                </div>
            </body></html>
            """
            _send_email(body.user_email, f"ðŸ™ Payment Received â€” {plan[1]} ({payment_id[:8]})", customer_body)
            _log_email(body.user_email, f"Payment received: {plan[1]}", "", "customer_ack", "sent")
    except Exception as e:
        print(f"Customer email failed: {e}")

    return {
        "status": "pending",
        "payment_id": payment_id,
        "amount": final_amount,
        "currency": currency,
        "method": body.method,
        "message": "Payment submitted. Admin will verify within 24 hours.",
    }

@app.get("/admin/payments/pending", tags=["Admin"])
def list_pending_payments(status: str = "pending"):
    """Admin: list pending payments."""
    import core.db_compat as sqlite3
    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()
    cur.execute("""
        SELECT id, user_id, user_email, plan_name, billing_cycle, amount, currency,
               method, utr_number, screenshot_data, status, created_at
        FROM pending_payments WHERE status = ?
        ORDER BY created_at DESC LIMIT 100
    """, (status,))
    rows = cur.fetchall()
    conn.close()
    return {"payments": [
        {"id": r[0], "user_id": r[1], "user_email": r[2], "plan_name": r[3],
         "billing_cycle": r[4], "amount": float(r[5] or 0), "currency": r[6],
         "method": r[7], "utr_number": r[8], "screenshot_data": r[9],
         "status": r[10], "created_at": r[11]}
        for r in rows
    ], "total": len(rows)}

@app.post("/admin/payments/{payment_id}/approve", tags=["Admin"])
async def approve_payment(payment_id: str, body: ApprovalRequest):
    """Admin: approve pending payment â†’ activate subscription."""
    import core.db_compat as sqlite3, uuid
    from datetime import datetime, timedelta

    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()

    cur.execute("SELECT user_id, plan_id, billing_cycle, amount, currency, method, status FROM pending_payments WHERE id=?", (payment_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Payment not found")
    if row[6] != "pending":
        conn.close()
        raise HTTPException(status_code=400, detail=f"Payment already {row[6]}")

    user_id, plan_id, billing_cycle, amount, currency, method = row[:6]

    cur.execute("SELECT name FROM subscription_plans WHERE id=?", (plan_id,))
    plan_row = cur.fetchone()
    plan_name = plan_row[0] if plan_row else "Unknown"

    now = datetime.utcnow()
    duration_days = 30 if billing_cycle == "monthly" else 365
    end_date = now + timedelta(days=duration_days)

    # Create payment record
    new_payment_id = str(uuid.uuid4())
    cur.execute("""
        INSERT INTO payments (id, payer_id, payee_type, payee_id, amount, currency,
              idempotency_key, status, gateway_ref, created_at, updated_at, payment_meta)
        VALUES (?, ?, 'platform', 'ai_glue', ?, ?, ?, 'success', ?, ?, ?, ?)
    """, (new_payment_id, user_id, amount, currency, payment_id,
          f"manual_{method}", now.isoformat(), now.isoformat(),
          json_lib_rev.dumps({"gateway": f"manual_{method}", "approved_by": "admin"})))

    # Create subscription
    subscription_id = str(uuid.uuid4())
    cur.execute("""
        INSERT INTO user_subscriptions (id, user_id, plan_id, status, start_date,
              end_date, auto_renew, payment_id, created_at, updated_at)
        VALUES (?, ?, ?, 'active', ?, ?, 0, ?, ?, ?)
    """, (subscription_id, user_id, plan_id, now.isoformat(), end_date.isoformat(),
          new_payment_id, now.isoformat(), now.isoformat()))

    # Create invoice
    invoice_id = str(uuid.uuid4())
    cur.execute("""
        INSERT INTO invoices (id, billed_to_id, amount, currency, status, issued_at,
              due_at, subscription_id, payment_id, invoice_number, description, paid_at)
        VALUES (?, ?, ?, ?, 'paid', ?, ?, ?, ?, ?, ?, ?)
    """, (invoice_id, user_id, amount, currency, now.isoformat(), now.isoformat(),
          subscription_id, new_payment_id, _generate_invoice_number(),
          f"{plan_name} â€” {billing_cycle} (manual {method})", now.isoformat()))

    # Update pending payment
    cur.execute("""
        UPDATE pending_payments SET status='approved', admin_note=?,
              subscription_id=?, updated_at=? WHERE id=?
    """, (body.admin_note, subscription_id, now.isoformat(), payment_id))

    conn.commit()
    conn.close()

    return {
        "status": "approved",
        "subscription_id": subscription_id,
        "user_id": user_id,
        "plan": plan_name,
        "ends_at": end_date.isoformat(),
    }

@app.post("/admin/payments/{payment_id}/reject", tags=["Admin"])
async def reject_payment(payment_id: str, body: ApprovalRequest):
    """Admin: reject pending payment."""
    import core.db_compat as sqlite3
    from datetime import datetime
    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()
    cur.execute("""
        UPDATE pending_payments SET status='rejected', admin_note=?,
              updated_at=? WHERE id=?
    """, (body.reject_reason, datetime.utcnow().isoformat(), payment_id))
    conn.commit()
    conn.close()
    return {"status": "rejected", "id": payment_id}

@app.get("/payments/my/{user_id}", tags=["Payments"])
def my_payments(user_id: str):
    """User: get their own pending/approved/rejected payments."""
    import core.db_compat as sqlite3
    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()
    cur.execute("""
        SELECT id, plan_name, billing_cycle, amount, currency, method,
               utr_number, status, admin_note, created_at
        FROM pending_payments WHERE user_id = ?
        ORDER BY created_at DESC LIMIT 50
    """, (user_id,))
    rows = cur.fetchall()
    conn.close()
    return {"payments": [
        {"id": r[0], "plan_name": r[1], "billing_cycle": r[2],
         "amount": float(r[3] or 0), "currency": r[4], "method": r[5],
         "utr_number": r[6], "status": r[7], "admin_note": r[8],
         "created_at": r[9]}
        for r in rows
    ], "total": len(rows)}

# ========== SEED DATABASE ENDPOINT ==========
@app.post("/admin/seed-db", tags=["Admin"])
def seed_database():
    """
    Seed database with initial data from seed_data.json.
    Idempotent â€” duplicate rows are skipped (INSERT OR IGNORE).
    """
    import json as json_lib_seed
    import core.db_compat as sqlite3
    import os as os_seed

    seed_path = os_seed.path.join(os_seed.path.dirname(__file__), "seed_data.json")
    if not os_seed.path.exists(seed_path):
        raise HTTPException(status_code=404, detail="seed_data.json not found in project root")

    with open(seed_path, "r", encoding="utf-8") as f:
        data = json_lib_seed.load(f)

    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()

    table_order = [
        'countries',
        'universities',
        'cities',
        'campuses',
        'departments',
        'courses',
        'intake_seats',
        'country_documents',
        'opportunities',
    ]

    results = {}

    for table in table_order:
        rows = data.get(table, [])
        if not rows:
            results[table] = {"inserted": 0, "skipped": 0, "total": 0}
            continue

        inserted = 0
        skipped = 0
        errors = []

        for row in rows:
            try:
                cols = list(row.keys())
                placeholders = ",".join(["?"] * len(cols))
                col_names = ",".join(cols)
                values = [row[c] for c in cols]

                cur.execute(
                    f"INSERT OR IGNORE INTO {table} ({col_names}) VALUES ({placeholders})",
                    values
                )
                if cur.rowcount > 0:
                    inserted += 1
                else:
                    skipped += 1
            except Exception as e:
                skipped += 1
                if len(errors) < 3:
                    errors.append(str(e))

        results[table] = {
            "inserted": inserted,
            "skipped": skipped,
            "total": len(rows),
        }
        if errors:
            results[table]["errors_sample"] = errors

    conn.commit()
    conn.close()

    return {
        "status": "seeded",
        "results": results,
        "message": "Database seeded. Duplicate rows skipped.",
    }


@app.get("/admin/db-counts", tags=["Admin"])
def db_counts():
    """Check row counts in key tables."""
    import core.db_compat as sqlite3
    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()
    tables = ['countries', 'universities', 'cities', 'campuses', 'departments',
              'courses', 'intake_seats', 'country_documents', 'opportunities']
    counts = {}
    for t in tables:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {t}")
            counts[t] = cur.fetchone()[0]
        except Exception as e:
            counts[t] = f"error: {e}"
    conn.close()
    return counts

# ========== STUDENT LIFE AI SUGGEST ==========
class StudentLifeSuggestRequest(BaseModel):
    category: str
    country: str = ""
    user_id: str = ""

@app.post("/student-life/ai-suggest", tags=["Student Life"])
async def student_life_ai_suggest(body: StudentLifeSuggestRequest):
    """AI suggests practical items for a student based on category + country."""
    if not groq_client:
        raise HTTPException(status_code=500, detail="AI not configured")

    category_map = {
        "sim": "SIM card / Mobile Internet",
        "bank": "Bank Account opening",
        "health": "Health Insurance",
        "accommodation": "Accommodation / Housing",
        "transport": "Transport / Metro / Bus",
        "food": "Food / Grocery stores",
        "books": "Books / Study materials",
        "emergency": "Emergency contacts & services",
    }

    category_label = category_map.get(body.category.lower(), body.category)
    country = body.country or "Germany"

    prompt = f"""You are a helpful study-abroad advisor.

A student needs help with: **{category_label}** in **{country}**.

Provide a practical list of 6-8 specific items/suggestions. For each, give:
- name (short title)
- description (1-2 sentences, practical for a student)
- cost (approximate, in local currency if possible)
- link (optional, official site)

Return ONLY JSON in this format:
{{
  "items": [
    {{
      "name": "...",
      "description": "...",
      "cost": "...",
      "link": "..."
    }}
  ],
  "ai_note": "Short helpful note"
}}

Rules:
- Be specific to {country}
- Include real brands/services available there
- Use student-friendly (cheap) options
- If {country} unknown, give general advice

Only return JSON, no markdown."""

    try:
        response = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=1500,
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        import json as json_lib_sl
        data = json_lib_sl.loads(content)
        return {
            "category": body.category,
            "country": country,
            "items": data.get("items", []),
            "ai_note": data.get("ai_note", ""),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error: {str(e)}")

# ========== HOUSING AI SUGGEST (Internal First, External Fallback) ==========
class HousingSuggestRequest(BaseModel):
    city: str = ""
    country: str = ""
    housing_type: str = "student_hostel"
    max_rent: float = 0

@app.post("/housing/ai-suggest", tags=["Housing"])
async def housing_ai_suggest(body: HousingSuggestRequest):
    """
    Housing suggestions:
    1. First check internal DB (vendor/agent listings)
    2. If none found, generate AI external suggestions
    """
    import core.db_compat as sqlite3

    # ---------- STEP 1: Check Internal DB ----------
    conn = sqlite3.connect('ai_glue.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    query = "SELECT * FROM housing WHERE status != 'CLOSED'"
    params = []

    if body.city:
        query += " AND LOWER(location) LIKE ?"
        params.append(f"%{body.city.lower()}%")
    if body.housing_type:
        query += " AND LOWER(housing_type) LIKE ?"
        params.append(f"%{body.housing_type.replace('_',' ').lower()}%")
    if body.max_rent and body.max_rent > 0:
        query += " AND monthly_rent <= ?"
        params.append(body.max_rent)

    query += " ORDER BY created_at DESC LIMIT 20"

    try:
        cur.execute(query, params)
        internal = [dict(r) for r in cur.fetchall()]
    except Exception:
        internal = []
    finally:
        conn.close()

    if internal:
        return {
            "source": "internal",
            "count": len(internal),
            "items": internal,
            "message": f"{len(internal)} verified listings from our partners",
        }

    # ---------- STEP 2: AI External Fallback ----------
    if not groq_client:
        return {
            "source": "external",
            "count": 0,
            "items": [],
            "message": "No internal listings. AI not configured for suggestions.",
        }

    type_labels = {
        "student_hostel": "student hostel / university dormitory",
        "shared_flat": "shared flat (WG / roommate)",
        "private_apartment": "private apartment",
        "pg": "paying guest (PG) accommodation",
        "homestay": "homestay with a local family",
        "temporary": "short-term / temporary stay (first weeks)",
    }
    type_label = type_labels.get(body.housing_type, "accommodation")
    location = body.city or body.country or "Germany"

    rent_hint = f"Budget: under {body.max_rent} per month" if body.max_rent else ""

    prompt = f"""You are a study-abroad housing advisor.

A student needs: **{type_label}** in **{location}**.
{rent_hint}

Provide 6 practical accommodation options/services. For each:
- name (real platform, hostel, or service)
- description (1-2 sentences, student-focused)
- rent_range (approximate monthly in local currency)
- link (official website)
- source_type: "platform" (WG-Gesucht, Uniplaces) or "service" (university housing office) or "tip" (practical advice)

Return ONLY JSON:
{{
  "items": [
    {{
      "name": "...",
      "description": "...",
      "rent_range": "...",
      "link": "...",
      "source_type": "..."
    }}
  ],
  "ai_note": "Short practical advice"
}}

Rules:
- Real platforms/services used in {location}
- Focus on student budgets
- Include at least 1 university housing office option
- Only JSON, no markdown."""

    try:
        response = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=1800,
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        import json as json_lib_hs
        data = json_lib_hs.loads(content)
        return {
            "source": "external",
            "count": len(data.get("items", [])),
            "items": data.get("items", []),
            "ai_note": data.get("ai_note", ""),
            "message": "No internal listings yet â€” here are AI suggestions",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error: {str(e)}")

# ========== FIX AND SEED (One Shot) ==========
@app.post("/admin/fix-and-seed", tags=["Admin"])
def fix_and_seed():
    """
    One endpoint to:
    1. Create missing tables/columns
    2. Seed all data from seed_data.json
    """
    import core.db_compat as sqlite3
    import json as json_lib_fs
    import os as os_fs

    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()
    fixes = []

    # ---------- STEP 1: FIX SCHEMA ----------
    # country_documents
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS country_documents (
                id TEXT PRIMARY KEY,
                country TEXT,
                document_name TEXT,
                is_mandatory INTEGER DEFAULT 0,
                description TEXT,
                estimated_days INTEGER,
                official_link TEXT
            )
        """)
        fixes.append("âœ“ country_documents table")
    except Exception as e:
        fixes.append(f"âœ— country_documents: {e}")

    # opportunities columns
    try:
        cur.execute("PRAGMA table_info(opportunities)")
        cols = [r[1] for r in cur.fetchall()]
        for col in ['country', 'company', 'salary']:
            if col not in cols:
                cur.execute(f"ALTER TABLE opportunities ADD COLUMN {col} TEXT")
                fixes.append(f"âœ“ opportunities.{col} added")
            else:
                fixes.append(f"â—‹ opportunities.{col} exists")
    except Exception as e:
        fixes.append(f"âœ— opportunities columns: {e}")

    conn.commit()

    # ---------- STEP 2: SEED DATA ----------
    seed_path = os_fs.path.join(os_fs.path.dirname(__file__), "seed_data.json")
    if not os_fs.path.exists(seed_path):
        conn.close()
        return {"status": "partial", "fixes": fixes, "seed": "seed_data.json not found"}

    with open(seed_path, "r", encoding="utf-8") as f:
        data = json_lib_fs.load(f)

    table_order = [
        'countries', 'universities', 'cities', 'campuses', 'departments',
        'courses', 'intake_seats', 'country_documents', 'opportunities'
    ]

    seed_results = {}
    for table in table_order:
        rows = data.get(table, [])
        if not rows:
            seed_results[table] = {"inserted": 0, "skipped": 0, "total": 0}
            continue

        inserted = 0
        skipped = 0
        for row in rows:
            try:
                cols = list(row.keys())
                placeholders = ",".join(["?"] * len(cols))
                col_names = ",".join(cols)
                values = [row[c] for c in cols]
                cur.execute(
                    f"INSERT OR IGNORE INTO {table} ({col_names}) VALUES ({placeholders})",
                    values
                )
                if cur.rowcount > 0:
                    inserted += 1
                else:
                    skipped += 1
            except Exception:
                skipped += 1

        seed_results[table] = {"inserted": inserted, "skipped": skipped, "total": len(rows)}

    conn.commit()
    conn.close()

    return {
        "status": "complete",
        "schema_fixes": fixes,
        "seed_results": seed_results,
        "message": "Schema fixed and data seeded"
    }

# ========== FORCE RESEED OPPORTUNITIES ==========
@app.post("/admin/force-reseed-opportunities", tags=["Admin"])
def force_reseed_opportunities():
    """Force replace opportunities rows from seed_data.json."""
    import core.db_compat as sqlite3
    import json as json_lib_op
    import os as os_op

    seed_path = os_op.path.join(os_op.path.dirname(__file__), "seed_data.json")
    if not os_op.path.exists(seed_path):
        raise HTTPException(status_code=404, detail="seed_data.json not found")

    with open(seed_path, "r", encoding="utf-8") as f:
        data = json_lib_op.load(f)

    opps = data.get("opportunities", [])
    if not opps:
        return {"status": "no_data", "message": "No opportunities in seed_data.json"}

    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()

    # Delete existing then re-insert fresh
    try:
        cur.execute("DELETE FROM opportunities")
        deleted = cur.rowcount
    except Exception as e:
        deleted = 0

    inserted = 0
    errors = []
    for row in opps:
        try:
            cols = list(row.keys())
            placeholders = ",".join(["?"] * len(cols))
            col_names = ",".join(cols)
            values = [row[c] for c in cols]
            cur.execute(
                f"INSERT INTO opportunities ({col_names}) VALUES ({placeholders})",
                values
            )
            inserted += 1
        except Exception as e:
            errors.append(str(e))

    conn.commit()
    conn.close()

    return {
        "status": "done",
        "deleted": deleted,
        "inserted": inserted,
        "total": len(opps),
        "errors_sample": errors[:3] if errors else [],
    }

# ========== AUTO-FIX COLUMNS (Smart) ==========
@app.post("/admin/auto-fix-columns", tags=["Admin"])
def auto_fix_columns():
    """
    Auto-detect missing columns from seed_data.json and add them.
    Then re-seed all data.
    """
    import core.db_compat as sqlite3
    import json as json_lib_ac
    import os as os_ac

    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()

    seed_path = os_ac.path.join(os_ac.path.dirname(__file__), "seed_data.json")
    if not os_ac.path.exists(seed_path):
        conn.close()
        return {"status": "error", "message": "seed_data.json not found"}

    with open(seed_path, "r", encoding="utf-8") as f:
        data = json_lib_ac.load(f)

    added = []
    errors = []

    # For each table, check all columns from JSON
    for table, rows in data.items():
        if not rows:
            continue

        # Get all unique columns from all rows
        all_cols = set()
        for row in rows:
            all_cols.update(row.keys())

        # Get existing columns in DB
        try:
            cur.execute(f"PRAGMA table_info({table})")
            existing = set(r[1] for r in cur.fetchall())
        except Exception as e:
            errors.append(f"{table}: {e}")
            continue

        # Add missing columns
        for col in all_cols:
            if col not in existing:
                try:
                    cur.execute(f'ALTER TABLE {table} ADD COLUMN "{col}" TEXT')
                    added.append(f"{table}.{col}")
                except Exception as e:
                    errors.append(f"{table}.{col}: {e}")

    conn.commit()

    # Now re-seed (DELETE + INSERT)
    for table in ['country_documents', 'intake_seats', 'courses', 'departments',
                  'campuses', 'cities', 'universities', 'countries', 'opportunities']:
        try:
            cur.execute(f"DELETE FROM {table}")
        except Exception:
            pass

    seeded = {}
    for table in ['countries', 'universities', 'cities', 'campuses', 'departments',
                  'courses', 'intake_seats', 'country_documents', 'opportunities']:
        rows = data.get(table, [])
        inserted = 0
        for row in rows:
            try:
                cols = list(row.keys())
                placeholders = ",".join(["?"] * len(cols))
                col_names = ",".join(f'"{c}"' for c in cols)
                values = [row[c] for c in cols]
                cur.execute(
                    f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})",
                    values
                )
                inserted += 1
            except Exception as e:
                if len(errors) < 5:
                    errors.append(f"{table}: {e}")
        seeded[table] = {"inserted": inserted, "total": len(rows)}

    conn.commit()
    conn.close()

    return {
        "status": "complete",
        "columns_added": added,
        "seeded": seeded,
        "errors": errors[:10] if errors else [],
        "message": "Auto-fix and re-seed complete"
    }

# ========== INIT ALL TABLES (One Shot) ==========
@app.post("/admin/init-all", tags=["Admin"])
def init_all():
    """Create all missing tables + seed everything from seed_data.json."""
    import core.db_compat as sqlite3
    import json as json_lib_init
    import os as os_init

    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()
    log = []

    # ---------- CREATE TABLES ----------
    tables_sql = {
        'country_documents': """
            CREATE TABLE IF NOT EXISTS country_documents (
                id TEXT PRIMARY KEY,
                country TEXT,
                document_name TEXT,
                is_mandatory INTEGER DEFAULT 0,
                description TEXT,
                estimated_days INTEGER,
                official_link TEXT
            )
        """,
        'countries': """
            CREATE TABLE IF NOT EXISTS countries (
                id TEXT PRIMARY KEY,
                name TEXT,
                iso_code TEXT,
                visa_difficulty REAL DEFAULT 0,
                cost_of_living_index REAL DEFAULT 0
            )
        """,
        'universities': """
            CREATE TABLE IF NOT EXISTS universities (
                id TEXT PRIMARY KEY,
                country_id TEXT,
                name TEXT,
                website TEXT,
                ranking_global INTEGER,
                ranking_national INTEGER,
                accreditation TEXT,
                domain TEXT
            )
        """,
        'cities': """
            CREATE TABLE IF NOT EXISTS cities (
                id TEXT PRIMARY KEY,
                country_id TEXT,
                name TEXT,
                state TEXT
            )
        """,
        'campuses': """
            CREATE TABLE IF NOT EXISTS campuses (
                id TEXT PRIMARY KEY,
                university_id TEXT,
                city_id TEXT,
                name TEXT,
                address TEXT,
                established_year INTEGER
            )
        """,
        'departments': """
            CREATE TABLE IF NOT EXISTS departments (
                id TEXT PRIMARY KEY,
                campus_id TEXT,
                name TEXT
            )
        """,
        'courses': """
            CREATE TABLE IF NOT EXISTS courses (
                id TEXT PRIMARY KEY,
                department_id TEXT,
                name TEXT,
                level TEXT,
                duration_months INTEGER,
                tuition_fee REAL,
                currency TEXT DEFAULT 'USD',
                admission_requirements TEXT,
                course_url TEXT
            )
        """,
        'intake_seats': """
            CREATE TABLE IF NOT EXISTS intake_seats (
                id TEXT PRIMARY KEY,
                course_id TEXT,
                academic_year TEXT,
                total_seats INTEGER,
                filled_seats INTEGER DEFAULT 0,
                waiting_seats INTEGER DEFAULT 0
            )
        """,
        'opportunities': """
            CREATE TABLE IF NOT EXISTS opportunities (
                id TEXT PRIMARY KEY,
                organization_id TEXT,
                type TEXT,
                title TEXT,
                description TEXT,
                requirements TEXT,
                fees TEXT,
                capacity INTEGER,
                deadline TEXT,
                status TEXT DEFAULT 'open',
                country TEXT,
                company TEXT,
                salary TEXT,
                location TEXT,
                created_at TEXT
            )
        """,
    }

    for name, sql in tables_sql.items():
        try:
            cur.execute(sql)
            log.append(f"âœ“ {name} table ready")
        except Exception as e:
            log.append(f"âœ— {name}: {e}")

    conn.commit()

    # ---------- LOAD SEED DATA ----------
    seed_path = os_init.path.join(os_init.path.dirname(__file__), "seed_data.json")
    if not os_init.path.exists(seed_path):
        conn.close()
        return {"status": "partial", "log": log, "error": "seed_data.json not found"}

    with open(seed_path, "r", encoding="utf-8") as f:
        data = json_lib_init.load(f)

    # DELETE existing data (fresh seed)
    for table in ['country_documents', 'intake_seats', 'courses', 'departments',
                  'campuses', 'cities', 'universities', 'countries', 'opportunities']:
        try:
            cur.execute(f"DELETE FROM {table}")
        except Exception:
            pass

    # INSERT data
    seeded = {}
    table_order = ['countries', 'universities', 'cities', 'campuses', 'departments',
                   'courses', 'intake_seats', 'country_documents', 'opportunities']

    for table in table_order:
        rows = data.get(table, [])
        inserted = 0
        errors = []
        for row in rows:
            try:
                cols = list(row.keys())
                placeholders = ",".join(["?"] * len(cols))
                col_names = ",".join(f'"{c}"' for c in cols)
                values = [row[c] for c in cols]
                cur.execute(
                    f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})",
                    values
                )
                inserted += 1
            except Exception as e:
                if len(errors) < 3:
                    errors.append(str(e))
        seeded[table] = {"inserted": inserted, "total": len(rows)}
        if errors:
            seeded[table]["errors"] = errors

    conn.commit()
    conn.close()

    return {
        "status": "complete",
        "log": log,
        "seeded": seeded,
        "message": "All tables created and data seeded"
    }

# ========== FIX OPPORTUNITIES ==========
@app.post("/admin/fix-opportunities", tags=["Admin"])
def fix_opportunities():
    """Force add missing columns to opportunities table and reseed."""
    import core.db_compat as sqlite3
    import json as json_lib_opp
    import os as os_opp

    conn = sqlite3.connect('ai_glue.db')
    cur = conn.cursor()
    log = []

    # 1. Add missing columns
    cur.execute("PRAGMA table_info(opportunities)")
    existing = set(r[1] for r in cur.fetchall())
    log.append(f"Existing columns: {sorted(existing)}")

    needed = ['country', 'company', 'salary', 'location', 'description',
              'requirements', 'fees', 'capacity', 'deadline', 'status',
              'organization_id', 'type', 'title', 'created_at']

    for col in needed:
        if col not in existing:
            try:
                cur.execute(f'ALTER TABLE opportunities ADD COLUMN "{col}" TEXT')
                log.append(f"âœ“ Added: {col}")
            except Exception as e:
                log.append(f"âœ— {col}: {e}")

    conn.commit()

    # 2. Reseed opportunities
    seed_path = os_opp.path.join(os_opp.path.dirname(__file__), "seed_data.json")
    if not os_opp.path.exists(seed_path):
        conn.close()
        return {"status": "partial", "log": log, "error": "seed_data.json missing"}

    with open(seed_path, "r", encoding="utf-8") as f:
        data = json_lib_opp.load(f)

    rows = data.get('opportunities', [])
    cur.execute("DELETE FROM opportunities")

    inserted = 0
    errors = []
    for row in rows:
        try:
            cols = list(row.keys())
            placeholders = ",".join(["?"] * len(cols))
            col_names = ",".join(f'"{c}"' for c in cols)
            values = [row[c] for c in cols]
            cur.execute(
                f"INSERT INTO opportunities ({col_names}) VALUES ({placeholders})",
                values
            )
            inserted += 1
        except Exception as e:
            if len(errors) < 5:
                errors.append(str(e))

    conn.commit()
    conn.close()

    return {
        "status": "complete",
        "log": log,
        "inserted": inserted,
        "total": len(rows),
        "errors": errors
    }
