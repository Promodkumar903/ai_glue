# ============================================================
# AI GLUE — OFFER ENGINE
# ============================================================
# Create, send, accept, decline offers
# ============================================================

from sqlalchemy.orm import Session
from core.database import Offer, Contract, db
from core.audit import audit
import uuid

class OfferEngine:
    @staticmethod
    def create_offer(application_id: str, organization_id: str, terms: dict, session: Session = None):
        if session is None:
            session = db.get_session()
        
        offer = Offer(
            id=str(uuid.uuid4()),
            application_id=application_id,
            organization_id=organization_id,
            terms=terms,
            status="DRAFT"
        )
        session.add(offer)
        session.commit()
        return offer

    @staticmethod
    def accept_offer(offer_id: str, session: Session = None):
        if session is None:
            session = db.get_session()
        
        offer = session.query(Offer).filter(Offer.id == offer_id).first()
        if not offer:
            raise ValueError("Offer not found")
        offer.status = "ACCEPTED"
        session.commit()
        return offer

    @staticmethod
    def create_contract(offer_id: str, candidate_signature: str = None, org_signature: str = None, session: Session = None):
        if session is None:
            session = db.get_session()
        
        contract = Contract(
            id=str(uuid.uuid4()),
            offer_id=offer_id,
            candidate_signature_at=candidate_signature,
            organization_signature_at=org_signature,
            status="PENDING"
        )
        session.add(contract)
        session.commit()
        return contract

    @staticmethod
    def sign_contract(contract_id: str, session: Session = None):
        if session is None:
            session = db.get_session()
        
        contract = session.query(Contract).filter(Contract.id == contract_id).first()
        if not contract:
            raise ValueError("Contract not found")
        contract.status = "SIGNED"
        session.commit()
        return contract

offer = OfferEngine()