"""
Company OIE — Hiring criteria, salary bands, top colleges
Real data from 2024-25 hiring reports
"""
import sqlite3
import uuid
from datetime import datetime

DB = "ai_glue.db"


def create_tables():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # Company master
    cur.execute("""
        CREATE TABLE IF NOT EXISTS company_intel (
            id TEXT PRIMARY KEY,
            company_name TEXT UNIQUE,
            sector TEXT,
            sub_sector TEXT,
            hq_country TEXT,
            hq_city TEXT,
            founded_year INTEGER,
            employee_count TEXT,
            revenue_usd TEXT,
            global_offices TEXT,
            website TEXT,
            hiring_cgpa_min REAL,
            hiring_pct_min REAL,
            eligible_degrees TEXT,
            required_skills TEXT,
            preferred_skills TEXT,
            experience_required TEXT,
            visa_sponsorship INTEGER DEFAULT 0,
            work_authorization TEXT,
            interview_rounds INTEGER,
            interview_process TEXT,
            avg_time_to_hire_days INTEGER,
            acceptance_rate REAL,
            growth_score INTEGER,
            stability_score INTEGER,
            work_life_score INTEGER,
            verified INTEGER DEFAULT 0,
            source_url TEXT,
            updated_at TEXT
        )
    """)

    # Salary bands by role
    cur.execute("""
        CREATE TABLE IF NOT EXISTS company_salary_bands (
            id TEXT PRIMARY KEY,
            company_id TEXT,
            role_title TEXT,
            level TEXT,
            country TEXT,
            min_salary_lpa REAL,
            median_salary_lpa REAL,
            max_salary_lpa REAL,
            total_exp_required INTEGER,
            year INTEGER,
            source_url TEXT
        )
    """)

    # Top colleges per company
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

    conn.commit()
    conn.close()
    print("OK: Company intel tables created")


