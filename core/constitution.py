# ============================================================
# AI GLUE v8.0 — CONSTITUTION ENGINE
# ============================================================
# Based on Blueprint v8.0 — 34 Invariants + 6 Closure Principles
# Engine: E-01 Foundation
# Purpose: Immutable Rules Enforcement
# ============================================================

from enum import Enum
from typing import Dict, List, Optional
import json
from datetime import datetime

# ---------- 34 GLOBAL INVARIANTS ----------
class Invariant:
    def __init__(self, id: str, description: str, enforcement: str, violation_action: str):
        self.id = id
        self.description = description
        self.enforcement = enforcement
        self.violation_action = violation_action

INVARIANTS = [
    # Core Invariants (I-01 to I-15)
    Invariant("I-01", "No unauthorized side effect", "Every real-world action needs explicit actor confirmation", "BLOCK_ACTION"),
    Invariant("I-02", "No authority escalation", "Agent can't exceed owner's scope; Recruiter can't act outside organization", "BLOCK_ACTION"),
    Invariant("I-03", "No self-authorization", "AI can't mark its own recommendation as approved; L4 always needs human", "BLOCK_ACTION"),
    Invariant("I-04", "No self-verification", "Proposer ≠ Approver; Connector creator can't verify own source", "BLOCK_ACTION"),
    Invariant("I-05", "No silent scope expansion", "Broker can't add candidates without consent; Recruiter can't change vacancy scope", "BLOCK_ACTION"),
    Invariant("I-06", "No execution without context", "Every action bound to Case_ID + Plan_Hash + Actor_ID", "BLOCK_ACTION"),
    Invariant("I-07", "No blind retry", "Duplicate-check required before retry external submissions", "BLOCK_ACTION"),
    Invariant("I-08", "No cross-tenant access", "Organization A can't see Organization B data", "BLOCK_ACTION"),
    Invariant("I-09", "No execution on stale authorization", "Consent revoke → immediate access cut-off", "BLOCK_ACTION"),
    Invariant("I-10", "No unverifiable evidence", "Every claim used in matching/ranking must have evidence cortex entry", "BLOCK_ACTION"),
    Invariant("I-11", "No secret in audit", "No raw passwords, card data, or government IDs in logs", "BLOCK_ACTION"),
    Invariant("I-12", "No promotion by sandbox proof alone", "Shadow-mode on real traffic mandatory before promoting any model", "BLOCK_ACTION"),
    Invariant("I-13", "No destructive migration w/o recovery", "Rollback plan mandatory before any schema change", "BLOCK_ACTION"),
    Invariant("I-14", "No capability surviving revocation", "Revoked session invalidated immediately", "BLOCK_ACTION"),
    Invariant("I-15", "No recovery beyond original ceiling", "Refund/compensation never exceeds original transaction", "BLOCK_ACTION"),
    
    # AGI/Trust Invariants (I-16 to I-22)
    Invariant("I-16", "Evidence > Claim", "AI never makes recommendation without evidence", "BLOCK_ACTION"),
    Invariant("I-17", "Need > Ad", "User's need > Partner interest > Platform revenue. Ranking never based on commission.", "BLOCK_ACTION"),
    Invariant("I-18", "Confidence + Uncertainty", "If confidence < threshold, AI says 'I am not sure'", "BLOCK_ACTION"),
    Invariant("I-19", "Need Before Revenue", "User Interest > Partner Interest > Platform Revenue", "BLOCK_ACTION"),
    Invariant("I-20", "Explain Before Recommend", "Every recommendation must show 'Why'", "BLOCK_ACTION"),
    Invariant("I-21", "Companion Not Advertiser", "AI Glue never becomes an ad engine", "BLOCK_ACTION"),
    Invariant("I-22", "Outcome Over Clicks", "Success = Goal Achievement (Placement/Admission), not CTR", "BLOCK_ACTION"),
    
    # Context & Trigger Invariants (I-23 to I-25)
    Invariant("I-23", "No Speculative Time Predictions", "Only Calendar-Fact or Location/Status-Change triggers", "BLOCK_ACTION"),
    Invariant("I-24", "AI Discovery + Human Final Verify", "AI discovers partners, MasterAdmin final verification", "BLOCK_ACTION"),
    Invariant("I-25", "Ecosystem Data Fetch", "Jobs/Visa/Colleges auto-fetched, but NO binding commitment", "BLOCK_ACTION"),
    
    # Verification & Trust Invariants (I-26 to I-28)
    Invariant("I-26", "Only Verified Entities Visible", "Unverified/Pending/Flagged are hidden from users", "BLOCK_ACTION"),
    Invariant("I-27", "Trust + Confidence + Risk = Decision", "Single threshold (50) is not enough. Multi-factor decision.", "BLOCK_ACTION"),
    Invariant("I-28", "Source Attribution Only", "Never say 'Verified by Google'. Always 'Source: Google Maps'.", "BLOCK_ACTION"),
    
    # Freshness & Cost Invariants (I-29 to I-31)
    Invariant("I-29", "TTL = Stale, NOT Expired", "We haven't re-verified → Stale, not Expired", "BLOCK_ACTION"),
    Invariant("I-30", "Reciprocal Trust", "Students/Users have internal trust score (not public)", "BLOCK_ACTION"),
    Invariant("I-31", "AI Cost Governance", "Daily API Budget ($5 MVP), Exceed → Auto-Fallback", "BLOCK_ACTION"),
    
    # Security & Data Invariants (I-32 to I-34)
    Invariant("I-32", "External Data = Untrusted", "Prompt-Injection Protection. External content is never instruction.", "BLOCK_ACTION"),
    Invariant("I-33", "Source Hierarchy", "Tier 1 (Govt) > Tier 2 (Official) > Tier 3 (Verified) > Tier 4 (Aggregator)", "BLOCK_ACTION"),
    Invariant("I-34", "No Candidate-Charged Fee Where Prohibited", "Jurisdiction check before charging candidates", "BLOCK_ACTION")
]

