"""
Dual Match — Student ↔ University ↔ Company
Links companies to colleges they hire from, then matches students end-to-end
"""
import sqlite3
import uuid
from datetime import datetime

DB = "ai_glue.db"


# ============================================================
# COMPANY → COLLEGE HIRING RELATIONSHIPS
# ============================================================
# (company_name, college_name, country, offers_per_year, avg_lpa, high_lpa, role)
COMPANY_COLLEGE_MAP = [
    # Google
    ("Google", "IIT Bombay", "India", 15, 45, 150, "SWE"),
    ("Google", "IIT Delhi", "India", 18, 48, 180, "SWE"),
    ("Google", "IIT Madras", "India", 12, 44, 160, "SWE"),
    ("Google", "IIT Kanpur", "India", 10, 42, 140, "SWE"),
    ("Google", "BITS Pilani", "India", 8, 38, 120, "SWE"),
    ("Google", "MIT", "USA", 25, 130, 250, "SWE"),
    ("Google", "Stanford", "USA", 22, 135, 260, "SWE"),
    ("Google", "Carnegie Mellon University", "USA", 20, 128, 240, "SWE"),
    ("Google", "University of Oxford", "UK", 10, 65, 120, "SWE"),
    ("Google", "ETH Zurich", "Switzerland", 8, 110, 200, "SWE"),

    # Microsoft
    ("Microsoft", "IIT Bombay", "India", 25, 40, 120, "SDE"),
    ("Microsoft", "IIT Delhi", "India", 22, 42, 130, "SDE"),
    ("Microsoft", "IIT Madras", "India", 20, 38, 110, "SDE"),
    ("Microsoft", "IIT Hyderabad", "India", 15, 35, 100, "SDE"),
    ("Microsoft", "NIT Trichy", "India", 12, 28, 75, "SDE"),
    ("Microsoft", "MIT", "USA", 18, 125, 230, "SDE"),
    ("Microsoft", "Stanford", "USA", 15, 128, 240, "SDE"),

    # Amazon
    ("Amazon", "IIT Bombay", "India", 30, 35, 88, "SDE"),
    ("Amazon", "IIT Delhi", "India", 30, 38, 100, "SDE"),
    ("Amazon", "IIT Madras", "India", 25, 34, 85, "SDE"),
    ("Amazon", "BITS Pilani", "India", 20, 30, 75, "SDE"),
    ("Amazon", "VIT Vellore", "India", 15, 18, 45, "SDE"),
    ("Amazon", "MIT", "USA", 20, 115, 220, "SDE"),

    # Meta
    ("Meta", "IIT Bombay", "India", 8, 60, 150, "SWE"),
    ("Meta", "IIT Delhi", "India", 10, 62, 160, "SWE"),
    ("Meta", "Stanford", "USA", 25, 145, 250, "SWE"),
    ("Meta", "MIT", "USA", 22, 148, 260, "SWE"),

    # Apple
    ("Apple", "IIT Bombay", "India", 5, 55, 130, "SWE"),
    ("Apple", "MIT", "USA", 15, 135, 240, "SWE"),
    ("Apple", "Stanford", "USA", 18, 140, 250, "SWE"),

    # Goldman Sachs
    ("Goldman Sachs", "IIT Bombay", "India", 12, 35, 80, "Analyst"),
    ("Goldman Sachs", "IIT Delhi", "India", 15, 38, 90, "Analyst"),
    ("Goldman Sachs", "IIM Ahmedabad", "India", 15, 35, 100, "Associate"),
    ("Goldman Sachs", "IIM Bangalore", "India", 12, 34, 95, "Associate"),
    ("Goldman Sachs", "MIT", "USA", 10, 110, 200, "Analyst"),

    # McKinsey
    ("McKinsey & Company", "IIM Ahmedabad", "India", 25, 32, 90, "Consultant"),
    ("McKinsey & Company", "IIM Bangalore", "India", 22, 31, 85, "Consultant"),
    ("McKinsey & Company", "IIT Delhi", "India", 8, 25, 60, "BA"),
    ("McKinsey & Company", "Harvard", "USA", 30, 130, 250, "Consultant"),

    # BCG
    ("BCG", "IIM Ahmedabad", "India", 20, 30, 85, "Consultant"),
    ("BCG", "IIM Bangalore", "India", 18, 29, 80, "Consultant"),
    ("BCG", "Harvard", "USA", 25, 125, 240, "Consultant"),

    # TCS
    ("Tata Consultancy Services (TCS)", "NIT Trichy", "India", 200, 6, 12, "SE"),
    ("Tata Consultancy Services (TCS)", "VIT Vellore", "India", 500, 4, 8, "SE"),
    ("Tata Consultancy Services (TCS)", "SRM Chennai", "India", 400, 4, 7, "SE"),
    ("Tata Consultancy Services (TCS)", "Manipal Institute of Technology", "India", 300, 5, 9, "SE"),

    # Infosys
    ("Infosys", "VIT Vellore", "India", 400, 4, 7, "SE"),
    ("Infosys", "SRM Chennai", "India", 350, 4, 6, "SE"),
    ("Infosys", "Manipal Institute of Technology", "India", 250, 5, 8, "SE"),

    # Flipkart
    ("Flipkart", "IIT Bombay", "India", 10, 25, 50, "SDE"),
    ("Flipkart", "IIT Delhi", "India", 12, 28, 55, "SDE"),
    ("Flipkart", "BITS Pilani", "India", 8, 22, 45, "SDE"),

    # Tesla
    ("Tesla", "IIT Madras", "India", 5, 55, 100, "SWE"),
    ("Tesla", "Stanford", "USA", 12, 130, 220, "SWE"),
    ("Tesla", "MIT", "USA", 10, 128, 215, "SWE"),

    # Siemens / Bosch
    ("Siemens", "IIT Bombay", "India", 8, 18, 35, "Engineer"),
    ("Siemens", "RWTH Aachen", "Germany", 15, 65, 90, "Engineer"),
    ("Bosch", "IIT Madras", "India", 10, 18, 35, "Engineer"),
    ("Bosch", "RWTH Aachen", "Germany", 20, 60, 85, "Engineer"),

    # Pfizer / J&J
    ("Pfizer", "AIIMS Delhi", "India", 5, 15, 25, "Research"),
    ("Johnson & Johnson", "CMC Vellore", "India", 8, 12, 20, "Clinical"),
]


