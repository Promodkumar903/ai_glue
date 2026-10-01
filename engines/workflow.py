"""
AI GLUE — Workflow Engine (State Machine)
"""
from sqlalchemy.orm import Session
from core.database import db, Application, Case
from core.workflow_states import WORKFLOW_STATES
from core.audit import log_audit

class WorkflowEngine:
    @staticmethod
    def get_next_states(entity_type: str, current_state: str):
        """Get allowed next states for an entity."""
        transitions = WORKFLOW_STATES.get(entity_type, {}).get("transitions", {})
        return transitions.get(current_state, [])

    @staticmethod
    def transition(
        entity_type: str,
        entity_id: str,
        target_state: str,
        actor_id: str = None,
        session: Session = None
    ):
        """Transition entity to a new state (with validation)."""
        if session is None:
            session = db.get_session()
        
        # Determine the model based on entity_type
        if entity_type == "STUDENT":
            model = Application
        elif entity_type == "COMPANY":
            model = Case
        else:
            return {"error": f"Unknown entity_type: {entity_type}"}
        
        entity = session.query(model).filter(model.id == entity_id).first()
        if not entity:
            return {"error": f"{entity_type} not found"}
        
        current_state = getattr(entity, "status", None)
        if not current_state:
            return {"error": "Entity has no status field"}
        
        # Validate transition
        allowed = WorkflowEngine.get_next_states(entity_type, current_state)
        if target_state not in allowed:
            return {
                "error": f"Invalid transition: {current_state} -> {target_state}. Allowed: {allowed}"
            }
        
        # Perform transition
        old_status = current_state
        entity.status = target_state
        
        # If it's an application, update submitted_at etc.
        if entity_type == "STUDENT" and target_state == "SUBMITTED":
            entity.submitted_at = datetime.utcnow()
        
        session.commit()
        
        # Audit log
        log_audit(
            actor_id=actor_id,
            action="WORKFLOW_TRANSITION",
            target_type=entity_type,
            target_id=str(entity.id),
            before={"status": old_status},
            after={"status": target_state},
            reason=f"State transition from {old_status} to {target_state}"
        )
        
        return {
            "entity_id": str(entity.id),
            "entity_type": entity_type,
            "old_state": old_status,
            "new_state": target_state,
            "message": f"Successfully transitioned to {target_state}"
        }

    @staticmethod
    def get_workflow_definition(entity_type: str):
        """Get full workflow definition for an entity type."""
        return WORKFLOW_STATES.get(entity_type, {})

workflow = WorkflowEngine()