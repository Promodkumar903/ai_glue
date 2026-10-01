# ============================================================
# AI GLUE — CONSTITUTION ENGINE (RULES & INVARIANTS)
# ============================================================
# 12 Articles, 15 Invariants, 6 Closure Principles.
# Enforced by every Engine before any state-changing action.
# ============================================================

class Constitution:
    """Central repository of all constitutional rules."""

    # ---------- 12 ARTICLES ----------
    ARTICLES = {
        "I": {"title": "Sovereignty", "rule": "Constitution applies to all Engines; no override except Human Emergency Override."},
        "II": {"title": "Truth & Evidence", "rule": "No Claim becomes Fact without Evidence. Every Data Point has Truth_State (VERIFIED/CONFLICTED/UNKNOWN)."},
        "III": {"title": "Authority Delegation", "rule": "L0–L4 — L4 actions (Payment, Offer Accept, Visa Submit) require Human only."},
        "IV": {"title": "Engine Boundaries", "rule": "Each Engine has MUST/MUST NOT/Limit (e.g., Search max 10,000 results)."},
        "V": {"title": "Dependency Coupling", "rule": "Direct DB Access forbidden; Event Bus mandatory."},
        "VI": {"title": "System Resources & Budget", "rule": "Token limit (50k/Request), Timeout (30s), Search Cap (10k)."},
        "VII": {"title": "External Interaction", "rule": "AI drafts, Human approves (Email/SMS/Outreach)."},
        "VIII": {"title": "Failure Recovery", "rule": "3 Strikes → Dead Letter → Human Escalation."},
        "IX": {"title": "Data Privacy", "rule": "Classification (Public/Internal/Private/Confidential) — Purpose Binding."},
        "X": {"title": "Audit", "rule": "Every State Change, L4 Action, AI Decision, System Error → Append-Only Log."},
        "XI": {"title": "Customer Communication", "rule": "Standardized Rejection Response (reason_code + user_message)."},
        "XII": {"title": "Amendment", "rule": "Only Master Admin + Governing Body (CR, Impact Analysis, Dual Approval, Rollback Plan)."},
    }

    # ---------- 15 INVARIANTS (I-01 to I-15) ----------
    INVARIANTS = {
        "I-01": "No unauthorized side effect: बिना Candidate/Company के final click के Application Submit/Payment/Contract नहीं।",
        "I-02": "No authority escalation: Broker_Agent अपने Owner से ज़्यादा Scope नहीं ले सकता।",
        "I-03": "No self-authorization: AI अपनी Recommendation को खुद Approve नहीं कर सकता।",
        "I-04": "No self-verification: Connector बनाने वाला उसे Verify नहीं कर सकता — GOVERNANCE_ADMIN अलग।",
        "I-05": "No silent scope expansion: Broker बिना नई Consent के Candidate-list नहीं बढ़ा सकता।",
        "I-06": "No execution without context: हर Submit एक Case_ID + Plan_Hash + Actor_ID से बंधा।",
        "I-07": "No blind retry: बिना Duplicate-Check के कभी दुबारा Submit नहीं।",
        "I-08": "No cross-tenant access: Org-A, Org-B का Data नहीं देख सकती।",
        "I-09": "No execution on stale authorization: Consent Revoke होते ही Broker की Access तुरंत Expire।",
        "I-10": "No unverifiable evidence: Matching/Ranking में हर Claim के पीछे Evidence Cortex होना चाहिए।",
        "I-11": "No secret in audit: Password/Card/ID कभी Raw नहीं जाएगा।",
        "I-12": "No promotion by sandbox alone: नया Model Shadow-Mode + Governance Approval के बिना Production में नहीं।",
        "I-13": "No destructive migration w/o recovery: Rollback-Plan अनिवार्य।",
        "I-14": "No capability surviving revocation: Revoke होने पर Session Token तुरंत Invalidate।",
        "I-15": "No recovery beyond original ceiling: Refund/Compensation मूल Amount/Scope से ज़्यादा नहीं।",
    }

    # ---------- 6 CLOSURE PRINCIPLES (C-01 to C-06) ----------
    CLOSURE_PRINCIPLES = {
        "C-01": "Trust Boundary: Government > Verified Org > Broker > Unverified – Chain हमेशा Explicit Anchor पर रुकती है।",
        "C-02": "Truth Limitation: Conflicting Sources → UNKNOWN एक Valid State है।",
        "C-03": "Authorization ≠ Correctness: AI को भेजने का अधिकार है, पर सही Match की गारंटी नहीं – HR/Candidate Final।",
        "C-04": "Effect Boundary: एक बार External Submit हो जाए, तो Access Revoke से Past Effect नहीं Undo।",
        "C-05": "Failure Policy: हर Operation के लिए Pre-defined FAIL-CLOSED/DEGRADE/HOLD।",
        "C-06": "Unsupported Action Closure: Default = DENY – जो RBAC में नहीं, वह Execute नहीं।",
    }

    @classmethod
    def check_invariant(cls, invariant_id: str, context: dict) -> bool:
        """Check if a given invariant holds in the current context."""
        # This will be implemented with actual logic in each Engine.
        # For now, placeholder.
        return True

    @classmethod
    def get_rule(cls, rule_id: str) -> str:
        """Retrieve a specific constitutional rule."""
        if rule_id in cls.ARTICLES:
            return cls.ARTICLES[rule_id]["rule"]
        elif rule_id in cls.INVARIANTS:
            return cls.INVARIANTS[rule_id]
        elif rule_id in cls.CLOSURE_PRINCIPLES:
            return cls.CLOSURE_PRINCIPLES[rule_id]
        return "Unknown rule"