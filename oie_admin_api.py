"""OIE Admin API — Endpoints for admin panel"""
import sqlite3
import sys
import os
import json
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from fastapi.responses import RedirectResponse
from fastapi import Request

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "OIE"))

router = APIRouter(prefix="/admin/oie", tags=["OIE Admin"])
import os as _os
DB = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "ai_glue.db")
print(f"[OIE API] Using DB: {DB}")


# ============================================================
# JOBS
# ============================================================
@router.get("/jobs/{job_id}")
def track_job_click(job_id: str, request: Request):
    """Track click → redirect to login or job detail"""
    # Check if user logged in (check cookie/session)
    user_token = request.cookies.get("access_token")
    
    # Log the click (analytics)
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS job_clicks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT,
                user_agent TEXT,
                clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("INSERT INTO job_clicks (job_id, user_agent) VALUES (?, ?)",
                    (job_id, request.headers.get("user-agent", "")))
        conn.commit()
    except: pass
    conn.close()
    
    # Redirect logic
    if user_token:
        # Logged in → go to job detail page
        return RedirectResponse(url=f"/admin/oie/job-detail/{job_id}")
    else:
        # Not logged in → login page with redirect back
        return RedirectResponse(url=f"/login?redirect=/jobs/{job_id}")

# ============================================================
# REGISTRY (Job Agents)
# ============================================================
@router.get("/registry")
def list_registry(entity_type: str = "", verified_only: bool = False, limit: int = 100):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    q = "SELECT * FROM registry_entities WHERE 1=1"
    params = []
    if entity_type:
        q += " AND entity_type = ?"
        params.append(entity_type)
    if verified_only:
        q += " AND is_verified = 1"
    q += " ORDER BY trust_score DESC LIMIT ?"
    params.append(limit)
    cur.execute(q, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"count": len(rows), "entities": rows}


# ============================================================
# REQUESTS (supports vertical filter)
# ============================================================
@router.get("/requests")
def list_requests(status: str = "", vertical: str = "", limit: int = 100):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    q = "SELECT * FROM oie_requests WHERE 1=1"
    params = []
    if status:
        q += " AND status = ?"
        params.append(status)
    if vertical:
        q += " AND vertical = ?"
        params.append(vertical)
    q += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    cur.execute(q, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"count": len(rows), "requests": rows}


class StudyRequestBody(BaseModel):
    to_agent_name: str = ""
    to_agent_id: str = ""
    subject: str
    message: str
    context: dict = {}


