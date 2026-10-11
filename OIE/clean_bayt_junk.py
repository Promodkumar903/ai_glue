"""
Clean Bayt junk jobs — only keep real job listings.
Bayt real job URL pattern: /en/{country}/jobs/{slug}-{job_id}/
Bayt junk URLs: /company/, /register, /candidate/, /apply/
"""
import sqlite3, os, re

DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ai_glue.db")

# Junk titles (buttons, nav, generic)
JUNK_TITLES = [
    "easy apply", "apply now", "view job", "view details", "read more",
    "register", "sign in", "login", "sign up", "click here",
    "company profile", "see more", "show more", "find out more",
    "job description", "full description", "more info",
]

def is_junk_title(title):
    if not title:
        return True
    t = title.lower().strip()
    if len(t) < 4:
        return True
    for junk in JUNK_TITLES:
        if t == junk or t.startswith(junk):
            return True
    return False

def is_real_job_url(url):
    """Bayt real job URL: /en/{country}/jobs/{slug}-{number}/"""
    if not url:
        return False
    url_lower = url.lower()
    
    # Reject known junk patterns
    junk_patterns = ["/company/", "/register", "/candidate/", "/apply/",
                     "/profile/", "/login", "/signup", "/about", "/help",
                     "/cv/", "/search?"]
    for p in junk_patterns:
        if p in url_lower:
            return False
    
    # Real job URL must have /jobs/ followed by slug-number
    if re.search(r"/jobs/[a-z0-9\-]+-\d+/?", url_lower):
        return True
    
    return False

def main():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    
    # Get all Bayt jobs
    rows = cur.execute("""
        SELECT id, job_title, job_url FROM verified_jobs
        WHERE ats_platform = 'bayt_com' OR company_name LIKE '%Bayt%'
    """).fetchall()
    
    print(f"Total Bayt jobs: {len(rows)}")
    
    to_delete = []
    for job_id, title, url in rows:
        if is_junk_title(title) or not is_real_job_url(url):
            to_delete.append((job_id, title, url))
    
    print(f"Junk jobs to delete: {len(to_delete)}")
    print()
    print("Sample junk jobs (first 10):")
    for job_id, title, url in to_delete[:10]:
        print(f"  [{title[:40]}]  {url[:70]}")
    
    # Delete from verified_jobs
    if to_delete:
        ids = [j[0] for j in to_delete]
        placeholders = ",".join(["?"] * len(ids))
        cur.execute(f"DELETE FROM verified_jobs WHERE id IN ({placeholders})", ids)
        print()
        print(f"[OK] Deleted {cur.rowcount} junk jobs from verified_jobs")
    
    # Also clean from scraped_company_jobs
    scraped_rows = cur.execute("""
        SELECT id, job_title, job_url FROM scraped_company_jobs
        WHERE ats_platform = 'bayt_com'
    """).fetchall()
    
    to_delete_scraped = []
    for s_id, title, url in scraped_rows:
        if is_junk_title(title) or not is_real_job_url(url):
            to_delete_scraped.append(s_id)
    
    if to_delete_scraped:
        placeholders = ",".join(["?"] * len(to_delete_scraped))
        cur.execute(f"DELETE FROM scraped_company_jobs WHERE id IN ({placeholders})", to_delete_scraped)
        print(f"[OK] Deleted {cur.rowcount} junk jobs from scraped_company_jobs")
    
    conn.commit()
    
    # Final stats
    print()
    print("=" * 60)
    total_verified = cur.execute("SELECT COUNT(*) FROM verified_jobs").fetchone()[0]
    total_bayt = cur.execute("SELECT COUNT(*) FROM verified_jobs WHERE ats_platform='bayt_com'").fetchone()[0]
    print(f"Total verified_jobs: {total_verified}")
    print(f"Bayt jobs remaining: {total_bayt}")
    print()
    print("Remaining Bayt sample:")
    for r in cur.execute("SELECT job_title, job_url FROM verified_jobs WHERE ats_platform='bayt_com' LIMIT 8").fetchall():
        print(f"  {r[0][:50]:50}  {r[1][:60]}")
    
    conn.close()

if __name__ == "__main__":
    main()