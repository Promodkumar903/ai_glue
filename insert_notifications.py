# ============================================================
# AI GLUE — INSERT SAMPLE NOTIFICATIONS
# ============================================================

from core.database import db, User, Notification
import uuid
from datetime import datetime

session = db.get_session()

user = session.query(User).filter(User.email == "pramod.rf@gmail.com").first()

if not user:
    print("❌ User not found")
    exit()

print(f"✅ User ID: {user.id}")

samples = [
    ("🎉 Offer Received!", "You received an offer from TechCorp GmbH for AI Engineer role."),
    ("📅 Interview Scheduled", "Interview with Siemens AG on 20 Sep at 10:00 AM."),
    ("⚠️ Document Expiring", "Your passport expires in 60 days. Please renew it."),
    ("✅ Application Shortlisted", "Your application for Data Analyst role was shortlisted!"),
    ("🔍 New Job Matches", "12 new jobs match your profile. Check them out!"),
]

for title, msg in samples:
    notif = Notification(
        id=str(uuid.uuid4()),
        user_id=user.id,
        title=title,
        message=msg,
        is_read=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(notif)

session.commit()

count = session.query(Notification).filter(Notification.user_id == user.id).count()
print(f"✅ Created {count} notifications for {user.email}")

session.close()
print("✅ Done!")