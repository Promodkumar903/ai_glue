"""
OIE New Only — Sirf NAYE jobs add karo. Purane skip.
Tracks: first_seen, last_seen
"""
import re
import json
import uuid
import sqlite3
import requests
from datetime import datetime

DB = "ai_glue.db"


def strip_html(text):
    if not text:
        return ""
    text = re.sub(r"<script[^>]*>.*?</script>", " ", text, flags=re.DOTALL | re.I)
    text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.DOTALL | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("&nbsp;", " ").replace("&amp;", "&")
    text = text.replace("&#39;", "'").replace("&quot;", '"')
    return re.sub(r"\s+", " ", text).strip()


# ============================================================
# FETCHERS (same as before)
# ============================================================
def fetch_all():
    results = []
    try:
        print("[Arbeitnow]...")
        r = requests.get("https://www.arbeitnow.com/api/job-board-api",
                         timeout=60, headers={"User-Agent": "Mozilla/5.0"})
        for j in r.json().get("data", [])[:50]:
            results.append(("arbeitnow", j))
    except Exception as e:
        print(f"  FAIL: {e}")

    try:
        print("[Remotive]...")
        r = requests.get("https://remotive.com/api/remote-jobs",
                         timeout=60, headers={"User-Agent": "Mozilla/5.0"})
        for j in r.json().get("jobs", [])[:50]:
            results.append(("remotive", j))
    except Exception as e:
        print(f"  FAIL: {e}")

    try:
        print("[RemoteOK]...")
        r = requests.get("https://remoteok.com/api",
                         timeout=60, headers={"User-Agent": "Mozilla/5.0"})
        cnt = 0
        for j in r.json():
            if isinstance(j, dict) and "position" in j:
                results.append(("remoteok", j))
                cnt += 1
                if cnt >= 50:
                    break
    except Exception as e:
        print(f"  FAIL: {e}")

    try:
        print("[Himalayas]...")
        r = requests.get("https://himalayas.app/jobs/api",
                         timeout=60, headers={"User-Agent": "Mozilla/5.0"})
        for j in r.json().get("jobs", [])[:50]:
            results.append(("himalayas", j))
    except Exception as e:
        print(f"  FAIL: {e}")

    try:
        print("[Jobicy]...")
        r = requests.get("https://jobicy.com/api/v2/remote-jobs?count=50",
                         timeout=60, headers={"User-Agent": "Mozilla/5.0"})
        for j in r.json().get("jobs", [])[:50]:
            results.append(("jobicy", j))
    except Exception as e:
        print(f"  FAIL: {e}")

    return results


# ============================================================
# NORMALIZERS
# ============================================================
CONTRACT_MAP = {
    "FULL_TIME": "FULL_TIME", "FULL TIME": "FULL_TIME",
    "PART_TIME": "PART_TIME", "PART TIME": "PART_TIME",
    "CONTRACT": "CONTRACT", "CONTRACTOR": "CONTRACT",
    "FREELANCE": "FREELANCE", "INTERNSHIP": "INTERNSHIP",
}

COUNTRY_MAP = {
    "USA": "United States", "US": "United States",
    "UK": "United Kingdom", "ENGLAND": "United Kingdom",
    "UAE": "United Arab Emirates",
}


def norm_contract(ct):
    if not ct:
        return "UNKNOWN"
    if isinstance(ct, list):
        ct = ct[0] if ct else "UNKNOWN"
    key = str(ct).upper().strip().replace("-", "_").replace(" ", "_")
    return CONTRACT_MAP.get(key.replace("_", " "), CONTRACT_MAP.get(key, "OTHER"))


def norm_country(c):
    if not c:
        return "UNKNOWN"
    c = str(c).strip()
    if "," in c:
        c = c.split(",")[0].strip()
    return COUNTRY_MAP.get(c.upper(), c)