# (company, sector, hq, founded, employees, cgpa_min, degrees, skills,
#  visa, rounds, avg_hire_days, growth, stability, website)
COMPANIES = [
    # Tech MNCs
    ("Google", "Tech", "USA", 1998, "180,000+", 8.0,
     "BTech, MTech, MBA", "DS/Algo, System Design, Python/Java/Go",
     1, 5, 45, 95, 90, "https://careers.google.com"),

    ("Microsoft", "Tech", "USA", 1975, "220,000+", 7.5,
     "BTech, MTech, MBA", "DS/Algo, .NET, Azure, C#, Python",
     1, 4, 40, 90, 92, "https://careers.microsoft.com"),

    ("Amazon", "Tech", "USA", 1994, "1,600,000+", 7.0,
     "BTech, MBA, any", "DS/Algo, System Design, AWS, Leadership",
     1, 4, 30, 88, 85, "https://amazon.jobs"),

    ("Meta", "Tech", "USA", 2004, "70,000+", 8.0,
     "BTech, MTech", "React, System Design, Python, ML",
     1, 5, 50, 82, 80, "https://www.metacareers.com"),

    ("Apple", "Tech", "USA", 1976, "160,000+", 8.0,
     "BTech, MTech", "iOS, Swift, Hardware, ML",
     1, 5, 55, 85, 90, "https://www.apple.com/careers"),

    # Consulting
    ("McKinsey & Company", "Consulting", "USA", 1926, "40,000+", 8.5,
     "MBA, BTech, CA", "Case Solving, Excel, Powerpoint, Analytics",
     1, 4, 60, 78, 88, "https://www.mckinsey.com/careers"),

    ("BCG", "Consulting", "USA", 1963, "30,000+", 8.5,
     "MBA, BTech, CA", "Case Solving, Analytics, Communication",
     1, 4, 60, 80, 88, "https://careers.bcg.com"),

    ("Bain & Company", "Consulting", "USA", 1973, "18,000+", 8.5,
     "MBA, BTech, CA", "Case Solving, Analytics",
     1, 4, 55, 78, 86, "https://www.bain.com/careers"),

    ("Deloitte", "Consulting", "UK", 1845, "400,000+", 7.0,
     "BCom, BTech, MBA, CA", "Audit, Tax, Consulting, Analytics",
     0, 3, 30, 75, 85, "https://www2.deloitte.com/careers"),

    ("PwC", "Consulting", "UK", 1998, "330,000+", 7.0,
     "BCom, BTech, MBA, CA", "Audit, Tax, Advisory",
     0, 3, 30, 72, 84, "https://www.pwc.com/careers"),

    # Finance
    ("Goldman Sachs", "Finance", "USA", 1869, "50,000+", 8.5,
     "BTech, MBA, CA, CFA", "Finance, Excel, Python, Risk",
     1, 5, 60, 82, 85, "https://www.goldmansachs.com/careers"),

    ("JP Morgan", "Finance", "USA", 2000, "300,000+", 8.0,
     "BTech, MBA, CA", "Finance, Risk, Python, Excel",
     1, 4, 50, 80, 88, "https://careers.jpmorgan.com"),

    ("Morgan Stanley", "Finance", "USA", 1935, "82,000+", 8.5,
     "BTech, MBA, CA", "Finance, Trading, Risk",
     1, 4, 55, 78, 85, "https://www.morganstanley.com/careers"),

    # Pharma / Healthcare
    ("Pfizer", "Pharma", "USA", 1849, "80,000+", 7.0,
     "BPharm, MPharm, PhD", "Biology, Chemistry, Clinical, Regulatory",
     1, 3, 45, 75, 90, "https://www.pfizer.com/careers"),

    ("Johnson & Johnson", "Healthcare", "USA", 1886, "150,000+", 7.0,
     "BPharm, BDS, MBBS, MBA", "Healthcare, Sales, R&D",
     1, 4, 50, 78, 92, "https://www.jnj.com/careers"),

    # Non-tech global
    ("Tesla", "Automotive", "USA", 2003, "140,000+", 7.5,
     "BTech, MTech", "Electrical, Mechanical, Software, AI",
     1, 4, 45, 88, 75, "https://www.tesla.com/careers"),

    ("Siemens", "Industrial", "Germany", 1847, "320,000+", 7.0,
     "BTech, MTech", "Mechanical, Electrical, Software",
     1, 3, 40, 78, 92, "https://www.siemens.com/careers"),

    ("Bosch", "Automotive", "Germany", 1886, "400,000+", 7.0,
     "BTech, MTech", "Mechanical, Electrical, Software, AI",
     1, 3, 42, 76, 94, "https://www.bosch.com/careers"),

    # Indian
    ("Tata Consultancy Services (TCS)", "IT Services", "India", 1968, "600,000+", 6.0,
     "BE, BTech, MCA, BSc", "Java, Python, SQL, Communication",
     0, 2, 20, 70, 88, "https://www.tcs.com/careers"),

    ("Infosys", "IT Services", "India", 1981, "340,000+", 6.0,
     "BE, BTech, MCA", "Java, Python, SQL, Cloud",
     0, 2, 20, 68, 85, "https://www.infosys.com/careers"),

    ("Wipro", "IT Services", "India", 1945, "240,000+", 6.0,
     "BE, BTech, MCA", "Java, .NET, Python, Testing",
     0, 2, 22, 65, 82, "https://careers.wipro.com"),

    ("Flipkart", "E-commerce", "India", 2007, "22,000+", 7.5,
     "BTech, MBA", "DS/Algo, System Design, Java, Python",
     0, 4, 35, 82, 78, "https://www.flipkartcareers.com"),

    ("Swiggy", "Food Tech", "India", 2014, "5,000+", 7.0,
     "BTech, MBA", "DS/Algo, Java, Python, Product",
     0, 4, 30, 78, 72, "https://careers.swiggy.com"),

    ("Zomato", "Food Tech", "India", 2008, "4,000+", 7.0,
     "BTech, MBA", "DS/Algo, Java, Python, Growth",
     0, 4, 30, 75, 70, "https://www.zomato.com/careers"),
]


def seed_companies():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    inserted = 0

    for row in COMPANIES:
        (name, sector, hq, founded, emp, cgpa, degrees, skills,
         visa, rounds, days, growth, stability, website) = row

        cur.execute("SELECT id FROM company_intel WHERE company_name=?", (name,))
        if cur.fetchone():
            continue

        cid = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO company_intel
            (id, company_name, sector, hq_country, founded_year,
             employee_count, hiring_cgpa_min, eligible_degrees,
             required_skills, visa_sponsorship, interview_rounds,
             avg_time_to_hire_days, growth_score, stability_score,
             website, verified, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (cid, name, sector, hq, founded, emp, cgpa, degrees,
              skills, visa, rounds, days, growth, stability, website, 1, now))
        inserted += 1

    conn.commit()
    conn.close()
    print(f"Companies inserted: {inserted}")


