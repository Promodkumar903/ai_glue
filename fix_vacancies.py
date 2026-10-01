from core.database import db, Opportunity

session = db.get_session()

drafts = session.query(Opportunity).filter(Opportunity.status == "DRAFT").all()
print(f"Found {len(drafts)} DRAFT opportunities")

for opp in drafts:
    print(f"  → {opp.title} (was {opp.status})")
    opp.status = "ACTIVE"

session.commit()
print(f"✅ {len(drafts)} opportunities set to ACTIVE")

active = session.query(Opportunity).filter(Opportunity.status == "ACTIVE").count()
print(f"📊 Total ACTIVE: {active}")

session.close()
print("✅ Done!")