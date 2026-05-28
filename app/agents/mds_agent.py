from typing import Any

from app.agents.base import ProductionAgent
from app.schemas.production_state import (
    EquipmentContext,
    ProductionTroubleshootingState,
)


class MDSAgent(ProductionAgent):
    name = "MDS Agent"
    stage = "intake"

    def run(self, state: ProductionTroubleshootingState) -> dict[str, Any]:
        request = state.request
        equipment_context = EquipmentContext(
            machine_id=request.machine_id,
            asset_path=["Plant A", "Line 2", "CNC Cell", request.machine_id],
            line="Line 2",
            shift="A",
            cell="CNC Cell",
            recurrence_flags=["similar_alarm_last_7_days"] if request.alarm_code else [],
        )

        return {
            "equipment_context": equipment_context,
            "audit_log": self.audit(state, "Loaded equipment context."),
        }