def seed_company_colleges():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # Ensure table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS company_top_colleges (
            id TEXT PRIMARY KEY,
            company_id TEXT,
            college_name TEXT,
            country TEXT,
            offers_per_year INTEGER,
            avg_package_lpa REAL,
            highest_package_lpa REAL,
            preferred_role TEXT,
            year INTEGER,
            source_url TEXT
        )
    """)

    # Get company IDs
    cur.execute("SELECT id, company_name FROM company_intel")
    companies = {name: cid for cid, name in cur.fetchall()}

    inserted = 0
    for (comp, college, country, offers, avg, high, role) in COMPANY_COLLEGE_MAP:
        if comp not in companies:
            continue
        cid = companies[comp]
        row_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO company_top_colleges
            (id, company_id, college_name, country, offers_per_year,
             avg_package_lpa, highest_package_lpa, preferred_role,
             year, source_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (row_id, cid, college, country, offers, avg, high, role,
              2024, "placement report"))
        inserted += 1

    conn.commit()
    conn.close()
    print(f"Company-College links inserted: {inserted}")


# ============================================================
# DUAL MATCH — Student → University → Company
# ============================================================
def dual_match(student_profile, university_name, company_name):
    """
    End-to-end: Can this student go to this university, then get hired by this company?
    """
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    result = {
        "university_match": None,
        "company_hire_possible": None,
        "overall_score": 0,
        "pathway": [],
    }

    # 1. University match
    cur.execute("""
        SELECT id, cutoff_percentile, placement_pct, avg_package_lpa,
               tuition_annual_inr, rank_qs
        FROM university_intel WHERE university_name LIKE ?
        LIMIT 1
    """, (f"%{university_name}%",))
    uni = cur.fetchone()

    if not uni:
        result["pathway"].append(f"❌ University {university_name} not in intel")
        conn.close()
        return result

    uni_id, cutoff, placement, avg_pkg, tuition, rank = uni

    student_pct = student_profile.get("marks_percentile", 0)
    student_budget = student_profile.get("budget_annual_inr", 0)

    # Uni eligibility
    if student_pct >= cutoff:
        uni_score = 30
        result["pathway"].append(f"✅ University eligible ({student_pct}% >= {cutoff}%)")
    else:
        uni_score = 0
        result["pathway"].append(f"❌ University cutoff not met ({student_pct}% < {cutoff}%)")

    if student_budget >= tuition:
        uni_score += 10
        result["pathway"].append(f"✅ Budget OK (₹{student_budget} >= ₹{tuition})")
    else:
        result["pathway"].append(f"⚠️ Budget gap (₹{student_budget} < ₹{tuition})")

    result["university_match"] = {
        "name": university_name,
        "cutoff": cutoff,
        "placement_pct": placement,
        "avg_package_lpa": avg_pkg,
        "qs_rank": rank,
        "score": uni_score,
    }

    # 2. Company hire possible
    cur.execute("SELECT id, company_name, hiring_cgpa_min, growth_score FROM company_intel WHERE company_name LIKE ? LIMIT 1",
                (f"%{company_name}%",))
    comp = cur.fetchone()

    if not comp:
        result["pathway"].append(f"❌ Company {company_name} not in intel")
        conn.close()
        return result

    comp_id, comp_name, cgpa_min, growth = comp

    # Student CGPA
    student_cgpa = student_profile.get("cgpa", 0)
    student_skills = set(s.lower() for s in student_profile.get("skills", []))

    comp_score = 0
    if student_cgpa >= cgpa_min:
        comp_score += 20
        result["pathway"].append(f"✅ CGPA OK ({student_cgpa} >= {cgpa_min})")
    else:
        result["pathway"].append(f"❌ CGPA low ({student_cgpa} < {cgpa_min})")

    # Is this company hiring from this university?
    cur.execute("""
        SELECT offers_per_year, avg_package_lpa, preferred_role
        FROM company_top_colleges
        WHERE company_id=? AND LOWER(college_name) LIKE ?
        LIMIT 1
    """, (comp_id, f"%{university_name.split()[0].lower()}%"))
    hire = cur.fetchone()

    if hire:
        offers, cmp_avg, role = hire
        comp_score += 20
        result["pathway"].append(f"✅ Company hires from this university: {offers} offers/yr, {role}")
        result["expected_package_lpa"] = cmp_avg
    else:
        result["pathway"].append(f"⚠️ No direct hiring link found")

    result["company_hire_possible"] = {
        "name": comp_name,
        "min_cgpa": cgpa_min,
        "growth_score": growth,
        "score": comp_score,
    }

    # Overall
    result["overall_score"] = uni_score + comp_score

    conn.close()
    return result


def demo():
    print("\n" + "=" * 80)
    print("DUAL MATCH DEMO — Student → University → Company")
    print("=" * 80)

    student = {
        "name": "Rajesh Kumar",
        "marks_percentile": 99.5,
        "cgpa": 8.2,
        "budget_annual_inr": 250000,
        "skills": ["python", "dsa", "system design"],
    }

    print(f"\nStudent: {student['name']}")
    print(f"  Marks: {student['marks_percentile']}% percentile")
    print(f"  CGPA: {student['cgpa']}")
    print(f"  Budget: ₹{student['budget_annual_inr']:,}/year")
    print(f"  Skills: {student['skills']}")

    # Try 3 pathways
    pathways = [
        ("IIT Bombay", "Google"),
        ("IIT Madras", "Amazon"),
        ("BITS Pilani", "Microsoft"),
    ]

    for uni, comp in pathways:
        print("\n" + "-" * 80)
        print(f"PATHWAY: {uni} → {comp}")
        print("-" * 80)
        result = dual_match(student, uni, comp)
        print(f"\nOverall Score: {result['overall_score']}/80")
        print("Pathway:")
        for step in result["pathway"]:
            print(f"  {step}")
        if "expected_package_lpa" in result:
            print(f"\n💰 Expected package: ₹{result['expected_package_lpa']}L")


def report_links():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    print("\n" + "=" * 80)
    print("COMPANY → COLLEGE HIRING SUMMARY")
    print("=" * 80)

    cur.execute("""
        SELECT ci.company_name, COUNT(DISTINCT ctc.college_name) as colleges,
               SUM(ctc.offers_per_year) as total_offers,
               AVG(ctc.avg_package_lpa) as avg_pkg
        FROM company_intel ci
        JOIN company_top_colleges ctc ON ctc.company_id = ci.id
        GROUP BY ci.company_name
        ORDER BY total_offers DESC
    """)
    print(f"\n{'Company':25} {'Colleges':9} {'Offers/Yr':10} {'Avg LPA':8}")
    print("-" * 80)
    for n, c, o, a in cur.fetchall():
        print(f"{str(n)[:25]:25} {c:9} {o:10} ₹{a:.1f}L")

    conn.close()


if __name__ == "__main__":
    print("=" * 80)
    print("DUAL MATCH + COMPANY-COLLEGE LINK")
    print("=" * 80)
    seed_company_colleges()
    report_links()
    demo()
    print("\nDone.")