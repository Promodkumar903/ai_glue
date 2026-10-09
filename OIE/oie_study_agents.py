"""
Study OIE — Study Agents Registry + University Contacts
"""
import sqlite3
import uuid
import re
from datetime import datetime

DB = "ai_glue.db"


def create_schema():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS study_agents (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            legal_name TEXT,
            country TEXT,
            city TEXT,
            website TEXT,
            email TEXT,
            phone TEXT,
            license_number TEXT,
            license_authority TEXT,
            established_year INTEGER,
            services_offered TEXT,
            target_countries TEXT,
            specializations TEXT,
            trust_score INTEGER DEFAULT 0,
            verification_status TEXT DEFAULT 'PENDING',
            is_genuine INTEGER DEFAULT 0,
            is_verified INTEGER DEFAULT 0,
            fake_flags TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS study_contacts (
            id TEXT PRIMARY KEY,
            university_name TEXT NOT NULL,
            country TEXT,
            website TEXT,
            admissions_officer TEXT,
            designation TEXT,
            email TEXT,
            phone TEXT,
            application_url TEXT,
            verification_status TEXT DEFAULT 'PENDING',
            contact_attempts INTEGER DEFAULT 0,
            verified_at TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("OK: Study schema created")


STUDY_AGENTS = [
    {"name": "IDP Education India", "legal_name": "IDP Education India Pvt Ltd", "country": "India", "city": "Chennai", "website": "https://www.idp.com/india", "email": "info@idp.com", "phone": "+91-44-4005-8000", "license_number": "AIRC/IN/2005/001", "license_authority": "AIRC", "established_year": 1969, "services_offered": "Study abroad counseling, IELTS, admission", "target_countries": "Australia, UK, USA, Canada, NZ, Ireland", "specializations": "All courses"},
    {"name": "British Council India", "legal_name": "British Council Division", "country": "India", "city": "New Delhi", "website": "https://www.britishcouncil.in", "email": "info@britishcouncil.in", "phone": "+91-11-4149-7300", "license_number": "UK-GOV-OFFICIAL", "license_authority": "UK Government", "established_year": 1948, "services_offered": "UK education, IELTS, scholarships", "target_countries": "United Kingdom", "specializations": "All UK universities"},
    {"name": "AECC Global India", "legal_name": "AECC Global Pvt Ltd", "country": "India", "city": "Hyderabad", "website": "https://www.aeccglobal.in", "email": "info@aeccglobal.in", "phone": "+91-40-4851-5100", "license_number": "AIRC/IN/2010/045", "license_authority": "AIRC", "established_year": 2010, "services_offered": "Study abroad, visa, scholarships", "target_countries": "Australia, UK, Canada, USA, NZ, Germany", "specializations": "Engineering, Business, IT"},
    {"name": "Edwise International", "legal_name": "Edwise International", "country": "India", "city": "Mumbai", "website": "https://www.edwiseinternational.com", "email": "info@edwiseinternational.com", "phone": "+91-22-4081-3333", "license_number": "AIRC/IN/2003/012", "license_authority": "AIRC", "established_year": 1991, "services_offered": "Study abroad counseling", "target_countries": "USA, UK, Canada, Australia, NZ, Singapore", "specializations": "All courses"},
    {"name": "Global Reach Nepal", "legal_name": "Global Reach Pvt Ltd", "country": "Nepal", "city": "Kathmandu", "website": "https://www.globalreach.com.np", "email": "info@globalreach.com.np", "phone": "+977-1-4412-345", "license_number": "NEP-EDU-2015-089", "license_authority": "Nepal Education Ministry", "established_year": 2015, "services_offered": "Study in Australia, Japan, Korea", "target_countries": "Australia, Japan, South Korea, Germany", "specializations": "Engineering, Healthcare, IT"},
    {"name": "Fake Fast Visa Consultancy", "country": "India", "website": "http://fastvisa.tk", "email": "info@fastvisagmail.com", "phone": "12345", "license_number": "123", "established_year": 2020, "services_offered": "100% visa guarantee, pay first", "target_countries": "Any"},
]

FAKE_PATTERNS = {
    "visa_guarantee": r"guarantee.*visa|visa.*guarantee|100% visa",
    "advance_payment": r"pay.*first|advance payment",
    "suspicious_domain": r"\.tk$|\.xyz$|\.ml$",
}


def detect_fake(data):
    flags = []
    text = " ".join(str(v) for v in data.values() if v).lower()
    for name, regex in FAKE_PATTERNS.items():
        if re.search(regex, text, re.IGNORECASE):
            flags.append(name)
    lic = data.get("license_number", "")
    if lic and len(lic) < 6:
        flags.append("short_license_number")
    return flags


def calc_trust(data):
    score = 0
    if data.get("legal_name"): score += 10
    if data.get("license_number"): score += 15
    if data.get("license_authority"): score += 10
    if data.get("established_year") and 1950 <= data["established_year"] <= 2025: score += 10
    if data.get("website"): score += 5
    if data.get("email"): score += 5
    if data.get("phone"): score += 5
    return min(score, 100)


def seed_study_agents():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    inserted = 0

    for agent in STUDY_AGENTS:
        cur.execute("SELECT id FROM study_agents WHERE name=?", (agent["name"],))
        if cur.fetchone():
            continue

        fake_flags = detect_fake(agent)
        trust = calc_trust(agent)

        cur.execute("""
            INSERT INTO study_agents
            (id, name, legal_name, country, city, website, email, phone,
             license_number, license_authority, established_year,
             services_offered, target_countries, specializations,
             trust_score, verification_status, fake_flags,
             created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()), agent["name"], agent.get("legal_name", ""),
            agent.get("country", ""), agent.get("city", ""),
            agent.get("website", ""), agent.get("email", ""), agent.get("phone", ""),
            agent.get("license_number", ""), agent.get("license_authority", ""),
            agent.get("established_year"),
            agent.get("services_offered", ""), agent.get("target_countries", ""),
            agent.get("specializations", ""),
            trust, "FLAGGED" if fake_flags else "PENDING", ",".join(fake_flags),
            now, now
        ))
        inserted += 1
        status = "FLAGGED" if fake_flags else "OK"
        print(f"  {agent['name']:35} -> {status} (trust: {trust})")

    conn.commit()
    conn.close()
    print(f"\nInserted: {inserted} study agents")


UNIVERSITY_CONTACTS = [
    ("Technical University of Munich", "Germany", "https://www.tum.de", "International Admissions", "Admissions Office", "international@tum.de", "+49-89-289-01", "https://www.tum.de/en/studies/application"),
    ("RWTH Aachen University", "Germany", "https://www.rwth-aachen.de", "International Office", "Admissions", "international@rwth-aachen.de", "+49-241-80-1", "https://www.rwth-aachen.de/go/id/bdml/"),
    ("University of Toronto", "Canada", "https://www.utoronto.ca", "International Admissions", "Admissions Officer", "admissions@utoronto.ca", "+1-416-978-2011", "https://future.utoronto.ca/apply"),
    ("University of Oxford", "United Kingdom", "https://www.ox.ac.uk", "International Office", "Admissions", "admissions@ox.ac.uk", "+44-1865-270000", "https://www.ox.ac.uk/admissions"),
    ("MIT", "USA", "https://www.mit.edu", "International Admissions", "Admissions Officer", "admissions@mit.edu", "+1-617-253-1000", "https://mitadmissions.org/apply"),
    ("Stanford University", "USA", "https://www.stanford.edu", "International Office", "Admissions", "admission@stanford.edu", "+1-650-723-2300", "https://admission.stanford.edu/apply"),
    ("University of Tokyo", "Japan", "https://www.u-tokyo.ac.jp", "International Affairs", "Admissions Officer", "intl-adm@u-tokyo.ac.jp", "+81-3-3812-2111", "https://www.u-tokyo.ac.jp/en/prospective-students/"),
    ("ETH Zurich", "Switzerland", "https://ethz.ch", "Admissions Office", "International Admissions", "admissions@ethz.ch", "+41-44-632-11-11", "https://ethz.ch/en/studies/registration-application.html"),
]


def seed_university_contacts():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    inserted = 0

    for (name, country, website, officer, designation, email, phone, app_url) in UNIVERSITY_CONTACTS:
        cur.execute("SELECT id FROM study_contacts WHERE university_name=?", (name,))
        if cur.fetchone():
            continue
        cur.execute("""
            INSERT INTO study_contacts
            (id, university_name, country, website, admissions_officer,
             designation, email, phone, application_url,
             verification_status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()), name, country, website, officer, designation,
            email, phone, app_url, "PENDING", now, now
        ))
        inserted += 1

    conn.commit()
    conn.close()
    print(f"Inserted: {inserted} university contacts")


def report():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    print("\n" + "=" * 90)
    print("STUDY AGENTS")
    print("=" * 90)
    cur.execute("""
        SELECT name, country, trust_score, verification_status, fake_flags
        FROM study_agents ORDER BY trust_score DESC
    """)
    for n, c, t, s, f in cur.fetchall():
        flag = f" FLAG: {f}" if f else ""
        print(f"  {str(n)[:35]:35} | {c:8} | Trust: {t:3} | {s}{flag}")

    print("\n" + "=" * 90)
    print("UNIVERSITY CONTACTS")
    print("=" * 90)
    cur.execute("""
        SELECT university_name, country, admissions_officer, email
        FROM study_contacts ORDER BY country, university_name
    """)
    for n, c, o, e in cur.fetchall():
        print(f"  {str(n)[:35]:35} | {c:15} | {str(o)[:22]:22} | {e[:30]}")

    cur.execute("SELECT COUNT(*) FROM study_agents")
    print(f"\nTotal study agents: {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM study_contacts")
    print(f"Total university contacts: {cur.fetchone()[0]}")
    conn.close()


if __name__ == "__main__":
    print("=" * 90)
    print("STUDY OIE — AGENTS + CONTACTS")
    print("=" * 90)
    create_schema()
    print("\nSeeding study agents...")
    seed_study_agents()
    print("\nSeeding university contacts...")
    seed_university_contacts()
    report()
    print("\nDone.")