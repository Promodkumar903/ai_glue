"""
Payment Smoke Test — AI Glue
"""
import os
from dotenv import load_dotenv
load_dotenv()

try:
    import razorpay
except ImportError:
    print("❌ Razorpay not installed. Run: pip install razorpay")
    exit()

def test_payment():
    key_id = os.getenv("RAZORPAY_KEY_ID")
    key_secret = os.getenv("RAZORPAY_KEY_SECRET")

    if not key_id or not key_secret:
        print("❌ Razorpay keys missing in .env")
        return False

    try:
        client = razorpay.Client(auth=(key_id, key_secret))
        order = client.order.create({
            "amount": 10000,  # ₹100
            "currency": "INR",
            "payment_capture": 1
        })
        print("✅ Test Order Created:", order['id'])
        return True
    except Exception as e:
        print("❌ Payment Test Failed:", e)
        return False

if __name__ == "__main__":
    test_payment()