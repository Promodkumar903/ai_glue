"""
OIE Registry — Verified Agents, Brokers, Universities, Companies
Trust-based verification for B2B partnerships
"""
import sqlite3
import uuid
import re
from datetime import datetime

DB = "ai_glue.db"


# ============================================================
# REGISTRY SCHEMA
# ============================================================
def create_registry_schema():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # Main registry table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS registry_entities (
            id TEXT PRIMARY KEY,
            entity_type TEXT,
            name TEXT NOT NULL,
            legal_name TEXT,
            country TEXT,
            city TEXT,
            website TEXT,
            email TEXT,
            phone TEXT,
            established_year INTEGER,
            license_number TEXT,
            license_authority TEXT,
            employee_count TEXT,
            services_offered TEXT,
            specializations TEXT,
            countries_served TEXT,
            trust_score INTEGER DEFAULT 0,
            verification_status TEXT DEFAULT 'PENDING',
            is_genuine INTEGER DEFAULT 0,
            is_verified INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            fake_flags TEXT,
            positive_feedback INTEGER DEFAULT 0,
            negative_feedback INTEGER DEFAULT 0,
            total_placements INTEGER DEFAULT 0,
            avg_response_time_hours INTEGER DEFAULT 0,
            admin_notes TEXT,
            verified_by TEXT,
            verified_at TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)

    # Request log — who requested what from whom
    cur.execute("""
        CREATE TABLE IF NOT EXISTS registry_requests (
            id TEXT PRIMARY KEY,
            from_user_id TEXT,
            from_role TEXT,
            to_entity_id TEXT,
            request_type TEXT,
            subject TEXT,
            message TEXT,
            context_data TEXT,
            status TEXT DEFAULT 'PENDING',
            sent_at TEXT,
            responded_at TEXT,
            response TEXT
        )
    """)

    # Feedback from users about entities
    cur.execute("""
        CREATE TABLE IF NOT EXISTS registry_feedback (
            id TEXT PRIMARY KEY,
            entity_id TEXT,
            user_id TEXT,
            rating INTEGER,
            comment TEXT,
            experience_type TEXT,
            created_at TEXT
        )
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_re_type ON registry_entities(entity_type)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_re_verified ON registry_entities(is_verified)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_re_country ON registry_entities(country)")

    conn.commit()
    conn.close()
    print("OK: Registry schema created")
    print("  - registry_entities")
    print("  - registry_requests")
    print("  - registry_feedback")


# ============================================================
# FAKE DETECTION RULES
# ============================================================
FAKE_PATTERNS = {
    "free_visa_guarantee": r"guarantee.*visa|visa.*guarantee|100% visa",
    "too_good_salary": r"salary.*[0-9]{6,}.*instant|instant.*placement",
    "no_office": r"no physical|online only|whatsapp only",
    "advance_payment": r"pay.*first|advance payment|registration fee.*before",
    "fake_license": r"license.*[A-Z]{0,2}[0-9]{4,}",
    "copy_paste": r"exact same as|lorem ipsum|dummy",
    "suspicious_domain": r"\.tk$|\.xyz$|\.ml$|\.ga$",
}


def detect_fake_indicators(data):
    """Scan for fake patterns"""
    flags = []
    text = " ".join(str(v) for v in data.values() if v).lower()

    for pattern_name, regex in FAKE_PATTERNS.items():
        if re.search(regex, text, re.IGNORECASE):
            flags.append(pattern_name)

    # Check license number authenticity
    license_num = data.get("license_number", "")
    if license_num and len(license_num) < 6:
        flags.append("short_license_number")

    # Check established year
    est = data.get("established_year")
    if est and (est < 1900 or est > 2026):
        flags.append("invalid_establishment_year")

    # Check email domain vs website
    email = data.get("email", "")
    website = data.get("website", "")
    if email and website:
        email_domain = email.split("@")[-1] if "@" in email else ""
        website_domain = re.sub(r"https?://(www\.)?", "", website).split("/")[0]
        if email_domain and website_domain and email_domain != website_domain:
            # Not always fake — could be gmail
            if "gmail" not in email_domain and "yahoo" not in email_domain:
                flags.append("email_domain_mismatch")

    return flags


# ============================================================
# TRUST SCORE CALCULATION
# ============================================================
def calculate_entity_trust(entity):
    """Calculate trust score 0-100"""
    score = 0

    # Base: KYC data completeness
    if entity.get("legal_name"): score += 10
    if entity.get("license_number"): score += 15
    if entity.get("license_authority"): score += 10
    if entity.get("established_year") and 1950 <= entity.get("established_year", 0) <= 2025:
        score += 10
    if entity.get("website"): score += 5
    if entity.get("email"): score += 5
    if entity.get("phone"): score += 5

    # License verification (add later)
    if entity.get("is_verified"): score += 15

    # Feedback
    pos = entity.get("positive_feedback", 0)
    neg = entity.get("negative_feedback", 0)
    total_fb = pos + neg
    if total_fb > 0:
        feedback_score = (pos / total_fb) * 15
        score += feedback_score
    else:
        score += 5  # neutral

    # Placement history
    placements = entity.get("total_placements", 0)
    score += min(placements / 10, 10)

    # Penalty for fake flags
    fake_flags = entity.get("fake_flags", "")
    if fake_flags:
        score -= len(fake_flags.split(",")) * 15

    return max(0, min(100, int(score)))


# ============================================================
# REGISTER ENTITY
# ============================================================
def register_entity(data):
    """
    Register an agent/broker/university/company
    data: {
        entity_type: 'AGENT'|'BROKER'|'UNIVERSITY'|'COMPANY',
        name, legal_name, country, city, website, email, phone,
        established_year, license_number, license_authority,
        services_offered, specializations, countries_served
    }
    """
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()

    # Check duplicate
    cur.execute("""
        SELECT id FROM registry_entities
        WHERE LOWER(name)=? AND country=?
    """, (data.get("name", "").lower(), data.get("country", "")))
    if cur.fetchone():
        conn.close()
        return {"error": "Entity already exists"}

    # Detect fake indicators
    fake_flags = detect_fake_indicators(data)

    entity = {
        "id": str(uuid.uuid4()),
        "entity_type": data.get("entity_type", "AGENT"),
        "name": data.get("name", ""),
        "legal_name": data.get("legal_name", ""),
        "country": data.get("country", ""),
        "city": data.get("city", ""),
        "website": data.get("website", ""),
        "email": data.get("email", ""),
        "phone": data.get("phone", ""),
        "established_year": data.get("established_year"),
        "license_number": data.get("license_number", ""),
        "license_authority": data.get("license_authority", ""),
        "services_offered": data.get("services_offered", ""),
        "specializations": data.get("specializations", ""),
        "countries_served": data.get("countries_served", ""),
        "fake_flags": ",".join(fake_flags),
        "verification_status": "FLAGGED" if fake_flags else "PENDING",
    }

    trust = calculate_entity_trust(entity)

    cur.execute("""
        INSERT INTO registry_entities
        (id, entity_type, name, legal_name, country, city, website, email, phone,
         established_year, license_number, license_authority,
         services_offered, specializations, countries_served,
         trust_score, verification_status, fake_flags,
         created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        entity["id"], entity["entity_type"], entity["name"], entity["legal_name"],
        entity["country"], entity["city"], entity["website"], entity["email"],
        entity["phone"], entity["established_year"], entity["license_number"],
        entity["license_authority"], entity["services_offered"],
        entity["specializations"], entity["countries_served"],
        trust, entity["verification_status"], entity["fake_flags"],
        now, now
    ))

    conn.commit()
    conn.close()

    return {
        "id": entity["id"],
        "trust_score": trust,
        "status": entity["verification_status"],
        "fake_flags": fake_flags,
    }


