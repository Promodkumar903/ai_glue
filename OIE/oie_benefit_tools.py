"""
OIE Benefit Tools — Copilot integration for work conditions
8 new tools for benefit-based search
"""
import sqlite3

DB = "ai_glue.db"


def _connect():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================
# TOOL 1: Full Package Jobs (Visa + Ticket + Accommodation)
# ============================================================
def full_package_jobs(country="", category="", limit=20):
    conn = _connect()
    cur = conn.cursor()
    clauses = ["visa_free=1", "ticket_free=1", "accommodation=1"]
    params = []
    if country:
        clauses.append("LOWER(country) LIKE ?")
        params.append(f"%{country.lower()}%")
    if category:
        clauses.append("LOWER(category) LIKE ?")
        params.append(f"%{category.lower()}%")
    where = " AND ".join(clauses)
    params.append(limit)
    cur.execute(f"""
        SELECT company_name, job_title, country, category,
               hours_per_day, days_per_week, overtime_rate, off_days,
               food_lunch, food_dinner, food_breakfast, shift_timing
        FROM job_benefits_deep WHERE {where}
        ORDER BY country, company_name LIMIT ?
    """, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"count": len(rows), "jobs": rows}


# ============================================================
# TOOL 2: Food Provided Jobs
# ============================================================
def food_provided_jobs(country="", meals="any", limit=20):
    """meals: any/lunch/dinner/breakfast/full"""
    conn = _connect()
    cur = conn.cursor()
    clauses = []
    if meals == "lunch":
        clauses.append("food_lunch=1")
    elif meals == "dinner":
        clauses.append("food_dinner=1")
    elif meals == "breakfast":
        clauses.append("food_breakfast=1")
    elif meals == "full":
        clauses.append("food_lunch=1 AND food_dinner=1 AND food_breakfast=1")
    else:
        clauses.append("(food_lunch=1 OR food_dinner=1 OR food_breakfast=1)")

    params = []
    if country:
        clauses.append("LOWER(country) LIKE ?")
        params.append(f"%{country.lower()}%")
    where = " AND ".join(clauses)
    params.append(limit)
    cur.execute(f"""
        SELECT company_name, job_title, country, category,
               food_lunch, food_dinner, food_breakfast,
               food_allowance_usd, hours_per_day, days_per_week
        FROM job_benefits_deep WHERE {where} LIMIT ?
    """, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"count": len(rows), "jobs": rows}


# ============================================================
# TOOL 3: Working Hours Filter
# ============================================================
def jobs_by_working_hours(max_hours=8, max_days=5, limit=20):
    conn = _connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT company_name, job_title, country, category,
               hours_per_day, days_per_week, overtime_rate, off_days
        FROM job_benefits_deep
        WHERE hours_per_day <= ? AND days_per_week <= ?
        ORDER BY hours_per_day, days_per_week LIMIT ?
    """, (max_hours, max_days, limit))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"count": len(rows), "jobs": rows}


# ============================================================
# TOOL 4: Overtime Available Jobs
# ============================================================
def overtime_jobs(country="", min_rate="", limit=20):
    conn = _connect()
    cur = conn.cursor()
    clauses = ["overtime_available=1"]
    params = []
    if country:
        clauses.append("LOWER(country) LIKE ?")
        params.append(f"%{country.lower()}%")
    where = " AND ".join(clauses)
    params.append(limit)
    cur.execute(f"""
        SELECT company_name, job_title, country, category,
               overtime_rate, hours_per_day, days_per_week, off_days
        FROM job_benefits_deep WHERE {where} LIMIT ?
    """, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"count": len(rows), "jobs": rows}


# ============================================================
# TOOL 5: Weekend Off Jobs
# ============================================================
def weekend_off_jobs(country="", limit=20):
    conn = _connect()
    cur = conn.cursor()
    clauses = ["(off_days LIKE '%Sat%' OR off_days LIKE '%Sunday%' OR off_days LIKE '%Sun%')"]
    params = []
    if country:
        clauses.append("LOWER(country) LIKE ?")
        params.append(f"%{country.lower()}%")
    where = " AND ".join(clauses)
    params.append(limit)
    cur.execute(f"""
        SELECT company_name, job_title, country, category, off_days,
               hours_per_day, days_per_week
        FROM job_benefits_deep WHERE {where} LIMIT ?
    """, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"count": len(rows), "jobs": rows}


# ============================================================
# TOOL 6: Compare Companies
# ============================================================
def compare_companies(company1="", company2="", limit=10):
    conn = _connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT company_name, country, job_title, category,
               visa_free, ticket_free, accommodation,
               food_lunch, food_dinner, food_breakfast,
               hours_per_day, days_per_week, overtime_available, overtime_rate,
               off_days, shift_timing, medical_insurance
        FROM job_benefits_deep
        WHERE LOWER(company_name) LIKE ? OR LOWER(company_name) LIKE ?
        LIMIT ?
    """, (f"%{company1.lower()}%", f"%{company2.lower()}%", limit))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"count": len(rows), "companies": rows}


# ============================================================
# TOOL 7: Jobs with Medical Insurance
# ============================================================
def medical_insurance_jobs(country="", limit=20):
    conn = _connect()
    cur = conn.cursor()
    clauses = ["medical_insurance=1"]
    params = []
    if country:
        clauses.append("LOWER(country) LIKE ?")
        params.append(f"%{country.lower()}%")
    where = " AND ".join(clauses)
    params.append(limit)
    cur.execute(f"""
        SELECT company_name, job_title, country, category,
               medical_insurance, hours_per_day, days_per_week
        FROM job_benefits_deep WHERE {where} LIMIT ?
    """, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"count": len(rows), "jobs": rows}


