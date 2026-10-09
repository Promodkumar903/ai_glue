"""
Study OIE — Student Matching Engine
Deterministic 7-factor scoring (same pattern as jobs)
"""
import json
import uuid
import sqlite3
from datetime import datetime

DB = "ai_glue.db"


# ============================================================
# ELIGIBILITY — Hard constraints
# ============================================================
def check_eligibility(student, uni):
    blocking = []

    # Country preference
    target_countries = (student.get("target_countries") or "").lower()
    if target_countries:
        countries = [c.strip() for c in target_countries.split(",")]
        uni_country = (uni.get("country") or "").lower()
        if uni_country not in [c.lower() for c in countries]:
            blocking.append(f"Country {uni.get('country')} not in targets")

    # Language requirement
    uni_lang = (uni.get("language") or "").lower()
    if "german" in uni_lang:
        if (student.get("german_level") or 0) < 0.5:
            blocking.append("Needs German proficiency")

    return blocking


# ============================================================
# 7-FACTOR SCORE
# ============================================================
def compute_match(student, uni):
    """Student ↔ University match"""
    blocking = check_eligibility(student, uni)
    if blocking:
        return {
            "eligible": False,
            "score": 0,
            "blocking_reasons": blocking,
            "breakdown": {},
        }

    breakdown = {}

    # 1. Country Fit (25) — target country match
    tc = (student.get("target_countries") or "").lower()
    if tc and uni.get("country", "").lower() in tc:
        breakdown["country_fit"] = 25
    else:
        breakdown["country_fit"] = 10

    # 2. Academic Fit (20) — education level match
    edu_student = (student.get("education_level") or "").lower()
    uni_type = (uni.get("degree_level") or "").lower()
    if edu_student in ("bachelor", "undergrad") and uni_type in ("bachelor", "undergraduate", ""):
        breakdown["academic_fit"] = 20
    elif edu_student in ("master", "masters", "postgrad") and uni_type in ("master", "postgraduate", ""):
        breakdown["academic_fit"] = 20
    else:
        breakdown["academic_fit"] = 15

    # 3. Budget Fit (20) — tuition vs budget
    budget = student.get("budget_usd") or 0
    tuition = uni.get("tuition_fee") or 0
    if budget == 0 or tuition == 0:
        breakdown["budget_fit"] = 15  # unknown, partial score
    elif tuition <= budget:
        breakdown["budget_fit"] = 20
    else:
        gap_pct = (tuition - budget) / tuition * 100
        breakdown["budget_fit"] = max(0, int(20 - gap_pct / 5))

    # 4. English Requirement (15)
    ielts = student.get("ielts") or 0
    toefl = student.get("toefl") or 0
    if ielts >= 6.5 or toefl >= 90:
        breakdown["english_fit"] = 15
    elif ielts >= 6.0 or toefl >= 80:
        breakdown["english_fit"] = 12
    elif ielts >= 5.5 or toefl >= 70:
        breakdown["english_fit"] = 8
    else:
        breakdown["english_fit"] = 5

    # 5. Intake Availability (10)
    if uni.get("intake"):
        breakdown["intake_fit"] = 10
    else:
        breakdown["intake_fit"] = 5

    # 6. Evidence Quality (5) — from source
    breakdown["evidence_quality"] = 5

    # 7. Freshness (5)
    breakdown["freshness"] = 5

    total = sum(breakdown.values())

    return {
        "eligible": True,
        "score": min(total, 100),
        "blocking_reasons": [],
        "breakdown": breakdown,
    }


# ============================================================
# SAVE PROFILE
# ============================================================
def save_student_profile(user_id, profile):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()

    cur.execute("""
        INSERT OR REPLACE INTO student_profiles_oie
        (user_id, education_level, field_of_study, gpa, ielts, toefl,
         budget_usd, target_countries, target_degree, preferred_intake,
         work_experience_years, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        profile.get("education_level", ""),
        profile.get("field_of_study", ""),
        profile.get("gpa", 0),
        profile.get("ielts", 0),
        profile.get("toefl", 0),
        profile.get("budget_usd", 0),
        profile.get("target_countries", ""),
        profile.get("target_degree", ""),
        profile.get("preferred_intake", ""),
        profile.get("work_experience_years", 0),
        now,
    ))
    conn.commit()
    conn.close()


# ============================================================
# MATCH STUDENT → ALL UNIVERSITIES
# ============================================================
def match_student(user_id, limit=20):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("SELECT * FROM student_profiles_oie WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return []

    cols = [d[0] for d in cur.description]
    student = dict(zip(cols, row))

    cur.execute("""
        SELECT id, university_name, country, city, tuition_fee,
               language, degree_level, application_url
        FROM study_opportunities
        WHERE status='DISCOVERED'
    """)
    unis = cur.fetchall()
    u_cols = [d[0] for d in cur.description]
    conn.close()

    results = []
    for u in unis:
        uni = dict(zip(u_cols, u))
        match = compute_match(student, uni)
        if match["eligible"]:
            results.append({
                "uni_id": uni["id"],
                "university_name": uni["university_name"],
                "country": uni["country"],
                "score": match["score"],
                "breakdown": match["breakdown"],
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]


# ============================================================
# TEST
# ============================================================
def test_with_sample():
    """Create sample student and test matching"""
    sample_user = "test_student_001"
    sample_profile = {
        "education_level": "bachelor",
        "field_of_study": "Computer Science",
        "gpa": 3.5,
        "ielts": 6.5,
        "toefl": 0,
        "budget_usd": 20000,
        "target_countries": "germany,canada",
        "target_degree": "master",
        "preferred_intake": "Fall 2026",
        "work_experience_years": 2,
    }

    print("Creating sample student profile...")
    save_student_profile(sample_user, sample_profile)
    print(f"  User: {sample_user}")
    print(f"  Country targets: {sample_profile['target_countries']}")
    print(f"  Budget: ${sample_profile['budget_usd']}")
    print(f"  IELTS: {sample_profile['ielts']}")

    print("\nMatching against 3639 universities...")
    results = match_student(sample_user, limit=10)

    print(f"\n{'='*70}")
    print(f"TOP 10 MATCHES FOR {sample_user}")
    print(f"{'='*70}")
    for i, r in enumerate(results, 1):
        print(f"\n[{i}] {r['university_name'][:55]}")
        print(f"    Country: {r['country']}")
        print(f"    Score: {r['score']}/100")
        print(f"    Breakdown: {r['breakdown']}")


if __name__ == "__main__":
    print("=" * 70)
    print("STUDY OIE — MATCHING ENGINE TEST")
    print("=" * 70)
    test_with_sample()