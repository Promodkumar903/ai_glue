"""
OIE Verification Engine
Truth states, evidence chain, conflict detection, trust scoring
"""
import sqlite3
import json
import hashlib
import uuid
from datetime import datetime

DB = "ai_glue.db"

# ============================================================
# TRUTH STATES (9 states)
# ============================================================
TRUTH_STATES = {
    "CONFIRMED":       {"min_score": 90, "color": "green", "icon": "✓"},
    "HIGH_CONFIDENCE": {"min_score": 80, "color": "green", "icon": "✓"},
    "VERIFIED":        {"min_score": 70, "color": "blue",  "icon": "✓"},
    "SUPPORTED":       {"min_score": 50, "color": "blue",  "icon": "○"},
    "INFERRED":        {"min_score": 30, "color": "yellow","icon": "~"},
    "PARTIAL":         {"min_score": 20, "color": "yellow","icon": "~"},
    "UNKNOWN":         {"min_score": 0,  "color": "gray",  "icon": "?"},
    "CONFLICTING":     {"min_score": 0,  "color": "red",   "icon": "⚠"},
    "OUTDATED":        {"min_score": 0,  "color": "gray",  "icon": "⌛"},
}

# ============================================================
# SOURCE TRUST HIERARCHY
# ============================================================
SOURCE_TIERS = {
    # Government / Official
    "make-it-in-germany.com": {"tier": 1, "weight": 95, "type": "GOV"},
    "make-it-in-germany": {"tier": 1, "weight": 95, "type": "GOV"},
    "ncs.gov.in": {"tier": 1, "weight": 95, "type": "GOV"},
    "ncs": {"tier": 1, "weight": 95, "type": "GOV"},
    "eures.europa.eu": {"tier": 1, "weight": 95, "type": "GOV"},
    "eures": {"tier": 1, "weight": 95, "type": "GOV"},
    "gov.uk": {"tier": 1, "weight": 95, "type": "GOV"},
    "daad.de": {"tier": 1, "weight": 95, "type": "GOV"},
    "daad": {"tier": 1, "weight": 95, "type": "GOV"},

    # Registries
    "hipolabs.com": {"tier": 2, "weight": 85, "type": "REGISTRY"},
    "hipolabs": {"tier": 2, "weight": 85, "type": "REGISTRY"},
    "nirf": {"tier": 2, "weight": 85, "type": "REGISTRY"},
    "qs.com": {"tier": 2, "weight": 85, "type": "REGISTRY"},

    # Employers (direct)
    "official-employer": {"tier": 2, "weight": 80, "type": "EMPLOYER"},
    "employer": {"tier": 2, "weight": 80, "type": "EMPLOYER"},

    # Job boards / APIs
    "arbeitnow.com": {"tier": 4, "weight": 60, "type": "API"},
    "arbeitnow": {"tier": 4, "weight": 60, "type": "API"},
    "remotive.com": {"tier": 4, "weight": 60, "type": "API"},
    "remotive": {"tier": 4, "weight": 60, "type": "API"},
    "remoteok.com": {"tier": 4, "weight": 60, "type": "API"},
    "remoteok": {"tier": 4, "weight": 60, "type": "API"},
    "himalayas.app": {"tier": 4, "weight": 60, "type": "API"},
    "himalayas": {"tier": 4, "weight": 60, "type": "API"},
    "jobicy.com": {"tier": 4, "weight": 60, "type": "API"},
    "jobicy": {"tier": 4, "weight": 60, "type": "API"},

    # Unknown
    "unknown": {"tier": 4, "weight": 30, "type": "UNKNOWN"},
}

