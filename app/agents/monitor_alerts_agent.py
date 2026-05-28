from typing import Any

from app.agents.base import ProductionAgent
from app.schemas.production_state import (
    CorrelatedAlert,
    ProductionTroubleshootingState,
)
from app.services.schemas import SensorDataRequest, ThresholdCheckRequest
from app.tools.check_sensor_thresholds import check_sensor_thresholds
from app.tools.get_sensor_data import get_sensor_data


class MonitorAlertsAgent(ProductionAgent):
    name = "Monitor Alerts Agent"
    stage = "intake"

    def run(self, state: ProductionTroubleshootingState) -> dict[str, Any]:
        request = state.request
        sensor_data = get_sensor_data(
            SensorDataRequest(
                machine_id=request.machine_id,
                profile=request.sensor_profile,
            )
        )
        threshold_result = check_sensor_thresholds(
            ThresholdCheckRequest(sensor_data=sensor_data)
        )

        alerts = [
            CorrelatedAlert(
                source="threshold_monitor",
                code=alert.metric,
                message=alert.message,
                severity="critical" if alert.status == "critical" else "medium",
                score=0.9 if alert.status == "critical" else 0.65,
            )
            for alert in threshold_result.alerts
        ]

        if request.alarm_code:
            alerts.append(
                CorrelatedAlert(
                    source="cnc_alarm",
                    code=request.alarm_code,
                    message=f"Alarm {request.alarm_code} reported by operator context.",
                    severity="high",
                    score=0.75,
                )
            )

        return {
            "correlated_alerts": alerts,
            "audit_log": self.audit(state, f"Correlated {len(alerts)} alert(s)."),
        }
