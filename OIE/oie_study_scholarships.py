"""
Study OIE — Real Scholarships for International Students
Data source: Official scholarship websites (2025-26)
"""
import sqlite3
import uuid
from datetime import datetime

DB = "ai_glue.db"

# (name, provider, country, amount_usd, coverage, subjects, eligibility, deadline, url)
SCHOLARSHIPS = [
    # ==== GERMANY ====
    ("DAAD Scholarship", "DAAD", "Germany", 12000,
     "Monthly stipend + travel + insurance",
     "All subjects",
     "Bachelor/Master/PhD, 2+ years work exp for some",
     "Varies (Oct-Jan)", "https://www.daad.de/en/"),

    ("Erasmus Mundus Joint Master", "EU Commission", "Europe", 25000,
     "Tuition + stipend + travel",
     "Multiple (varies by program)",
     "Bachelor degree, English proficiency",
     "Jan-Feb", "https://erasmus-plus.ec.europa.eu/"),

    ("Heinrich Böll Foundation", "HBS", "Germany", 10000,
     "Monthly stipend + insurance",
     "All subjects, focus on sustainability",
     "Excellent academic record, social engagement",
     "Varies", "https://www.boell.de/en"),

    ("Konrad-Adenauer-Stiftung", "KAS", "Germany", 10000,
     "Monthly stipend",
     "All subjects",
     "Academic excellence, political interest",
     "Varies", "https://www.kas.de/en/"),

    # ==== UK ====
    ("Chevening Scholarship", "UK Government", "United Kingdom", 35000,
     "Full tuition + living + travel",
     "All subjects",
     "Bachelor degree, 2 years work exp, IELTS 6.5",
     "Aug-Nov", "https://www.chevening.org/"),

    ("Commonwealth Scholarship", "Commonwealth", "United Kingdom", 30000,
     "Full tuition + stipend + travel",
     "Development-related subjects",
     "Citizens of Commonwealth countries",
     "Oct-Dec", "https://cscuk.fcdo.gov.uk/"),

    ("Rhodes Scholarship", "Rhodes Trust", "United Kingdom", 50000,
     "Full tuition + stipend",
     "All subjects (Oxford)",
     "Age 18-28, academic excellence",
     "Jun-Oct", "https://www.rhodeshouse.ox.ac.uk/"),

    ("Gates Cambridge", "Gates Foundation", "United Kingdom", 45000,
     "Full tuition + stipend",
     "All PhD/Masters (Cambridge)",
     "Non-UK citizens, academic excellence",
     "Oct-Dec", "https://www.gatescambridge.org/"),

    # ==== USA ====
    ("Fulbright Foreign Student", "US Government", "United States", 40000,
     "Tuition + living + travel",
     "All subjects",
     "Bachelor degree, English proficiency",
     "May-Jul", "https://foreign.fulbrightonline.org/"),

    ("Hubert Humphrey Fellowship", "US Government", "United States", 35000,
     "Tuition + stipend + travel",
     "Public service, policy",
     "Mid-career professionals",
     "Varies", "https://humphreyfellowship.org/"),

    # ==== CANADA ====
    ("Vanier Canada Graduate", "Canada Government", "Canada", 50000,
     "Stipend (3 years)",
     "PhD only",
     "Academic excellence, leadership",
     "Nov", "https://vanier.gc.ca/"),

    ("Lester B. Pearson Scholarship", "University of Toronto", "Canada", 40000,
     "Full tuition + living",
     "All undergrad subjects",
     "International students, academic excellence",
     "Nov-Jan", "https://future.utoronto.ca/"),

    # ==== AUSTRALIA ====
    ("Australia Awards", "Australian Government", "Australia", 35000,
     "Tuition + living + travel",
     "Development-related",
     "Citizens of developing countries",
     "Varies", "https://www.dfat.gov.au/"),

    ("Research Training Program", "Australian Government", "Australia", 30000,
     "Tuition + stipend",
     "Research Masters/PhD",
     "Academic excellence",
     "Varies", "https://www.education.gov.au/"),

    # ==== JAPAN ====
    ("MEXT Scholarship", "Japan Government", "Japan", 15000,
     "Tuition + monthly allowance + travel",
     "All subjects",
     "Age under 35, Bachelor degree",
     "Apr-May", "https://www.mext.go.jp/en/"),

    ("JASSO Scholarship", "JASSO", "Japan", 8000,
     "Monthly stipend",
     "All subjects",
     "Enrolled students in Japan",
     "Varies", "https://www.jasso.go.jp/en/"),

    # ==== NETHERLANDS ====
    ("Orange Tulip Scholarship", "Nuffic", "Netherlands", 20000,
     "Partial tuition",
     "All subjects",
     "Non-EU students",
     "Feb-Apr", "https://www.nuffic.nl/"),

    ("Holland Scholarship", "Dutch Government", "Netherlands", 5000,
     "One-time grant",
     "All subjects",
     "Non-EEA students",
     "Feb-May", "https://www.studyinnl.org/"),

    # ==== SWITZERLAND ====
    ("Swiss Government Excellence", "Swiss Government", "Switzerland", 30000,
     "Monthly stipend + tuition",
     "All subjects",
     "Master/PhD/Postdoc",
     "Varies", "https://www.sbfi.admin.ch/"),

    # ==== IRELAND ====
    ("Government of Ireland Scholarship", "Irish Government", "Ireland", 25000,
     "Tuition + stipend",
     "All subjects",
     "Non-EU students",
     "Varies", "https://hea.ie/"),

    # ==== SWEDEN ====
    ("Swedish Institute Scholarship", "SI", "Sweden", 30000,
     "Tuition + living + travel",
     "All subjects",
     "Citizens of 42 countries (includes India)",
     "Feb", "https://si.se/en/"),

    # ==== FINLAND ====
    ("Finland Scholarship", "Finnish Universities", "Finland", 20000,
     "Tuition + living",
     "All subjects",
     "Non-EU students",
     "Jan", "https://www.studyinfinland.fi/"),

    # ==== NORWAY ====
    ("Norwegian Quota Scheme", "Norway Government", "Norway", 25000,
     "Tuition + living",
     "All subjects",
     "Developing countries only",
     "Dec-Feb", "https://www.norway.no/"),
]