# ============================================================
# VERIFY ENTITY (Admin action)
# ============================================================
def verify_entity(entity_id, admin_id, is_genuine=True, notes=""):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()

    cur.execute("""
        UPDATE registry_entities
        SET is_genuine=?, is_verified=1, verification_status=?,
            admin_notes=?, verified_by=?, verified_at=?, updated_at=?
        WHERE id=?
    """, (
        1 if is_genuine else 0,
        "VERIFIED" if is_genuine else "REJECTED",
        notes, admin_id, now, now, entity_id
    ))

    # Recalculate trust
    cur.execute("SELECT * FROM registry_entities WHERE id=?", (entity_id,))
    row = cur.fetchone()
    if row:
        cols = [d[0] for d in cur.description]
        entity = dict(zip(cols, row))
        trust = calculate_entity_trust(entity)
        cur.execute("UPDATE registry_entities SET trust_score=? WHERE id=?", (trust, entity_id))

    conn.commit()
    conn.close()
    return {"ok": True}


# ============================================================
# SEARCH REGISTRY
# ============================================================
def search_registry(entity_type="", country="", verified_only=True, min_trust=70, limit=20):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    clauses = ["is_active=1"]
    params = []

    if entity_type:
        clauses.append("entity_type=?")
        params.append(entity_type)
    if country:
        clauses.append("LOWER(country) LIKE ?")
        params.append(f"%{country.lower()}%")
    if verified_only:
        clauses.append("is_verified=1")
    if min_trust:
        clauses.append("trust_score >= ?")
        params.append(min_trust)

    where = " AND ".join(clauses)
    params.append(limit)

    cur.execute(f"""
        SELECT id, entity_type, name, country, city, website,
               trust_score, total_placements, avg_response_time_hours
        FROM registry_entities WHERE {where}
        ORDER BY trust_score DESC LIMIT ?
    """, params)

    rows = [dict(zip([d[0] for d in cur.description], r)) for r in cur.fetchall()]
    conn.close()
    return {"count": len(rows), "entities": rows}


