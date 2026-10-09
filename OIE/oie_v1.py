"""
AI Glue OIE v1 — Complete Standalone Module
Tables + Grading + Matching + Duplicate + Test
"""
import sqlite3
import uuid
import json
from datetime import datetime

DB = "ai_glue.db"


# ============================================================
# STEP 1: MIGRATE — Create OIE tables
# ============================================================
def migrate():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # claims table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS claims (
            id TEXT PRIMARY KEY,
            opportunity_id TEXT NOT NULL,
            field_name TEXT NOT NULL,
            claimed_value TEXT,
            truth_state TEXT DEFAULT 'UNKNOWN',
            source_priority INTEGER DEFAULT 4,
            confidence REAL DEFAULT 0.0,
            created_at TEXT,
            updated_at TEXT
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_claims_opp ON claims(opportunity_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_claims_field ON claims(field_name)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_claims_state ON claims(truth_state)")

    # opportunity_grades table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS opportunity_grades (
            opportunity_id TEXT PRIMARY KEY,
            job_level TEXT,
            trust_score INTEGER,
            reasons TEXT,
            graded_at TEXT
        )
    """)

    # duplicate_groups
    cur.execute("""
        CREATE TABLE IF NOT EXISTS duplicate_groups (
            id TEXT PRIMARY KEY,
            canonical_id TEXT,
            duplicate_id TEXT,
            similarity REAL,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("OK: OIE tables created (claims, opportunity_grades, duplicate_groups)")


# ============================================================
# STEP 2: GRADING AI — D/C/B/A + Trust Score
# ============================================================
def grade_opportunity(opp: dict) -> dict:
    """D/C/B/A level + Trust score"""
    exp = opp.get("experience_years", 0) or 0
    edu = (opp.get("education") or "").lower()
    skills = opp.get("skills") or []

    # Job Level
    if exp >= 5 and ("degree" in edu or "bachelor" in edu or "master" in edu):
        level = "A"
    elif exp >= 3 and skills:
        level = "B"
    elif exp >= 1 or skills:
        level = "C"
    else:
        level = "D"

    # Trust Score
    trust = 0
    src = opp.get("source_type", "PORTAL")
    if src == "GOV":
        trust += 40
    elif src == "EMPLOYER":
        trust += 25
    elif src == "AGENCY":
        trust += 10

    if opp.get("visa_evidence"):
        trust += 15
    if opp.get("accommodation_evidence"):
        trust += 10
    if opp.get("ticket_evidence"):
        trust += 5
    if opp.get("no_fee_evidence"):
        trust += 10
    if opp.get("employer_url"):
        trust += 10
    if not opp.get("deadline_expired"):
        trust += 10

    trust = min(trust, 100)
    if trust < 0:
        trust = 0

    return {
        "job_level": level,
        "trust_score": trust,
        "reasons": {
            "experience_years": exp,
            "education": edu or "UNKNOWN",
            "skills_count": len(skills),
            "source_type": src,
        }
    }


def save_grade(opportunity_id: str, grade: dict):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO opportunity_grades
        (opportunity_id, job_level, trust_score, reasons, graded_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        opportunity_id,
        grade["job_level"],
        grade["trust_score"],
        json.dumps(grade["reasons"]),
        datetime.utcnow().isoformat()
    ))
    conn.commit()
    conn.close()


# ============================================================
# STEP 3: MATCHING AI — 7-Factor Deterministic
# ============================================================
def match_score(candidate: dict, opp: dict) -> dict:
    """
    7-factor scoring:
    Eligibility 25% + Evidence 20% + Quality 15% +
    Affordability 15% + Accessibility 10% + Benefits 10% +
    Freshness 5%
    """
    scores = {}
    blocking = []
    missing = []

    # Hard constraints
    c_age = candidate.get("age")
    o_age_min = opp.get("age_min")
    o_age_max = opp.get("age_max")
    if c_age and o_age_min and c_age < o_age_min:
        blocking.append(f"Age {c_age} below minimum {o_age_min}")
    if c_age and o_age_max and c_age > o_age_max:
        blocking.append(f"Age {c_age} above maximum {o_age_max}")

    c_lang = set((candidate.get("languages") or "").lower().split(","))
    o_lang = set((opp.get("language") or "").lower().split(","))
    missing_lang = o_lang - c_lang
    if missing_lang:
        blocking.append(f"Missing languages: {missing_lang}")

    if blocking:
        return {
            "eligible": False,
            "score": 0,
            "blocking_reasons": blocking,
            "missing_requirements": missing,
        }

    # 1. Eligibility (25 pts)
    exp_c = candidate.get("experience_years", 0) or 0
    exp_o = opp.get("experience_years", 0) or 0
    if exp_c >= exp_o:
        scores["eligibility"] = 25
    else:
        gap = exp_o - exp_c
        scores["eligibility"] = max(0, 25 - gap * 5)
        missing.append(f"Need {gap} more years experience")

    # 2. Evidence (20 pts)
    ev = 0
    if opp.get("visa_evidence"): ev += 8
    if opp.get("accommodation_evidence"): ev += 6
    if opp.get("ticket_evidence"): ev += 3
    if opp.get("source_type") == "GOV": ev += 3
    scores["evidence"] = min(ev, 20)

    # 3. Opportunity Quality (15 pts) — via trust score
    trust = opp.get("trust_score", 50)
    scores["quality"] = int(trust * 0.15)

    # 4. Affordability (15 pts) — salary vs candidate expectation
    salary = opp.get("salary_numeric", 0) or 0
    expected = candidate.get("min_salary", 0) or 0
    if expected == 0:
        scores["affordability"] = 15
    elif salary >= expected:
        scores["affordability"] = 15
    else:
        scores["affordability"] = max(0, 15 - int((expected - salary) / expected * 15))

    # 5. Accessibility (10 pts)
    acc = 0
    if exp_o <= 1: acc += 4
    if not opp.get("education") or opp.get("education").lower() in ["none", ""]: acc += 3
    if not opp.get("language"): acc += 3
    scores["accessibility"] = min(acc, 10)

    # 6. Benefits (10 pts)
    ben = 0
    if opp.get("accommodation_evidence"): ben += 4
    if opp.get("ticket_evidence"): ben += 3
    if opp.get("food_evidence"): ben += 2
    if opp.get("no_fee_evidence"): ben += 1
    scores["benefits"] = min(ben, 10)

    # 7. Freshness (5 pts)
    scores["freshness"] = 5  # placeholder — fresh check later

    total = sum(scores.values())
    total = min(total, 100)

    return {
        "eligible": True,
        "score": total,
        "breakdown": scores,
        "blocking_reasons": [],
        "missing_requirements": missing,
        "recommended_action": "APPLY" if total >= 70 else "VERIFY" if total >= 50 else "SKIP",
    }