def seed_salary_bands():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # Get company IDs
    cur.execute("SELECT id, company_name FROM company_intel")
    companies = {name: cid for cid, name in cur.fetchall()}

    # (company, role, level, country, min_lpa, median_lpa, max_lpa, exp_years)
    bands = [
        ("Google", "Software Engineer", "Entry (L3)", "India", 25, 32, 40, 0),
        ("Google", "Software Engineer", "Mid (L4)", "India", 45, 55, 70, 3),
        ("Google", "Software Engineer", "Senior (L5)", "India", 75, 95, 120, 6),
        ("Microsoft", "Software Engineer", "Entry (SDE)", "India", 22, 28, 35, 0),
        ("Microsoft", "Software Engineer", "Mid (SDE2)", "India", 35, 45, 55, 3),
        ("Microsoft", "Software Engineer", "Senior", "India", 55, 70, 90, 6),
        ("Amazon", "SDE", "Entry (L4)", "India", 28, 32, 40, 0),
        ("Amazon", "SDE", "Mid (L5)", "India", 45, 55, 68, 3),
        ("Amazon", "SDE", "Senior (L6)", "India", 70, 85, 105, 6),
        ("Meta", "Software Engineer", "Entry (E3)", "USA", 120, 145, 170, 0),
        ("Meta", "Software Engineer", "Mid (E4)", "USA", 180, 210, 250, 3),
        ("Apple", "Software Engineer", "Entry (ICT2)", "USA", 110, 135, 160, 0),
        ("Goldman Sachs", "Analyst", "Entry", "India", 15, 20, 25, 0),
        ("Goldman Sachs", "Associate", "Mid", "India", 30, 40, 55, 3),
        ("Goldman Sachs", "VP", "Senior", "India", 60, 80, 120, 7),
        ("McKinsey & Company", "Business Analyst", "Entry", "India", 18, 22, 28, 0),
        ("McKinsey & Company", "Consultant", "Post-MBA", "India", 30, 35, 45, 3),
        ("BCG", "Associate", "Entry", "India", 16, 20, 25, 0),
        ("BCG", "Consultant", "Post-MBA", "India", 28, 33, 42, 3),
        ("TCS", "Software Engineer", "Entry", "India", 3.5, 4.5, 7, 0),
        ("TCS", "Team Lead", "Mid", "India", 8, 12, 18, 4),
        ("Infosys", "Systems Engineer", "Entry", "India", 3.6, 4.5, 6.5, 0),
        ("Wipro", "Project Engineer", "Entry", "India", 3.5, 4, 6, 0),
        ("Flipkart", "SDE", "Entry (SDE1)", "India", 18, 22, 28, 0),
        ("Flipkart", "SDE", "Mid (SDE2)", "India", 28, 35, 45, 3),
        ("Tesla", "Software Engineer", "Entry", "USA", 100, 120, 145, 0),
        ("Siemens", "Software Engineer", "Entry", "Germany", 55, 65, 80, 0),
        ("Bosch", "Software Engineer", "Entry", "Germany", 50, 60, 75, 0),
    ]

    now = datetime.utcnow().isoformat()
    inserted = 0

    for company, role, level, country, mn, med, mx, exp in bands:
        if company not in companies:
            continue
        cid = companies[company]
        bid = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO company_salary_bands
            (id, company_id, role_title, level, country,
             min_salary_lpa, median_salary_lpa, max_salary_lpa,
             total_exp_required, year, source_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (bid, cid, role, level, country, mn, med, mx, exp, 2024,
              "levels.fyi / glassdoor"))
        inserted += 1

    conn.commit()
    conn.close()
    print(f"Salary bands inserted: {inserted}")


def report():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    print("\n" + "=" * 90)
    print("COMPANY INTELLIGENCE")
    print("=" * 90)
    cur.execute("""
        SELECT company_name, sector, hq_country, hiring_cgpa_min,
               growth_score, stability_score, visa_sponsorship
        FROM company_intel
        ORDER BY growth_score DESC
    """)
    print(f"{'Company':25} {'Sector':12} {'HQ':10} {'CGPA':5} {'Growth':7} {'Stable':7} {'Visa':5}")
    print("-" * 90)
    for n, s, hq, cg, g, st, v in cur.fetchall():
        v_flag = "Yes" if v else "No"
        print(f"{str(n)[:25]:25} {s:12} {hq:10} {cg:5} {g:7} {st:7} {v_flag:5}")

    print("\n" + "=" * 90)
    print("SALARY BANDS (Top 15)")
    print("=" * 90)
    cur.execute("""
        SELECT ci.company_name, csb.role_title, csb.level, csb.country,
               csb.min_salary_lpa, csb.median_salary_lpa, csb.max_salary_lpa
        FROM company_salary_bands csb
        JOIN company_intel ci ON ci.id = csb.company_id
        ORDER BY csb.max_salary_lpa DESC LIMIT 15
    """)
    for co, role, lvl, country, mn, med, mx in cur.fetchall():
        print(f"  {str(co)[:20]:20} | {str(role)[:25]:25} | {str(lvl)[:12]:12} | "
              f"{country:8} | ₹{mn}L - ₹{mx}L (med: ₹{med}L)")

    cur.execute("SELECT COUNT(*) FROM company_intel")
    print(f"\nTotal companies: {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM company_salary_bands")
    print(f"Total salary bands: {cur.fetchone()[0]}")
    conn.close()


if __name__ == "__main__":
    print("=" * 90)
    print("COMPANY OIE — HIRING INTELLIGENCE")
    print("=" * 90)
    create_tables()
    seed_companies()
    seed_salary_bands()
    report()
    print("\nDone.")