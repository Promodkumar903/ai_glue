"""
Study OIE — Extend schema with deep filters
Columns: free_education, has_scholarship, hostel, books, library, etc.
New tables: scholarships, hostels, subject_demand
"""
import sqlite3

DB = "ai_glue.db"


NEW_COLUMNS = [
    ("free_education", "INTEGER DEFAULT 0"),
    ("scholarship_available", "INTEGER DEFAULT 0"),
    ("scholarship_amount_usd", "REAL DEFAULT 0"),
    ("hostel_available", "INTEGER DEFAULT 0"),
    ("hostel_cost_monthly_usd", "REAL DEFAULT 0"),
    ("books_provided", "INTEGER DEFAULT 0"),
    ("library_facility", "INTEGER DEFAULT 0"),
    ("direct_apply", "INTEGER DEFAULT 0"),
    ("sponsor_required", "INTEGER DEFAULT 0"),
    ("part_time_allowed", "INTEGER DEFAULT 0"),
    ("post_study_work_years", "INTEGER DEFAULT 0"),
    ("demand_score", "REAL DEFAULT 0"),
    ("acceptance_rate", "REAL DEFAULT 0"),
    ("ranking_qs", "INTEGER DEFAULT 0"),
]


def extend_schema():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # Add columns
    for col, dtype in NEW_COLUMNS:
        try:
            cur.execute(f"ALTER TABLE study_opportunities ADD COLUMN {col} {dtype}")
            print(f"  + {col}")
        except Exception as e:
            print(f"  = {col} (exists)")

    # Scholarships table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS scholarships (
            id TEXT PRIMARY KEY,
            name TEXT,
            provider TEXT,
            country TEXT,
            amount_usd REAL,
            coverage TEXT,
            subjects TEXT,
            eligibility TEXT,
            deadline TEXT,
            application_url TEXT,
            source_url TEXT,
            verified INTEGER DEFAULT 0,
            created_at TEXT
        )
    """)

    # Hostels table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS hostels (
            id TEXT PRIMARY KEY,
            university_id TEXT,
            name TEXT,
            country TEXT,
            city TEXT,
            monthly_cost_usd REAL,
            deposit_usd REAL,
            room_type TEXT,
            facilities TEXT,
            distance_km REAL,
            contact_url TEXT,
            verified INTEGER DEFAULT 0,
            created_at TEXT
        )
    """)

    # Subject demand table
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

    print("\nOK: schema extended")
    print("  New tables: scholarships, hostels, subject_demand")


def verify():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(study_opportunities)")
    print("\nstudy_opportunities columns:")
    for r in cur.fetchall():
        print(f"  {r[1]:30} {r[2]}")
    conn.close()


if __name__ == "__main__":
    print("=" * 70)
    print("STUDY OIE — SCHEMA EXTEND")
    print("=" * 70)
    extend_schema()
    verify()
    print("\nDone.")