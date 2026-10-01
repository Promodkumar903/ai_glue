# ============================================================
# AI GLUE v8.0 — WORKFLOW STATES (Centralized Definition)
# ============================================================
# Purpose: Define all possible states for workflows across modules.
# ============================================================

# Core workflow states used by engines/workflow.py and others
WORKFLOW_STATES = {
    "APPLICATION": {
        "states": ["DRAFT", "SUBMITTED", "UNDER_REVIEW", "REVIEWED", "OFFER_SENT", "ACCEPTED", "REJECTED", "WITHDRAWN"],
        "transitions": {
            "DRAFT": ["SUBMITTED", "WITHDRAWN"],
            "SUBMITTED": ["UNDER_REVIEW", "REJECTED", "WITHDRAWN"],
            "UNDER_REVIEW": ["REVIEWED", "REJECTED"],
            "REVIEWED": ["OFFER_SENT", "REJECTED"],
            "OFFER_SENT": ["ACCEPTED", "REJECTED"],
            "ACCEPTED": [],
            "REJECTED": [],
            "WITHDRAWN": []
        }
    },
    "VISA": {
        "states": ["NOT_STARTED", "APPLIED", "SCHEDULED", "IN_PROGRESS", "APPROVED", "REJECTED"],
        "transitions": {
            "NOT_STARTED": ["APPLIED"],
            "APPLIED": ["SCHEDULED", "REJECTED"],
            "SCHEDULED": ["IN_PROGRESS"],
            "IN_PROGRESS": ["APPROVED", "REJECTED"],
            "APPROVED": [],
            "REJECTED": []
        }
    },
    "OFFER": {
        "states": ["DRAFT", "SENT", "ACCEPTED", "DECLINED", "EXPIRED"],
        "transitions": {
            "DRAFT": ["SENT", "EXPIRED"],
            "SENT": ["ACCEPTED", "DECLINED", "EXPIRED"],
            "ACCEPTED": [],
            "DECLINED": [],
            "EXPIRED": []
        }
    }
}

# Optional: function to get valid transitions for a state
def get_transitions(workflow_type: str, current_state: str):
    """Return list of possible next states for given workflow and state."""
    workflow = WORKFLOW_STATES.get(workflow_type)
    if not workflow:
        return []
    return workflow["transitions"].get(current_state, [])

# Optional: validate if a transition is allowed
def is_valid_transition(workflow_type: str, from_state: str, to_state: str) -> bool:
    """Check if moving from_state -> to_state is valid for the workflow."""
    allowed = get_transitions(workflow_type, from_state)
    return to_state in allowed