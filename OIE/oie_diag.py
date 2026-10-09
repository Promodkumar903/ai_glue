"""Diagnose work_scope coverage"""
import sqlite3

conn = sqlite3.connect("ai_glue.db")
cur = conn.cursor()

print("=" * 60)
print("WORK_SCOPE DIAGNOSTIC")
print("=" * 60)

cur.execute("SELECT COUNT(*) FROM opportunities")
total = cur.fetchone()[0]
print(f"\nTotal opportunities: {total}")

cur.execute("SELECT COUNT(*) FROM opportunities WHERE work_scope IS NOT NULL AND work_scope != ''")
has_ws = cur.fetchone()[0]
print(f"With work_scope: {has_ws}")

cur.execute("SELECT COUNT(*) FROM opportunities WHERE work_scope IS NULL OR work_scope = ''")
no_ws = cur.fetchone()[0]
print(f"Without work_scope: {no_ws}")

# By source
print("\n" + "=" * 60)
print("By source (first 5 chars of description URL):")
cur.execute("""
    SELECT SUBSTR(description, 1, 30) as src, COUNT(*),
           SUM(CASE WHEN work_scope IS NOT NULL AND work_scope != '' THEN 1 ELSE 0 END) as has_ws
    FROM opportunities
    GROUP BY SUBSTR(description, 1, 30)
    LIMIT 10
""")
for src, cnt, hw in cur.fetchall():
    print(f"  {src:32} total={cnt:4} with_ws={hw}")

# Sample
print("\n" + "=" * 60)
print("Sample work_scope values:")
cur.execute("SELECT title, work_scope FROM opportunities WHERE work_scope != '' LIMIT 5")
for t, ws in cur.fetchall():
    print(f"\n  Title: {t[:50]}")
    print(f"  WS: {str(ws)[:120]}")

conn.close()