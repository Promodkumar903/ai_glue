"""Add source_tier column to verified_jobs + set tiers"""
import sqlite3, os

DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ai_glue.db")

def main():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    
    # 1. Add column if not exists
    try:
        cur.execute("ALTER TABLE verified_jobs ADD COLUMN source_tier INTEGER DEFAULT 3")
        print("[OK] Added source_tier column")
    except sqlite3.OperationalError as e:
        print(f"[SKIP] Column already exists: {e}")
    
    # 2. Set Tier 1 for government/official sources
    cur.execute("""UPDATE verified_jobs SET source_tier=1 
        WHERE job_url LIKE '%arbeitsagentur.de%' 
        OR job_url LIKE '%eures%' 
        OR job_url LIKE '%beoe.gov.pk%'""")
    tier1_count = cur.rowcount
    print(f"[OK] Tier 1 (govt/official): {tier1_count} jobs")
    
    # 3. Set Tier 3 for aggregators
    cur.execute("""UPDATE verified_jobs SET source_tier=3 
        WHERE job_url LIKE '%bayt.com%' 
        OR job_url LIKE '%naukrigulf.com%' 
        OR job_url LIKE '%arbeitnow%'""")
    tier3_count = cur.rowcount
    print(f"[OK] Tier 3 (aggregator): {tier3_count} jobs")
    
    # 4. Rest as Tier 2 (cross-verified)
    cur.execute("UPDATE verified_jobs SET source_tier=2 WHERE source_tier IS NULL OR source_tier=0")
    tier2_count = cur.rowcount
    print(f"[OK] Tier 2 (cross-verified): {tier2_count} jobs")
    
    conn.commit()
    
    # 5. Show summary
    print()
    print("=" * 50)
    print("SUMMARY")
    print("=" * 50)
    for tier, label in [(1, "Tier 1 - Official"), (2, "Tier 2 - Verified"), (3, "Tier 3 - Aggregator")]:
        count = cur.execute("SELECT COUNT(*) FROM verified_jobs WHERE source_tier=?", (tier,)).fetchone()[0]
        print(f"  {label:<25} {count:>6} jobs")
    
    print()
    print("Sample Tier 1 jobs:")
    for r in cur.execute("SELECT company_name, job_title FROM verified_jobs WHERE source_tier=1 LIMIT 3").fetchall():
        print(f"  * {r[0]} - {r[1]}")
    
    print()
    print("Sample Tier 3 jobs:")
    for r in cur.execute("SELECT company_name, job_title FROM verified_jobs WHERE source_tier=3 LIMIT 3").fetchall():
        print(f"  * {r[0]} - {r[1]}")
    
    conn.close()

if __name__ == "__main__":
    main()