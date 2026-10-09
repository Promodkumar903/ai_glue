"""
Study OIE — Fetch universities from Hipolabs API (free, 10,000+)
"""
import requests
import json
import uuid
import sqlite3
from datetime import datetime

DB = "ai_glue.db"
HIPOLABS_API = "http://universities.hipolabs.com/search"


def fetch_universities(country=None):
    """Fetch universities. country=None means all (10000+)."""
    if country:
        print(f"[Hipolabs] Fetching universities for {country}...")
        url = f"{HIPOLABS_API}?country={requests.utils.quote(country)}"
    else:
        print("[Hipolabs] Fetching ALL universities (this may take 30s)...")
        url = HIPOLABS_API

    try:
        r = requests.get(url, timeout=60, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        data = r.json()
        print(f"  Got {len(data)} universities")
        return data
    except Exception as e:
        print(f"  FAIL: {e}")
        return []


def save_university(u):
    """Save one university as study_opportunity"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()

    # Use name+country+url as unique key
    name = u.get("name") or "UNKNOWN"
    country = u.get("country") or "UNKNOWN"
    url = (u.get("web_pages") or [""])[0] or "UNKNOWN"

    # Check existing
    cur.execute("""
        SELECT id FROM study_opportunities
        WHERE university_name=? AND country=?
    """, (name, country))
    if cur.fetchone():
        conn.close()
        return None  # Skip duplicate

    oid = str(uuid.uuid4())
    org_id = str(uuid.uuid4())
    domains = ", ".join(u.get("domains") or [])

    cur.execute("""
        INSERT INTO study_opportunities
        (id, organization_id, type, title, description, status,
         first_seen, last_seen, created_at, updated_at,
         country, city, university_name, course_name,
         degree_level, field_of_study, language, application_url, work_scope)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        oid, org_id, "UNIVERSITY",
        name,                            # title
        url,                             # description = official URL
        "DISCOVERED",
        now, now, now, now,
        country,
        "",                              # city (Hipolabs doesn't provide)
        name,                            # university_name
        "",                              # course_name
        "",                              # degree_level
        "",                              # field_of_study
        "",                              # language
        url,
        f"Domains: {domains}",
    ))

    # Claims
    claims = [
        ("university_name", name),
        ("country", country),
        ("application_url", url),
    ]
    if u.get("alpha_two_code"):
        claims.append(("country_code", u["alpha_two_code"]))
    if domains:
        claims.append(("domains", domains))

    for field, value in claims:
        if value in (None, "", "UNKNOWN"):
            continue
        claim_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO study_claims
            (id, study_id, field_name, claimed_value, truth_state,
             source_priority, confidence, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (claim_id, oid, field, str(value), "SUPPORTED", 3, 0.85, now, now))

        # Evidence
        ev_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO study_evidence
            (id, claim_id, source_id, captured_at, hash, confidence,
             freshness_days, valid_until)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (ev_id, claim_id, "hipolabs", now,
              str(hash(str(value)))[:32], 0.85, 0, None))

    conn.commit()
    conn.close()
    return oid


def fetch_by_country(countries):
    total_saved = 0
    for c in countries:
        unis = fetch_universities(c)
        saved = 0
        for u in unis:
            if save_university(u):
                saved += 1
        print(f"  Saved {saved} new universities from {c}")
        total_saved += saved
    return total_saved


if __name__ == "__main__":
    print("=" * 70)
    print("STUDY OIE — UNIVERSITY FETCHER")
    print("=" * 70)

    # Top study destinations
    target_countries = [
        "Germany",
        "United Kingdom",
        "Canada",
        "United States",
        "Australia",
        "Japan",
    ]

    total = fetch_by_country(target_countries)

    print(f"\nTotal universities saved: {total}")

    # Report
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM study_opportunities")
    print(f"Total study opportunities: {cur.fetchone()[0]}")
    cur.execute("""
        SELECT country, COUNT(*) FROM study_opportunities
        GROUP BY country ORDER BY COUNT(*) DESC LIMIT 15
    """)
    print("\nBy country:")
    for c, n in cur.fetchall():
        print(f"  {str(c):25} {n}")
    cur.execute("SELECT COUNT(*) FROM study_claims")
    print(f"\nTotal study claims: {cur.fetchone()[0]}")

    # Sample
    print("\nSample universities:")
    cur.execute("""
        SELECT university_name, country FROM study_opportunities
        LIMIT 10
    """)
    for name, c in cur.fetchall():
        print(f"  {str(name)[:60]:60} | {c}")

    conn.close()