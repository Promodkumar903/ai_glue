"""View OIE jobs with all fields"""
import sqlite3

conn = sqlite3.connect("ai_glue.db")
cur = conn.cursor()

print("=" * 100)
print("OIE JOBS — Full View")
print("=" * 100)

cur.execute("""
    SELECT id, title, country, location, company, salary,
           contract_type, duration, work_scope, description
    FROM opportunities
    WHERE status='DISCOVERED'
    ORDER BY created_at DESC LIMIT 20
""")

for i, row in enumerate(cur.fetchall(), 1):
    (oid, title, country, location, company, salary,
     ctype, duration, work_scope, app_url) = row
    print(f"\n[{i}] {title}")
    print(f"    Country:      {country or 'UNKNOWN'}")
    print(f"    Location:     {location or 'UNKNOWN'}")
    print(f"    Company:      {company or 'UNKNOWN'}")
    print(f"    Salary:       {salary or 'UNKNOWN'}")
    print(f"    Contract:     {ctype or 'UNKNOWN'}")
    print(f"    Duration:     {duration or 'UNKNOWN'}")
    print(f"    Work Scope:   {(work_scope or 'UNKNOWN')[:150]}")
    print(f"    Apply URL:    {app_url or 'UNKNOWN'}")

# Summary stats
print("\n" + "=" * 100)
print("STATS")
print("=" * 100)

cur.execute("""
    SELECT contract_type, COUNT(*)
    FROM opportunities WHERE status='DISCOVERED'
    GROUP BY contract_type
""")
print("\nBy Contract Type:")
for ct, c in cur.fetchall():
    print(f"  {str(ct):20} {c}")

cur.execute("""
    SELECT duration, COUNT(*)
    FROM opportunities WHERE status='DISCOVERED'
    GROUP BY duration
""")
print("\nBy Duration:")
for d, c in cur.fetchall():
    print(f"  {str(d):20} {c}")

cur.execute("""
    SELECT country, COUNT(*)
    FROM opportunities WHERE status='DISCOVERED'
    GROUP BY country ORDER BY COUNT(*) DESC LIMIT 10
""")
print("\nTop 10 Countries:")
for co, c in cur.fetchall():
    print(f"  {str(co):20} {c}")

conn.close()