# ============================================================
# EXTRACTORS
# ============================================================
def extract(source, raw):
    if source == "arbeitnow":
        desc = strip_html(raw.get("description") or "")
        return {
            "title": raw.get("title") or "UNKNOWN",
            "country": "Germany",
            "city": raw.get("location") or "UNKNOWN",
            "url": raw.get("url") or "UNKNOWN",
            "company": raw.get("company_name") or "UNKNOWN",
            "work_scope": desc[:800],
            "contract_type": norm_contract(raw.get("job_types") or "FULL_TIME"),
            "duration": "PERMANENT",
            "skills": [t.lower() for t in (raw.get("tags") or [])][:10],
        }
    elif source == "remotive":
        desc = strip_html(raw.get("description") or "")
        location = (raw.get("candidate_required_location") or "").lower()
        return {
            "title": raw.get("title") or "UNKNOWN",
            "country": norm_country(
                "Remote" if "remote" in location
                else (raw.get("candidate_required_location") or "UNKNOWN")),
            "city": "UNKNOWN",
            "url": raw.get("url") or "UNKNOWN",
            "company": raw.get("company_name") or "UNKNOWN",
            "work_scope": desc[:800],
            "contract_type": norm_contract(raw.get("job_type") or "FULL_TIME"),
            "duration": "PERMANENT",
            "skills": [t.lower() for t in (raw.get("tags") or [])][:10],
        }
    elif source == "remoteok":
        desc = strip_html(raw.get("description") or "")
        return {
            "title": raw.get("position") or "UNKNOWN",
            "country": raw.get("location") or "Remote",
            "city": "UNKNOWN",
            "url": raw.get("url") or raw.get("apply_url") or "UNKNOWN",
            "company": raw.get("company") or "UNKNOWN",
            "work_scope": desc[:800],
            "contract_type": "FULL_TIME",
            "duration": "PERMANENT",
            "skills": [t.lower() for t in (raw.get("tags") or [])][:10],
        }
    elif source == "himalayas":
        desc = strip_html(raw.get("description") or "")
        return {
            "title": raw.get("title") or "UNKNOWN",
            "country": norm_country((raw.get("locationRestrictions") or ["Remote"])[0]),
            "city": "UNKNOWN",
            "url": raw.get("applicationLink") or raw.get("guid") or "UNKNOWN",
            "company": raw.get("companyName") or "UNKNOWN",
            "work_scope": desc[:800],
            "contract_type": norm_contract(raw.get("employmentType") or "FULL_TIME"),
            "duration": "PERMANENT",
            "skills": (raw.get("categories") or [])[:10],
        }
    elif source == "jobicy":
        desc = strip_html(raw.get("jobDescription") or raw.get("jobExcerpt") or "")
        jt = raw.get("jobType") or "FULL_TIME"
        return {
            "title": raw.get("jobTitle") or "UNKNOWN",
            "country": norm_country(raw.get("jobGeo") or "Remote"),
            "city": "UNKNOWN",
            "url": raw.get("url") or "UNKNOWN",
            "company": raw.get("companyName") or "UNKNOWN",
            "work_scope": desc[:800],
            "contract_type": norm_contract(jt),
            "duration": "PERMANENT" if "FULL" in str(jt).upper() else "CONTRACT",
            "skills": [],
        }
    return None


# ============================================================
# CHECK: URL already in DB?
# ============================================================
def url_exists(url):
    if not url or url == "UNKNOWN":
        return True  # treat as exists to skip
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT id FROM opportunities WHERE description=?", (url,))
    row = cur.fetchone()
    if row:
        # Update last_seen for existing
        now = datetime.utcnow().isoformat()
        cur.execute("UPDATE opportunities SET last_seen=? WHERE id=?", (now, row[0]))
        conn.commit()
    conn.close()
    return bool(row)


# ============================================================
# INSERT ONLY IF NEW
# ============================================================
def insert_if_new(source, ext):
    if not ext:
        return False

    if url_exists(ext["url"]):
        return False  # SKIP — already in DB

    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    opp_id = str(uuid.uuid4())
    org_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    cur.execute("""
        INSERT INTO opportunities
        (id, organization_id, type, title, description, status,
         first_seen, last_seen, created_at, updated_at,
         country, salary, company, location,
         work_scope, contract_type, duration)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        opp_id, org_id, "JOB",
        ext["title"], ext["url"], "DISCOVERED",
        now, now, now, now,
        ext["country"], "0", ext["company"], ext["city"],
        ext["work_scope"], ext["contract_type"], ext["duration"],
    ))

    # Claims
    for field in ["title", "country", "city", "work_scope",
                  "contract_type", "duration", "skills"]:
        value = ext.get(field)
        if value in (None, "", [], 0, "UNKNOWN"):
            continue
        claim_id = str(uuid.uuid4())
        val_str = value if isinstance(value, str) else json.dumps(value)
        cur.execute("""
            INSERT INTO claims
            (id, opportunity_id, field_name, claimed_value, truth_state,
             source_priority, confidence, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (claim_id, opp_id, field, val_str, "SUPPORTED", 3, 0.75, now, now))

    conn.commit()
    conn.close()
    return True


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=" * 70)
    print("OIE NEW ONLY — Sirf naye jobs")
    print("=" * 70)

    before = 0
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM opportunities")
    before = cur.fetchone()[0]
    conn.close()
    print(f"\nBefore: {before} opportunities\n")

    items = fetch_all()
    print(f"\nFetched: {len(items)} from all sources")

    new_count = 0
    old_count = 0
    for source, raw in items:
        try:
            ext = extract(source, raw)
            if insert_if_new(source, ext):
                new_count += 1
            else:
                old_count += 1
        except Exception as e:
            old_count += 1

    print(f"\n{'='*70}")
    print(f"NEW jobs inserted: {new_count}")
    print(f"Already existing (skipped): {old_count}")
    print(f"{'='*70}")

    # Report
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM opportunities")
    after = cur.fetchone()[0]
    print(f"\nAfter: {after} opportunities")
    print(f"Net new: {after - before}")

    # New jobs preview
    if new_count > 0:
        print(f"\nNew jobs added:")
        cur.execute("""
            SELECT title, country, company FROM opportunities
            ORDER BY created_at DESC LIMIT 10
        """)
        for t, c, co in cur.fetchall():
            print(f"  {str(t)[:55]:55} | {str(c)[:15]:15} | {str(co)[:20]}")

    conn.close()