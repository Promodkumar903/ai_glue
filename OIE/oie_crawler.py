"""
OIE Crawler — Multi-source crawling + Duplicate + Conflict detection
"""
import sys
import os
import sqlite3
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from oie_pipeline import run_pipeline, SOURCE_TIERS

DB = "ai_glue.db"

# ============================================================
# SOURCE CONFIG (start small, expand later)
# ============================================================
SOURCES = [
    # (url, source_type, label)
    ("https://en.wikipedia.org/wiki/Nursing_in_Germany", "GOV", "Wikipedia-NursingDE"),
    ("https://en.wikipedia.org/wiki/Healthcare_in_Canada", "GOV", "Wikipedia-HealthCA"),
    ("https://en.wikipedia.org/wiki/Information_technology_in_India", "GOV", "Wikipedia-IT-India"),
    ("https://en.wikipedia.org/wiki/Employment_in_Japan", "GOV", "Wikipedia-EmpJP"),
]


# ============================================================
# DUPLICATE DETECTION
# ============================================================
def token_sim(a, b):
    if not a or not b:
        return 0.0
    a_t = set(a.lower().split())
    b_t = set(b.lower().split())
    if not a_t or not b_t:
        return 0.0
    return len(a_t & b_t) / len(a_t | b_t)


def find_duplicates(threshold=0.80):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT id, title, country FROM opportunities WHERE status='DISCOVERED'")
    rows = cur.fetchall()
    conn.close()

    dups = []
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            a_sig = f"{rows[i][1]} {rows[i][2]}"
            b_sig = f"{rows[j][1]} {rows[j][2]}"
            s = token_sim(a_sig, b_sig)
            if s >= threshold:
                dups.append({
                    "canonical_id": rows[i][0],
                    "duplicate_id": rows[j][0],
                    "similarity": round(s, 3),
                    "title": rows[i][1],
                })
    return dups


# ============================================================
# CONFLICT DETECTION
# ============================================================
def find_conflicts():
    """
    Find conflicts: same field across 2+ claims for same opportunity
    with different values.
    """
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        SELECT opportunity_id, field_name, COUNT(DISTINCT claimed_value) as distinct_vals
        FROM claims
        WHERE truth_state != 'UNKNOWN'
        GROUP BY opportunity_id, field_name
        HAVING distinct_vals > 1
    """)
    rows = cur.fetchall()
    conn.close()

    conflicts = []
    for opp_id, field, cnt in rows:
        conflicts.append({
            "opportunity_id": opp_id,
            "field_name": field,
            "distinct_values": cnt,
        })
    return conflicts


# ============================================================
# CRAWL ALL SOURCES
# ============================================================
def crawl_all():
    print("\n" + "=" * 70)
    print("OIE CRAWLER — Starting full crawl")
    print("=" * 70)

    results = []
    for i, (url, src_type, label) in enumerate(SOURCES, 1):
        print(f"\n--- [{i}/{len(SOURCES)}] {label} ---")
        try:
            opp_id = run_pipeline(url, source_type=src_type)
            results.append({
                "label": label,
                "url": url,
                "status": "OK" if opp_id else "FAIL",
                "opp_id": opp_id,
            })
        except Exception as e:
            print(f"  EXCEPTION: {e}")
            results.append({
                "label": label, "url": url,
                "status": "ERROR", "error": str(e),
            })

    return results


# ============================================================
# REPORT
# ============================================================
def print_report(crawl_results):
    print("\n" + "=" * 70)
    print("OIE CRAWLER REPORT")
    print("=" * 70)

    # Crawl summary
    ok = sum(1 for r in crawl_results if r["status"] == "OK")
    print(f"\nSources crawled: {len(crawl_results)}")
    print(f"Successful: {ok}")
    print(f"Failed: {len(crawl_results) - ok}")

    # DB stats
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM opportunities WHERE status='DISCOVERED'")
    total_opps = cur.fetchone()[0]
    print(f"\nTotal opportunities: {total_opps}")

    cur.execute("SELECT COUNT(*) FROM claims")
    total_claims = cur.fetchone()[0]
    print(f"Total claims: {total_claims}")

    cur.execute("""SELECT truth_state, COUNT(*) FROM claims
                   GROUP BY truth_state""")
    print("\nTruth state breakdown:")
    for state, cnt in cur.fetchall():
        print(f"  {state:15} {cnt}")

    conn.close()

    # Duplicates
    dups = find_duplicates()
    print(f"\nDuplicate groups (similarity >= 0.80): {len(dups)}")
    for d in dups[:5]:
        print(f"  {d['similarity']} | {d['title']}")

    # Conflicts
    conflicts = find_conflicts()
    print(f"\nConflicts detected: {len(conflicts)}")
    for c in conflicts[:5]:
        print(f"  {c['field_name']} | {c['distinct_values']} distinct values")

    print("\n" + "=" * 70)
    print("CRAWL COMPLETE")
    print("=" * 70)


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    results = crawl_all()
    print_report(results)