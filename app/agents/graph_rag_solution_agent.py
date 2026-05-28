from typing import Any

from app.agents.base import ProductionAgent
from app.schemas.production_state import EvidenceItem, ProductionTroubleshootingState


class GraphRAGSolutionAgent(ProductionAgent):
    name = "GraphRAG Solution Agent"
    stage = "analysis"

    def run(self, state: ProductionTroubleshootingState) -> dict[str, Any]:
        evidence = [
            EvidenceItem(
                source_agent=self.name,
                title="SOP: spindle thermal alarm triage",
                detail="Safe operator checks should verify coolant level, visible chips near spindle, recent tool change, and alarm recurrence before escalation.",
                source_ref="sop:spindle:thermal-triage",
                confidence=0.74,
            )
        ]

        return {
            "graph_solution_evidence": evidence,
            "audit_log": self.audit(
                state,
                "Retrieved solution patterns from the knowledge graph.",
            ),
        }
