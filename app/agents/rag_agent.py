from typing import Any

from app.agents.base import ProductionAgent
from app.schemas.production_state import KnowledgeDocument, ProductionTroubleshootingState


class RAGAgent(ProductionAgent):
    name = "RAG Agent"
    stage = "planning"

    def run(self, state: ProductionTroubleshootingState) -> dict[str, Any]:
        selected_cause = state.ranked_causes[0] if state.ranked_causes else None
        query_hint = selected_cause.description if selected_cause else state.request.symptom

        documents = [
            KnowledgeDocument(
                title="Spindle troubleshooting guide",
                content=f"Retrieved local placeholder content for: {query_hint}",
                source="local_rag_placeholder",
                relevance=0.81,
            )
        ]

        return {
            "retrieved_documents": documents,
            "audit_log": self.audit(
                state,
                "Retrieved SOP/manual context for the selected cause.",
            ),
        }
