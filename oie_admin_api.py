"""OIE Admin API — Jobs + Studies separated"""
import sqlite3
import sys
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "OIE"))

router = APIRouter(prefix="/admin/oie", tags=["OIE Admin"])
DB = "ai_glue.db"


# ============================================================
# JOBS — Vertical = JOB
# ============================================================
@router.get("/jobs")
def list_jobs(status: str = "", limit: int = 100):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    q = """
        SELECT jbd.id, jbd.company_name, jbd.job_title, jbd.country,
               jbd.category, jbd.salary_currency, jbd.salary_min_usd,
               jbd.salary_max_usd, jbd.visa_free, jbd.ticket_free,
               jbd.accommodation, jbd.overtime_available, jbd.hours_per_day,
               jbd.off_days, hrc.verification_status, hrc.hr_email, hrc.hr_phone,
               hrc.contact_attempts, jbd.verified
        FROM job_benefits_deep jbd
        LEFT JOIN hr_contacts hrc ON LOWER(hrc.company_name) = LOWER(jbd.company_name)
    """
    params = []
    if status:
        q += " WHERE hrc.verification_status = ?"
        params.append(status)
    q += " ORDER BY jbd.company_name LIMIT ?"
    params.append(limit)
    cur.execute(q, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"count": len(rows), "jobs": rows}


@router.get("/job-registry")
def list_job_registry(verified_only: bool = False, limit: int = 100):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    q = "SELECT * FROM registry_entities WHERE vertical = 'JOB'"
    params = []
    if verified_only:
        q += " AND is_verified = 1"
    q += " ORDER BY trust_score DESC LIMIT ?"
    params.append(limit)
    cur.execute(q, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"count": len(rows), "entities": rows}


@router.get("/job-requests")
def list_job_requests(status: str = "", limit: int = 100):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    q = "SELECT * FROM oie_requests WHERE vertical = 'JOB'"
    params = []
    if status:
        q += " AND status = ?"
        params.append(status)
    q += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    cur.execute(q, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"count": len(rows), "requests": rows}


@router.get("/job-contacts")
def job_contact_log(company: str = "", limit: int = 100):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    q = "SELECT * FROM hr_contact_log WHERE vertical = 'JOB'"
    params = []
    if company:
        q += " AND LOWER(company_name) LIKE ?"
        params.append(f"%{company.lower()}%")
    q += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    cur.execute(q, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"count": len(rows), "contacts": rows}


@router.get("/job-detail/{job_id}")
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
# STUDIES — Vertical = STUDY
# ============================================================
@router.get("/studies")
def list_studies(
    country: str = "",
    free_only: bool = False,
    pr_only: bool = False,
    scholarship_only: bool = False,
    search: str = "",
    limit: int = 100,
):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    q = """
        SELECT id, university_name, country, city, tuition_fee,
               currency, language, free_education, scholarship_available,
               scholarship_amount_usd, hostel_available,
               hostel_cost_monthly_usd, post_study_work_years,
               pr_possible, demand_score, application_url,
               direct_apply
        FROM study_opportunities
        WHERE status = 'DISCOVERED'
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


@router.get("/study-registry")
def list_study_registry(verified_only: bool = False, limit: int = 100):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    q = "SELECT * FROM registry_entities WHERE vertical = 'STUDY'"
    params = []
    if verified_only:
        q += " AND is_verified = 1"
    q += " ORDER BY trust_score DESC LIMIT ?"
    params.append(limit)
    cur.execute(q, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"count": len(rows), "entities": rows}


@router.get("/study-requests")
def list_study_requests(status: str = "", limit: int = 100):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    q = "SELECT * FROM oie_requests WHERE vertical = 'STUDY'"
    params = []
    if status:
        q += " AND status = ?"
        params.append(status)
    q += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    cur.execute(q, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"count": len(rows), "requests": rows}


@router.get("/study-contacts")
def study_contact_log(limit: int = 100):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM study_contacts ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"count": len(rows), "contacts": rows}


# ============================================================
# STATS — Separate for Jobs and Studies
# ============================================================
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
        FROM study_agents
        ORDER BY trust_score DESC LIMIT ?
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
        FROM study_contacts
        ORDER BY country, university_name LIMIT ?
    """, (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"count": len(rows), "contacts": rows}


@router.get("/stats/jobs")
def stats_jobs():
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
        cur.execute("SELECT COUNT(*) FROM registry_entities WHERE vertical='JOB'")
        out["registry_total"] = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM oie_requests WHERE vertical='JOB' AND status='PENDING'")
        out["requests_pending"] = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM hr_contact_log WHERE vertical='JOB'")
        out["contact_attempts"] = cur.fetchone()[0]
    except Exception as e:
        out["error"] = str(e)
    conn.close()
    return out


@router.get("/stats/studies")
def stats_studies():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    out = {}
    try:
        cur.execute("SELECT COUNT(*) FROM study_opportunities WHERE status='DISCOVERED'")
        out["total_universities"] = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM study_opportunities WHERE free_education=1")
        out["free_tuition"] = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM study_opportunities WHERE pr_possible=1")
        out["pr_pathway"] = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM study_opportunities WHERE scholarship_available=1")
        out["scholarships"] = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM registry_entities WHERE vertical='STUDY'")
        out["study_agents"] = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM study_contacts")
        out["contact_attempts"] = cur.fetchone()[0]
    except Exception as e:
        out["error"] = str(e)
    conn.close()
    return out


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