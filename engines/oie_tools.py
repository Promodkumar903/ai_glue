"""
OIE Tools — 8 tools for AI Glue Copilot
All params safe-handled for None
"""
import sqlite3

DB = "ai_glue.db"


def _conn():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================
# TOOL 1: Search Jobs
# ============================================================
def search_jobs(query=None, country=None, limit=10):
    query = query or ""
    country = country or ""
    limit = limit or 10
    conn = _conn(); cur = conn.cursor()
    clauses = ["status='DISCOVERED'"]
    params = []
    if country:
        clauses.append("LOWER(country) LIKE ?")
        params.append(f"%{country.lower()}%")
    if query:
        clauses.append("(LOWER(title) LIKE ? OR LOWER(company) LIKE ?)")
        params.extend([f"%{query.lower()}%", f"%{query.lower()}%"])
    where = " AND ".join(clauses)
    params.append(limit)
    cur.execute(f"""
        SELECT title, country, company, work_scope, contract_type
        FROM opportunities WHERE {where}
        ORDER BY created_at DESC LIMIT ?
    """, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"count": len(rows), "jobs": rows}


# ============================================================
# TOOL 2: Search Universities
# ============================================================
def search_universities(country=None, free_only=False, pr_only=False, query=None, limit=10):
    country = country or ""
    query = query or ""
    limit = limit or 10
    conn = _conn(); cur = conn.cursor()
    clauses = ["status='DISCOVERED'"]
    params = []
    if country:
        clauses.append("LOWER(country) LIKE ?")
        params.append(f"%{country.lower()}%")
    if free_only:
        clauses.append("free_education=1")
    if pr_only:
        clauses.append("pr_possible=1")
    if query:
        clauses.append("LOWER(university_name) LIKE ?")
        params.append(f"%{query.lower()}%")
    where = " AND ".join(clauses)
    params.append(limit)
    cur.execute(f"""
        SELECT university_name, country, tuition_fee,
               hostel_cost_monthly_usd, free_education, pr_possible,
               scholarship_amount_usd, post_study_work_years
        FROM study_opportunities WHERE {where} LIMIT ?
    """, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"count": len(rows), "universities": rows}


# ============================================================
# TOOL 3: Search Scholarships
# ============================================================
def search_scholarships(country=None, subject=None, limit=10):
    country = country or ""
    subject = subject or ""
    limit = limit or 10
    conn = _conn(); cur = conn.cursor()
    clauses = ["1=1"]
    params = []
    if country:
        clauses.append("LOWER(country) LIKE ?")
        params.append(f"%{country.lower()}%")
    if subject:
        clauses.append("LOWER(subjects) LIKE ?")
        params.append(f"%{subject.lower()}%")
    where = " AND ".join(clauses)
    params.append(limit)
    cur.execute(f"""
        SELECT name, provider, country, amount_usd, coverage,
               subjects, deadline
        FROM scholarships WHERE {where}
        ORDER BY amount_usd DESC LIMIT ?
    """, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"count": len(rows), "scholarships": rows}


# ============================================================
# TOOL 4: Salary Band Lookup
# ============================================================
def salary_band_lookup(company=None, role=None, limit=10):
    company = company or ""
    role = role or ""
    limit = limit or 10
    conn = _conn(); cur = conn.cursor()
    clauses = ["1=1"]
    params = []
    if company:
        clauses.append("LOWER(ci.company_name) LIKE ?")
        params.append(f"%{company.lower()}%")
    if role:
        clauses.append("LOWER(csb.role_title) LIKE ?")
        params.append(f"%{role.lower()}%")
    where = " AND ".join(clauses)
    params.append(limit)
    cur.execute(f"""
        SELECT ci.company_name, csb.role_title, csb.level, csb.country,
               csb.min_salary_lpa, csb.median_salary_lpa, csb.max_salary_lpa
        FROM company_salary_bands csb
        JOIN company_intel ci ON ci.id = csb.company_id
        WHERE {where} ORDER BY csb.max_salary_lpa DESC LIMIT ?
    """, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"count": len(rows), "salary_bands": rows}


# ============================================================
# TOOL 5: Company Intel
# ============================================================
def company_intel(company=None, limit=10):
    company = company or ""
    limit = limit or 10
    conn = _conn(); cur = conn.cursor()
    clauses = ["1=1"]
    params = []
    if company:
        clauses.append("LOWER(company_name) LIKE ?")
        params.append(f"%{company.lower()}%")
    where = " AND ".join(clauses)
    params.append(limit)
    cur.execute(f"""
        SELECT company_name, sector, hq_country, hiring_cgpa_min,
               eligible_degrees, required_skills, visa_sponsorship,
               growth_score, stability_score
        FROM company_intel WHERE {where} LIMIT ?
    """, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"count": len(rows), "companies": rows}


# ============================================================
# TOOL 6: Placement Lookup
# ============================================================
def placement_lookup(university=None, limit=5):
    university = university or ""
    limit = limit or 5
    conn = _conn(); cur = conn.cursor()
    params = []
    clauses = ["1=1"]
    if university:
        clauses.append("LOWER(university_name) LIKE ?")
        params.append(f"%{university.lower()}%")
    where = " AND ".join(clauses)
    params.append(limit)
    cur.execute(f"""
        SELECT university_name, country, rank_nirf, rank_qs,
               cutoff_percentile, placement_pct,
               avg_package_lpa, highest_package_lpa, top_recruiters
        FROM university_intel WHERE {where} LIMIT ?
    """, params)
    rows = [dict(r) for r in cur.fetchall()]

    for row in rows:
        cur.execute("""
            SELECT ur.company_name, ur.offers_made, ur.avg_package_lpa
            FROM university_recruiters ur
            JOIN university_intel ui ON ui.id = ur.university_id
            WHERE ui.university_name = ? LIMIT 5
        """, (row['university_name'],))
        row['recruiters'] = [dict(r) for r in cur.fetchall()]

    conn.close()
    return {"count": len(rows), "universities": rows}


