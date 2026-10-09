"""
OIE Pipeline Runner — Ek saath saare steps
Aur Windows Task Scheduler se attach kar sakte ho
"""
import subprocess
import sys
from datetime import datetime

STEPS = [
    ("New Only", "oie_new_only.py"),
    ("Dedup Title", "oie_dedup_title.py"),
    ("Deep Extract", "oie_deep_extract.py"),
    ("Categories", "oie_categories.py"),
    ("Clean", "oie_clean.py"),
]


def run_step(name, script):
    print(f"\n{'='*70}")
    print(f"STEP: {name} ({script})")
    print(f"{'='*70}")
    try:
        result = subprocess.run(
            [sys.executable, f"C:/Users/Administrator/ai_glue/OIE/{script}"],
            cwd="C:/Users/Administrator/ai_glue",
            capture_output=True,
            text=True,
            timeout=600,
        )
        # Print last few lines
        lines = result.stdout.strip().split("\n")
        for line in lines[-15:]:
            print(line)
        if result.returncode != 0:
            print(f"  ERROR: {result.stderr[:300]}")
            return False
        return True
    except Exception as e:
        print(f"  EXCEPTION: {e}")
        return False


if __name__ == "__main__":
    print("=" * 70)
    print(f"OIE FULL PIPELINE — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    ok = 0
    fail = 0
    for name, script in STEPS:
        if run_step(name, script):
            ok += 1
        else:
            fail += 1

    print(f"\n{'='*70}")
    print(f"PIPELINE DONE — {ok} success, {fail} failed")
    print(f"{'='*70}")

    # Final stats
    import sqlite3
    conn = sqlite3.connect("C:/Users/Administrator/ai_glue/ai_glue.db")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM opportunities WHERE status='DISCOVERED'")
    print(f"Live opportunities: {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM claims")
    print(f"Total claims: {cur.fetchone()[0]}")
    cur.execute("SELECT category, COUNT(*) FROM opportunity_categories GROUP BY category ORDER BY COUNT(*) DESC")
    print("\nBy category:")
    for cat, c in cur.fetchall():
        print(f"  {str(cat):15} {c}")
    conn.close()