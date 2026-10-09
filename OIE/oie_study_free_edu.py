"""
Study OIE — Free Education Countries + Policy Data
Real policy data for international students (2025-26)
"""
import sqlite3
import uuid
from datetime import datetime

DB = "ai_glue.db"

# Country-level study policy data
# (country, free_tuition, avg_tuition_usd, post_study_work_years,
#  part_time_hours, pr_possible, language, notes)
COUNTRY_POLICY = [
    ("Germany", 1, 500, 18, 20, 1, "English/German",
     "Free tuition at public universities. 18-month post-study work visa. Path to PR."),
    ("Norway", 1, 0, 12, 20, 1, "Norwegian/English",
     "Free tuition for all (including non-EU) at public universities."),
    ("Finland", 0, 12000, 24, 25, 1, "English/Finnish",
     "Tuition for non-EU but generous scholarships. 2-year post-study."),
    ("Sweden", 0, 15000, 12, 20, 1, "English/Swedish",
     "Tuition for non-EU. Strong scholarships. 1-year post-study."),
    ("Denmark", 0, 14000, 24, 20, 1, "English/Danish",
     "Tuition for non-EU. 2-year post-study work permit."),
    ("Switzerland", 0, 1500, 6, 15, 0, "English/German/French",
     "Low tuition even for non-EU. Limited post-study work."),
    ("Austria", 1, 1500, 12, 20, 1, "German/English",
     "Low tuition for EU; higher for non-EU. Post-study possible."),
    ("Iceland", 1, 700, 6, 15, 0, "Icelandic/English",
     "Free tuition at public universities."),
    ("United Kingdom", 0, 30000, 24, 20, 0, "English",
     "High tuition. 2-year Graduate Route visa (since 2021)."),
    ("Canada", 0, 25000, 36, 20, 1, "English/French",
     "Tuition moderate. 3-year PGWP. Strong PR pathway."),
    ("United States", 0, 40000, 12, 20, 0, "English",
     "Highest tuition. 1-year OPT (3 for STEM). H1B lottery."),
    ("Australia", 0, 35000, 24, 40, 1, "English",
     "High tuition. 2-4 year post-study work. PR pathway."),
    ("Japan", 0, 5000, 24, 28, 1, "Japanese/English",
     "Low tuition. MEXT scholarships. Path to PR."),
    ("South Korea", 0, 6000, 24, 20, 0, "Korean/English",
     "Low tuition. Strong scholarships. Limited PR."),
    ("France", 0, 5000, 12, 20, 0, "French/English",
     "Low tuition at public universities. Post-study possible."),
    ("Netherlands", 0, 15000, 12, 16, 1, "English/Dutch",
     "Tuition moderate. 1-year orientation year for job search."),
    ("Ireland", 0, 25000, 24, 20, 0, "English",
     "Tuition moderate. 2-year post-study (Stamp 1G)."),
    ("New Zealand", 0, 25000, 36, 20, 1, "English",
     "3-year post-study work. PR pathway."),
    ("Singapore", 0, 20000, 12, 16, 0, "English",
     "Moderate tuition. Strong job market. Limited PR."),
    ("Malaysia", 0, 5000, 6, 20, 0, "English/Malay",
     "Low tuition. Popular for UK/Australia twinning."),
]


def ensure_country_policy_table():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS country_study_policy (
            country TEXT PRIMARY KEY,
            free_tuition INTEGER,
            avg_tuition_usd REAL,
            post_study_work_years INTEGER,
            part_time_hours_per_week INTEGER,
            pr_possible INTEGER,
            language TEXT,
            notes TEXT,
            updated_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def seed_policies():
    ensure_country_policy_table()
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    inserted = 0

    for (country, free, avg_t, work_yrs, pt_hours, pr, lang, notes) in COUNTRY_POLICY:
        cur.execute("SELECT country FROM country_study_policy WHERE country=?", (country,))
        if cur.fetchone():
            cur.execute("""
                UPDATE country_study_policy
                SET free_tuition=?, avg_tuition_usd=?, post_study_work_years=?,
                    part_time_hours_per_week=?, pr_possible=?, language=?, notes=?,
                    updated_at=?
                WHERE country=?
            """, (free, avg_t, work_yrs, pt_hours, pr, lang, notes, now, country))
        else:
            cur.execute("""
                INSERT INTO country_study_policy
                (country, free_tuition, avg_tuition_usd, post_study_work_years,
                 part_time_hours_per_week, pr_possible, language, notes, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (country, free, avg_t, work_yrs, pt_hours, pr, lang, notes, now))
            inserted += 1

    conn.commit()
    conn.close()
    print(f"Policies inserted: {inserted}")
    print(f"Total policies: {len(COUNTRY_POLICY)}")


def update_universities():
    """Update study_opportunities with country-level policy data"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    print("\nUpdating universities with country policy...")
    for (country, free, avg_t, work_yrs, pt_hours, pr, lang, _) in COUNTRY_POLICY:
        cur.execute("""
            UPDATE study_opportunities
            SET free_education = ?,
                post_study_work_years = ?,
                part_time_allowed = 1
            WHERE country = ?
        """, (free, work_yrs, country))
        print(f"  {country:20} : {cur.rowcount} universities")

    conn.commit()
    conn.close()


def report():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    print("\n" + "=" * 70)
    print("FREE EDUCATION COUNTRIES")
    print("=" * 70)
    cur.execute("""
        SELECT country, avg_tuition_usd, post_study_work_years, pr_possible
        FROM country_study_policy
        WHERE free_tuition = 1
        ORDER BY country
    """)
    for c, t, w, pr in cur.fetchall():
        pr_flag = "Yes" if pr else "No"
        print(f"  {c:20} Tuition: ${t:>6} | Post-study: {w}mo | PR: {pr_flag}")

    print("\n" + "=" * 70)
    print("TOP POST-STUDY WORK COUNTRIES")
    print("=" * 70)
    cur.execute("""
        SELECT country, post_study_work_years, pr_possible
        FROM country_study_policy
        ORDER BY post_study_work_years DESC LIMIT 8
    """)
    for c, w, pr in cur.fetchall():
        pr_flag = "Yes" if pr else "No"
        print(f"  {c:20} {w} months | PR: {pr_flag}")

    print("\n" + "=" * 70)
    print("UNIVERSITY STATS")
    print("=" * 70)
    cur.execute("SELECT COUNT(*) FROM study_opportunities WHERE free_education=1")
    print(f"Free education universities: {cur.fetchone()[0]}")
    cur.execute("""
        SELECT country, COUNT(*) FROM study_opportunities
        WHERE free_education=1 GROUP BY country
    """)
    for c, n in cur.fetchall():
        print(f"  {c:20} {n}")

    conn.close()


if __name__ == "__main__":
    print("=" * 70)
    print("STUDY OIE — FREE EDUCATION + COUNTRY POLICY")
    print("=" * 70)
    seed_policies()
    update_universities()
    report()
    print("\nDone.")