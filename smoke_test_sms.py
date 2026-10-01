"""
SMS Smoke Test — AI Glue
"""
import os
from dotenv import load_dotenv
load_dotenv()

try:
    from twilio.rest import Client
except ImportError:
    print("❌ Twilio not installed. Run: pip install twilio")
    exit()

def send_test_sms():
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_phone = os.getenv("TWILIO_PHONE")
    to_phone = input("Enter your phone number with country code (e.g., +919876543210): ")

    if not account_sid or not auth_token or not from_phone:
        print("❌ Twilio credentials missing in .env")
        return False

    try:
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body="AI Glue — SMS Smoke Test: If you receive this, SMS is working!",
            from_=from_phone,
            to=to_phone
        )
        print("✅ SMS sent! SID:", message.sid)
        return True
    except Exception as e:
        print("❌ SMS Failed:", e)
        return False

if __name__ == "__main__":
    send_test_sms()