# ============================================================
# SEED SAMPLE GENUINE ENTITIES (for testing)
# ============================================================
def seed_genuine_entities():
    samples = [
        # Genuine agents
        {
            "entity_type": "AGENT", "name": "Global Education Consultancy",
            "legal_name": "Global Education Pvt Ltd", "country": "India",
            "city": "Delhi", "website": "https://gec.in", "email": "info@gec.in",
            "phone": "+91-11-4567890", "established_year": 2005,
            "license_number": "MEA/AG/2005/12345", "license_authority": "MEA India",
            "services_offered": "Study abroad, visa assistance",
            "specializations": "Germany, Canada, UK",
            "countries_served": "India",
        },
        {
            "entity_type": "AGENT", "name": "Nepal Career Services",
            "legal_name": "NCS Pvt Ltd", "country": "Nepal",
            "city": "Kathmandu", "website": "https://ncs.com.np", "email": "info@ncs.com.np",
            "phone": "+977-1-4567890", "established_year": 2010,
            "license_number": "DoFE/2010/4567", "license_authority": "DoFE Nepal",
            "services_offered": "Overseas employment",
            "specializations": "Japan, Korea, Gulf",
            "countries_served": "Nepal",
        },
        # Genuine brokers
        {
            "entity_type": "BROKER", "name": "Euro Manpower Solutions",
            "legal_name": "Euro Manpower GmbH", "country": "Germany",
            "city": "Munich", "website": "https://euro-manpower.de", "email": "info@euro-manpower.de",
            "phone": "+49-89-12345678", "established_year": 2015,
            "license_number": "BA/2015/DE/789", "license_authority": "Bundesagentur für Arbeit",
            "services_offered": "Manpower supply",
            "specializations": "Healthcare, IT",
            "countries_served": "Germany",
        },
        # Fake one (should be flagged)
        {
            "entity_type": "AGENT", "name": "QuickVisa Guarantee",
            "country": "India", "website": "http://quickvisa.tk",
            "email": "info@quickvisa.gmail.com", "phone": "12345",
            "established_year": 2020,
            "license_number": "123", "license_authority": "",
            "services_offered": "100% visa guarantee, pay first",
            "specializations": "Any country",
        },
    ]

    results = []
    for s in samples:
        r = register_entity(s)
        results.append(r)
        print(f"  {s['name']:40} → {r.get('status', 'ERROR')} (trust: {r.get('trust_score', 0)})")
        if r.get('fake_flags'):
            print(f"    ⚠️ Flags: {r['fake_flags']}")

    return results


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=" * 70)
    print("OIE REGISTRY — Agent/Broker Verification")
    print("=" * 70)

    create_registry_schema()

    print("\nSeeding sample entities...")
    seed_genuine_entities()

    print("\n" + "=" * 70)
    print("GENUINE ENTITIES (verified, trust 70+)")
    print("=" * 70)
    r = search_registry(verified_only=False, min_trust=0, limit=20)
    for e in r["entities"]:
        print(f"  [{e['entity_type']:10}] {e['name']:35} | Trust: {e['trust_score']:3} | {e['country']}")

    print("\nDone.")