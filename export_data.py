import sqlite3
import json

TABLES = [
    'countries',
    'universities',
    'cities',
    'campuses',
    'departments',
    'courses',
    'intake_seats',
    'country_documents',
    'opportunities',
]

data = {}
conn = sqlite3.connect('ai_glue.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

for table in TABLES:
    try:
        cur.execute(f"SELECT * FROM {table}")
        rows = cur.fetchall()
        data[table] = [dict(r) for r in rows]
        print(f"{table}: {len(rows)} rows exported")
    except Exception as e:
        print(f"{table}: ERROR - {e}")
        data[table] = []

conn.close()

with open('seed_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, default=str)

print("")
print("DONE - seed_data.json created")