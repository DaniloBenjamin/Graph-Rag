from typing import Any

from app.agents.base import ProductionAgent
from app.schemas.production_state import ProductionTroubleshootingState


class KnowledgeHarvestingAgent(ProductionAgent):
    name = "Knowledge Harvesting Agent"
    stage = "knowledge"

    def run(self, state: ProductionTroubleshootingState) -> dict[str, Any]:
        capture = state.knowledge_capture
        if capture is not None:
            capture = capture.model_copy(update={"approval_status": "pending_admin_approval"})

        return {
            "knowledge_capture": capture,
            "audit_log": self.audit(
                state,
                "Routed lesson learned to admin approval.",
            ),
        }