def seed_scholarships():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    inserted = 0

    for (name, provider, country, amount, coverage, subjects,
         eligibility, deadline, url) in SCHOLARSHIPS:

        # Check existing
        cur.execute("SELECT id FROM scholarships WHERE name=? AND provider=?",
                    (name, provider))
        if cur.fetchone():
            continue

        sid = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO scholarships
            (id, name, provider, country, amount_usd, coverage, subjects,
             eligibility, deadline, application_url, source_url, verified, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (sid, name, provider, country, amount, coverage, subjects,
              eligibility, deadline, url, url, 1, now))
        inserted += 1

    conn.commit()

    # Report
    cur.execute("SELECT COUNT(*) FROM scholarships")
    total = cur.fetchone()[0]
    conn.close()

    print(f"Inserted: {inserted} new scholarships")
    print(f"Total scholarships: {total}")


def link_to_universities():
    """Update study_opportunities — mark scholarship_available for matching countries"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # For each scholarship country, mark universities in that country
    cur.execute("SELECT DISTINCT country FROM scholarships")
    countries = [r[0] for r in cur.fetchall()]

    for country in countries:
        # Get total scholarship amount for this country
        cur.execute("SELECT SUM(amount_usd), COUNT(*) FROM scholarships WHERE country=?",
                    (country,))
        total_amt, count = cur.fetchone()

        cur.execute("""
            UPDATE study_opportunities
            SET scholarship_available = 1,
                scholarship_amount_usd = ?
            WHERE country = ?
        """, (total_amt or 0, country))
        print(f"  {country}: {cur.rowcount} universities marked (scholarships worth ${total_amt})")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    print("=" * 70)
    print("STUDY OIE — SCHOLARSHIPS SEED")
    print("=" * 70)
    seed_scholarships()

    print("\nLinking scholarships to universities...")
    link_to_universities()

    # Report
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    print("\n" + "=" * 70)
    print("SCHOLARSHIPS BY COUNTRY")
    print("=" * 70)
    cur.execute("""
        SELECT country, COUNT(*), SUM(amount_usd)
        FROM scholarships GROUP BY country ORDER BY COUNT(*) DESC
    """)
    for c, n, amt in cur.fetchall():
        print(f"  {str(c):20} {n} scholarships | ${amt:,.0f} total")

    cur.execute("SELECT COUNT(*) FROM study_opportunities WHERE scholarship_available=1")
    print(f"\nUniversities with scholarship: {cur.fetchone()[0]}")

    conn.close()