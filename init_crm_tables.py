import sqlite3

conn = sqlite3.connect('ai_glue.db')
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS leads (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    student_name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    country TEXT,
    course TEXT,
    budget TEXT,
    intake TEXT,
    source TEXT DEFAULT 'manual',
    stage TEXT DEFAULT 'NEW',
    priority TEXT DEFAULT 'MEDIUM',
    notes TEXT,
    next_followup TEXT,
    last_contacted TEXT,
    converted_to_user_id TEXT,
    created_at TEXT,
    updated_at TEXT
)""")

cur.execute("""CREATE TABLE IF NOT EXISTS lead_documents (
    id TEXT PRIMARY KEY,
    lead_id TEXT NOT NULL,
    document_type TEXT NOT NULL,
    document_name TEXT,
    file_url TEXT,
    status TEXT DEFAULT 'MISSING',
    uploaded_at TEXT,
    verified_at TEXT,
    verified_by TEXT,
    rejection_reason TEXT
)""")

cur.execute("""CREATE TABLE IF NOT EXISTS lead_activities (
    id TEXT PRIMARY KEY,
    lead_id TEXT NOT NULL,
    activity_type TEXT NOT NULL,
    description TEXT,
    actor_id TEXT,
    created_at TEXT
)""")

conn.commit()
conn.close()
print("CRM tables created in local SQLite")