"""
OIE Benefits Extractor
Groq reads job description → extracts 25+ benefit fields automatically
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


PROMPT = """You are a job offer analyzer. Read the job description and extract ALL work conditions. Return ONLY valid JSON.

JOB TITLE: {title}
COUNTRY: {country}
DESCRIPTION:
{description}

Extract these fields (use 0/NO/UNKNOWN if not mentioned):

{{
  "visa_free": 0 or 1,
  "visa_type": "type or UNKNOWN",
  "ticket_free": 0 or 1,
  "ticket_type": "one-way/return/full or UNKNOWN",
  "airport_pickup": 0 or 1,
  "accommodation": 0 or 1,
  "accommodation_type": "shared/private/dormitory or UNKNOWN",
  "accommodation_ac": 0 or 1,
  "food_lunch": 0 or 1,
  "food_dinner": 0 or 1,
  "food_breakfast": 0 or 1,
  "food_allowance_usd": 0,
  "hours_per_day": 8.0,
  "days_per_week": 5,
  "overtime_available": 0 or 1,
  "overtime_rate": "1.5x or UNKNOWN",
  "off_days": "Sat-Sun / Friday / Rotating / UNKNOWN",
  "shift_timing": "9-6 PM or UNKNOWN",
  "shift_type": "DAY/NIGHT/ROTATING/FLEXIBLE/UNKNOWN",
  "night_shift": 0 or 1,
  "medical_insurance": 0 or 1,
  "transport_free": 0 or 1,
  "uniform_free": 0 or 1,
  "contract_duration_months": 0,
  "contract_extension": "Yes/No/UNKNOWN",
  "leave_days_per_year": 0,
  "leave_ticket": 0 or 1,
  "visa_sponsorship": "YES/NO/UNKNOWN",
  "relocation_support": "YES/NO/UNKNOWN",
  "language_required": "English or UNKNOWN"
}}

RULES:
- Only extract if explicitly mentioned in description
- If not mentioned → 0 or "UNKNOWN"
- Do NOT guess
- Return JSON only"""


def create_table_if_missing():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS job_benefits_deep (
            id TEXT PRIMARY KEY,
            company_name TEXT, country TEXT, job_title TEXT, category TEXT,
            visa_free INTEGER DEFAULT 0, visa_type TEXT,
            ticket_free INTEGER DEFAULT 0, ticket_type TEXT, airport_pickup INTEGER DEFAULT 0,
            accommodation INTEGER DEFAULT 0, accommodation_type TEXT,
            accommodation_shared INTEGER DEFAULT 0, accommodation_ac INTEGER DEFAULT 0,
            food_lunch INTEGER DEFAULT 0, food_dinner INTEGER DEFAULT 0,
            food_breakfast INTEGER DEFAULT 0, food_allowance_usd REAL DEFAULT 0,
            hours_per_day REAL DEFAULT 0, days_per_week INTEGER DEFAULT 0,
            overtime_available INTEGER DEFAULT 0, overtime_rate TEXT, off_days TEXT,
            shift_timing TEXT, shift_type TEXT, night_shift INTEGER DEFAULT 0,
            medical_insurance INTEGER DEFAULT 0, transport_free INTEGER DEFAULT 0,
            uniform_free INTEGER DEFAULT 0,
            contract_duration_months INTEGER DEFAULT 0, contract_extension TEXT,
            leave_days_per_year INTEGER DEFAULT 0, leave_ticket INTEGER DEFAULT 0,
            source TEXT, verified INTEGER DEFAULT 0, updated_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def extract_benefits(title, country, description):
    if not client:
        return {"error": "Groq not configured"}
    if not description or len(description) < 50:
        return {"error": "description too short"}

    desc = re.sub(r"<[^>]+>", " ", description)[:4000]
    desc = re.sub(r"\s+", " ", desc)

    try:
        resp = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": PROMPT.format(
                title=title or "Unknown", country=country or "Unknown", description=desc)}],
            temperature=0.1,
            max_tokens=2000,
        )
        content = resp.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        return json.loads(content.strip())
    except Exception as e:
        return {"error": str(e)}


def save_benefits(company, country, title, category, data):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()

    # Check if already exists
    cur.execute("""
        SELECT id FROM job_benefits_deep
        WHERE company_name=? AND job_title=?
    """, (company, title))
    if cur.fetchone():
        conn.close()
        return False

    bid = str(uuid.uuid4())
    cur.execute("""
        INSERT INTO job_benefits_deep
        (id, company_name, country, job_title, category,
         visa_free, visa_type, ticket_free, ticket_type, airport_pickup,
         accommodation, accommodation_type, accommodation_shared, accommodation_ac,
         food_lunch, food_dinner, food_breakfast, food_allowance_usd,
         hours_per_day, days_per_week, overtime_available, overtime_rate, off_days,
         shift_timing, shift_type, night_shift,
         medical_insurance, transport_free, uniform_free,
         contract_duration_months, contract_extension,
         leave_days_per_year, leave_ticket,
         source, verified, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        bid, company, country, title, category,
        data.get("visa_free", 0), data.get("visa_type", "UNKNOWN"),
        data.get("ticket_free", 0), data.get("ticket_type", "UNKNOWN"),
        data.get("airport_pickup", 0),
        data.get("accommodation", 0), data.get("accommodation_type", "UNKNOWN"),
        0, data.get("accommodation_ac", 0),
        data.get("food_lunch", 0), data.get("food_dinner", 0),
        data.get("food_breakfast", 0), data.get("food_allowance_usd", 0),
        data.get("hours_per_day", 0), data.get("days_per_week", 0),
        data.get("overtime_available", 0), data.get("overtime_rate", "UNKNOWN"),
        data.get("off_days", "UNKNOWN"),
        data.get("shift_timing", "UNKNOWN"), data.get("shift_type", "UNKNOWN"),
        data.get("night_shift", 0),
        data.get("medical_insurance", 0), data.get("transport_free", 0),
        data.get("uniform_free", 0),
        data.get("contract_duration_months", 0), data.get("contract_extension", "UNKNOWN"),
        data.get("leave_days_per_year", 0), data.get("leave_ticket", 0),
        "groq_extract", 0, now
    ))

    conn.commit()
    conn.close()
    return True