# ============================================================
# TOOL 7: Full Package Jobs
# ============================================================
def full_package_jobs(country=None, limit=20):
    country = country or ""
    limit = limit or 20
    conn = _conn(); cur = conn.cursor()
    clauses = ["visa_free=1", "ticket_free=1", "accommodation=1"]
    params = []
    if country:
        clauses.append("LOWER(country) LIKE ?")
        params.append(f"%{country.lower()}%")
    where = " AND ".join(clauses)
    params.append(limit)
    cur.execute(f"""
        SELECT company_name, job_title, country, hours_per_day,
               days_per_week, overtime_rate, off_days,
               food_lunch, food_dinner, shift_timing
        FROM job_benefits_deep WHERE {where} LIMIT ?
    """, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"count": len(rows), "jobs": rows}


# ============================================================
# TOOL 8: OIE Stats
# ============================================================
def oie_stats():
    conn = _conn(); cur = conn.cursor()
    out = {}
    try:
        cur.execute("SELECT COUNT(*) FROM opportunities WHERE status='DISCOVERED'")
        out["jobs"] = cur.fetchone()[0]
    except: pass
    try:
        cur.execute("SELECT COUNT(*) FROM study_opportunities WHERE status='DISCOVERED'")
        out["universities"] = cur.fetchone()[0]
    except: pass
    try:
        cur.execute("SELECT COUNT(*) FROM scholarships")
        out["scholarships"] = cur.fetchone()[0]
    except: pass
    try:
        cur.execute("SELECT COUNT(*) FROM company_intel")
        out["companies"] = cur.fetchone()[0]
    except: pass
    try:
        cur.execute("SELECT COUNT(*) FROM job_benefits_deep WHERE visa_free=1")
        out["visa_free_jobs"] = cur.fetchone()[0]
    except: pass
    conn.close()
    return out


# ============================================================
# TOOL DEFINITIONS
# ============================================================
OIE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_jobs",
            "description": "Search real jobs by title, company, or country",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "country": {"type": "string"},
                    "limit": {"type": "integer"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_universities",
            "description": "Search universities by country, free tuition, PR-friendly",
            "parameters": {
                "type": "object",
                "properties": {
                    "country": {"type": "string"},
                    "free_only": {"type": "boolean"},
                    "pr_only": {"type": "boolean"},
                    "query": {"type": "string"},
                    "limit": {"type": "integer"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_scholarships",
            "description": "Find scholarships by country or subject",
            "parameters": {
                "type": "object",
                "properties": {
                    "country": {"type": "string"},
                    "subject": {"type": "string"},
                    "limit": {"type": "integer"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "salary_band_lookup",
            "description": "Get salary bands for company/role",
            "parameters": {
                "type": "object",
                "properties": {
                    "company": {"type": "string"},
                    "role": {"type": "string"},
                    "limit": {"type": "integer"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "company_intel",
            "description": "Get hiring criteria, skills for a company",
            "parameters": {
                "type": "object",
                "properties": {
                    "company": {"type": "string"},
                    "limit": {"type": "integer"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "placement_lookup",
            "description": "Get placement %, package, top recruiters for a university",
            "parameters": {
                "type": "object",
                "properties": {
                    "university": {"type": "string"},
                    "limit": {"type": "integer"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "full_package_jobs",
            "description": "Jobs with FREE visa + ticket + accommodation",
            "parameters": {
                "type": "object",
                "properties": {
                    "country": {"type": "string"},
                    "limit": {"type": "integer"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "oie_stats",
            "description": "Get overall OIE statistics",
            "parameters": {"type": "object", "properties": {}}
        }
    },
]


# ============================================================
# EXECUTOR
# ============================================================
def execute_oie_tool(name, args):
    try:
        if name == "search_jobs":
            return search_jobs(**args)
        elif name == "search_universities":
            return search_universities(**args)
        elif name == "search_scholarships":
            return search_scholarships(**args)
        elif name == "salary_band_lookup":
            return salary_band_lookup(**args)
        elif name == "company_intel":
            return company_intel(**args)
        elif name == "placement_lookup":
            return placement_lookup(**args)
        elif name == "full_package_jobs":
            return full_package_jobs(**args)
        elif name == "oie_stats":
            return oie_stats()
        else:
            return {"error": f"Unknown: {name}"}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    print("Testing 8 OIE tools...\n")
    print("1. Jobs:", search_jobs(country="Germany", limit=3)["count"])
    print("2. Universities:", search_universities(free_only=True, limit=3)["count"])
    print("3. Scholarships:", search_scholarships(limit=3)["count"])
    print("4. Salary bands:", salary_band_lookup(company="Google")["count"])
    print("5. Companies:", company_intel()["count"])
    print("6. Placement:", placement_lookup(university="IIT")["count"])
    print("7. Full package:", full_package_jobs()["count"])
    print("8. Stats:", oie_stats())