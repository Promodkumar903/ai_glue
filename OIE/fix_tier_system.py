"""
Fix source_tier using ats_platform (not URL pattern).
ats_platform tells us the REAL source of each job.
"""
import sqlite3, os

DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ai_glue.db")

# Source → Tier mapping
# Tier 1 = Official govt/direct company source
# Tier 2 = Cross-verified
# Tier 3 = Aggregator (needs verification)
TIER_MAP = {
    # Tier 1 — Official sources
    "bundesagentur": 1,      # Germany Federal Employment Agency
    "eures": 1,               # EU official
    "beoe": 1,                # Pakistan govt
    "emigrate": 1,            # India govt
    
    # Tier 3 — Aggregators
    "bayt": 3,
    "naukrigulf": 3,
    "arbeitnow": 3,
    "workable": 3,
    "greenhouse": 3,
    "lever": 3,
    "custom": 3,              # Unknown custom scrape
}

def main():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    
    # 1. Add ats_platform column to verified_jobs (if not exists)
    try:
        cur.execute("ALTER TABLE verified_jobs ADD COLUMN ats_platform TEXT")
        print("[OK] Added ats_platform column")
    except Exception:
        print("[SKIP] ats_platform already exists")
    
    # 2. Sync ats_platform from scraped_company_jobs (join on job_url)
    cur.execute("""
        UPDATE verified_jobs
        SET ats_platform = (
            SELECT ats_platform FROM scraped_company_jobs 
            WHERE scraped_company_jobs.job_url = verified_jobs.job_url 
            LIMIT 1
        )
        WHERE ats_platform IS NULL
    """)
    synced = cur.rowcount
    print(f"[OK] Synced ats_platform for {synced} jobs")
    
    # 3. Reset all tiers
    cur.execute("UPDATE verified_jobs SET source_tier = 3")
    
    # 4. Assign tiers based on ats_platform
    for platform, tier in TIER_MAP.items():
        cur.execute("UPDATE verified_jobs SET source_tier = ? WHERE ats_platform = ?", (tier, platform))
        print(f"  {platform:15} -> Tier {tier}: {cur.rowcount} jobs")
    
    conn.commit()
    
    # 5. Show summary
    print()
    print("=" * 60)
    print("TIER SUMMARY")
    print("=" * 60)
    
    for tier, label in [(1, "Tier 1 - Official"), (2, "Tier 2 - Cross-verified"), (3, "Tier 3 - Aggregator")]:
        count = cur.execute("SELECT COUNT(*) FROM verified_jobs WHERE source_tier=?", (tier,)).fetchone()[0]
        print(f"  {label:<30} {count:>6} jobs")
    
    # 6. Sample jobs per tier
    print()
    print("=" * 60)
    print("SAMPLE JOBS")
    print("=" * 60)
    
    for tier, label in [(1, "Tier 1 - OFFICIAL"), (3, "Tier 3 - AGGREGATOR")]:
        print(f"\n{label}:")
        rows = cur.execute(
            "SELECT company_name, job_title, ats_platform FROM verified_jobs WHERE source_tier=? LIMIT 5",
            (tier,)
        ).fetchall()
        for r in rows:
            company = (r[0] or "")[:40]
            title = (r[1] or "")[:50]
            print(f"  [{r[2] or '?'}] {company} - {title}")
    
    # 7. Platform breakdown
    print()
    print("=" * 60)
    print("JOBS BY PLATFORM")
    print("=" * 60)
    rows = cur.execute("""
        SELECT ats_platform, COUNT(*) FROM verified_jobs 
        GROUP BY ats_platform ORDER BY COUNT(*) DESC
    """).fetchall()
    for r in rows:
        print(f"  {(r[0] or 'unknown'):20} {r[1]:>6} jobs")
    
    conn.close()

if __name__ == "__main__":
    main()