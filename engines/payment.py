# ============================================================
# AI GLUE — PAYMENT ENGINE
# ============================================================
# Initiate, verify, refund payments
# ============================================================

from sqlalchemy.orm import Session
from core.database import Payment, db
from core.audit import audit
import uuid

class PaymentEngine:
    @staticmethod
    def initiate_payment(payer_id: str, amount: float, currency: str, purpose: str, session: Session = None):
        if session is None:
            session = db.get_session()
        
        payment = Payment(
            id=str(uuid.uuid4()),
            payer_id=payer_id,
            amount=amount,
            currency=currency,
            status="PENDING"
        )
        session.add(payment)
        session.commit()
        return payment

payment_engine = PaymentEngine()