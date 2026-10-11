"""Sync scraped Gulf jobs to verified_jobs (with proper Tier 3)"""
import sqlite3, os, uuid

DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ai_glue.db")

def main():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    
    # Get Gulf jobs from scraped_company_jobs that aren't in verified_jobs
    rows = cur.execute("""
        SELECT s.company_name, s.company_country, s.company_region, 
               s.job_title, s.job_url, s.ats_platform
        FROM scraped_company_jobs s
        WHERE s.company_region = 'Middle East'
          AND s.job_url NOT IN (SELECT job_url FROM verified_jobs WHERE job_url IS NOT NULL)
    """).fetchall()
    
    print(f"Found {len(rows)} Gulf jobs to sync")
    
    saved = 0
    for r in rows:
        company_name, country, region, job_title, job_url, ats_platform = r
        try:
            cur.execute("""INSERT OR IGNORE INTO verified_jobs 
                (id, company_name, job_title, country, region, job_url, 
                 no_commission, status, verification_score, source_tier, ats_platform)
                VALUES (?, ?, ?, ?, ?, ?, 1, 'VERIFIED', 70, 3, ?)""",
                (str(uuid.uuid4()), company_name, job_title, country, region, 
                 job_url, ats_platform))
            if cur.rowcount > 0:
                saved += 1
        except Exception as e:
            print(f"  X Error: {e}")
    
    conn.commit()
    
    print(f"[OK] Synced {saved} new jobs")
    print()
    
    # Final counts
    total = cur.execute("SELECT COUNT(*) FROM verified_jobs").fetchone()[0]
    print(f"Total verified_jobs: {total}")
    print()
    print("By region:")
    for r in cur.execute("SELECT region, COUNT(*) FROM verified_jobs GROUP BY region").fetchall():
        print(f"  {r[0]:15} {r[1]}")
    print()
    print("By tier:")
    for r in cur.execute("SELECT source_tier, COUNT(*) FROM verified_jobs GROUP BY source_tier").fetchall():
        print(f"  Tier {r[0]}: {r[1]}")
    
    conn.close()

if __name__ == "__main__":
    main()