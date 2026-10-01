# ============================================================
# AI GLUE v8.0 — EVENT TRIGGERS (Placeholder)
# ============================================================
# Purpose: Trigger actions on important system events
# These functions are called from various engines.
# ============================================================

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

def trigger_application_submitted(application_id: str, candidate_id: str, **kwargs):
    """Called when an application is submitted."""
    logger.info(f"Event: application_submitted | app_id={application_id}, candidate={candidate_id}")
    # Future: send email, update workflows, etc.

def trigger_offer_created(offer_id: str, application_id: str, **kwargs):
    """Called when an offer is created."""
    logger.info(f"Event: offer_created | offer_id={offer_id}, app_id={application_id}")

def trigger_visa_status_update(visa_case_id: str, new_status: str, **kwargs):
    """Called when visa status changes."""
    logger.info(f"Event: visa_status_update | visa_case={visa_case_id}, status={new_status}")

def trigger_payment_success(payment_id: str, amount: float, payer_id: str, **kwargs):
    """Called when a payment is successfully completed."""
    logger.info(f"Event: payment_success | payment_id={payment_id}, amount={amount}, payer={payer_id}")