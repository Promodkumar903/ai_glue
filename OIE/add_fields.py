"""Add work_scope + contract_type + duration to schema"""
import sqlite3

conn = sqlite3.connect("ai_glue.db")
cur = conn.cursor()

# Add columns to opportunities (for quick view)
try:
    cur.execute("ALTER TABLE opportunities ADD COLUMN work_scope TEXT")
    print("Added: opportunities.work_scope")
except Exception as e:
    print(f"work_scope: {e}")

try:
    cur.execute("ALTER TABLE opportunities ADD COLUMN contract_type TEXT")
    print("Added: opportunities.contract_type")
except Exception as e:
    print(f"contract_type: {e}")

try:
    cur.execute("ALTER TABLE opportunities ADD COLUMN duration TEXT")
    print("Added: opportunities.duration")
except Exception as e:
    print(f"duration: {e}")

conn.commit()
conn.close()
print("\nDone. Fields ready.")