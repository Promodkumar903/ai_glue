"""
OIE Pipeline — Discovery -> Extraction -> Evidence -> Verification
"""
import os
import re
import json
import uuid
import sqlite3
import requests
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

DB = "ai_glue.db"
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


SCHEMA_FIELDS = [
    "title", "country", "city", "salary", "currency",
    "visa_sponsorship", "accommodation", "airfare", "food",
    "transport", "experience_years", "education", "language",
    "skills", "application_url",
]

SOURCE_TIERS = {"GOV": 1, "EMPLOYER": 2, "AGENCY": 3, "PORTAL": 4}


def fetch_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml",
    }
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    return r.text


def strip_html(html):
    html = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.DOTALL | re.I)
    html = re.sub(r"<style[^>]*>.*?</style>", " ", html, flags=re.DOTALL | re.I)
    text = re.sub(r"<[^>]+>", " ", html)
    text = text.replace("&nbsp;", " ").replace("&amp;", "&")
    text = text.replace("&lt;", "<").replace("&gt;", ">")
    text = text.replace("&#39;", "'").replace("&quot;", '"')
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_with_groq(text, url):
    if not client:
        return {"error": "Groq client not configured"}
    prompt = "You are an extraction engine for an opportunity platform.\n\n"
    prompt += "URL: " + url + "\n\n"
    prompt += "TEXT:\n" + text[:5000] + "\n\n"
    prompt += "Return ONLY valid JSON with these 15 fields:\n"
    prompt += '{\n'
    prompt += '  "title": "job title",\n'
    prompt += '  "country": "country or UNKNOWN",\n'
    prompt += '  "city": "city or UNKNOWN",\n'
    prompt += '  "salary": 0,\n'
    prompt += '  "currency": "EUR/USD/etc or UNKNOWN",\n'
    prompt += '  "visa_sponsorship": "true/false/UNKNOWN",\n'
    prompt += '  "accommodation": "true/false/UNKNOWN",\n'
    prompt += '  "airfare": "true/false/UNKNOWN",\n'
    prompt += '  "food": "true/false/UNKNOWN",\n'
    prompt += '  "transport": "true/false/UNKNOWN",\n'
    prompt += '  "experience_years": 0,\n'
    prompt += '  "education": "level or UNKNOWN",\n'
    prompt += '  "language": "languages or UNKNOWN",\n'
    prompt += '  "skills": [],\n'
    prompt += '  "application_url": "link or UNKNOWN"\n'
    prompt += '}\n\n'
    prompt += 'RULES:\n'
    prompt += '- If not mentioned, use "UNKNOWN" or 0 or []\n'
    prompt += '- Do NOT guess\n'
    prompt += '- Return JSON only'

    resp = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=1200,
    )
    content = resp.choices[0].message.content.strip()
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    content = content.strip()
    try:
        return json.loads(content)
    except Exception as e:
        return {"error": "JSON parse failed: " + str(e), "raw": content[:500]}


def extract_evidence(text, extracted):
    evidence = {}
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if len(s.strip()) > 20]
    for field in SCHEMA_FIELDS:
        value = extracted.get(field)
        if value in ("UNKNOWN", None, "", 0, []) and field != "visa_sponsorship":
            continue
        key = field.replace("_", " ").lower()
        for s in sentences:
            sl = s.lower()
            if key in sl:
                evidence[field] = {"text": s[:250]}
                break
            if isinstance(value, str) and value != "UNKNOWN" and value.lower() in sl:
                evidence[field] = {"text": s[:250]}
                break
    return evidence


def verify_claim(field, value, has_evidence, source_type):
    if value in ("UNKNOWN", None, "", 0, []):
        return "UNKNOWN", 0.0
    if not has_evidence:
        return "UNKNOWN", 0.0
    if source_type == "GOV":
        return "CONFIRMED", 0.95
    if source_type == "EMPLOYER":
        return "SUPPORTED", 0.80
    if source_type == "AGENCY":
        return "SUPPORTED", 0.60
    return "SUPPORTED", 0.50


def save_opportunity(url, source_type, extracted, evidence):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    opp_id = str(uuid.uuid4())
    org_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    cur.execute("""
        INSERT INTO opportunities
        (id, organization_id, type, title, description, status, first_seen, last_seen,
         created_at, updated_at, country, salary, company, location)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        opp_id,
        org_id,
        "JOB",
        extracted.get("title", "Unknown"),
        url,
        "DISCOVERED",
        now, now, now, now,
        extracted.get("country", ""),
        str(extracted.get("salary", "")),
        "",
        extracted.get("city", ""),
    ))

    source_tier = SOURCE_TIERS.get(source_type, 4)
    for field in SCHEMA_FIELDS:
        value = extracted.get(field)
        if value in (None, "", [], 0) and field != "visa_sponsorship":
            continue
        has_ev = field in evidence
        truth, conf = verify_claim(field, value, has_ev, source_type)
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
                (id, claim_id, source_id, captured_at, hash, confidence, freshness_days, valid_until)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (ev_id, claim_id, url, now, str(hash(evidence[field]["text"]))[:32], conf, 0, None))

    conn.commit()
    conn.close()
    return opp_id


def run_pipeline(url, source_type="GOV"):
    print("=" * 60)
    print("URL: " + url)
    print("Source: " + source_type)
    print("=" * 60)

    print("\n[1/4] Discovery: fetching...")
    try:
        html = fetch_page(url)
        print("  OK: " + str(len(html)) + " bytes")
    except Exception as e:
        print("  FAIL: " + str(e))
        return None

    print("[2/4] Extraction...")
    text = strip_html(html)
    print("  Text: " + str(len(text)) + " chars")
    if len(text) < 500:
        print("  WARN: text too short (JS-heavy page?)")

    extracted = extract_with_groq(text, url)
    if "error" in extracted:
        print("  FAIL: " + extracted["error"])
        return None
    print("  Title: " + str(extracted.get("title")))
    print("  Country: " + str(extracted.get("country")))

    print("[3/4] Evidence...")
    evidence = extract_evidence(text, extracted)
    print("  Evidence found for " + str(len(evidence)) + " fields")

    print("[4/4] Save...")
    opp_id = save_opportunity(url, source_type, extracted, evidence)
    print("  Saved: " + opp_id)
    return opp_id


if __name__ == "__main__":
    test_url = "https://en.wikipedia.org/wiki/Nursing_in_Germany"
    run_pipeline(test_url, source_type="GOV")

    print("\n" + "=" * 60)
    print("DB CHECK")
    print("=" * 60)
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM opportunities WHERE status='DISCOVERED'")
    print("Opportunities: " + str(cur.fetchone()[0]))
    cur.execute("SELECT COUNT(*) FROM claims")
    print("Claims: " + str(cur.fetchone()[0]))
    cur.execute("SELECT field_name, truth_state, confidence FROM claims LIMIT 15")
    print("Sample claims:")
    for r in cur.fetchall():
        print("  " + str(r[0]) + " | " + str(r[1]) + " | " + str(r[2]))
    conn.close()