@router.post("/study-requests")
def create_study_request(body: StudyRequestBody):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    rid = str(uuid.uuid4())
    cur.execute("""
        INSERT INTO oie_requests
        (id, from_name, from_role, to_name, to_role, request_type,
         subject, message, context_json, priority, status, vertical,
         created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        rid, "AI Glue Admin", "ADMIN", body.to_agent_name, "STUDY_AGENT",
        "STUDY_ADMISSION", body.subject, body.message,
        json.dumps(body.context), "NORMAL", "PENDING", "STUDY", now, now
    ))
    conn.commit()
    conn.close()
    return {"id": rid, "status": "SENT"}


# ============================================================
# CONTACT LOG (HR)
# ============================================================
@router.get("/contact-log")
def contact_log(company: str = "", limit: int = 100):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    q = "SELECT * FROM hr_contact_log WHERE 1=1"
    params = []
    if company:
        q += " AND LOWER(company_name) LIKE ?"
        params.append(f"%{company.lower()}%")
    q += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    cur.execute(q, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"count": len(rows), "log": rows}


# ============================================================
# CONFLICTS (Cross-source)
# ============================================================
@router.get("/conflicts")
def list_conflicts(resolved: bool = False, limit: int = 100):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    q = "SELECT * FROM verification_conflicts WHERE 1=1"
    params = []
    if not resolved:
        q += " AND (resolved = 0 OR resolved IS NULL)"
    q += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    cur.execute(q, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"count": len(rows), "conflicts": rows}


# ============================================================
# JOB DETAIL
# ============================================================
@router.get("/job-full-context/{job_id}")
def job_detail(job_id: str):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM job_full_context WHERE benefit_id = ?", (job_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        raise HTTPException(404, "Job not found")
    result = dict(row)
    cur.execute("SELECT * FROM company_health WHERE company_name = ?", (result["company_name"],))
    h = cur.fetchone()
    if h: result["company_health"] = dict(h)
    cur.execute("SELECT * FROM visa_stats WHERE company_name = ?", (result["company_name"],))
    v = cur.fetchone()
    if v: result["visa_stats"] = dict(v)
    cur.execute("SELECT * FROM employee_reviews WHERE company_name = ?", (result["company_name"],))
    r = cur.fetchone()
    if r: result["reviews"] = dict(r)
    cur.execute("SELECT * FROM placements_history WHERE company_name = ? ORDER BY year DESC LIMIT 2", (result["company_name"],))
    result["placements"] = [dict(x) for x in cur.fetchall()]
    conn.close()
    return result


# ============================================================
# VERIFY / REJECT
# ============================================================
class VerifyBody(BaseModel):
    admin_id: str = "admin"
    notes: str = ""


@router.post("/verify/{company_name}")
def verify(company_name: str, body: VerifyBody):
    try:
        from oie_admin_actions import admin_verify
        return admin_verify(company_name, body.admin_id, body.notes)
    except Exception as e:
        raise HTTPException(500, f"Verify failed: {str(e)}")


@router.post("/reject/{company_name}")
def reject(company_name: str, body: VerifyBody):
    try:
        from oie_admin_actions import admin_reject
        return admin_reject(company_name, body.admin_id, body.notes)
    except Exception as e:
        raise HTTPException(500, f"Reject failed: {str(e)}")


# ============================================================
# STATS
# ============================================================
@router.get("/stats")
def stats():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    out = {}
    try:
        cur.execute("SELECT COUNT(*) FROM job_benefits_deep")
        out["total_jobs"] = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM hr_contacts WHERE verification_status='VERIFIED'")
        out["verified_jobs"] = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM hr_contacts WHERE verification_status='PENDING'")
        out["pending_jobs"] = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM registry_entities")
        out["registry_total"] = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM registry_entities WHERE is_verified=1")
        out["registry_verified"] = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM oie_requests WHERE status='PENDING'")
        out["requests_pending"] = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM hr_contact_log")
        out["contact_attempts"] = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM verification_conflicts WHERE resolved=0")
        out["conflicts"] = cur.fetchone()[0]
    except Exception as e:
        out["error"] = str(e)
    conn.close()
    return out


# ============================================================
# STUDIES
# ============================================================
@router.get("/studies")
def list_studies(
    country: str = "", free_only: bool = False, pr_only: bool = False,
    scholarship_only: bool = False, search: str = "", limit: int = 100,
):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    q = """
        SELECT id, university_name, country, city, tuition_fee,
               currency, language, free_education, scholarship_available,
               scholarship_amount_usd, hostel_available,
               hostel_cost_monthly_usd, post_study_work_years,
               pr_possible, demand_score, application_url, direct_apply
        FROM study_opportunities WHERE status = 'DISCOVERED'
    """
    params = []
    if country:
        q += " AND LOWER(country) LIKE ?"
        params.append(f"%{country.lower()}%")
    if free_only:
        q += " AND free_education = 1"
    if pr_only:
        q += " AND pr_possible = 1"
    if scholarship_only:
        q += " AND scholarship_available = 1"
    if search:
        q += " AND LOWER(university_name) LIKE ?"
        params.append(f"%{search.lower()}%")
    q += " ORDER BY pr_possible DESC, free_education DESC, university_name LIMIT ?"
    params.append(limit)
    cur.execute(q, params)
    rows = [dict(r) for r in cur.fetchall()]

    cur.execute("""
        SELECT country, COUNT(*) as cnt FROM study_opportunities
        WHERE status='DISCOVERED' GROUP BY country ORDER BY cnt DESC LIMIT 20
    """)
    countries = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"count": len(rows), "studies": rows, "countries": countries}


@router.get("/study-agents")
def list_study_agents(limit: int = 100):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT id, name, legal_name, country, city, website, email, phone,
               license_number, license_authority, established_year,
               services_offered, target_countries, specializations,
               trust_score, verification_status, fake_flags
        FROM study_agents ORDER BY trust_score DESC LIMIT ?
    """, (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"count": len(rows), "agents": rows}


@router.get("/study-contacts")
def list_study_contacts(limit: int = 100):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT id, university_name, country, website, admissions_officer,
               designation, email, phone, application_url, verification_status
        FROM study_contacts ORDER BY country, university_name LIMIT ?
    """, (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"count": len(rows), "contacts": rows}



# ============================================================
# JOB DETAIL — single verified job
# ============================================================
@router.get("/job-detail/{job_id}")
def get_job_detail(job_id: str):
    """Return single job by ID"""
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    row = cur.execute("SELECT * FROM verified_jobs WHERE id = ?", (job_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Job not found")
    return dict(row)



# ═══════════════════════════════════════════
# VERIFIED JOBS — Admin listing with filters
# ═══════════════════════════════════════════
@router.get("/verified-jobs")
def list_verified_jobs(
    country: str = "",
    region: str = "",
    search: str = "",
    page: int = 1,
    limit: int = 50,
):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    where = ["status = 'VERIFIED'"]
    params = []
    
    if country:
        where.append("LOWER(country) = ?")
        params.append(country.lower())
    if region:
        where.append("LOWER(region) = ?")
        params.append(region.lower())
    if search:
        where.append("(LOWER(job_title) LIKE ? OR LOWER(company_name) LIKE ?)")
        s = f"%{search.lower()}%"
        params.extend([s, s])
    
    where_clause = " WHERE " + " AND ".join(where)
    
    # Total count
    total = cur.execute(f"SELECT COUNT(*) FROM verified_jobs{where_clause}", params).fetchone()[0]
    
    # Page data
    offset = (page - 1) * limit
    rows = cur.execute(
        f"""SELECT id, company_name, job_title, country, region,
                   verification_score, job_url, verified_at, no_commission
            FROM verified_jobs{where_clause}
            ORDER BY verified_at DESC
            LIMIT ? OFFSET ?""",
        params + [limit, offset]
    ).fetchall()
    
    conn.close()
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit,
        "jobs": [dict(r) for r in rows],
    }


@router.get("/verified-jobs/stats")
def verified_jobs_stats():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    out = {}
    
    out["total"] = cur.execute("SELECT COUNT(*) FROM verified_jobs WHERE status='VERIFIED'").fetchone()[0]
    
    out["by_country"] = [
        {"country": r[0], "count": r[1]}
        for r in cur.execute("""SELECT country, COUNT(*) FROM verified_jobs
            WHERE status='VERIFIED' GROUP BY country ORDER BY COUNT(*) DESC""").fetchall()
    ]
    
    out["by_region"] = [
        {"region": r[0], "count": r[1]}
        for r in cur.execute("""SELECT region, COUNT(*) FROM verified_jobs
            WHERE status='VERIFIED' GROUP BY region ORDER BY COUNT(*) DESC""").fetchall()
    ]
    
    conn.close()
    return out


@router.delete("/verified-jobs/{job_id}")
def delete_verified_job(job_id: str):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("DELETE FROM verified_jobs WHERE id=?", (job_id,))
    deleted = cur.rowcount
    conn.commit()
    conn.close()
    return {"deleted": deleted, "job_id": job_id}


@router.post("/verified-jobs/{job_id}/unpublish")
def unpublish_verified_job(job_id: str):
    """Hide from user dashboards but keep in DB"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("UPDATE verified_jobs SET status='HIDDEN' WHERE id=?", (job_id,))
    conn.commit()
    conn.close()
    return {"status": "HIDDEN", "job_id": job_id}


@router.post("/verified-jobs/{job_id}/publish")
def publish_verified_job(job_id: str):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("UPDATE verified_jobs SET status='VERIFIED' WHERE id=?", (job_id,))
    conn.commit()
    conn.close()
    return {"status": "VERIFIED", "job_id": job_id}



# ═══════════════════════════════════════════
# MY MATCHES — logged-in job seeker के लिए
# ═══════════════════════════════════════════
@router.get("/my-matches")
def my_matches(user_id: str, limit: int = 50, min_score: int = 30, country: str = ""):
    """
    Candidate के profile से match होने वाली jobs
    Sorted by match score (descending)
    """
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # Get candidate profile
    profile = cur.execute("SELECT * FROM student_profiles_oie WHERE user_id=?", (user_id,)).fetchone()
    if not profile:
        conn.close()
        return {"error": "No profile found", "jobs": [], "total": 0}
    
    profile = dict(profile)
    target_countries = (profile.get("target_countries") or "").lower()
    # English → German keyword translation
    FIELD_TRANSLATIONS = {
        "driver": ["fahrer", "kraftfahrer", "berufskraftfahrer", "chauffeur", "lieferfahrer"],
        "cook": ["koch", "köchin", "cook"],
        "chef": ["koch", "chef de partie"],
        "cleaner": ["reinigung", "reinigungskraft", "putz"],
        "nurse": ["krankenpfleger", "altenpfleger", "krankenschwester", "pfleger"],
        "security": ["sicherheit", "sicherheitsmitarbeiter", "wachmann"],
        "warehouse": ["lager", "lagerist", "kommissionierer", "lagerhelfer"],
        "construction": ["bauhelfer", "maurer", "zimmermann", "bau"],
        "welder": ["schweißer", "schweisser"],
        "electrician": ["elektriker"],
        "mechanic": ["mechaniker"],
        "carpenter": ["tischler", "schreiner", "zimmermann"],
        "waiter": ["kellner", "servicekraft"],
        "sales": ["verkäufer", "verkaufer"],
    }
    field = (profile.get("field_of_study") or "").lower()
    budget = profile.get("budget_usd") or 0
    exp = profile.get("work_experience_years") or 0
    
    # Get verified jobs (filtered)
    q = """SELECT id, company_name, job_title, country, region,
                  free_visa, free_ticket, accommodation, no_commission,
                  verification_score, job_url, verified_at,
                  MIN(id) as id
           FROM verified_jobs WHERE status='VERIFIED'"""
    params = []
    if country:
        q += " AND LOWER(country)=?"
        params.append(country.lower())
    q += " GROUP BY company_name, job_title, country"
    q += " LIMIT 5000"
    
    jobs = [dict(r) for r in cur.execute(q, params).fetchall()]
    
    # Score each job
    scored = []
    for job in jobs:
        score = 0
        jc = (job.get("country") or "").lower()
        jt = (job.get("job_title") or "").lower()
        
        # Country match (40%)
        if jc and target_countries and jc in target_countries:
            score += 40
        elif target_countries:
            score += 5
        
        # Field match (30%)
                # Field match (30%) — with translations
        if field and jt:
            field_words = field.lower().split()
            job_words = jt.lower()
            matched = False
            for w in field_words:
                if len(w) < 3:
                    continue
                if w in job_words:
                    matched = True
                    break
                # Check translations
                for eng, germans in FIELD_TRANSLATIONS.items():
                    if eng in w or w in eng:
                        if any(g in job_words for g in germans):
                            matched = True
                            break
                if matched:
                    break
            if matched:
                score += 30
        
        # Salary/budget (20%)
        smin = job.get("salary_min") or 0
        if smin and budget and smin >= budget * 0.8:
            score += 20
        elif smin:
            score += 10
        else:
            score += 5
        
        # Experience (10%)
        score += 10 if exp <= 2 else 5
        
        score = min(score, 100)
        if score >= min_score:
            job["match_score"] = score
            scored.append(job)
    
    # Sort by score, then by verified_at
    scored.sort(key=lambda x: (-x["match_score"], x.get("verified_at", "")))
    
    conn.close()
    return {
        "total": len(scored),
        "jobs": scored[:limit],
        "profile": {
            "target_countries": profile.get("target_countries"),
            "field_of_study": profile.get("field_of_study"),
            "budget_usd": profile.get("budget_usd"),
        }
    }