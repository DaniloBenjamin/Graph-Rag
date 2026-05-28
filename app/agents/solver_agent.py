from typing import Any

from app.agents.base import ProductionAgent
from app.schemas.production_state import (
    ProductionTroubleshootingState,
    TroubleshootingPlan,
    TroubleshootingStep,
)


class SolverAgent(ProductionAgent):
    name = "Solver Agent"
    stage = "planning"

    def run(self, state: ProductionTroubleshootingState) -> dict[str, Any]:
        selected_cause = state.ranked_causes[0]
        plan = TroubleshootingPlan(
            selected_cause_id=selected_cause.cause_id,
            priority="high" if selected_cause.confidence >= 0.75 else "medium",
            summary=f"Troubleshooting plan for {selected_cause.description}",
            steps=[
                TroubleshootingStep(
                    step_id="step_1",
                    instruction="Confirm the active alarm code, machine state, and whether the spindle is still heating.",
                    expected_result="The incident context is confirmed and no unsafe machine state is present.",
                    safety_note="Do not bypass interlocks or guards.",
                    on_pass="step_2",
                    on_fail="escalate",
                ),
                TroubleshootingStep(
                    step_id="step_2",
                    instruction="Inspect visible coolant/lubrication indicators and remove visible chips only if the machine is in a safe stopped state.",
                    expected_result="Coolant/lubrication appears available and no visible obstruction remains.",
                    safety_note="Only perform operator-level visual checks.",
                    on_pass="step_3",
                    on_fail="open_ticket",
                ),
                TroubleshootingStep(
                    step_id="step_3",
                    instruction="Review recent tool change and cutting parameters for abnormal load conditions.",
                    expected_result="Tool and parameters are consistent with the operation.",
                    on_pass="monitor",
                    on_fail="open_ticket",
                ),
            ],
            escalation_criteria=[
                "Temperature remains critical after operator-level checks.",
                "Alarm recurs during the next supervised cycle.",
                "Any action requires opening electrical, spindle, or protected mechanical assemblies.",
            ],
        )

        return {
            "troubleshooting_plan": plan,
            "audit_log": self.audit(
                state,
                "Generated operator-safe troubleshooting plan.",
            ),
        }
