"""
OIE Admin Actions — Verify, Reject, Contact log
For admin to manually verify each job with HR
"""
import sqlite3
import uuid
from datetime import datetime

DB = "ai_glue.db"


# ============================================================
# CONTACT ATTEMPT LOG
# ============================================================
def ensure_contact_log():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS hr_contact_log (
            id TEXT PRIMARY KEY,
            hr_contact_id TEXT,
            company_name TEXT,
            attempt_type TEXT,
            contacted_by TEXT,
            attempt_date TEXT,
            notes TEXT,
            outcome TEXT,
            next_action TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def log_contact(company_name, attempt_type, contacted_by, notes="", outcome=""):
    """
    attempt_type: 'EMAIL'|'PHONE'|'WHATSAPP'|'WEBSITE'
    outcome: 'NO_ANSWER'|'WRONG_INFO'|'VERIFIED'|'CALL_BACK'|'DECLINED'
    """
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()

    # Get hr_contact_id
    cur.execute("SELECT id FROM hr_contacts WHERE company_name=?", (company_name,))
    row = cur.fetchone()
    hid = row[0] if row else None

    # Next action based on outcome
    next_actions = {
        "NO_ANSWER": "Try again tomorrow",
        "WRONG_INFO": "Find correct HR",
        "VERIFIED": "Mark verified, publish",
        "CALL_BACK": "Follow up in 24h",
        "DECLINED": "Mark rejected",
    }

    lid = str(uuid.uuid4())
    cur.execute("""
        INSERT INTO hr_contact_log
        (id, hr_contact_id, company_name, attempt_type, contacted_by,
         attempt_date, notes, outcome, next_action, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        lid, hid, company_name, attempt_type, contacted_by,
        now, notes, outcome, next_actions.get(outcome, ""), now
    ))

    # If verified, update job verification status
    if outcome == "VERIFIED":
        cur.execute("""
            UPDATE hr_contacts
            SET verification_status='VERIFIED',
                verified_by=?, verified_at=?, last_contact_attempt=?
            WHERE company_name=?
        """, (contacted_by, now, now, company_name))

        cur.execute("""
            UPDATE job_benefits_deep
            SET verified=1, updated_at=?
            WHERE company_name=?
        """, (now, company_name))

    elif outcome == "DECLINED":
        cur.execute("""
            UPDATE hr_contacts
            SET verification_status='REJECTED',
                verified_at=?, last_contact_attempt=?
            WHERE company_name=?
        """, (now, now, company_name))

    # Update attempt counter
    cur.execute("""
        UPDATE hr_contacts
        SET contact_attempts = COALESCE(contact_attempts, 0) + 1,
            last_contact_attempt = ?
        WHERE company_name=?
    """, (now, company_name))

    conn.commit()
    conn.close()
    return {"id": lid, "company": company_name, "outcome": outcome}


# ============================================================
# ADMIN ACTIONS
# ============================================================
def admin_verify(company_name, admin_id, notes=""):
    """Mark job as verified and ready for publish"""
    return log_contact(company_name, "PHONE", admin_id,
                       notes=notes, outcome="VERIFIED")


def admin_reject(company_name, admin_id, reason=""):
    """Reject this job — don't publish"""
    return log_contact(company_name, "PHONE", admin_id,
                       notes=f"Rejected: {reason}", outcome="DECLINED")


def admin_request_info(company_name, admin_id, message=""):
    """Request more info — mark for review"""
    return log_contact(company_name, "EMAIL", admin_id,
                       notes=f"Requested info: {message}", outcome="CALL_BACK")


# ============================================================
# ADMIN WORKLIST — What needs action
# ============================================================
def admin_worklist():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
        SELECT
            jbd.company_name,
            jbd.job_title,
            jbd.country,
            hrc.verification_status,
            hrc.hr_email,
            hrc.hr_phone,
            hrc.contact_attempts,
            hrc.last_contact_attempt,
            hrc.verified_at
        FROM job_benefits_deep jbd
        LEFT JOIN hr_contacts hrc ON LOWER(hrc.company_name) = LOWER(jbd.company_name)
        ORDER BY
            CASE hrc.verification_status
                WHEN 'PENDING' THEN 1
                WHEN 'VERIFIED' THEN 2
                WHEN 'REJECTED' THEN 3
                ELSE 4
            END,
            jbd.company_name
    """)

    print("\n" + "=" * 100)
    print("📋 ADMIN WORKLIST")
    print("=" * 100)
    print(f"\n{'Company':25} {'Job':25} {'Status':12} {'Attempts':9} {'Email':30}")
    print("-" * 100)

    pending = 0
    verified = 0
    rejected = 0

    for co, job, country, status, email, phone, att, last, vat in cur.fetchall():
        status = status or "PENDING"
        att = att or 0
        print(f"{str(co)[:25]:25} {str(job)[:25]:25} {status:12} {att:9} {str(email or '')[:30]:30}")
        if status == "PENDING": pending += 1
        elif status == "VERIFIED": verified += 1
        elif status == "REJECTED": rejected += 1

    print(f"\n📊 Summary:")
    print(f"   ⏳ Pending:  {pending}")
    print(f"   ✅ Verified: {verified}")
    print(f"   ❌ Rejected: {rejected}")

    conn.close()


def show_log(company_name=""):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    if company_name:
        cur.execute("""
            SELECT company_name, attempt_type, contacted_by, attempt_date,
                   outcome, notes, next_action
            FROM hr_contact_log WHERE company_name=?
            ORDER BY created_at DESC LIMIT 20
        """, (company_name,))
    else:
        cur.execute("""
            SELECT company_name, attempt_type, contacted_by, attempt_date,
                   outcome, notes, next_action
            FROM hr_contact_log ORDER BY created_at DESC LIMIT 20
        """)

    print(f"\n{'='*100}")
    print(f"📞 CONTACT LOG {'— ' + company_name if company_name else '(All)'}")
    print(f"{'='*100}")

    rows = cur.fetchall()
    if not rows:
        print("No contact attempts yet.")
    else:
        for co, at, by, dt, out, notes, next_act in rows:
            print(f"\n  [{out}] {co} via {at}")
            print(f"  By: {by} | When: {dt[:16] if dt else 'N/A'}")
            if notes: print(f"  Notes: {notes}")
            if next_act: print(f"  → Next: {next_act}")

    conn.close()


# ============================================================
# DEMO — Simulate admin working through worklist
# ============================================================
def demo():
    print("=" * 100)
    print("DEMO — Admin Verify Flow")
    print("=" * 100)

    # 1. Show worklist
    admin_worklist()

    # 2. Simulate 3 actions
    print(f"\n{'='*100}")
    print("SIMULATING ADMIN ACTIONS")
    print(f"{'='*100}")

    print("\n[1] Calling Saudi Aramco HR...")
    r = admin_verify("Saudi Aramco", "admin-001",
                     notes="Called +966-13-872-0115. Confirmed all details. Job is legit.")
    print(f"  → Status: {r['outcome']}")

    print("\n[2] Calling Charité Berlin HR...")
    r = admin_request_info("Charité Berlin", "admin-001",
                          message="Need updated salary range for 2025")
    print(f"  → Status: {r['outcome']}")

    print("\n[3] Rejecting fake company...")
    r = admin_reject("QuickVisa Guarantee", "admin-001",
                     reason="Could not verify license. No response in 3 days.")
    print(f"  → Status: {r['outcome']}")

    # 3. Show updated worklist
    admin_worklist()

    # 4. Show contact log
    show_log()


if __name__ == "__main__":
    print("=" * 100)
    print("OIE ADMIN ACTIONS — Verify, Reject, Log")
    print("=" * 100)
    ensure_contact_log()
    demo()
    print("\nDone.")