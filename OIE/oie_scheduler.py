"""
OIE Scheduler — Auto crawler + duplicate + conflict + report
Runs on demand (manual) or as daemon (every N hours)
"""
import sys
import os
import time
import sqlite3
import json
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

DB = "ai_glue.db"


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


def run_duplicate_scan(threshold=0.85):
    """Find duplicates in opportunities, mark older ones as DUPLICATE"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        SELECT id, title, company, country, created_at
        FROM opportunities
        WHERE status='DISCOVERED'
        ORDER BY created_at ASC
    """)
    rows = cur.fetchall()

    marked = 0
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            a, b = rows[i], rows[j]
            if b[0] == a[0]:
                continue
            sig_a = f"{a[1]} {a[2]} {a[3]}"
            sig_b = f"{b[1]} {b[2]} {b[3]}"
            s = token_sim(sig_a, sig_b)
            if s >= threshold:
                # Mark newer one as DUPLICATE
                cur.execute("UPDATE opportunities SET status='DUPLICATE' WHERE id=?", (b[0],))
                marked += 1

    conn.commit()
    conn.close()
    return marked


# ============================================================
# CONFLICT DETECTION
# ============================================================
def run_conflict_scan():
    """Find fields with conflicting values across sources"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        SELECT opportunity_id, field_name, COUNT(DISTINCT claimed_value) as vals
        FROM claims
        WHERE truth_state != 'UNKNOWN'
        GROUP BY opportunity_id, field_name
        HAVING vals > 1
    """)
    conflicts = cur.fetchall()
    conn.close()
    return len(conflicts)


# ============================================================
# STATS REPORT
# ============================================================
def print_stats():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM opportunities")
    total = cur.fetchone()[0]

    cur.execute("SELECT status, COUNT(*) FROM opportunities GROUP BY status")
    by_status = dict(cur.fetchall())

    cur.execute("SELECT COUNT(*) FROM claims")
    claims = cur.fetchone()[0]

    cur.execute("SELECT truth_state, COUNT(*) FROM claims GROUP BY truth_state")
    by_truth = dict(cur.fetchall())

    conn.close()

    print("\n" + "=" * 60)
    print(f"OIE STATS — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print(f"Total opportunities: {total}")
    print(f"  DISCOVERED:  {by_status.get('DISCOVERED', 0)}")
    print(f"  DUPLICATE:   {by_status.get('DUPLICATE', 0)}")
    print(f"  VERIFIED:    {by_status.get('VERIFIED', 0)}")
    print(f"\nTotal claims: {claims}")
    for state in ["CONFIRMED", "SUPPORTED", "INFERRED", "UNKNOWN", "CONFLICTING"]:
        if state in by_truth:
            print(f"  {state:12} {by_truth[state]}")


# ============================================================
# MAIN CYCLE
# ============================================================
def run_cycle():
    print("\n" + "=" * 60)
    print(f"OIE CYCLE — {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)

    # 1. Crawl
    print("\n[1/3] Crawling sources...")
    try:
        from oie_real_jobs import run as crawl_real_jobs
        crawl_real_jobs()
    except Exception as e:
        print(f"  Crawl failed: {e}")

    # 2. Duplicates
    print("\n[2/3] Duplicate scan...")
    marked = run_duplicate_scan()
    print(f"  Marked {marked} duplicates")

    # 3. Conflicts
    print("\n[3/3] Conflict scan...")
    conflicts = run_conflict_scan()
    print(f"  Found {conflicts} conflicts")

    # Stats
    print_stats()


# ============================================================
# DAEMON MODE — every N hours
# ============================================================
def run_daemon(hours=6):
    print(f"OIE DAEMON — will run every {hours} hours")
    print("Press Ctrl+C to stop\n")
    while True:
        try:
            run_cycle()
        except Exception as e:
            print(f"CYCLE ERROR: {e}")
        print(f"\nSleeping {hours} hours...")
        time.sleep(hours * 3600)


# ============================================================
# ENTRY
# ============================================================
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--daemon", action="store_true", help="Run in loop")
    parser.add_argument("--hours", type=int, default=6)
    args = parser.parse_args()

    if args.daemon:
        run_daemon(args.hours)
    else:
        run_cycle()