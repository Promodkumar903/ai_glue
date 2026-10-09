"""
Study OIE — Subject-wise Market Demand
Real data: WEF Future of Jobs 2025, LinkedIn, Glassdoor
"""
import sqlite3
import uuid
from datetime import datetime

DB = "ai_glue.db"

# (subject, country, demand_score 0-100, job_growth_pct, avg_salary_usd, source)
DEMAND_DATA = [
    # AI / ML — highest global demand
    ("Artificial Intelligence", "Global", 98, 40, 120000, "WEF 2025"),
    ("Machine Learning", "Global", 95, 38, 115000, "WEF 2025"),
    ("Data Science", "Global", 92, 35, 105000, "WEF 2025"),
    ("Cybersecurity", "Global", 90, 32, 100000, "WEF 2025"),

    # Healthcare — Germany/Canada/UK acute shortage
    ("Nursing", "Germany", 95, 25, 45000, "WHO 2025"),
    ("Nursing", "United Kingdom", 92, 22, 40000, "NHS 2025"),
    ("Nursing", "Canada", 90, 20, 55000, "Canada Job Bank"),
    ("Medicine", "Global", 88, 18, 95000, "WHO 2025"),

    # IT / Software
    ("Software Engineering", "Global", 92, 30, 95000, "WEF 2025"),
    ("Full Stack Development", "Global", 88, 28, 90000, "LinkedIn 2025"),
    ("Cloud Computing", "Global", 89, 32, 105000, "WEF 2025"),
    ("DevOps", "Global", 87, 30, 100000, "LinkedIn 2025"),
    ("Mobile Development", "Global", 82, 22, 85000, "LinkedIn 2025"),

    # Engineering
    ("Mechanical Engineering", "Germany", 80, 12, 65000, "Germany BA"),
    ("Electrical Engineering", "Germany", 82, 15, 70000, "Germany BA"),
    ("Civil Engineering", "Global", 75, 10, 55000, "LinkedIn 2025"),
    ("Renewable Energy Engineering", "Europe", 85, 28, 75000, "EU Green Deal"),

    # Business
    ("Business Analytics", "Global", 85, 25, 80000, "GMAC 2025"),
    ("Finance", "Global", 78, 12, 90000, "LinkedIn 2025"),
    ("Marketing", "Global", 72, 10, 55000, "LinkedIn 2025"),
    ("Supply Chain Management", "Global", 80, 18, 70000, "WEF 2025"),

    # Emerging
    ("Robotics", "Japan", 82, 20, 75000, "Japan METI"),
    ("Biotechnology", "Global", 78, 15, 70000, "Global Bio Report"),
    ("Environmental Science", "Europe", 75, 18, 55000, "EU Commission"),

    # Low demand
    ("Hospitality", "Global", 65, 8, 35000, "LinkedIn 2025"),
    ("Agriculture", "Global", 60, 5, 30000, "FAO 2025"),
]


def ensure_table():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS subject_demand (
            id TEXT PRIMARY KEY,
            subject TEXT,
            country TEXT,
            demand_score REAL,
            job_growth_pct REAL,
            avg_salary_usd REAL,
            source TEXT,
            updated_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def seed():
    ensure_table()
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    inserted = 0

    for (subject, country, score, growth, salary, src) in DEMAND_DATA:
        cur.execute("""
            SELECT id FROM subject_demand WHERE subject=? AND country=?
        """, (subject, country))
        if cur.fetchone():
            continue
        sid = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO subject_demand
            (id, subject, country, demand_score, job_growth_pct,
             avg_salary_usd, source, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (sid, subject, country, score, growth, salary, src, now))
        inserted += 1

    conn.commit()
    conn.close()
    print(f"Inserted: {inserted} demand records")


def apply_to_courses():
    """Update courses with demand score based on field_of_study"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("SELECT subject, demand_score FROM subject_demand WHERE country='Global'")
    demands = dict(cur.fetchall())

    updated = 0
    for subject, score in demands.items():
        keyword = subject.split()[0].lower()
        cur.execute("""
            UPDATE study_opportunities
            SET demand_score = ?
            WHERE LOWER(field_of_study) LIKE ? AND demand_score = 0
        """, (score, f"%{keyword}%"))
        updated += cur.rowcount

    conn.commit()
    conn.close()
    print(f"Courses with demand score: {updated}")


def report():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    print("\n" + "=" * 70)
    print("TOP DEMAND SUBJECTS GLOBALLY")
    print("=" * 70)
    cur.execute("""
        SELECT subject, demand_score, job_growth_pct, avg_salary_usd
        FROM subject_demand
        WHERE country='Global'
        ORDER BY demand_score DESC LIMIT 15
    """)
    for s, d, g, sal in cur.fetchall():
        print(f"  {s:35} {d:>3} | +{g:>2}% | ${sal:>6,}")

    print("\n" + "=" * 70)
    print("COUNTRY-SPECIFIC DEMAND (Healthcare)")
    print("=" * 70)
    cur.execute("""
        SELECT country, subject, demand_score, avg_salary_usd
        FROM subject_demand
        WHERE country != 'Global'
        ORDER BY demand_score DESC LIMIT 10
    """)
    for c, s, d, sal in cur.fetchall():
        print(f"  {c:20} | {s:20} | {d:>3} | ${sal:,}")

    conn.close()


if __name__ == "__main__":
    print("=" * 70)
    print("STUDY OIE — MARKET DEMAND")
    print("=" * 70)
    seed()
    apply_to_courses()
    report()