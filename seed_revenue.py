import sqlite3, uuid, json
from datetime import datetime

conn = sqlite3.connect('ai_glue.db')
cur = conn.cursor()

# 1. Add missing columns to invoices
cols = [
    'subscription_id VARCHAR(36)',
    'payment_id VARCHAR(36)',
    'invoice_number VARCHAR(50)',
    'description TEXT',
    'paid_at TIMESTAMP'
]
for c in cols:
    try:
        cur.execute(f'ALTER TABLE invoices ADD COLUMN {c}')
        print(f'Added: {c}')
    except Exception:
        print(f'Skipped: {c}')

# 2. Seed 4 plans
plans = [
    ('Free', 'Basic resume, 5 job matches/month', 0, 0,
     json.dumps(['5 job matches/month', 'Basic resume builder', 'Email support'])),
    ('Basic', 'Unlimited matches + 1 visa assist', 499, 4999,
     json.dumps(['Unlimited job matches', 'Resume builder', '1 visa assist', 'Priority email'])),
    ('Pro', 'All features + priority support', 1499, 14999,
     json.dumps(['Everything in Basic', 'Unlimited visa assist', 'AI interview prep', 'Priority support', 'Document vault'])),
    ('Enterprise', 'Multi-user + custom', 4999, 49999,
     json.dumps(['Everything in Pro', 'Multi-user (10 seats)', 'Custom integrations', 'Dedicated manager', 'API access'])),
]

now = datetime.utcnow().isoformat()
for name, desc, pm, py, feats in plans:
    cur.execute('SELECT id FROM subscription_plans WHERE name = ?', (name,))
    if not cur.fetchone():
        cur.execute(
            'INSERT INTO subscription_plans (id, name, description, price_monthly, price_yearly, features, is_active, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)',
            (str(uuid.uuid4()), name, desc, pm, py, feats, now, now)
        )
        print(f'Seeded: {name}')
    else:
        print(f'Exists: {name}')

conn.commit()

cur.execute('SELECT name, price_monthly, price_yearly FROM subscription_plans ORDER BY price_monthly')
print('')
print('=== Plans ===')
for r in cur.fetchall():
    print(f'  {r[0]}: Rs {r[1]}/mo, Rs {r[2]}/yr')

conn.close()
print('')
print('DONE')