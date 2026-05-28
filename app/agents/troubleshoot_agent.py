from typing import Any

from app.agents.base import ProductionAgent
from app.schemas.production_state import ProductionTroubleshootingState


class TroubleshootAgent(ProductionAgent):
    name = "Troubleshoot Agent"
    stage = "planning"

    def run(self, state: ProductionTroubleshootingState) -> dict[str, Any]:
        # In production this agent runs the interactive branch loop with the operator.
        return {
            "step_outcomes": state.step_outcomes,
            "audit_log": self.audit(
                state,
                "Prepared branching loop; awaiting operator step outcomes.",
            ),
        }
