from core.database import db, User, Organization, OrganizationMember, Opportunity
import uuid

session = db.get_session()

# User ढूँढो
user = session.query(User).filter(User.email == "pramod.rf@gmail.com").first()
print(f"✅ User: {user.full_name} ({user.id})")

# सबसे ज़्यादा Opportunities वाली Org ढूँढो
from sqlalchemy import func
orgs_with_opps = session.query(
    Opportunity.organization_id,
    func.count(Opportunity.id).label('count')
).group_by(Opportunity.organization_id).order_by(func.count(Opportunity.id).desc()).all()

if not orgs_with_opps:
    print("❌ No organizations with opportunities found")
    session.close()
    exit()

top_org_id = orgs_with_opps[0][0]
top_org = session.query(Organization).filter(Organization.id == top_org_id).first()
print(f"✅ Target Org: {top_org.name} ({top_org.id})")

# पहले से Membership है क्या?
existing = session.query(OrganizationMember).filter(
    OrganizationMember.user_id == user.id,
    OrganizationMember.organization_id == top_org.id
).first()

if existing:
    print(f"ℹ️  User is already a member with role: {existing.role_code}")
else:
    member = OrganizationMember(
        id=str(uuid.uuid4()),
        user_id=user.id,
        organization_id=top_org.id,
        role_code="ORG_ADMIN"
    )
    session.add(member)
    session.commit()
    print(f"✅ Added {user.full_name} as ORG_ADMIN to {top_org.name}")

# Verify
count = session.query(OrganizationMember).filter(
    OrganizationMember.user_id == user.id
).count()
print(f"📊 User is now member of {count} organizations")

session.close()
print("✅ Done!")