# ============================================================
# AI GLUE — SAMPLE DATA INSERT SCRIPT
# ============================================================
# यह Script Broker Dashboard के लिए Test Data Insert करेगी
# ============================================================

from core.database import db, User, Application, Opportunity, Organization, UserRole, Case
import uuid
from datetime import datetime, timedelta

session = db.get_session()

print("=" * 60)
print("AI GLUE — SAMPLE DATA INSERT")
print("=" * 60)

# ---------- 1. BROKER USER ढूँढो ----------
broker = session.query(User).filter(User.email == "pramod.rf@gmail.com").first()
if not broker:
    print("❌ Broker user not found. Please register first.")
    session.close()
    exit()

print(f"✅ Broker found: {broker.full_name} ({broker.email})")

# ---------- 2. CANDIDATES बनाओ ----------
candidates_data = [
    ("Rajesh Kumar", "rajesh@test.com"),
    ("Priya Sharma", "priya@test.com"),
    ("Anil Mehta", "anil@test.com"),
    ("Sunita Rao", "sunita@test.com"),
    ("Vikram Singh", "vikram@test.com"),
]

candidates = []
for name, email in candidates_data:
    existing = session.query(User).filter(User.email == email).first()
    if not existing:
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            password_hash="$2b$12$dummyhash",  # dummy hash
            full_name=name,
            status="ACTIVE"
        )
        session.add(user)
        session.commit()
        candidates.append(user)
        print(f"   ✅ Created candidate: {name}")
    else:
        candidates.append(existing)
        print(f"   ℹ️  Existing candidate: {name}")

print(f"✅ Total candidates: {len(candidates)}")

# ---------- 3. ORGANIZATION बनाओ ----------
org = session.query(Organization).filter(Organization.name == "TechCorp GmbH").first()
if not org:
    org = Organization(
        id=str(uuid.uuid4()),
        name="TechCorp GmbH",
        type="COMPANY",
        verification_status="VERIFIED"
    )
    session.add(org)
    session.commit()
    print(f"✅ Created organization: {org.name}")
else:
    print(f"✅ Using existing organization: {org.name}")

# ---------- 4. OPPORTUNITY बनाओ ----------
opp = session.query(Opportunity).filter(Opportunity.title == "AI Engineer").first()
if not opp:
    opp = Opportunity(
        id=str(uuid.uuid4()),
        organization_id=org.id,
        type="VACANCY",
        title="AI Engineer",
        description="Looking for AI Engineer with Python/ML skills",
        requirements={"skills": ["Python", "ML", "AI"], "experience": 3},
        status="ACTIVE",
        deadline=datetime.utcnow() + timedelta(days=30)
    )
    session.add(opp)
    session.commit()
    print(f"✅ Created opportunity: {opp.title}")
else:
    print(f"✅ Using existing opportunity: {opp.title}")

# ---------- 5. BROKER ROLE SET करो ----------
session.query(UserRole).filter(UserRole.user_id == broker.id).delete()
session.add(UserRole(
    id=str(uuid.uuid4()),
    user_id=broker.id,
    role_code="BROKER"
))
session.commit()
print(f"✅ Broker role set for {broker.full_name}")

# ---------- 6. APPLICATIONS बनाओ (Broker के through) ----------
statuses = ["SHORTLISTED", "INTERVIEW", "OFFERED", "JOINED", "REJECTED"]
created_count = 0

for i, candidate in enumerate(candidates):
    # Check if application already exists
    existing_app = session.query(Application).filter(
        Application.candidate_id == candidate.id,
        Application.opportunity_id == opp.id
    ).first()

    if existing_app:
        # Update broker_id
        existing_app.broker_id = broker.id
        existing_app.status = statuses[i % len(statuses)]
        print(f"   ℹ️  Updated application for: {candidate.full_name}")
    else:
        # Create Case
        case = Case(
            id=str(uuid.uuid4()),
            candidate_id=candidate.id,
            case_type="JOB",
            status="OPEN"
        )
        session.add(case)
        session.commit()

        # Create Application
        app = Application(
            id=str(uuid.uuid4()),
            case_id=case.id,
            candidate_id=candidate.id,
            opportunity_id=opp.id,
            broker_id=broker.id,  # ✅ Broker ID Set करो
            status=statuses[i % len(statuses)],
            match_score=85.5
        )
        session.add(app)
        session.commit()
        created_count += 1
        print(f"   ✅ Created application for: {candidate.full_name} ({statuses[i % len(statuses)]})")

print(f"\n✅ Created {created_count} new applications")

# ---------- 7. SUMMARY ----------
print("\n" + "=" * 60)
print("📊 DATABASE SUMMARY")
print("=" * 60)
print(f"   Users: {session.query(User).count()}")
print(f"   Applications: {session.query(Application).count()}")
print(f"   Opportunities: {session.query(Opportunity).count()}")
print(f"   Organizations: {session.query(Organization).count()}")

# Broker के under कितनी applications हैं
broker_apps = session.query(Application).filter(Application.broker_id == broker.id).count()
print(f"   Applications under BROKER {broker.full_name}: {broker_apps}")

session.close()
print("\n✅ Sample data inserted successfully!")
print("=" * 60)