# ============================================================
# TOOL 8: Contract Duration Filter
# ============================================================
def jobs_by_contract_duration(min_months=0, max_months=120, country="", limit=20):
    conn = _connect()
    cur = conn.cursor()
    clauses = ["contract_duration_months >= ?", "contract_duration_months <= ?"]
    params = [min_months, max_months]
    if country:
        clauses.append("LOWER(country) LIKE ?")
        params.append(f"%{country.lower()}%")
    where = " AND ".join(clauses)
    params.append(limit)
    cur.execute(f"""
        SELECT company_name, job_title, country, category,
               contract_duration_months, contract_extension, leave_days_per_year
        FROM job_benefits_deep WHERE {where} LIMIT ?
    """, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"count": len(rows), "jobs": rows}


# ============================================================
# TOOL DEFINITIONS FOR GROQ
# ============================================================
BENEFIT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "full_package_jobs",
            "description": "Get jobs with FREE visa + FREE ticket + accommodation. Use when user asks about full-package jobs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "country": {"type": "string"},
                    "category": {"type": "string"},
                    "limit": {"type": "integer", "default": 20}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "food_provided_jobs",
            "description": "Jobs where food (lunch/dinner/breakfast) is provided",
            "parameters": {
                "type": "object",
                "properties": {
                    "country": {"type": "string"},
                    "meals": {"type": "string", "enum": ["any", "lunch", "dinner", "breakfast", "full"]},
                    "limit": {"type": "integer", "default": 20}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "jobs_by_working_hours",
            "description": "Find jobs with max hours/day and days/week",
            "parameters": {
                "type": "object",
                "properties": {
                    "max_hours": {"type": "integer", "default": 8},
                    "max_days": {"type": "integer", "default": 5},
                    "limit": {"type": "integer", "default": 20}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "overtime_jobs",
            "description": "Jobs with overtime available",
            "parameters": {
                "type": "object",
                "properties": {
                    "country": {"type": "string"},
                    "limit": {"type": "integer", "default": 20}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "weekend_off_jobs",
            "description": "Jobs where Saturday/Sunday are off",
            "parameters": {
                "type": "object",
                "properties": {
                    "country": {"type": "string"},
                    "limit": {"type": "integer", "default": 20}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compare_companies",
            "description": "Compare 2 companies' work conditions",
            "parameters": {
                "type": "object",
                "properties": {
                    "company1": {"type": "string"},
                    "company2": {"type": "string"},
                    "limit": {"type": "integer", "default": 10}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "medical_insurance_jobs",
            "description": "Jobs with medical insurance",
            "parameters": {
                "type": "object",
                "properties": {
                    "country": {"type": "string"},
                    "limit": {"type": "integer", "default": 20}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "jobs_by_contract_duration",
            "description": "Filter jobs by contract months",
            "parameters": {
                "type": "object",
                "properties": {
                    "min_months": {"type": "integer"},
                    "max_months": {"type": "integer"},
                    "country": {"type": "string"},
                    "limit": {"type": "integer", "default": 20}
                }
            }
        }
    },
]


def execute_benefit_tool(name, args):
    try:
        if name == "full_package_jobs":
            return full_package_jobs(**args)
        elif name == "food_provided_jobs":
            return food_provided_jobs(**args)
        elif name == "jobs_by_working_hours":
            return jobs_by_working_hours(**args)
        elif name == "overtime_jobs":
            return overtime_jobs(**args)
        elif name == "weekend_off_jobs":
            return weekend_off_jobs(**args)
        elif name == "compare_companies":
            return compare_companies(**args)
        elif name == "medical_insurance_jobs":
            return medical_insurance_jobs(**args)
        elif name == "jobs_by_contract_duration":
            return jobs_by_contract_duration(**args)
        else:
            return {"error": f"Unknown tool: {name}"}
    except Exception as e:
        return {"error": str(e)}


# ============================================================
# TEST
# ============================================================
if __name__ == "__main__":
    print("=" * 80)
    print("OIE BENEFIT TOOLS — Test")
    print("=" * 80)

    print("\n### Test 1: Full package jobs (visa+ticket+accommodation)")
    r = full_package_jobs(limit=5)
    print(f"Found: {r['count']}")
    for j in r['jobs'][:5]:
        print(f"  • {j['company_name']} — {j['job_title']} ({j['country']})")

    print("\n### Test 2: Jobs with full food")
    r = food_provided_jobs(meals="full", limit=5)
    print(f"Found: {r['count']}")
    for j in r['jobs'][:5]:
        print(f"  • {j['company_name']} — {j['job_title']} ({j['country']})")

    print("\n### Test 3: 8-hour 5-day jobs")
    r = jobs_by_working_hours(max_hours=8, max_days=5, limit=5)
    print(f"Found: {r['count']}")

    print("\n### Test 4: Weekend off")
    r = weekend_off_jobs(limit=5)
    print(f"Found: {r['count']}")
    for j in r['jobs'][:5]:
        print(f"  • {j['company_name']} — {j['job_title']} | Off: {j['off_days']}")