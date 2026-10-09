"""
OIE Cross-Source Dedup — Same title+company = duplicate
Keeps oldest (first_seen), marks newer as DUPLICATE
"""
import sqlite3
from datetime import datetime


def normalize(s):
    if not s:
        return ""
    return " ".join(str(s).lower().strip().split())


def run_dedup():
    conn = sqlite3.connect("ai_glue.db")
    cur = conn.cursor()

    print("=" * 70)
    print("OIE CROSS-SOURCE DEDUP")
    print("=" * 70)

    cur.execute("""
        SELECT id, title, company, country, first_seen, description
        FROM opportunities
        WHERE status = 'DISCOVERED'
        ORDER BY first_seen ASC
    """)
    rows = cur.fetchall()
    print(f"\nScanning {len(rows)} opportunities...")

    # Group by title+company+country
    groups = {}
    for row in rows:
        oid, title, company, country, first_seen, url = row
        key = (normalize(title), normalize(company), normalize(country))
        if key not in groups:
            groups[key] = []
        groups[key].append((oid, first_seen, url))

    marked = 0
    for key, opps in groups.items():
        if len(opps) <= 1:
            continue

        # Keep oldest (first in sorted order)
        keep = opps[0]
        for oid, _, _ in opps[1:]:
            cur.execute("UPDATE opportunities SET status='DUPLICATE' WHERE id=?", (oid,))
            marked += 1
            print(f"  DUP: {key[0][:40]:40} | kept={keep[0][:8]}")

    conn.commit()

    # Report
    cur.execute("SELECT COUNT(*) FROM opportunities WHERE status='DISCOVERED'")
    live = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM opportunities WHERE status='DUPLICATE'")
    dupes = cur.fetchone()[0]

    print(f"\n{'='*70}")
    print(f"Duplicates marked: {marked}")
    print(f"Live (DISCOVERED):  {live}")
    print(f"Duplicates total:   {dupes}")
    print(f"{'='*70}")

    # Preview live
    print("\nTop live jobs:")
    cur.execute("""
        SELECT title, country, company FROM opportunities
        WHERE status='DISCOVERED'
        ORDER BY created_at DESC LIMIT 10
    """)
    for t, c, co in cur.fetchall():
        print(f"  {str(t)[:55]:55} | {str(c)[:15]:15} | {str(co)[:20]}")

    conn.close()


if __name__ == "__main__":
    run_dedup()