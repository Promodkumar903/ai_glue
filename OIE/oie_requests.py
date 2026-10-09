"""
OIE Request System
- Admin sends requests to genuine agents/brokers/unis
- Auto-suggest best entity for a task
- Track responses
"""
import sqlite3
import uuid
import json
from datetime import datetime

DB = "ai_glue.db"


# ============================================================
# REQUEST SCHEMA
# ============================================================
def ensure_request_schema():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS oie_requests (
            id TEXT PRIMARY KEY,
            from_entity_id TEXT,
            from_name TEXT,
            from_role TEXT,
            to_entity_id TEXT,
            to_name TEXT,
            to_role TEXT,
            request_type TEXT,
            subject TEXT,
            message TEXT,
            context_json TEXT,
            priority TEXT DEFAULT 'NORMAL',
            status TEXT DEFAULT 'PENDING',
            response_text TEXT,
            response_at TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)

    # Auto-suggest log
    cur.execute("""
        CREATE TABLE IF NOT EXISTS oie_suggestions (
            id TEXT PRIMARY KEY,
            task_type TEXT,
            context_key TEXT,
            suggested_entity_id TEXT,
            match_score INTEGER,
            reasons TEXT,
            chosen INTEGER DEFAULT 0,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("OK: Request schema ready")


# ============================================================
# SUGGEST BEST ENTITY FOR A TASK
# ============================================================
def suggest_entity_for_task(task_type, country="", specialization="", min_trust=70):
    """
    Given a task (e.g. "nurse placement to Germany"), find best entities
    task_type: 'PLACEMENT' | 'STUDENT_ADMISSION' | 'VISA_HELP' | 'HIRING' | 'COUNSELING'
    """
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # Get candidates
    cur.execute("""
        SELECT id, entity_type, name, country, specializations,
               countries_served, trust_score, total_placements,
               avg_response_time_hours
        FROM registry_entities
        WHERE is_verified=1 AND is_genuine=1 AND is_active=1
          AND trust_score >= ?
    """, (min_trust,))
    candidates = [dict(zip([d[0] for d in cur.description], r)) for r in cur.fetchall()]
    conn.close()

    # Score each candidate
    scored = []
    for c in candidates:
        score = 0
        reasons = []

        # Trust base
        score += c['trust_score'] * 0.4

        # Country match
        if country:
            if country.lower() in (c['countries_served'] or "").lower():
                score += 25
                reasons.append(f"Operates in {country}")

        # Specialization match
        if specialization:
            if specialization.lower() in (c['specializations'] or "").lower():
                score += 20
                reasons.append(f"Specializes in {specialization}")

        # Placement history
        if c['total_placements'] and c['total_placements'] > 0:
            score += min(c['total_placements'] / 5, 10)
            reasons.append(f"{c['total_placements']} past placements")

        # Response time
        if c['avg_response_time_hours'] and c['avg_response_time_hours'] < 24:
            score += 5
            reasons.append("Fast responder")

        scored.append({
            "entity_id": c['id'],
            "name": c['name'],
            "entity_type": c['entity_type'],
            "country": c['country'],
            "trust_score": c['trust_score'],
            "match_score": min(100, int(score)),
            "reasons": reasons,
        })

    scored.sort(key=lambda x: x['match_score'], reverse=True)
    return scored[:5]


# ============================================================
# CREATE REQUEST
# ============================================================
def create_request(from_entity_id, from_name, from_role,
                   to_entity_id, request_type, subject, message,
                   context=None, priority="NORMAL"):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()

    # Get receiver name
    cur.execute("SELECT name, entity_type FROM registry_entities WHERE id=?",
                (to_entity_id,))
    recv = cur.fetchone()
    if not recv:
        conn.close()
        return {"error": "Receiver not found"}

    req_id = str(uuid.uuid4())
    cur.execute("""
        INSERT INTO oie_requests
        (id, from_entity_id, from_name, from_role,
         to_entity_id, to_name, to_role,
         request_type, subject, message, context_json,
         priority, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        req_id, from_entity_id, from_name, from_role,
        to_entity_id, recv[0], recv[1],
        request_type, subject, message,
        json.dumps(context or {}),
        priority, "PENDING", now, now
    ))

    conn.commit()
    conn.close()
    return {"id": req_id, "status": "SENT", "to": recv[0]}


# ============================================================
# RESPOND TO REQUEST
# ============================================================
def respond_to_request(request_id, response_text, accept=True):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()

    status = "ACCEPTED" if accept else "DECLINED"
    cur.execute("""
        UPDATE oie_requests
        SET status=?, response_text=?, response_at=?, updated_at=?
        WHERE id=?
    """, (status, response_text, now, now, request_id))

    conn.commit()
    conn.close()
    return {"id": request_id, "status": status}


# ============================================================
# LIST REQUESTS
# ============================================================
def list_requests(status="", to_entity_id="", limit=50):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    clauses = ["1=1"]
    params = []
    if status:
        clauses.append("status=?")
        params.append(status)
    if to_entity_id:
        clauses.append("to_entity_id=?")
        params.append(to_entity_id)
    where = " AND ".join(clauses)
    params.append(limit)

    cur.execute(f"""
        SELECT id, from_name, to_name, request_type, subject,
               priority, status, created_at
        FROM oie_requests WHERE {where}
        ORDER BY created_at DESC LIMIT ?
    """, params)
    rows = [dict(zip([d[0] for d in cur.description], r)) for r in cur.fetchall()]
    conn.close()
    return {"count": len(rows), "requests": rows}


# ============================================================
# DEMO
# ============================================================
def demo():
    print("\n" + "=" * 70)
    print("DEMO — Auto-suggest for Germany nursing placement")
    print("=" * 70)

    suggestions = suggest_entity_for_task(
        task_type="PLACEMENT",
        country="Germany",
        specialization="Healthcare"
    )

    if not suggestions:
        print("\nNo verified entities found yet.")
        print("First run: python OIE\\oie_registry.py")
        print("Then verify entities: admin action required.")
        return

    print(f"\nFound {len(suggestions)} suggestions:")
    for i, s in enumerate(suggestions, 1):
        print(f"\n[{i}] {s['name']} ({s['entity_type']})")
        print(f"    Country: {s['country']} | Trust: {s['trust_score']}")
        print(f"    Match Score: {s['match_score']}/100")
        print(f"    Reasons: {', '.join(s['reasons'])}")

    # Demo: Send request to top entity
    if suggestions:
        top = suggestions[0]
        print(f"\n" + "=" * 70)
        print(f"Sending demo request to: {top['name']}")
        print("=" * 70)
        result = create_request(
            from_entity_id="admin-001",
            from_name="AI Glue Admin",
            from_role="ADMIN",
            to_entity_id=top['entity_id'],
            request_type="PLACEMENT",
            subject="Need 20 nurses for Germany placement",
            message="We have 20 verified nurses (B1 German, 2+ years experience) looking for placement in Germany. Can you help?",
            context={"nurses": 20, "country": "Germany", "language": "B1"},
            priority="HIGH"
        )
        print(f"  Request ID: {result.get('id')}")
        print(f"  Status: {result.get('status')}")
        print(f"  To: {result.get('to')}")

    # List
    print("\n" + "=" * 70)
    print("ALL REQUESTS")
    print("=" * 70)
    r = list_requests()
    for req in r['requests']:
        print(f"  [{req['status']:10}] {req['from_name'][:20]:20} → {req['to_name'][:20]:20} | {req['subject'][:40]}")


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=" * 70)
    print("OIE REQUEST SYSTEM")
    print("=" * 70)
    ensure_request_schema()
    demo()
    print("\nDone.")