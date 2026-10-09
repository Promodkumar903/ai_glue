"""
OIE More Jobs — RemoteOK + Himalayas + Jobicy
Extracts: title, salary, work_scope, duration, contract_type
"""
import requests
import json
import sqlite3
from oie_real_jobs import save_job


def fetch_remoteok(limit=30):
    print("[RemoteOK] Fetching...")
    try:
        r = requests.get("https://remoteok.com/api", timeout=60,
                         headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        data = r.json()
        jobs = [j for j in data if isinstance(j, dict) and "position" in j][:limit]
        print(f"  Got {len(jobs)} jobs")
        return jobs
    except Exception as e:
        print(f"  FAIL: {e}")
        return []


def fetch_himalayas(limit=30):
    print("[Himalayas] Fetching...")
    try:
        r = requests.get("https://himalayas.app/jobs/api", timeout=60,
                         headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        data = r.json()
        jobs = data.get("jobs", [])[:limit]
        print(f"  Got {len(jobs)} jobs")
        return jobs
    except Exception as e:
        print(f"  FAIL: {e}")
        return []


def fetch_jobicy(limit=30):
    print("[Jobicy] Fetching...")
    try:
        r = requests.get("https://jobicy.com/api/v2/remote-jobs?count=50",
                         timeout=60, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        data = r.json()
        jobs = data.get("jobs", [])[:limit]
        print(f"  Got {len(jobs)} jobs")
        return jobs
    except Exception as e:
        print(f"  FAIL: {e}")
        return []


# ============================================================
# EXTRACTORS — full data with work_scope + duration
# ============================================================
def extract_remoteok(raw):
    desc = (raw.get("description") or "").strip()
    return {
        "title": raw.get("position") or "UNKNOWN",
        "country": raw.get("location") or "Remote",
        "city": "UNKNOWN",
        "salary": int(raw.get("salary_min") or 0),
        "currency": "USD",
        "visa_sponsorship": "UNKNOWN",
        "accommodation": "UNKNOWN",
        "airfare": "UNKNOWN",
        "food": "UNKNOWN",
        "transport": "UNKNOWN",
        "experience_years": 0,
        "education": "UNKNOWN",
        "language": "UNKNOWN",
        "skills": [t.lower() for t in (raw.get("tags") or [])],
        "application_url": raw.get("url") or "UNKNOWN",
        "work_scope": desc[:500],                # description ka first 500 chars
        "contract_type": "FULL_TIME",            # RemoteOK default
        "duration": "PERMANENT",                 # Default
        "_evidence_text": desc[:1500],
        "_employer": raw.get("company") or "UNKNOWN",
    }


def extract_himalayas(raw):
    desc = (raw.get("description") or "").strip()
    return {
        "title": raw.get("title") or "UNKNOWN",
        "country": (raw.get("locationRestrictions") or ["Remote"])[0],
        "city": "UNKNOWN",
        "salary": int(raw.get("minSalary") or 0),
        "currency": "USD",
        "visa_sponsorship": "UNKNOWN",
        "accommodation": "UNKNOWN",
        "airfare": "UNKNOWN",
        "food": "UNKNOWN",
        "transport": "UNKNOWN",
        "experience_years": 0,
        "education": "UNKNOWN",
        "language": "UNKNOWN",
        "skills": (raw.get("categories") or [])[:10],
        "application_url": raw.get("applicationLink") or raw.get("guid") or "UNKNOWN",
        "work_scope": desc[:500],
        "contract_type": raw.get("employmentType") or "FULL_TIME",
        "duration": raw.get("duration") or "PERMANENT",
        "_evidence_text": desc[:1500],
        "_employer": raw.get("companyName") or "UNKNOWN",
    }


def extract_jobicy(raw):
    desc = (raw.get("jobDescription") or raw.get("jobExcerpt") or "").strip()
    # Jobicy provides jobType (full-time, contract, etc)
    jt = raw.get("jobType") or "FULL_TIME"
    if isinstance(jt, list):
        jt = jt[0] if jt else "FULL_TIME"
    jtype = str(jt).upper().replace("-", "_").replace(" ", "_")
    return {
        "title": raw.get("jobTitle") or "UNKNOWN",
        "country": raw.get("jobGeo") or "Remote",
        "city": "UNKNOWN",
        "salary": 0,
        "currency": "USD",
        "visa_sponsorship": "UNKNOWN",
        "accommodation": "UNKNOWN",
        "airfare": "UNKNOWN",
        "food": "UNKNOWN",
        "transport": "UNKNOWN",
        "experience_years": 0,
        "education": raw.get("jobLevel") or "UNKNOWN",
        "language": "UNKNOWN",
        "skills": [],
        "application_url": raw.get("url") or "UNKNOWN",
        "work_scope": desc[:500],
        "contract_type": jtype,
        "duration": "PERMANENT" if jtype == "FULL_TIME" else "CONTRACT",
        "_evidence_text": desc[:1500],
        "_employer": raw.get("companyName") or "UNKNOWN",
    }


SOURCES = [
    ("remoteok", fetch_remoteok, extract_remoteok),
    ("himalayas", fetch_himalayas, extract_himalayas),
    ("jobicy", fetch_jobicy, extract_jobicy),
]


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=" * 70)
    print("OIE MORE JOBS — 3 Sources")
    print("=" * 70)

    total_saved = 0
    for name, fetcher, extractor in SOURCES:
        try:
            jobs = fetcher(30)
            for raw in jobs:
                try:
                    ext = extractor(raw)
                    result = save_job(name, ext)
                    if result:
                        total_saved += 1
                except Exception as e:
                    print(f"    SAVE FAIL: {type(e).__name__}: {e}")
                    break
        except Exception as e:
            print(f"{name} failed: {e}")

    print(f"\nTotal new jobs saved: {total_saved}")

    # Show sample
    print("\n" + "=" * 70)
    print("SAMPLE JOBS (last 10)")
    print("=" * 70)
    conn = sqlite3.connect("ai_glue.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT title, country, company, salary FROM opportunities
        WHERE status='DISCOVERED'
        ORDER BY created_at DESC LIMIT 10
    """)
    for t, c, comp, sal in cur.fetchall():
        print(f"  {str(t)[:50]:50} | {str(c)[:12]:12} | {str(comp)[:20]}")

    cur.execute("SELECT COUNT(*) FROM opportunities")
    print(f"\nTotal opportunities: {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM claims")
    print(f"Total claims: {cur.fetchone()[0]}")
    conn.close()