from typing import Any

from app.agents.base import ProductionAgent
from app.schemas.production_state import KnowledgeCapture, ProductionTroubleshootingState


class KnowledgeAgent(ProductionAgent):
    name = "Knowledge Agent"
    stage = "knowledge"

    def run(self, state: ProductionTroubleshootingState) -> dict[str, Any]:
        selected_cause = state.ranked_causes[0]
        capture = KnowledgeCapture(
            candidate_title=f"Lesson learned: {state.request.machine_id} {state.request.symptom}",
            problem=state.request.symptom,
            confirmed_cause=selected_cause.description,
            validation_notes=[
                "Requires technician/admin validation before being added to the knowledge base."
            ],
        )

        return {
            "knowledge_capture": capture,
            "current_stage": "knowledge",
            "audit_log": self.audit(state, "Structured candidate knowledge capture."),
        }
