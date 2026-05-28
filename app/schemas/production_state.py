from datetime import datetime, timezone
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


StageName = Literal[
    "intake",
    "analysis",
    "planning",
    "ticketing",
    "knowledge",
]

Priority = Literal["low", "medium", "high", "critical"]
ConfidenceBand = Literal["low", "medium", "high"]


class IncidentRequest(BaseModel):
    incident_id: str = Field(..., description="Unique incident or alarm identifier.")
    machine_id: str = Field(..., description="Affected machine identifier.")
    alarm_code: Optional[str] = Field(default=None)
    symptom: str
    operator_id: Optional[str] = Field(default=None)
    sensor_profile: Optional[str] = Field(
        default=None,
        description="Local simulator profile. Replaced by MDS telemetry in production.",
    )
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EquipmentContext(BaseModel):
    machine_id: str
    asset_path: list[str] = Field(default_factory=list)
    line: Optional[str] = None
    shift: Optional[str] = None
    cell: Optional[str] = None
    recurrence_flags: list[str] = Field(default_factory=list)
    active_work_order_ids: list[str] = Field(default_factory=list)


class CorrelatedAlert(BaseModel):
    source: str
    code: str
    message: str
    severity: Priority = "medium"
    score: float = Field(default=0.0, ge=0.0, le=1.0)


class SensorTrendSlice(BaseModel):
    metric: str
    window_start: datetime
    window_end: datetime
    summary: str
    anomaly_score: float = Field(default=0.0, ge=0.0, le=1.0)


class MaintenanceRecord(BaseModel):
    work_order_id: str
    machine_id: str
    closed_at: Optional[datetime] = None
    summary: str
    replaced_parts: list[str] = Field(default_factory=list)
    outcome: Optional[str] = None


class EvidenceItem(BaseModel):
    source_agent: str
    title: str
    detail: str
    source_ref: Optional[str] = None
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)


class RankedCause(BaseModel):
    cause_id: str
    description: str
    confidence: float = Field(ge=0.0, le=1.0)
    confidence_band: ConfidenceBand
    evidence_refs: list[str] = Field(default_factory=list)
    recommended_next_check: Optional[str] = None


class KnowledgeDocument(BaseModel):
    title: str
    content: str
    source: Optional[str] = None
    page: Optional[int] = None
    relevance: float = Field(default=0.0, ge=0.0, le=1.0)


class TroubleshootingStep(BaseModel):
    step_id: str
    instruction: str
    expected_result: str
    safety_note: Optional[str] = None
    on_pass: Optional[str] = None
    on_fail: Optional[str] = None


class TroubleshootingPlan(BaseModel):
    selected_cause_id: str
    priority: Priority
    summary: str
    steps: list[TroubleshootingStep]
    escalation_criteria: list[str] = Field(default_factory=list)


class StepOutcome(BaseModel):
    step_id: str
    outcome: Literal["pass", "fail", "skipped", "blocked"]
    operator_note: Optional[str] = None
    captured_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MaintenanceTicketDraft(BaseModel):
    cmms_system: str = "CMMS"
    machine_id: str
    priority: Priority
    title: str
    description: str
    evidence: list[str] = Field(default_factory=list)
    recommended_parts: list[str] = Field(default_factory=list)


class KnowledgeCapture(BaseModel):
    candidate_title: str
    problem: str
    confirmed_cause: Optional[str] = None
    resolution: Optional[str] = None
    validation_notes: list[str] = Field(default_factory=list)
    approval_status: Literal["draft", "pending_admin_approval", "approved"] = "draft"


class ProductionTroubleshootingState(BaseModel):
    request: IncidentRequest
    current_stage: StageName = "intake"

    equipment_context: Optional[EquipmentContext] = None
    correlated_alerts: list[CorrelatedAlert] = Field(default_factory=list)

    trend_slices: list[SensorTrendSlice] = Field(default_factory=list)
    maintenance_records: list[MaintenanceRecord] = Field(default_factory=list)
    graph_cause_evidence: list[EvidenceItem] = Field(default_factory=list)
    graph_solution_evidence: list[EvidenceItem] = Field(default_factory=list)
    ranked_causes: list[RankedCause] = Field(default_factory=list)

    retrieved_documents: list[KnowledgeDocument] = Field(default_factory=list)
    troubleshooting_plan: Optional[TroubleshootingPlan] = None
    step_outcomes: list[StepOutcome] = Field(default_factory=list)

    ticket_draft: Optional[MaintenanceTicketDraft] = None
    knowledge_capture: Optional[KnowledgeCapture] = None

    audit_log: list[dict[str, Any]] = Field(default_factory=list)
