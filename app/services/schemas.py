from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, Field


ThresholdStatus = Literal["normal", "warning", "critical"]


class SensorDataRequest(BaseModel):
    machine_id: str = Field(..., description="Identificador da CNC.")
    profile: Optional[str] = Field(
        default=None,
        description="Perfil opcional para simular cenarios conhecidos.",
    )


class SensorData(BaseModel):
    machine_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    temperature_c: float = Field(..., description="Temperatura do spindle em Celsius.")
    torque_nm: float = Field(..., description="Torque atual do spindle em Nm.")
    rotation_rpm: int = Field(..., description="Rotacao atual do spindle em RPM.")
    tool_wear_pct: float = Field(..., description="Desgaste estimado da ferramenta em %.")


class Thresholds(BaseModel):
    temperature_warning_c: float = 70.0
    temperature_critical_c: float = 85.0
    torque_warning_nm: float = 120.0
    torque_critical_nm: float = 145.0
    min_rotation_rpm: int = 7000
    tool_wear_warning_pct: float = 65.0
    tool_wear_critical_pct: float = 85.0


class ThresholdCheckRequest(BaseModel):
    sensor_data: SensorData
    thresholds: Thresholds = Field(default_factory=Thresholds)


class SensorAlert(BaseModel):
    metric: Literal["temperature", "torque", "rotation", "tool_wear"]
    status: ThresholdStatus
    value: float
    limit: float
    message: str


class ThresholdCheckResult(BaseModel):
    machine_id: str
    overall_status: ThresholdStatus
    alerts: list[SensorAlert]
    sensor_data: SensorData


class ManualContextItem(BaseModel):
    content: str
    source: Optional[str] = None
    page: Optional[int] = None
    distance: Optional[float] = None


class DiagnosisRequest(BaseModel):
    machine_id: str
    symptom: str = Field(default="spindle high temperature")
    sensor_profile: Optional[str] = None
    n_manual_results: int = 4


class DiagnosisResult(BaseModel):
    machine_id: str
    status: ThresholdStatus
    summary: str
    probable_causes: list[str]
    recommended_actions: list[str]
    alerts: list[SensorAlert]
    manual_context: list[ManualContextItem]


class TroubleshootingState(BaseModel):
    request: DiagnosisRequest
    sensor_data: Optional[SensorData] = None
    threshold_result: Optional[ThresholdCheckResult] = None
    manual_context: list[ManualContextItem] = Field(default_factory=list)
    diagnosis: Optional[DiagnosisResult] = None
