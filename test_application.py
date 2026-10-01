from core.database import db
from engines.application import application

session = db.get_session()

# Get first user and first opportunity
from core.database import User, Opportunity
user = session.query(User).first()
opp = session.query(Opportunity).first()

if not user:
    print("❌ No user found. Please register first.")
    exit()
if not opp:
    print("❌ No opportunity found. Please run test_search.py first.")
    exit()

print(f"👤 User: {user.email}")
print(f"🎯 Opportunity: {opp.title}")

# 1. Create Application
result = application.create_application(user.id, opp.id, session)
print("📄 Create Application:", result)

if "application_id" in result:
    app_id = result["application_id"]
    
    # 2. Check Status
    status = application.get_application_status(app_id, session)
    print("📊 Status:", status)
    
    # 3. Submit Application
    submit = application.submit_application(app_id, session)
    print("📤 Submit:", submit)
    
    # 4. Check Status Again
    status_after = application.get_application_status(app_id, session)
    print("📊 Status After Submit:", status_after)