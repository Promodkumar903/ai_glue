"""Scraped company jobs — raw storage table"""
import sqlite3, os

DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ai_glue.db")

def init():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS scraped_company_jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT NOT NULL,
        company_country TEXT,
        company_region TEXT,
        job_title TEXT NOT NULL,
        job_location TEXT,
        job_url TEXT,
        requisition_id TEXT,
        ats_platform TEXT,
        scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(company_name, job_title, job_url)
    )
    """)
    
    cur.execute("CREATE INDEX IF NOT EXISTS idx_scj_company ON scraped_company_jobs(company_name)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_scj_region ON scraped_company_jobs(company_region)")
    
    conn.commit()
    conn.close()
    print(f"✅ Table created: scraped_company_jobs")

if __name__ == "__main__":
    init()