# ============================================================
# STEP 4: DUPLICATE AI — Fuzzy Match
# ============================================================
def similarity(a: str, b: str) -> float:
    """Simple token-based similarity (no external dep)"""
    if not a or not b:
        return 0.0
    a_t = set(a.lower().split())
    b_t = set(b.lower().split())
    if not a_t or not b_t:
        return 0.0
    common = a_t & b_t
    total = a_t | b_t
    return len(common) / len(total)


def find_duplicates(opportunities: list, threshold: float = 0.85):
    """Return list of (canonical_id, duplicate_id, similarity)"""
    dups = []
    n = len(opportunities)
    for i in range(n):
        for j in range(i + 1, n):
            a = opportunities[i]
            b = opportunities[j]
            # Match on title + company/country
            sig_a = f"{a.get('title', '')} {a.get('company', '')} {a.get('country', '')}"
            sig_b = f"{b.get('title', '')} {b.get('company', '')} {b.get('country', '')}"
            s = similarity(sig_a, sig_b)
            if s >= threshold:
                dups.append((a["id"], b["id"], round(s, 3)))
    return dups


# ============================================================
# TEST — Sample Data
# ============================================================
def run_tests():
    print("\n=== TEST 1: Grading ===")
    job = {
        "experience_years": 0,
        "education": "none",
        "skills": [],
        "source_type": "GOV",
        "visa_evidence": True,
        "accommodation_evidence": True,
        "ticket_evidence": False,
        "no_fee_evidence": True,
        "employer_url": "https://example.com",
    }
    g = grade_opportunity(job)
    print(f"Level: {g['job_level']}, Trust: {g['trust_score']}")
    assert g["job_level"] == "D", "Should be D"
    assert g["trust_score"] >= 70, "Trust should be high"
    print("PASS")

    print("\n=== TEST 2: Matching ===")
    candidate = {
        "age": 25,
        "experience_years": 0,
        "languages": "english,hindi",
        "min_salary": 0,
    }
    opp = {
        "experience_years": 0,
        "education": "none",
        "language": "english",
        "visa_evidence": True,
        "accommodation_evidence": True,
        "ticket_evidence": False,
        "food_evidence": False,
        "no_fee_evidence": True,
        "source_type": "GOV",
        "trust_score": 85,
        "salary_numeric": 0,
    }
    m = match_score(candidate, opp)
    print(f"Eligible: {m['eligible']}, Score: {m['score']}")
    print(f"Breakdown: {m.get('breakdown')}")
    print(f"Action: {m.get('recommended_action')}")
    assert m["eligible"] == True
    assert m["score"] >= 70
    print("PASS")

    print("\n=== TEST 3: Hard Constraint Block ===")
    candidate2 = {"age": 55, "experience_years": 5, "languages": "english"}
    opp2 = {"age_max": 45, "language": "english", "experience_years": 2}
    m2 = match_score(candidate2, opp2)
    print(f"Eligible: {m2['eligible']}, Blocking: {m2['blocking_reasons']}")
    assert m2["eligible"] == False
    assert len(m2["blocking_reasons"]) > 0
    print("PASS")

    print("\n=== TEST 4: Duplicate Detection ===")
    opps = [
        {"id": "A", "title": "Warehouse Worker", "company": "ABC GmbH", "country": "Germany"},
        {"id": "B", "title": "Warehouse Worker", "company": "ABC GmbH", "country": "Germany"},
        {"id": "C", "title": "Nurse", "company": "XYZ", "country": "Germany"},
    ]
    dups = find_duplicates(opps, threshold=0.8)
    print(f"Duplicates found: {dups}")
    assert len(dups) >= 1
    print("PASS")

    print("\n=== ALL TESTS PASSED ===")


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("AI Glue OIE v1 — Starting...")
    migrate()
    run_tests()
    print("\nDone. OIE v1 foundation ready.")