import sqlite3, uuid
from datetime import datetime

conn = sqlite3.connect('ai_glue.db')
cur = conn.cursor()

# 1. Payment settings (single-row config)
cur.execute("""
CREATE TABLE IF NOT EXISTS payment_settings (
    id TEXT PRIMARY KEY,
    upi_id_1 TEXT DEFAULT '',
    upi_id_2 TEXT DEFAULT '',
    upi_qr_image TEXT DEFAULT '',
    esewa_id TEXT DEFAULT '',
    esewa_name TEXT DEFAULT '',
    esewa_qr_image TEXT DEFAULT '',
    paypal_link TEXT DEFAULT '',
    paypal_qr_image TEXT DEFAULT '',
    updated_at TEXT
)
""")
print("[OK] payment_settings created")

# 2. Pending payments (manual verify queue)
cur.execute("""
CREATE TABLE IF NOT EXISTS pending_payments (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    user_email TEXT DEFAULT '',
    plan_id TEXT NOT NULL,
    plan_name TEXT DEFAULT '',
    billing_cycle TEXT DEFAULT 'monthly',
    amount REAL DEFAULT 0,
    currency TEXT DEFAULT 'INR',
    method TEXT DEFAULT 'upi',
    utr_number TEXT DEFAULT '',
    screenshot_data TEXT DEFAULT '',
    status TEXT DEFAULT 'pending',
    admin_note TEXT DEFAULT '',
    subscription_id TEXT DEFAULT '',
    created_at TEXT,
    updated_at TEXT
)
""")
print("[OK] pending_payments created")

# 3. Seed payment settings
now = datetime.utcnow().isoformat()
cur.execute("SELECT COUNT(*) FROM payment_settings")
if cur.fetchone()[0] == 0:
    cur.execute("""
        INSERT INTO payment_settings (id, upi_id_1, upi_id_2, esewa_id, esewa_name, paypal_link, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (str(uuid.uuid4()),
          'pramod.rf@oksbi',
          '8174015550@idfcfirst',
          '9826448788',
          'Promod Kumar',
          'https://paypal.me/aiglueagent',
          now))
    print("[OK] Seeded: UPI x2, eSewa, PayPal")

# Verify
cur.execute("SELECT upi_id_1, upi_id_2, esewa_id, esewa_name FROM payment_settings")
row = cur.fetchone()
print("")
print("=== Current Settings ===")
print(f"  UPI 1:  {row[0]}")
print(f"  UPI 2:  {row[1]}")
print(f"  eSewa:  {row[2]} ({row[3]})")

conn.commit()
conn.close()
print("")
print("DONE")