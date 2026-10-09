"""
Fetch universities from remaining countries
"""
import requests
import uuid
import sqlite3
from datetime import datetime

DB = "ai_glue.db"
HIPOLABS = "http://universities.hipolabs.com/search"

MORE_COUNTRIES = [
    "Norway", "Finland", "Sweden", "Denmark", "Netherlands",
    "Switzerland", "Austria", "Ireland", "France", "Italy",
    "Spain", "Poland", "Czech Republic", "South Korea",
    "Singapore", "Malaysia", "New Zealand", "Belgium",
    "Portugal", "Hungary",
]


def fetch_country(country):
    print(f"[{country}] fetching...")
    try:
        r = requests.get(f"{HIPOLABS}?country={requests.utils.quote(country)}",
                         timeout=60, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"  FAIL: {e}")
        return []


def save_univ(u):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()

    name = u.get("name") or "UNKNOWN"
    country = u.get("country") or "UNKNOWN"
    url = (u.get("web_pages") or [""])[0] or "UNKNOWN"

    cur.execute("SELECT id FROM study_opportunities WHERE university_name=? AND country=?",
                (name, country))
    if cur.fetchone():
        conn.close()
        return False

    oid = str(uuid.uuid4())
    org_id = str(uuid.uuid4())
    domains = ", ".join(u.get("domains") or [])

    cur.execute("""
        INSERT INTO study_opportunities
        (id, organization_id, type, title, description, status,
         first_seen, last_seen, created_at, updated_at,
         country, university_name, application_url, work_scope)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (oid, org_id, "UNIVERSITY", name, url, "DISCOVERED",
          now, now, now, now, country, name, url, f"Domains: {domains}"))

    # Claims
    for field, value in [("university_name", name), ("country", country),
                          ("application_url", url)]:
        claim_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO study_claims
            (id, study_id, field_name, claimed_value, truth_state,
             source_priority, confidence, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (claim_id, oid, field, str(value), "SUPPORTED", 3, 0.85, now, now))

    conn.commit()
    conn.close()
    return True


if __name__ == "__main__":
    print("=" * 70)
    print("STUDY OIE — FETCH REMAINING COUNTRIES")
    print("=" * 70)

    total = 0
    for country in MORE_COUNTRIES:
        unis = fetch_country(country)
        saved = 0
        for u in unis:
            if save_univ(u):
                saved += 1
        print(f"  Saved {saved} new from {country}")
        total += saved

    print(f"\nTotal new universities: {total}")

    # Apply country policy to new universities
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    print("\nApplying country policies...")
    cur.execute("SELECT country, free_tuition, post_study_work_years FROM country_study_policy")
    for c, free, work in cur.fetchall():
        cur.execute("""
            UPDATE study_opportunities
            SET free_education=?, post_study_work_years=?, part_time_allowed=1
            WHERE country=?
        """, (free, work, c))

    conn.commit()

    # Report
    cur.execute("SELECT country, COUNT(*) FROM study_opportunities GROUP BY country ORDER BY COUNT(*) DESC")
    print("\nUniversities per country:")
    for c, n in cur.fetchall():
        print(f"  {str(c):25} {n}")

    cur.execute("SELECT COUNT(*) FROM study_opportunities")
    print(f"\nTotal: {cur.fetchone()[0]}")
    conn.close()