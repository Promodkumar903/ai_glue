"""
AI GLUE — Payment Gateway Wrapper (Razorpay/Stripe)
"""
import os
import json
import razorpay
from sqlalchemy.orm import Session
from core.database import db, Payment

class PaymentGateway:
    @staticmethod
    def init_razorpay():
        key_id = os.getenv("RAZORPAY_KEY_ID")
        key_secret = os.getenv("RAZORPAY_KEY_SECRET")
        if not key_id or not key_secret:
            return None
        return razorpay.Client(auth=(key_id, key_secret))

    @staticmethod
    def create_order(amount: float, currency: str = "INR"):
        client = PaymentGateway.init_razorpay()
        if not client:
            return {"error": "Razorpay not configured"}
        
        order = client.order.create({
            "amount": int(amount * 100),  # paise
            "currency": currency,
            "payment_capture": 1
        })
        return order

    @staticmethod
    def verify_signature(order_id: str, payment_id: str, signature: str):
        client = PaymentGateway.init_razorpay()
        if not client:
            return False
        try:
            client.utility.verify_payment_signature({
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature
            })
            return True
        except:
            return False

    @staticmethod
    def refund_payment(payment_id: str, amount: float = None):
        client = PaymentGateway.init_razorpay()
        if not client:
            return {"error": "Razorpay not configured"}
        data = {}
        if amount:
            data["amount"] = int(amount * 100)
        refund = client.payment.refund(payment_id, data)
        return refund