"""
Notification Trigger Test
"""
from engines.notification import notification_engine
from core.database import db
from core.event_triggers import trigger_application_submitted

def test_notification():
    session = db.get_session()
    # Get first user
    from core.database import User
    user = session.query(User).first()
    if not user:
        print("❌ No user found")
        return False
    
    trigger_application_submitted(
        user_id=user.id,
        application_id="test-123",
        opportunity_title="Test Opportunity"
    )
    print("✅ Notification trigger executed. Check Email/SMS/In-App.")
    return True

if __name__ == "__main__":
    test_notification()