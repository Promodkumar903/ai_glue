"""
SMTP Smoke Test — AI Glue
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

def send_test_email():
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    to_email = input("Enter your email to receive test: ")

    if not smtp_host or not smtp_user or not smtp_pass:
        print("❌ SMTP credentials missing in .env")
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = to_email
        msg['Subject'] = "AI Glue — SMTP Smoke Test"
        body = "This is a test email from AI Glue. If you received this, SMTP is working!"
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        print("✅ Test email sent successfully to", to_email)
        return True
    except Exception as e:
        print("❌ SMTP Failed:", e)
        return False

if __name__ == "__main__":
    send_test_email()