from typing import Any

from app.agents.base import ProductionAgent
from app.schemas.production_state import ProductionTroubleshootingState, RankedCause


class ReasoningRecommenderAgent(ProductionAgent):
    name = "Reasoning & Recommender Agent"
    stage = "analysis"

    def run(self, state: ProductionTroubleshootingState) -> dict[str, Any]:
        high_temperature = any(
            alert.code == "temperature" for alert in state.correlated_alerts
        )
        high_torque = any(alert.code == "torque" for alert in state.correlated_alerts)

        causes = [
            RankedCause(
                cause_id="cause_lubrication_or_coolant_restriction",
                description="Insufficient lubrication or coolant restriction causing spindle heat buildup.",
                confidence=0.86 if high_temperature else 0.62,
                confidence_band="high" if high_temperature else "medium",
                evidence_refs=[
                    "threshold_monitor:temperature",
                    "fmea:spindle:overheating",
                ],
                recommended_next_check="Verify coolant/lubrication indicators and visible flow without opening protected panels.",
            ),
            RankedCause(
                cause_id="cause_tool_or_cutting_load",
                description="Excessive cutting load, tool wear, or wrong feed/speed increasing spindle torque.",
                confidence=0.79 if high_torque else 0.54,
                confidence_band="high" if high_torque else "medium",
                evidence_refs=["threshold_monitor:torque", "sop:spindle:thermal-triage"],
                recommended_next_check="Review the last tool change and cutting parameters with the operator.",
            ),
        ]

        return {
            "ranked_causes": sorted(
                causes,
                key=lambda cause: cause.confidence,
                reverse=True,
            ),
            "current_stage": "planning",
            "audit_log": self.audit(
                state,
                "Ranked probable causes with confidence scores.",
            ),
        }
