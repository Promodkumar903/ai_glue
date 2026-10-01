from core.database import db, User, Organization, OrganizationMember, Opportunity
from sqlalchemy import func
import uuid

session = db.get_session()

# User ढूँढो
user = session.query(User).filter(User.email == "pramod.rf@gmail.com").first()
print(f"✅ User: {user.full_name}")

# कौन-सी Organizations में Opportunities हैं — देखो
print("\n📊 Organizations with Opportunities:")
orgs_with_counts = session.query(
    Organization.id,
    Organization.name,
    func.count(Opportunity.id).label('opp_count')
).outerjoin(Opportunity, Opportunity.organization_id == Organization.id)\
 .group_by(Organization.id, Organization.name).all()

for org_id, org_name, count in orgs_with_counts:
    print(f"   {org_name}: {count} opportunities")

# पुरानी Memberships Delete करो
session.query(OrganizationMember).filter(
    OrganizationMember.user_id == user.id
).delete()
session.commit()
print(f"\n✅ Cleared old memberships")

# हर Organization में Add करो (जहाँ Opportunities हैं या नहीं भी)
for org_id, org_name, count in orgs_with_counts:
    member = OrganizationMember(
        id=str(uuid.uuid4()),
        user_id=user.id,
        organization_id=org_id,
        role_code="ORG_ADMIN"
    )
    session.add(member)
    print(f"   ✅ Added to {org_name}")

session.commit()

count = session.query(OrganizationMember).filter(
    OrganizationMember.user_id == user.id
).count()
print(f"\n📊 User is now member of {count} organizations")

session.close()
print("✅ Done!")