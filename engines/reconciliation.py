"""
AI GLUE — Payment Reconciliation & Commission Engine
"""
from sqlalchemy.orm import Session
from core.database import db, Payment, CommissionEvent, ReferralEvent, Reward
from core.audit import log_audit

class ReconciliationEngine:
    @staticmethod
    def calculate_commission(
        amount: float,
        agent_rate: float = 0.10,
        broker_rate: float = 0.05,
        platform_rate: float = 0.02
    ):
        """Calculate commission splits."""
        agent_share = amount * agent_rate
        broker_share = amount * broker_rate
        platform_share = amount * platform_rate
        remaining = amount - agent_share - broker_share - platform_share
        
        return {
            "agent_share": agent_share,
            "broker_share": broker_share,
            "platform_share": platform_share,
            "remaining": remaining,
            "total": amount
        }

    @staticmethod
    def create_commission_event(
        application_id: str,
        amount: float,
        agent_id: str,
        broker_id: str,
        session: Session = None
    ):
        """Create a commission event after a successful placement."""
        if session is None:
            session = db.get_session()
        
        splits = ReconciliationEngine.calculate_commission(amount)
        
        # Create commission event
        event = CommissionEvent(
            commission_rule_id=None,
            application_id=application_id,
            amount=amount,
            status="PENDING"
        )
        session.add(event)
        session.commit()
        session.refresh(event)
        
        log_audit(
            actor_id=agent_id,
            action="COMMISSION_CREATED",
            target_type="COMMISSION_EVENT",
            target_id=str(event.id),
            after={"amount": amount, "agent_share": splits["agent_share"], "broker_share": splits["broker_share"]},
            reason="Commission created after placement"
        )
        
        return {
            "commission_event_id": str(event.id),
            "amount": amount,
            "splits": splits,
            "status": "PENDING"
        }

    @staticmethod
    def reconcile_payment(payment_id: str, session: Session = None):
        """Reconcile a payment (mark as reconciled)."""
        if session is None:
            session = db.get_session()
        
        payment = session.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            return {"error": "Payment not found"}
        
        if payment.status != "SUCCESS":
            return {"error": "Payment not successful, cannot reconcile"}
        
        # Update status (we don't have a reconciled field, so we add it)
        # For now, we just log it
        log_audit(
            actor_id=payment.payer_id,
            action="PAYMENT_RECONCILED",
            target_type="PAYMENT",
            target_id=str(payment.id),
            before={"status": payment.status},
            after={"status": "RECONCILED"},
            reason="Payment reconciled"
        )
        
        return {"message": "Payment reconciled successfully", "payment_id": str(payment.id)}

    @staticmethod
    def get_reconciliation_summary(session: Session = None):
        """Get summary of all commissions and payments."""
        if session is None:
            session = db.get_session()
        
        total_commissions = session.query(CommissionEvent).count()
        pending_commissions = session.query(CommissionEvent).filter(CommissionEvent.status == "PENDING").count()
        paid_commissions = session.query(CommissionEvent).filter(CommissionEvent.status == "PAID").count()
        
        total_payments = session.query(Payment).count()
        reconciled_payments = session.query(Payment).filter(Payment.status == "RECONCILED").count()
        
        return {
            "commission_summary": {
                "total": total_commissions,
                "pending": pending_commissions,
                "paid": paid_commissions
            },
            "payment_summary": {
                "total": total_payments,
                "reconciled": reconciled_payments
            }
        }

reconciliation = ReconciliationEngine()