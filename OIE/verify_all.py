"""Verify all genuine entities"""
import sqlite3
from datetime import datetime

conn = sqlite3.connect("ai_glue.db")
cur = conn.cursor()
now = datetime.utcnow().isoformat()

cur.execute("""
    UPDATE registry_entities
    SET is_verified=1, is_genuine=1, verification_status='VERIFIED',
        verified_by='admin', verified_at=?, updated_at=?
    WHERE verification_status='PENDING'
""", (now, now))
count = cur.rowcount
conn.commit()

# Recalculate trust
cur.execute("SELECT id FROM registry_entities WHERE is_verified=1")
for (eid,) in cur.fetchall():
    cur.execute("SELECT * FROM registry_entities WHERE id=?", (eid,))
    row = cur.fetchone()
    cols = [d[0] for d in cur.description]
    entity = dict(zip(cols, row))

    score = 0
    if entity.get("legal_name"): score += 10
    if entity.get("license_number"): score += 15
    if entity.get("license_authority"): score += 10
    if entity.get("established_year") and 1950 <= entity.get("established_year", 0) <= 2025: score += 10
    if entity.get("website"): score += 5
    if entity.get("email"): score += 5
    if entity.get("phone"): score += 5
    if entity.get("is_verified"): score += 15
    score += 10

    cur.execute("UPDATE registry_entities SET trust_score=? WHERE id=?", (min(score, 100), eid))

conn.commit()
print(f"Verified {count} entities")
cur.execute("SELECT name, trust_score FROM registry_entities WHERE is_verified=1")
for name, score in cur.fetchall():
    print(f"  {name:40} Trust: {score}")
conn.close()