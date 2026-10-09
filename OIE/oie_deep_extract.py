"""
OIE Deep Extract — Groq reads job description, extracts details
Fills: visa_sponsorship, accommodation, salary, experience_years,
       language, education, airfare, food, transport
Saves as new claims with evidence.
"""
import os
import re
import json
import uuid
import sqlite3
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
DB = "ai_glue.db"
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Fields to extract from description
EXTRACT_FIELDS = [
    "visa_sponsorship", "accommodation", "airfare", "food",
    "transport", "salary", "currency", "experience_years",
    "education", "language",
]

PROMPT = """You are a strict extraction engine. Read this job description and extract ONLY what is explicitly stated. Do NOT guess.

JOB TITLE: {title}
JOB DESCRIPTION:
{description}

Return ONLY valid JSON:
{{
  "visa_sponsorship": "YES" | "NO" | "UNKNOWN",
  "accommodation": "YES" | "NO" | "UNKNOWN",
  "airfare": "YES" | "NO" | "UNKNOWN",
  "food": "YES" | "NO" | "UNKNOWN",
  "transport": "YES" | "NO" | "UNKNOWN",
  "salary": 0,
  "currency": "USD" | "EUR" | "GBP" | "INR" | "UNKNOWN",
  "experience_years": 0,
  "education": "degree level or UNKNOWN",
  "language": "language requirements or UNKNOWN",
  "evidence_sentences": {{
    "field_name": "exact sentence from description that supports it"
  }}
}}

RULES:
- If description says "visa sponsorship available" → visa_sponsorship: "YES"
- If not mentioned → "UNKNOWN"
- salary is a NUMBER only (annual). If "$50k/year" → 50000
- evidence_sentences: exact quote from description for each non-UNKNOWN field
- Return JSON only"""


def extract_deep(title, description):
    if not client:
        return {"error": "Groq not configured"}
    if not description or len(description) < 50:
        return {"error": "description too short"}

    desc = re.sub(r"<[^>]+>", " ", description)[:3000]
    desc = re.sub(r"\s+", " ", desc)

    try:
        resp = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": PROMPT.format(
                title=title or "Unknown", description=desc)}],
            temperature=0.1,
            max_tokens=1500,
        )
        content = resp.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        content = content.strip()
        return json.loads(content)
    except Exception as e:
        return {"error": str(e)}


def save_claim(opp_id, field, value, evidence_text, source="groq_extract"):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()

    # Skip if claim already exists for this field
    cur.execute("""
        SELECT id FROM claims WHERE opportunity_id=? AND field_name=?
        AND truth_state != 'UNKNOWN'
    """, (opp_id, field))
    if cur.fetchone():
        conn.close()
        return False

    claim_id = str(uuid.uuid4())
    conf = 0.70 if field == "salary" else 0.60

    cur.execute("""
        INSERT INTO claims
        (id, opportunity_id, field_name, claimed_value, truth_state,
         source_priority, confidence, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (claim_id, opp_id, field, str(value), "INFERRED", 3, conf, now, now))

    if evidence_text:
        ev_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO evidence
            (id, claim_id, source_id, captured_at, hash, confidence,
             freshness_days, valid_until)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (ev_id, claim_id, source, now, str(hash(evidence_text))[:32],
              conf, 0, None))

    conn.commit()
    conn.close()
    return True


def process_jobs(limit=30):
    """Extract deep info for jobs where visa/accommodation are UNKNOWN"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # Find jobs where visa_sponsorship is UNKNOWN and description exists
    cur.execute("""
        SELECT o.id, o.title, o.description
        FROM opportunities o
        WHERE o.status = 'DISCOVERED'
          AND o.description IS NOT NULL
          AND length(o.description) > 100
          AND NOT EXISTS (
              SELECT 1 FROM claims c
              WHERE c.opportunity_id = o.id
                AND c.field_name = 'visa_sponsorship'
                AND c.truth_state != 'UNKNOWN'
          )
        LIMIT ?
    """, (limit,))
    jobs = cur.fetchall()
    conn.close()

    print(f"Processing {len(jobs)} jobs for deep extraction...\n")

    saved_total = 0
    for i, (oid, title, url) in enumerate(jobs, 1):
        print(f"[{i}/{len(jobs)}] {str(title)[:50]}")
        # description field holds URL for API jobs — we need actual description
        # For now, use the work_scope which has the description text
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute("SELECT work_scope FROM opportunities WHERE id=?", (oid,))
        row = cur.fetchone()
        conn.close()

        work_scope = row[0] if row else ""
        if not work_scope or len(work_scope) < 50:
            print(f"    skip (no work_scope)")
            continue

        result = extract_deep(title, work_scope)
        if "error" in result:
            print(f"    FAIL: {result['error']}")
            continue

        ev = result.get("evidence_sentences", {})
        saved = 0
        for field in EXTRACT_FIELDS:
            val = result.get(field)
            if val in (None, "", "UNKNOWN", 0):
                continue
            if save_claim(oid, field, val, ev.get(field, "")):
                saved += 1

        print(f"    Saved {saved} new claims")
        saved_total += saved

    print(f"\nTotal new claims: {saved_total}")

    # Report
    print("\n" + "=" * 70)
    print("AFTER DEEP EXTRACT")
    print("=" * 70)
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""SELECT truth_state, COUNT(*) FROM claims
                   GROUP BY truth_state""")
    for s, c in cur.fetchall():
        print(f"  {s:15} {c}")
    cur.execute("""SELECT field_name, COUNT(*) FROM claims
                   WHERE field_name IN ('visa_sponsorship', 'accommodation',
                   'airfare', 'salary', 'experience_years', 'language')
                   AND truth_state != 'UNKNOWN'
                   GROUP BY field_name""")
    print("\nExtracted detail fields:")
    for f, c in cur.fetchall():
        print(f"  {f:20} {c}")
    conn.close()


if __name__ == "__main__":
    process_jobs(limit=30)