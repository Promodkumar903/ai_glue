"""
Study OIE — Schema for Universities + Courses + Seats + Scholarships
"""
import sqlite3

DB = "ai_glue.db"


def create_tables():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # Main study opportunities table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS study_opportunities (
            id TEXT PRIMARY KEY,
            organization_id TEXT,
            type TEXT,
            title TEXT,
            description TEXT,
            status TEXT DEFAULT 'DISCOVERED',
            first_seen TEXT,
            last_seen TEXT,
            created_at TEXT,
            updated_at TEXT,
            country TEXT,
            city TEXT,
            university_name TEXT,
            course_name TEXT,
            degree_level TEXT,
            field_of_study TEXT,
            duration_months INTEGER,
            tuition_fee REAL,
            currency TEXT,
            language TEXT,
            intake TEXT,
            deadline TEXT,
            seats_available INTEGER,
            seats_filled INTEGER,
            requirements TEXT,
            application_url TEXT,
            work_scope TEXT
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_study_country ON study_opportunities(country)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_study_degree ON study_opportunities(degree_level)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_study_status ON study_opportunities(status)")

    # Study claims — reuse same pattern as jobs
    cur.execute("""
        CREATE TABLE IF NOT EXISTS study_claims (
            id TEXT PRIMARY KEY,
            study_id TEXT NOT NULL,
            field_name TEXT NOT NULL,
            claimed_value TEXT,
            truth_state TEXT DEFAULT 'UNKNOWN',
            source_priority INTEGER DEFAULT 4,
            confidence REAL DEFAULT 0.0,
            created_at TEXT,
            updated_at TEXT
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sclaims_study ON study_claims(study_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sclaims_field ON study_claims(field_name)")

    # Study evidence
    cur.execute("""
        CREATE TABLE IF NOT EXISTS study_evidence (
            id TEXT PRIMARY KEY,
            claim_id TEXT NOT NULL,
            source_id TEXT,
            captured_at TEXT,
            hash TEXT,
            confidence REAL,
            freshness_days INTEGER,
            valid_until TEXT
        )
    """)

    # Student profile (for matching)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS student_profiles_oie (
            user_id TEXT PRIMARY KEY,
            education_level TEXT,
            field_of_study TEXT,
            gpa REAL,
            ielts REAL,
            toefl REAL,
            budget_usd REAL,
            target_countries TEXT,
            target_degree TEXT,
            preferred_intake TEXT,
            work_experience_years INTEGER,
            updated_at TEXT
        )
    """)

    # Study matching scores
    cur.execute("""
        CREATE TABLE IF NOT EXISTS study_match_scores (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            study_id TEXT,
            score REAL,
            eligible INTEGER,
            blocking_reasons TEXT,
            breakdown TEXT,
            computed_at TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("OK: Study OIE tables created")
    print("  - study_opportunities")
    print("  - study_claims")
    print("  - study_evidence")
    print("  - student_profiles_oie")
    print("  - study_match_scores")


def verify():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'study_%'")
    tables = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'student_%'")
    tables += [r[0] for r in cur.fetchall()]
    conn.close()

    print("\nTables present:")
    for t in sorted(tables):
        print(f"  ✓ {t}")


if __name__ == "__main__":
    print("=" * 60)
    print("STUDY OIE — SCHEMA SETUP")
    print("=" * 60)
    create_tables()
    verify()
    print("\nDone.")