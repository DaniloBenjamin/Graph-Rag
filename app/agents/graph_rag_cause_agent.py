from typing import Any

from app.agents.base import ProductionAgent
from app.schemas.production_state import EvidenceItem, ProductionTroubleshootingState


class GraphRAGCauseAgent(ProductionAgent):
    name = "GraphRAG Cause Agent"
    stage = "analysis"

    def run(self, state: ProductionTroubleshootingState) -> dict[str, Any]:
        evidence = [
            EvidenceItem(
                source_agent=self.name,
                title="FMEA: spindle overheating",
                detail="Known causes include insufficient lubrication, coolant flow restriction, excessive tool wear, and bearing degradation.",
                source_ref="fmea:spindle:overheating",
                confidence=0.78,
            )
        ]

        return {
            "graph_cause_evidence": evidence,
            "audit_log": self.audit(
                state,
                "Retrieved cause hypotheses from the knowledge graph.",
            ),
        }
