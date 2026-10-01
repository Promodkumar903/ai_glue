from core.database import db
from engines.search import search
from core.database import Opportunity, Organization

session = db.get_session()

# Check if we already have an organization; if not, create one
org = session.query(Organization).first()
if not org:
    org = Organization(name="Test University", type="INSTITUTION")
    session.add(org)
    session.commit()
    session.refresh(org)

# Now create a test opportunity
opp = Opportunity(
    organization_id=org.id,
    type="PROGRAMME",
    title="MSc Artificial Intelligence",
    description="Learn AI in Germany",
    status="OPEN"
)
session.add(opp)
session.commit()

# Search
results = search.search_opportunities("AI", session=session)
print(f"Found {len(results)} opportunities:")
for r in results:
    print(f"- {r.title}")