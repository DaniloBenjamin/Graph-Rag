from typing import Literal
from pydantic import BaseModel, Field


class Diagnosis(BaseModel):
    problem_summary: str = Field(
        description="Resumo técnico curto do problema identificado."
    )

    probable_root_causes: list[str] = Field(
        description="Lista de causas prováveis ordenadas da mais provável para a menos provável."
    )

    evidence: list[str] = Field(
        description="Evidências usadas no diagnóstico, incluindo sensores, thresholds e trechos do manual."
    )

    recommended_actions: list[str] = Field(
        description="Ações recomendadas para o operador executar com segurança."
    )

    safety_notes: list[str] = Field(
        description="Alertas de segurança e situações em que o operador deve acionar manutenção."
    )

    priority: Literal["low", "medium", "high", "critical"] = Field(
        description="Prioridade operacional do problema."
    )

    confidence: float = Field(
        ge=0,
        le=1,
        description="Confiança do diagnóstico entre 0 e 1."
    )

    should_open_ticket: bool = Field(
        description="Indica se um ticket de manutenção deve ser aberto."
    )