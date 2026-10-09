"""Add vertical column to separate JOB vs STUDY"""
import sqlite3

conn = sqlite3.connect("ai_glue.db")
cur = conn.cursor()

# 1. Add vertical to registry_entities
try:
    cur.execute("ALTER TABLE registry_entities ADD COLUMN vertical TEXT DEFAULT 'JOB'")
    print("+ registry_entities.vertical")
except Exception as e:
    print(f"= registry_entities.vertical: {e}")

# 2. Add vertical to oie_requests
try:
    cur.execute("ALTER TABLE oie_requests ADD COLUMN vertical TEXT DEFAULT 'JOB'")
    print("+ oie_requests.vertical")
except Exception as e:
    print(f"= oie_requests.vertical: {e}")

# 3. Add vertical to hr_contact_log
try:
    cur.execute("ALTER TABLE hr_contact_log ADD COLUMN vertical TEXT DEFAULT 'JOB'")
    print("+ hr_contact_log.vertical")
except Exception as e:
    print(f"= hr_contact_log.vertical: {e}")

# 4. Update existing records to JOB
cur.execute("UPDATE registry_entities SET vertical='JOB' WHERE vertical IS NULL")
cur.execute("UPDATE oie_requests SET vertical='JOB' WHERE vertical IS NULL")
cur.execute("UPDATE hr_contact_log SET vertical='JOB' WHERE vertical IS NULL")

conn.commit()

# 5. Create study_contacts table (universities' admissions officers)
cur.execute("""
    CREATE TABLE IF NOT EXISTS study_contacts (
        id TEXT PRIMARY KEY,
        university_id TEXT,
        university_name TEXT NOT NULL,
        country TEXT,
        website TEXT,
        admissions_officer TEXT,
        designation TEXT,
        email TEXT,
        phone TEXT,
        whatsapp TEXT,
        application_url TEXT,
        verification_status TEXT DEFAULT 'PENDING',
        contact_attempts INTEGER DEFAULT 0,
        last_contact_attempt TEXT,
        verified_at TEXT,
        source TEXT,
        created_at TEXT,
        updated_at TEXT
    )
""")
print("+ study_contacts table")

# 6. Create study_agents view (just filter)
print("\nOK: Vertical separation ready")

# Report
cur.execute("SELECT vertical, COUNT(*) FROM registry_entities GROUP BY vertical")
print("\nRegistry by vertical:")
for v, c in cur.fetchall():
    print(f"  {v}: {c}")

cur.execute("SELECT vertical, COUNT(*) FROM oie_requests GROUP BY vertical")
print("\nRequests by vertical:")
for v, c in cur.fetchall():
    print(f"  {v}: {c}")

conn.commit()
conn.close()
print("\nDone.")