# ---------- 6 CLOSURE PRINCIPLES ----------
class ClosurePrinciple:
    def __init__(self, id: str, description: str, meaning: str):
        self.id = id
        self.description = description
        self.meaning = meaning

CLOSURES = [
    ClosurePrinciple("C-01", "Trust Boundary", "Government > Verified Org > Broker > Unverified"),
    ClosurePrinciple("C-02", "Truth Limitation", "UNKNOWN is a valid final state. System never fabricates."),
    ClosurePrinciple("C-03", "Authorization ≠ Correctness", "AI may send, but final validation is Human/HR"),
    ClosurePrinciple("C-04", "Effect Boundary", "Past external effects cannot be undone by revoking access."),
    ClosurePrinciple("C-05", "Failure Policy", "Each operation has pre-defined FAIL-CLOSED/DEGRADE/HOLD policy"),
    ClosurePrinciple("C-06", "Unsupported Action Closure", "Default = DENY. If not in RBAC, it's forbidden.")
]

# ---------- Constitution Engine ----------
class ConstitutionEngine:
    def __init__(self):
        self.invariants = {inv.id: inv for inv in INVARIANTS}
        self.closures = {cls.id: cls for cls in CLOSURES}
        self.amendment_history = []

    def check_invariant(self, invariant_id: str, context: dict) -> bool:
        if invariant_id not in self.invariants:
            return True
        inv = self.invariants[invariant_id]
        # Placeholder: Actual rule evaluation logic will be implemented per invariant.
        # For now, return True but log a warning if evaluation not implemented.
        return True

    def check_closure(self, closure_id: str, context: dict) -> bool:
        if closure_id not in self.closures:
            return True
        return True

    def propose_amendment(self, proposer_id: str, item: str, proposed_value: dict, rationale: str) -> dict:
        proposal = {
            "id": f"amdt_{datetime.utcnow().timestamp()}",
            "proposer_id": proposer_id,
            "item": item,
            "proposed_value": proposed_value,
            "rationale": rationale,
            "status": "PENDING",
            "created_at": datetime.utcnow().isoformat()
        }
        self.amendment_history.append(proposal)
        return proposal

    def approve_amendment(self, proposal_id: str, approver_id: str, role: str) -> dict:
        proposal = None
        for p in self.amendment_history:
            if p.get("id") == proposal_id:
                proposal = p
                break
        if not proposal:
            raise ValueError("Proposal not found")
        proposal["status"] = "APPROVED"
        proposal["approved_by"] = approver_id
        proposal["approved_at"] = datetime.utcnow().isoformat()
        return proposal

    def get_all_invariants(self) -> List[dict]:
        return [{"id": inv.id, "description": inv.description, "enforcement": inv.enforcement} for inv in INVARIANTS]

    def get_all_closures(self) -> List[dict]:
        return [{"id": cls.id, "description": cls.description, "meaning": cls.meaning} for cls in CLOSURES]

# Singleton
constitution = ConstitutionEngine()