# ============================================================
# STEP 1: SCHEMA — Verification Tables
# ============================================================
def create_verification_schema():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # Verified records — approved opportunities
    cur.execute("""
        CREATE TABLE IF NOT EXISTS verified_records (
            id TEXT PRIMARY KEY,
            record_type TEXT,
            record_id TEXT,
            opportunity_id TEXT,
            title TEXT,
            summary TEXT,
            country TEXT,
            category TEXT,
            trust_score INTEGER DEFAULT 0,
            truth_state TEXT DEFAULT 'UNKNOWN',
            source_count INTEGER DEFAULT 0,
            evidence_count INTEGER DEFAULT 0,
            conflict_count INTEGER DEFAULT 0,
            is_approved INTEGER DEFAULT 0,
            approved_by TEXT,
            approved_at TEXT,
            visible_to_user INTEGER DEFAULT 0,
            hidden_source_url TEXT,
            public_display_data TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)

    # Evidence chain — full audit
    cur.execute("""
        CREATE TABLE IF NOT EXISTS verification_evidence (
            id TEXT PRIMARY KEY,
            verified_record_id TEXT,
            field_name TEXT,
            claimed_value TEXT,
            evidence_text TEXT,
            evidence_url TEXT,
            source_tier INTEGER,
            source_weight INTEGER,
            confidence REAL,
            captured_at TEXT,
            hash TEXT
        )
    """)

    # Conflicts detected
    cur.execute("""
        CREATE TABLE IF NOT EXISTS verification_conflicts (
            id TEXT PRIMARY KEY,
            verified_record_id TEXT,
            field_name TEXT,
            sources TEXT,
            conflict_values TEXT,
            severity TEXT,
            resolved INTEGER DEFAULT 0,
            resolution TEXT,
            created_at TEXT
        )
    """)

    # Verification log
    cur.execute("""
        CREATE TABLE IF NOT EXISTS verification_log (
            id TEXT PRIMARY KEY,
            record_id TEXT,
            event_type TEXT,
            before_state TEXT,
            after_state TEXT,
            reason TEXT,
            actor TEXT,
            created_at TEXT
        )
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_vr_approved ON verified_records(is_approved)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_vr_type ON verified_records(record_type)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ve_record ON verification_evidence(verified_record_id)")

    conn.commit()
    conn.close()
    print("OK: Verification schema ready")
    print("  - verified_records")
    print("  - verification_evidence")
    print("  - verification_conflicts")
    print("  - verification_log")


# ============================================================
# STEP 2: SOURCE LOOKUP
# ============================================================
def get_source_info(source_url):
    if not source_url:
        return SOURCE_TIERS["unknown"]
    url = source_url.lower()
    for key, info in SOURCE_TIERS.items():
        if key in url:
            return info
    return SOURCE_TIERS["unknown"]


# ============================================================
# STEP 3: TRUST SCORE CALCULATION
# ============================================================
def calculate_trust_score(record_type, sources, evidence_count, conflict_count, freshness_days=0):
    """
    Trust score = weighted average of source tiers
    """
    if not sources:
        return 50

    weights = [get_source_info(s).get('weight', 30) for s in sources]
    base = sum(weights) / len(weights)

    if base < 50:
        base = 50

    evidence_boost = min(evidence_count * 2, 15)
    conflict_penalty = min(conflict_count * 10, 25)

    if freshness_days > 365:
        freshness_penalty = 20
    elif freshness_days > 180:
        freshness_penalty = 10
    elif freshness_days > 90:
        freshness_penalty = 5
    else:
        freshness_penalty = 0

    score = base + evidence_boost - conflict_penalty - freshness_penalty
    return max(0, min(100, int(score)))

# ============================================================
# STEP 4: DETERMINE TRUTH STATE
# ============================================================
def determine_truth_state(trust_score, source_tiers, conflict_count, evidence_count):
    if conflict_count > 0:
        return "CONFLICTING"
    if trust_score >= 90 and min(source_tiers) <= 1:
        return "CONFIRMED"
    if trust_score >= 80:
        return "HIGH_CONFIDENCE"
    if trust_score >= 70:
        return "VERIFIED"
    if trust_score >= 60 and evidence_count > 0:
        return "SUPPORTED"
    if trust_score >= 40:
        return "INFERRED"
    if evidence_count == 0:
        return "UNKNOWN"
    return "PARTIAL"


# ============================================================
# STEP 5: VERIFY AN OPPORTUNITY
# ============================================================
def verify_opportunity(opp_id, record_type="JOB"):
    """Main verification function for jobs"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # Get opportunity data
    cur.execute("""
        SELECT id, title, country, company, location, salary,
               contract_type, duration, work_scope, description
        FROM opportunities WHERE id=?
    """, (opp_id,))
    opp = cur.fetchone()
    if not opp:
        conn.close()
        return {"error": "Opportunity not found"}

    opp_dict = dict(zip(
        ["id", "title", "country", "company", "location", "salary",
         "contract_type", "duration", "work_scope", "description"],
        opp
    ))

    # Get all claims for this opportunity
    cur.execute("""
        SELECT id, field_name, claimed_value, truth_state, source_priority, confidence
        FROM claims WHERE opportunity_id=?
    """, (opp_id,))
    claims = cur.fetchall()

    # Get evidence
    cur.execute("""
        SELECT id, claim_id, source_id, captured_at, confidence
        FROM evidence WHERE claim_id IN (
            SELECT id FROM claims WHERE opportunity_id=?
        )
    """, (opp_id,))
    evidence_rows = cur.fetchall()

    # Analyze
    sources = set()
    for ev in evidence_rows:
        sources.add(ev[2])  # source_id
    source_urls = list(sources)

    source_tiers = []
    for s in source_urls:
        info = get_source_info(s)
        source_tiers.append(info['tier'])

    # Count conflicts (fields with multiple different values)
    conflicts = 0
    field_values = {}
    for c in claims:
        field = c[1]
        val = c[2]
        if field not in field_values:
            field_values[field] = set()
        field_values[field].add(str(val))
    for field, vals in field_values.items():
        if len(vals) > 1:
            conflicts += 1

    # Calculate trust
    trust = calculate_trust_score(
        record_type,
        source_urls,
        len(evidence_rows),
        conflicts
    )

    # Truth state
    truth_state = determine_truth_state(
        trust,
        source_tiers if source_tiers else [4],
        conflicts,
        len(evidence_rows)
    )

    # Build public data (hide source URLs)
    public_data = {
        "title": opp_dict["title"],
        "country": opp_dict["country"],
        "company": opp_dict["company"],
        "location": opp_dict["location"],
        "salary": opp_dict["salary"],
        "contract_type": opp_dict["contract_type"],
        "duration": opp_dict["duration"],
        "work_scope": opp_dict["work_scope"][:500] if opp_dict["work_scope"] else "",
        "brand": "AI Glue Verified",  # ← Ye user ko dikhega
    }

    # Save verified record
    record_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    cur.execute("""
        INSERT OR REPLACE INTO verified_records
        (id, record_type, record_id, opportunity_id, title, summary,
         country, trust_score, truth_state, source_count, evidence_count,
         conflict_count, is_approved, hidden_source_url, public_display_data,
         created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        record_id, record_type, opp_id, opp_id,
        opp_dict["title"], opp_dict["work_scope"][:200] if opp_dict["work_scope"] else "",
        opp_dict["country"],
        trust, truth_state,
        len(sources), len(evidence_rows), conflicts,
        0,  # not approved yet
        ",".join(source_urls),  # hidden
        json.dumps(public_data),
        now, now
    ))

    # Save evidence chain
    for ev in evidence_rows:
        ev_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO verification_evidence
            (id, verified_record_id, field_name, evidence_text, source_tier,
             source_weight, confidence, captured_at, hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ev_id, record_id, "general", "Evidence from source",
            2, 70, ev[4] or 0.5, ev[3] or now,
            hashlib.md5(str(ev[0]).encode()).hexdigest()[:16]
        ))

    # Save conflicts
    for field, vals in field_values.items():
        if len(vals) > 1:
            conflict_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO verification_conflicts
                 (id, verified_record_id, field_name, sources, conflict_values,
                 severity, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                conflict_id, record_id, field,
                ",".join(source_urls),
                json.dumps(list(vals)),
                "HIGH" if len(vals) > 2 else "MEDIUM",
                now
            ))

    # Log
    log_id = str(uuid.uuid4())
    cur.execute("""
        INSERT INTO verification_log
        (id, record_id, event_type, after_state, reason, actor, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        log_id, record_id, "VERIFIED", truth_state,
        f"Trust: {trust}, Sources: {len(sources)}, Evidence: {len(evidence_rows)}, Conflicts: {conflicts}",
        "OIE_ENGINE", now
    ))

    conn.commit()
    conn.close()

    return {
        "record_id": record_id,
        "trust_score": trust,
        "truth_state": truth_state,
        "sources": len(sources),
        "evidence": len(evidence_rows),
        "conflicts": conflicts,
    }


# ============================================================
# STEP 6: BATCH VERIFY ALL JOBS
# ============================================================
def verify_all_jobs(limit=100):
    """Verify all discovered jobs in batch"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        SELECT id FROM opportunities
        WHERE status='DISCOVERED'
        LIMIT ?
    """, (limit,))
    job_ids = [r[0] for r in cur.fetchall()]
    conn.close()

    print(f"Verifying {len(job_ids)} jobs...\n")

    stats = {
        "CONFIRMED": 0, "HIGH_CONFIDENCE": 0, "VERIFIED": 0,
        "SUPPORTED": 0, "INFERRED": 0, "UNKNOWN": 0,
        "CONFLICTING": 0, "PARTIAL": 0
    }

    for i, jid in enumerate(job_ids, 1):
        result = verify_opportunity(jid, "JOB")
        if "error" not in result:
            stats[result["truth_state"]] += 1
            if i % 20 == 0:
                print(f"  [{i}/{len(job_ids)}] Trust: {result['trust_score']}, State: {result['truth_state']}")

    print(f"\n{'='*60}")
    print("VERIFICATION COMPLETE")
    print(f"{'='*60}")
    for state, count in stats.items():
        if count > 0:
            print(f"  {state:20} {count}")

    return stats


# ============================================================
# STEP 7: REPORT
# ============================================================
def verification_report():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM verified_records")
    total = cur.fetchone()[0]
    print(f"\nTotal verified records: {total}")

    cur.execute("""
        SELECT truth_state, COUNT(*) FROM verified_records
        GROUP BY truth_state ORDER BY COUNT(*) DESC
    """)
    print("\nTruth states:")
    for s, c in cur.fetchall():
        print(f"  {s:20} {c}")

    cur.execute("""
        SELECT trust_score, title, truth_state FROM verified_records
        ORDER BY trust_score DESC LIMIT 5
    """)
    print("\nTop trust scores:")
    for score, title, state in cur.fetchall():
        print(f"  {score:3} | {str(title)[:50]:50} | {state}")

    conn.close()


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=" * 70)
    print("OIE VERIFICATION ENGINE")
    print("=" * 70)

    # Step 1: Schema
    create_verification_schema()

    # Step 2: Verify all jobs
    print("\nStarting batch verification...")
    verify_all_jobs(limit=100)

    # Step 3: Report
    verification_report()

    print("\nDone.")