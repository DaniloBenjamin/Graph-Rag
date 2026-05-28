from typing import Any

from app.agents.base import ProductionAgent
from app.schemas.production_state import (
    MaintenanceTicketDraft,
    ProductionTroubleshootingState,
)


class MaintenanceTicketAgent(ProductionAgent):
    name = "Maintenance Ticket Agent"
    stage = "ticketing"

    def run(self, state: ProductionTroubleshootingState) -> dict[str, Any]:
        plan = state.troubleshooting_plan
        selected_cause = state.ranked_causes[0]
        cause_description = selected_cause.description.rstrip(".")

        ticket = MaintenanceTicketDraft(
            machine_id=state.request.machine_id,
            priority=plan.priority if plan else "medium",
            title=f"{state.request.machine_id}: {state.request.symptom}",
            description=(
                f"Probable cause: {cause_description}. "
                f"Confidence: {selected_cause.confidence:.0%}. "
                f"Operator-safe plan generated for incident {state.request.incident_id}."
            ),
            evidence=[
                *(alert.message for alert in state.correlated_alerts),
                *(trend.summary for trend in state.trend_slices),
            ],
        )

        return {
            "ticket_draft": ticket,
            "current_stage": "ticketing",
            "audit_log": self.audit(state, "Assembled CMMS ticket draft."),
        }
