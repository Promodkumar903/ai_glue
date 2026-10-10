"""OIE — Verified Jobs Tables Init"""
import sqlite3, os

DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ai_glue.db")

def init():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS verified_jobs (
        id TEXT PRIMARY KEY,
        company_name TEXT NOT NULL,
        job_title TEXT NOT NULL,
        country TEXT NOT NULL,
        region TEXT,
        city TEXT,
        salary_min REAL,
        salary_max REAL,
        salary_currency TEXT,
        free_visa INTEGER DEFAULT 0,
        free_ticket INTEGER DEFAULT 0,
        accommodation INTEGER DEFAULT 0,
        no_commission INTEGER DEFAULT 1,
        job_url TEXT,
        requisition_id TEXT,
        verification_score INTEGER,
        source_agent TEXT,
        status TEXT DEFAULT 'VERIFIED',
        verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS job_evidence (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id TEXT,
        company_url TEXT,
        ats_platform TEXT,
        matched_title TEXT,
        matched_location TEXT,
        matched_requisition_id TEXT,
        match_score INTEGER,
        screenshot_path TEXT,
        verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS agent_blacklist (
        agent_name TEXT PRIMARY KEY,
        agent_email TEXT,
        rejected_count INTEGER DEFAULT 0,
        last_reason TEXT,
        blacklisted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS manual_review_queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        raw_job_json TEXT,
        match_score INTEGER,
        reason TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS company_scan_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT,
        country TEXT,
        region TEXT,
        jobs_found INTEGER,
        scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()
    print(f"✅ Tables created in: {DB}")
    print("   - verified_jobs")
    print("   - job_evidence")
    print("   - agent_blacklist")
    print("   - manual_review_queue")
    print("   - company_scan_log")

if __name__ == "__main__":
    init()