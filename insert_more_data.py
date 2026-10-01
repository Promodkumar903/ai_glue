# ============================================================
# AI GLUE — MORE SAMPLE DATA (D)
# ============================================================
# यह Script existing data में और Organizations, Opportunities,
# Agents, Offers, Commissions add करेगी।
# Duplicate से बचने के लिए Check करके Insert करती है।
# ============================================================

from core.database import (
    db, User, Application, Opportunity, Organization,
    UserRole, Case, Offer, Payment
)
import uuid
from datetime import datetime, timedelta

session = db.get_session()

print("=" * 60)
print("AI GLUE — MORE SAMPLE DATA (D)")
print("=" * 60)

# ---------- 1. Broker ढूँढो ----------
broker = session.query(User).filter(User.email == "pramod.rf@gmail.com").first()
if not broker:
    print("❌ Broker not found.")
    session.close()
    exit()

print(f"✅ Broker: {broker.full_name}")

# ---------- 2. Agents बनाओ ----------
agents_data = [
    ("Ravi Sharma", "ravi.agent@test.com"),
    ("Neha Verma", "neha.agent@test.com"),
    ("Sanjay Patel", "sanjay.agent@test.com"),
]

agents = []
for name, email in agents_data:
    existing = session.query(User).filter(User.email == email).first()
    if not existing:
        agent = User(
            id=str(uuid.uuid4()),
            email=email,
            password_hash="$2b$12$dummyhash",
            full_name=name,
            status="ACTIVE"
        )
        session.add(agent)
        session.commit()
        session.refresh(agent)
        # Assign AGENT role
        session.add(UserRole(
            id=str(uuid.uuid4()),
            user_id=agent.id,
            role_code="AGENT"
        ))
        session.commit()
        agents.append(agent)
        print(f"   ✅ Created agent: {name}")
    else:
        agents.append(existing)
        print(f"   ℹ️  Existing agent: {name}")

# ---------- 3. Organizations बनाओ ----------
orgs_data = [
    ("Siemens AG", "COMPANY", "Germany"),
    ("Fraunhofer Institute", "COMPANY", "Germany"),
    ("University of Berlin", "INSTITUTION", "Germany"),
    ("TCS Global", "COMPANY", "India"),
]

orgs = []
for name, otype, country in orgs_data:
    existing = session.query(Organization).filter(Organization.name == name).first()
    if not existing:
        org = Organization(
            id=str(uuid.uuid4()),
            name=name,
            type=otype,
            verification_status="VERIFIED"
        )
        session.add(org)
        session.commit()
        session.refresh(org)
        orgs.append(org)
        print(f"   ✅ Created org: {name}")
    else:
        orgs.append(existing)
        print(f"   ℹ️  Existing org: {name}")

# ---------- 4. Opportunities बनाओ ----------
opps_data = [
    ("Senior Data Scientist", "VACANCY", ["Python", "ML", "SQL"], 5),
    ("Frontend Developer", "VACANCY", ["React", "JavaScript"], 2),
    ("DevOps Engineer", "VACANCY", ["Docker", "Kubernetes", "AWS"], 4),
    ("MSc Computer Science", "PROGRAMME", ["Bachelor's"], 2),
    ("Research Fellowship", "SCHOLARSHIP", ["PhD"], 3),
]

opps = []
for i, (title, otype, skills, exp) in enumerate(opps_data):
    existing = session.query(Opportunity).filter(Opportunity.title == title).first()
    if not existing:
        opp = Opportunity(
            id=str(uuid.uuid4()),
            organization_id=orgs[i % len(orgs)].id,
            type=otype,
            title=title,
            description=f"Looking for candidates for {title}",
            requirements={"skills": skills, "experience": exp},
            status="ACTIVE",
            deadline=datetime.utcnow() + timedelta(days=30 + i * 5)
        )
        session.add(opp)
        session.commit()
        session.refresh(opp)
        opps.append(opp)
        print(f"   ✅ Created opportunity: {title}")
    else:
        opps.append(existing)
        print(f"   ℹ️  Existing opportunity: {title}")

# ---------- 5. Existing Candidates ढूँढो ----------
candidates = session.query(User).filter(
    User.email.like('candidate%@test.com')
).all()
print(f"\n✅ Found {len(candidates)} existing candidates")

# ---------- 6. More Applications बनाओ ----------
statuses = ["DRAFT", "SUBMITTED", "UNDER_REVIEW", "SHORTLISTED",
            "INTERVIEW", "OFFERED", "ACCEPTED", "REJECTED", "JOINED"]
created_apps = 0

for opp in opps:
    for i, candidate in enumerate(candidates[:4]):
        # Check if exists
        existing = session.query(Application).filter(
            Application.candidate_id == candidate.id,
            Application.opportunity_id == opp.id
        ).first()
        if existing:
            continue

        # Case बनाओ
        case = Case(
            id=str(uuid.uuid4()),
            candidate_id=candidate.id,
            case_type="JOB" if opp.type == "VACANCY" else "ADMISSION",
            status="OPEN"
        )
        session.add(case)
        session.commit()

        # Assigned agent rotation
        assigned_broker = broker
        if i < len(agents) and (i + created_apps) % 2 == 0:
            assigned_broker = agents[i]

        app = Application(
            id=str(uuid.uuid4()),
            case_id=case.id,
            candidate_id=candidate.id,
            opportunity_id=opp.id,
            broker_id=assigned_broker.id,
            status=statuses[(i + created_apps) % len(statuses)],
            match_score=70 + (i * 5) % 30
        )
        session.add(app)
        session.commit()
        created_apps += 1

print(f"✅ Created {created_apps} new applications")

# ---------- 7. Offers बनाओ (ACCEPTED — Revenue के लिए) ----------
accepted_apps = session.query(Application).filter(
    Application.status.in_(["ACCEPTED", "JOINED", "OFFERED"])
).limit(6).all()

created_offers = 0
for app in accepted_apps:
    existing = session.query(Offer).filter(Offer.application_id == app.id).first()
    if existing:
        continue
    offer = Offer(
        id=str(uuid.uuid4()),
        application_id=app.id,
        organization_id=app.opportunity.organization_id if hasattr(app, 'opportunity') else orgs[0].id,
        terms={"salary": 75000, "start_date": "2026-12-01"},
        scholarship_amount=0,
        status="ACCEPTED",
        sent_at=datetime.utcnow() - timedelta(days=5)
    )
    session.add(offer)
    session.commit()
    created_offers += 1

print(f"✅ Created {created_offers} accepted offers")

# ---------- 8. Summary ----------
print("\n" + "=" * 60)
print("📊 UPDATED DATABASE SUMMARY")
print("=" * 60)
print(f"   Users: {session.query(User).count()}")
print(f"   Organizations: {session.query(Organization).count()}")
print(f"   Opportunities: {session.query(Opportunity).count()}")
print(f"   Applications: {session.query(Application).count()}")
print(f"   Offers: {session.query(Offer).count()}")

broker_apps = session.query(Application).filter(Application.broker_id == broker.id).count()
print(f"   Applications under Broker {broker.full_name}: {broker_apps}")

session.close()
print("\n✅ More data inserted successfully!")
print("=" * 60)