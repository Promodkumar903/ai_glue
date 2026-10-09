"""
OIE Real Jobs — Arbeitnow (Germany) + Remotive (Remote)
With work_scope, contract_type, duration
"""
import os
import json
import uuid
import sqlite3
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
DB = "ai_glue.db"

SOURCE_TIERS = {"GOV": 1, "EMPLOYER": 2, "AGENCY": 3, "API": 3, "PORTAL": 4}


def fetch_arbeitnow(limit=30):
    print("[Arbeitnow] Fetching Germany jobs...")
    r = requests.get("https://www.arbeitnow.com/api/job-board-api",
                     timeout=60, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    jobs = r.json().get("data", [])[:limit]
    print(f"  Got {len(jobs)} jobs")
    return [("arbeitnow", j) for j in jobs]


def fetch_remotive(limit=30):
    print("[Remotive] Fetching remote jobs...")
    r = requests.get("https://remotive.com/api/remote-jobs",
                     timeout=60, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    jobs = r.json().get("jobs", [])[:limit]
    print(f"  Got {len(jobs)} jobs")
    return [("remotive", j) for j in jobs]


def extract_arbeitnow(raw):
    desc = (raw.get("description") or "").strip()
    return {
        "title": raw.get("title") or "UNKNOWN",
        "country": "Germany",
        "city": raw.get("location") or "UNKNOWN",
        "salary": 0,
        "currency": "EUR",
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
        "work_scope": desc[:500],
        "contract_type": raw.get("job_types", ["FULL_TIME"])[0] if raw.get("job_types") else "FULL_TIME",
        "duration": "PERMANENT",
        "_evidence_text": desc[:1500],
        "_employer": raw.get("company_name") or "UNKNOWN",
    }


def extract_remotive(raw):
    desc = (raw.get("description") or "").strip()
    location = (raw.get("candidate_required_location") or "").lower()
    jtype = (raw.get("job_type") or "full_time").upper().replace("-", "_")
    return {
        "title": raw.get("title") or "UNKNOWN",
        "country": "Remote" if "remote" in location else (raw.get("candidate_required_location") or "UNKNOWN"),
        "city": "UNKNOWN",
        "salary": 0,
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
        "work_scope": desc[:500],
        "contract_type": jtype,
        "duration": "PERMANENT" if jtype == "FULL_TIME" else "CONTRACT",
        "_evidence_text": desc[:1500],
        "_employer": raw.get("company_name") or "UNKNOWN",
    }


EXTRACTORS = {"arbeitnow": extract_arbeitnow, "remotive": extract_remotive}


def build_evidence(extracted):
    text = extracted.get("_evidence_text", "")
    ev = {}
    if extracted.get("title") and extracted["title"] != "UNKNOWN":
        ev["title"] = text[:250] or "from API title field"
    if extracted.get("skills"):
        ev["skills"] = "Tags: " + ", ".join(extracted["skills"][:10])
    if extracted.get("city") and extracted["city"] != "UNKNOWN":
        ev["city"] = f"Location: {extracted['city']}"
    if extracted.get("work_scope"):
        ev["work_scope"] = extracted["work_scope"][:250]
    return ev


def verify_claim(field, value, has_evidence, source_type):
    if value in ("UNKNOWN", None, "", 0, []):
        return "UNKNOWN", 0.0
    if source_type == "API":
        if has_evidence or field in ("title", "country", "application_url"):
            return "SUPPORTED", 0.85
        return "SUPPORTED", 0.70
    if source_type == "GOV" and has_evidence:
        return "CONFIRMED", 0.95
    if not has_evidence:
        return "UNKNOWN", 0.0
    return "SUPPORTED", 0.60


def save_job(source, extracted):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # Duplicate check by URL
    app_url = extracted.get("application_url", "")
    if app_url and app_url != "UNKNOWN":
        cur.execute("SELECT id FROM opportunities WHERE description=?", (app_url,))
        if cur.fetchone():
            conn.close()
            return None

    opp_id = str(uuid.uuid4())
    org_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    cur.execute("""
        INSERT INTO opportunities
        (id, organization_id, type, title, description, status, first_seen, last_seen,
         created_at, updated_at, country, salary, company, location,
         work_scope, contract_type, duration)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        opp_id, org_id, "JOB",
        extracted.get("title", "UNKNOWN"),
        app_url,
        "DISCOVERED",
        now, now, now, now,
        extracted.get("country", ""),
        str(extracted.get("salary", "")),
        extracted.get("_employer", ""),
        extracted.get("city", ""),
        (extracted.get("work_scope") or "")[:500],
        extracted.get("contract_type", "UNKNOWN"),
        extracted.get("duration", "UNKNOWN"),
    ))

    source_tier = SOURCE_TIERS.get(source, 4)
    evidence = build_evidence(extracted)

    fields = [
        "title", "country", "city", "salary", "currency",
        "visa_sponsorship", "accommodation", "airfare", "food",
        "transport", "experience_years", "education", "language",
        "skills", "application_url",
        "work_scope", "contract_type", "duration"
    ]
    for field in fields:
        value = extracted.get(field)
        if value in (None, "", [], 0) and field not in ("title", "country"):
            continue
        has_ev = field in evidence
        truth, conf = verify_claim(field, value, has_ev, source)
        claim_id = str(uuid.uuid4())
        val_str = value if isinstance(value, str) else json.dumps(value)
        cur.execute("""
            INSERT INTO claims
            (id, opportunity_id, field_name, claimed_value, truth_state,
             source_priority, confidence, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (claim_id, opp_id, field, val_str, truth, source_tier, conf, now, now))

        if has_ev:
            ev_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO evidence
                (id, claim_id, source_id, captured_at, hash, confidence,
                 freshness_days, valid_until)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (ev_id, claim_id, source, now, str(hash(str(evidence[field])))[:32],
                  conf, 0, None))

    conn.commit()
    conn.close()
    return opp_id


def run():
    print("=" * 70)
    print("OIE REAL JOBS — Free APIs")
    print("=" * 70)

    all_jobs = []
    try:
        all_jobs += fetch_arbeitnow(30)
    except Exception as e:
        print(f"  Arbeitnow failed: {e}")

    try:
        all_jobs += fetch_remotive(30)
    except Exception as e:
        print(f"  Remotive failed: {e}")

    print(f"\nTotal fetched: {len(all_jobs)} jobs\n")

    saved = 0
    for source, raw in all_jobs:
        try:
            extracted = EXTRACTORS[source](raw)
            result = save_job(source, extracted)
            if result:
                saved += 1
        except Exception as e:
            print(f"  Save fail: {e}")

    print(f"Saved: {saved}")


if __name__ == "__main__":
    run()