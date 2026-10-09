"""
OIE Refresh — UPSERT all sources with work_scope + contract_type + duration
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
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ============================================================
# FETCHERS
# ============================================================
def fetch_all():
    results = []

    # Arbeitnow
    try:
        print("[Arbeitnow] Fetching...")
        r = requests.get("https://www.arbeitnow.com/api/job-board-api",
                         timeout=60, headers={"User-Agent": "Mozilla/5.0"})
        for j in r.json().get("data", [])[:40]:
            results.append(("arbeitnow", j))
        print(f"  {len(results)} so far")
    except Exception as e:
        print(f"  Arbeitnow FAIL: {e}")

    # Remotive
    try:
        print("[Remotive] Fetching...")
        r = requests.get("https://remotive.com/api/remote-jobs",
                         timeout=60, headers={"User-Agent": "Mozilla/5.0"})
        for j in r.json().get("jobs", [])[:40]:
            results.append(("remotive", j))
        print(f"  {len(results)} so far")
    except Exception as e:
        print(f"  Remotive FAIL: {e}")

    # RemoteOK
    try:
        print("[RemoteOK] Fetching...")
        r = requests.get("https://remoteok.com/api",
                         timeout=60, headers={"User-Agent": "Mozilla/5.0"})
        for j in r.json():
            if isinstance(j, dict) and "position" in j:
                results.append(("remoteok", j))
            if len([x for x in results if x[0] == "remoteok"]) >= 40:
                break
        print(f"  {len(results)} so far")
    except Exception as e:
        print(f"  RemoteOK FAIL: {e}")

    # Himalayas
    try:
        print("[Himalayas] Fetching...")
        r = requests.get("https://himalayas.app/jobs/api",
                         timeout=60, headers={"User-Agent": "Mozilla/5.0"})
        for j in r.json().get("jobs", [])[:40]:
            results.append(("himalayas", j))
        print(f"  {len(results)} so far")
    except Exception as e:
        print(f"  Himalayas FAIL: {e}")

    # Jobicy
    try:
        print("[Jobicy] Fetching...")
        r = requests.get("https://jobicy.com/api/v2/remote-jobs?count=50",
                         timeout=60, headers={"User-Agent": "Mozilla/5.0"})
        for j in r.json().get("jobs", [])[:40]:
            results.append(("jobicy", j))
        print(f"  {len(results)} so far")
    except Exception as e:
        print(f"  Jobicy FAIL: {e}")

    return results


# ============================================================
# NORMALIZERS
# ============================================================
CONTRACT_MAP = {
    "FULL_TIME": "FULL_TIME", "FULL TIME": "FULL_TIME", "FULLTIME": "FULL_TIME",
    "PART_TIME": "PART_TIME", "PART TIME": "PART_TIME",
    "CONTRACT": "CONTRACT", "CONTRACTOR": "CONTRACT",
    "FREELANCE": "FREELANCE", "INTERNSHIP": "INTERNSHIP",
    "TEMPORARY": "TEMPORARY",
}

COUNTRY_MAP = {
    "USA": "United States", "US": "United States",
    "UNITED STATES OF AMERICA": "United States",
    "UK": "United Kingdom", "ENGLAND": "United Kingdom",
    "GREAT BRITAIN": "United Kingdom",
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
                else (raw.get("candidate_required_location") or "UNKNOWN")
            ),
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
            "country": norm_country(
                (raw.get("locationRestrictions") or ["Remote"])[0]
            ),
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
# UPSERT
# ============================================================
def upsert(source, ext):
    if not ext or not ext.get("url") or ext["url"] == "UNKNOWN":
        return "skip"

    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()

    # Check existing
    cur.execute("SELECT id FROM opportunities WHERE description=?", (ext["url"],))
    row = cur.fetchone()

    if row:
        # UPDATE
        cur.execute("""
            UPDATE opportunities
            SET title=?, country=?, location=?, company=?,
                work_scope=?, contract_type=?, duration=?, updated_at=?
            WHERE id=?
        """, (
            ext["title"], ext["country"], ext["city"], ext["company"],
            ext["work_scope"], ext["contract_type"], ext["duration"], now,
            row[0],
        ))
        conn.commit()
        conn.close()
        return "updated"
    else:
        # INSERT
        opp_id = str(uuid.uuid4())
        org_id = str(uuid.uuid4())
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

        # Add claims
        for field, value in ext.items():
            if field in ("url", "company", "work_scope", "contract_type", "duration"):
                continue
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
        return "inserted"


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=" * 70)
    print("OIE REFRESH — UPSERT All Sources")
    print("=" * 70)

    items = fetch_all()
    print(f"\nTotal fetched: {len(items)}\n")

    inserted = updated = skipped = 0
    for source, raw in items:
        try:
            ext = extract(source, raw)
            result = upsert(source, ext)
            if result == "inserted":
                inserted += 1
            elif result == "updated":
                updated += 1
            else:
                skipped += 1
        except Exception as e:
            skipped += 1

    print(f"Inserted: {inserted}")
    print(f"Updated:  {updated}")
    print(f"Skipped:  {skipped}")

    # Report
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM opportunities")
    print(f"\nTotal opportunities: {cur.fetchone()[0]}")
    cur.execute("""
        SELECT COUNT(*) FROM opportunities
        WHERE work_scope IS NOT NULL AND work_scope != ''
    """)
    print(f"With work_scope: {cur.fetchone()[0]}")
    cur.execute("SELECT contract_type, COUNT(*) FROM opportunities GROUP BY contract_type")
    print("\nContract types:")
    for ct, c in cur.fetchall():
        print(f"  {str(ct):15} {c}")
    conn.close()