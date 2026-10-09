"""
OIE Cleaner — HTML strip + normalize + salary extract
Run once on existing data, then integrate into save_job
"""
import re
import sqlite3

DB = "ai_glue.db"


def strip_html(text):
    if not text:
        return ""
    text = re.sub(r"<script[^>]*>.*?</script>", " ", text, flags=re.DOTALL | re.I)
    text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.DOTALL | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("&nbsp;", " ").replace("&amp;", "&")
    text = text.replace("&lt;", "<").replace("&gt;", ">")
    text = text.replace("&#39;", "'").replace("&quot;", '"')
    text = re.sub(r"\s+", " ", text)
    return text.strip()


CONTRACT_MAP = {
    "FULL_TIME": "FULL_TIME",
    "FULL TIME": "FULL_TIME",
    "FULLTIME": "FULL_TIME",
    "PART_TIME": "PART_TIME",
    "PART TIME": "PART_TIME",
    "CONTRACT": "CONTRACT",
    "CONTRACTOR": "CONTRACT",
    "FREELANCE": "FREELANCE",
    "INTERNSHIP": "INTERNSHIP",
    "TEMPORARY": "TEMPORARY",
    "OTHER": "OTHER",
}


def normalize_contract(ct):
    if not ct:
        return "UNKNOWN"
    key = str(ct).upper().strip().replace("-", "_")
    return CONTRACT_MAP.get(key, "OTHER")


COUNTRY_MAP = {
    "USA": "United States",
    "US": "United States",
    "UNITED STATES OF AMERICA": "United States",
    "UK": "United Kingdom",
    "GREAT BRITAIN": "United Kingdom",
    "ENGLAND": "United Kingdom",
    "UAE": "United Arab Emirates",
    "EMIRATES": "United Arab Emirates",
}


def normalize_country(c):
    if not c:
        return "UNKNOWN"
    c = str(c).strip()
    # Multi-country: take first
    if "," in c:
        c = c.split(",")[0].strip()
    key = c.upper()
    return COUNTRY_MAP.get(key, c)


def extract_salary(text):
    """Try to find salary in description"""
    if not text:
        return 0, "UNKNOWN"
    patterns = [
        r"\$\s*([\d,]+)(?:k|K)?",
        r"USD\s*([\d,]+)",
        r"€\s*([\d,]+)",
        r"£\s*([\d,]+)",
    ]
    for p in patterns:
        m = re.search(p, text)
        if m:
            try:
                val = int(m.group(1).replace(",", ""))
                if val < 1000:
                    val *= 1000  # handle "50k" style
                return val, ("USD" if "$" in p else "EUR" if "€" in p else "GBP")
            except Exception:
                pass
    return 0, "UNKNOWN"


def clean_all():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("SELECT id, work_scope, contract_type, country, salary FROM opportunities")
    rows = cur.fetchall()

    print(f"Cleaning {len(rows)} opportunities...")
    changed = 0

    for oid, ws, ct, country, salary in rows:
        new_ws = strip_html(ws)[:500] if ws else ""
        new_ct = normalize_contract(ct)
        new_country = normalize_country(country)

        # Salary extract from work_scope if 0
        new_salary = salary
        if (not salary or str(salary) == "0") and new_ws:
            val, _ = extract_salary(new_ws)
            if val > 0:
                new_salary = str(val)

        if (new_ws != ws or new_ct != ct or new_country != country
                or new_salary != salary):
            cur.execute("""
                UPDATE opportunities
                SET work_scope=?, contract_type=?, country=?, salary=?
                WHERE id=?
            """, (new_ws, new_ct, new_country, str(new_salary), oid))
            changed += 1

    # Also clean claims
    cur.execute("SELECT id, claimed_value FROM claims WHERE field_name='work_scope'")
    for cid, val in cur.fetchall():
        cleaned = strip_html(val)[:500] if val else ""
        if cleaned != val:
            cur.execute("UPDATE claims SET claimed_value=? WHERE id=?", (cleaned, cid))

    conn.commit()

    # Stats
    print(f"\nCleaned {changed} records")
    print("\n" + "=" * 60)
    print("AFTER CLEANING")
    print("=" * 60)

    cur.execute("SELECT contract_type, COUNT(*) FROM opportunities GROUP BY contract_type")
    print("\nContract Types:")
    for ct, c in cur.fetchall():
        print(f"  {str(ct):20} {c}")

    cur.execute("SELECT country, COUNT(*) FROM opportunities GROUP BY country ORDER BY COUNT(*) DESC LIMIT 15")
    print("\nTop Countries:")
    for co, c in cur.fetchall():
        print(f"  {str(co):25} {c}")

    cur.execute("SELECT COUNT(*) FROM opportunities WHERE CAST(salary AS INTEGER) > 0")
    print(f"\nJobs with salary: {cur.fetchone()[0]}")

    conn.close()


if __name__ == "__main__":
    clean_all()