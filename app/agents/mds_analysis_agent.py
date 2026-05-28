from datetime import timedelta
from typing import Any

from app.agents.base import ProductionAgent
from app.schemas.production_state import (
    ProductionTroubleshootingState,
    SensorTrendSlice,
)


class MDSAnalysisAgent(ProductionAgent):
    name = "MDS Analysis Agent"
    stage = "analysis"

    def run(self, state: ProductionTroubleshootingState) -> dict[str, Any]:
        request = state.request
        window_end = request.occurred_at
        window_start = window_end - timedelta(minutes=30)

        trend_slices = [
            SensorTrendSlice(
                metric="spindle_temperature",
                window_start=window_start,
                window_end=window_end,
                summary="Temperature increased during the incident window.",
                anomaly_score=0.82,
            ),
            SensorTrendSlice(
                metric="spindle_torque",
                window_start=window_start,
                window_end=window_end,
                summary="Torque remained above expected load during cutting.",
                anomaly_score=0.68,
            ),
        ]

        return {
            "trend_slices": trend_slices,
            "current_stage": "analysis",
            "audit_log": self.audit(state, "Created incident-window trend slices."),
        }
