"""
OIE Job Categorizer — Job title se category nikaalo
"""
import re
import sqlite3
import json
import uuid
from datetime import datetime

DB = "ai_glue.db"

# Category rules — keyword → category
CATEGORY_RULES = [
    # IT / Software
    ("IT_SOFTWARE", [
        "developer", "engineer", "software", "programmer", "devops",
        "backend", "frontend", "fullstack", "full-stack", "full stack",
        "data scientist", "data engineer", "ml engineer", "ai engineer",
        "machine learning", "python", "java", "kotlin", "golang",
        "react", "node", "architect", "sre", "cloud", "kubernetes",
        "qa engineer", "test engineer", "cybersecurity", "security engineer",
        "platform engineer", "infrastructure",
    ]),
    # Healthcare
    ("HEALTHCARE", [
        "nurse", "nursing", "doctor", "physician", "surgeon", "medical",
        "clinical", "healthcare", "pharmacist", "therapist", "dentist",
        "caregiver", "care worker", "patient", "hospital", "rn ", " rn,",
    ]),
    # Sales / Business Development
    ("SALES_BD", [
        "sales", "account executive", "business development", "bd ",
        "account manager", "growth manager", "partnership", "revenue",
    ]),
    # Marketing
    ("MARKETING", [
        "marketing", "seo", "content", "copywriter", "brand",
        "social media", "advertis", "campaign", "growth",
    ]),
    # Finance / Accounting
    ("FINANCE", [
        "finance", "financial", "accountant", "accounting", "audit",
        "fp&a", "cfo", "controller", "treasurer", "tax", "receivable",
    ]),
    # Engineering (non-IT)
    ("ENGINEERING", [
        "mechanical", "electrical", "civil", "chemical", "industrial engineer",
        "manufacturing engineer", "construction", "welder", "electrician",
        "plumber", "hvac", "machinist", "cnc",
    ]),
    # Education
    ("EDUCATION", [
        "teacher", "professor", "tutor", "educator", "instructor",
        "lecturer", "academic", "school", "university",
    ]),
    # Logistics / Warehouse
    ("LOGISTICS", [
        "logistics", "warehouse", "supply chain", "driver", "delivery",
        "packer", "picker", "forklift", "store keeper", "inventory",
    ]),
    # Hospitality
    ("HOSPITALITY", [
        "chef", "cook", "waiter", "waitress", "hotel", "restaurant",
        "housekeeping", "front desk", "barista", "bartender",
    ]),
    # Legal
    ("LEGAL", [
        "legal", "lawyer", "attorney", "counsel", "paralegal", "compliance",
        "contract manager",
    ]),
    # HR / Recruitment
    ("HR", [
        "hr ", "human resource", "recruiter", "talent", "recruitment",
        "people operations",
    ]),
    # Design
    ("DESIGN", [
        "designer", "ux", "ui ", "graphic", "product design", "visual",
        "motion", "art director",
    ]),
    # Management / Operations
    ("MANAGEMENT", [
        "manager", "director", "head of", "vp ", "vice president",
        "chief", "coo", "ceo", "cto", "operations manager", "program manager",
        "project manager", "team lead",
    ]),
    # Customer Support
    ("SUPPORT", [
        "customer success", "customer support", "support engineer",
        "help desk", "call center", "customer service",
    ]),
]


def categorize(title):
    if not title:
        return "OTHER"
    t = title.lower()
    # Highest priority match
    for cat, keywords in CATEGORY_RULES:
        for kw in keywords:
            if kw in t:
                return cat
    return "OTHER"


def ensure_category_table():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS opportunity_categories (
            opportunity_id TEXT PRIMARY KEY,
            category TEXT,
            subcategory TEXT,
            categorized_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def categorize_all():
    ensure_category_table()
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("SELECT id, title FROM opportunities")
    rows = cur.fetchall()
    print(f"Categorizing {len(rows)} jobs...")

    now = datetime.utcnow().isoformat()
    counts = {}

    for oid, title in rows:
        cat = categorize(title)
        counts[cat] = counts.get(cat, 0) + 1
        cur.execute("""
            INSERT OR REPLACE INTO opportunity_categories
            (opportunity_id, category, subcategory, categorized_at)
            VALUES (?, ?, ?, ?)
        """, (oid, cat, "", now))

    conn.commit()

    # Report
    print("\n" + "=" * 70)
    print("JOB CATEGORIES")
    print("=" * 70)
    sorted_cats = sorted(counts.items(), key=lambda x: -x[1])
    for cat, cnt in sorted_cats:
        print(f"  {cat:20} {cnt}")

    # Sample per category
    print("\n" + "=" * 70)
    print("SAMPLE JOBS BY CATEGORY")
    print("=" * 70)
    for cat, _ in sorted_cats[:8]:
        print(f"\n[{cat}]")
        cur.execute("""
            SELECT o.title, o.company, o.country
            FROM opportunities o
            JOIN opportunity_categories c ON c.opportunity_id = o.id
            WHERE c.category = ? AND o.status='DISCOVERED'
            LIMIT 3
        """, (cat,))
        for t, comp, co in cur.fetchall():
            print(f"  • {str(t)[:50]:50} | {str(comp)[:20]:20} | {co}")

    conn.close()


if __name__ == "__main__":
    categorize_all()