from abc import ABC, abstractmethod
from typing import Any

from app.schemas.production_state import ProductionTroubleshootingState, StageName


class ProductionAgent(ABC):
    name: str
    stage: StageName

    def audit(
        self,
        state: ProductionTroubleshootingState,
        summary: str,
    ) -> list[dict[str, Any]]:
        return [
            *state.audit_log,
            {
                "agent": self.name,
                "stage": self.stage,
                "summary": summary,
            },
        ]

    @abstractmethod
    def run(self, state: ProductionTroubleshootingState) -> dict[str, Any]:
        raise NotImplementedError