def process_jobs(limit=20):
    """Extract benefits from existing opportunities"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        SELECT o.id, o.title, o.country, o.company, o.work_scope
        FROM opportunities o
        WHERE o.status='DISCOVERED'
          AND o.work_scope IS NOT NULL
          AND length(o.work_scope) > 100
          AND NOT EXISTS (
              SELECT 1 FROM job_benefits_deep jbd
              WHERE jbd.job_title = o.title AND jbd.company_name = o.company
          )
        LIMIT ?
    """, (limit,))
    jobs = cur.fetchall()
    conn.close()

    print(f"Processing {len(jobs)} jobs for deep extraction...\n")

    saved = 0
    for i, (oid, title, country, company, work_scope) in enumerate(jobs, 1):
        print(f"[{i}/{len(jobs)}] {str(title)[:50]}")
        result = extract_benefits(title, country, work_scope)
        if "error" in result:
            print(f"    FAIL: {result['error']}")
            continue

        # Check if any field actually extracted
        has_data = any(result.get(k) not in (0, "", "UNKNOWN", None) for k in [
            "visa_free", "ticket_free", "accommodation", "food_lunch",
            "hours_per_day", "overtime_available", "medical_insurance"
        ])

        if not has_data:
            print(f"    skip (no benefits mentioned)")
            continue

        if save_benefits(company or "Unknown", country or "Unknown",
                         title, "", result):
            saved += 1
            print(f"    ✅ Visa:{result.get('visa_free')} Ticket:{result.get('ticket_free')} "
                  f"Accom:{result.get('accommodation')} Food:{result.get('food_lunch')} "
                  f"Hrs:{result.get('hours_per_day')}")

    print(f"\n{'='*60}")
    print(f"Saved: {saved} new benefit records")


def report():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM job_benefits_deep")
    total = cur.fetchone()[0]
    print(f"\nTotal benefit records: {total}")

    cur.execute("SELECT COUNT(*) FROM job_benefits_deep WHERE visa_free=1")
    print(f"Free visa: {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM job_benefits_deep WHERE ticket_free=1")
    print(f"Free ticket: {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM job_benefits_deep WHERE accommodation=1")
    print(f"Accommodation: {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM job_benefits_deep WHERE food_lunch=1 OR food_dinner=1")
    print(f"Food provided: {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM job_benefits_deep WHERE overtime_available=1")
    print(f"Overtime: {cur.fetchone()[0]}")
    conn.close()


if __name__ == "__main__":
    print("=" * 70)
    print("OIE BENEFITS EXTRACTOR — Auto from Descriptions")
    print("=" * 70)
    create_table_if_missing()
    process_jobs(limit=20)
    report()
    print("\nDone.")