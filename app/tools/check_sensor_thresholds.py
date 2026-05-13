from app.services.schemas import (
    SensorAlert,
    ThresholdCheckRequest,
    ThresholdCheckResult,
    ThresholdStatus,
)


STATUS_RANK: dict[ThresholdStatus, int] = {
    "normal": 0,
    "warning": 1,
    "critical": 2,
}


def _max_status(current: ThresholdStatus, candidate: ThresholdStatus) -> ThresholdStatus:
    return candidate if STATUS_RANK[candidate] > STATUS_RANK[current] else current


def check_sensor_thresholds(request: ThresholdCheckRequest) -> ThresholdCheckResult:
    """
    Verifica temperatura, torque, rotacao e desgaste contra limites configuraveis.
    """
    data = request.sensor_data
    thresholds = request.thresholds
    alerts: list[SensorAlert] = []
    overall_status: ThresholdStatus = "normal"

    if data.temperature_c >= thresholds.temperature_critical_c:
        status: ThresholdStatus = "critical"
        alerts.append(
            SensorAlert(
                metric="temperature",
                status=status,
                value=data.temperature_c,
                limit=thresholds.temperature_critical_c,
                message="Temperatura do spindle em nivel critico.",
            )
        )
        overall_status = _max_status(overall_status, status)
    elif data.temperature_c >= thresholds.temperature_warning_c:
        status = "warning"
        alerts.append(
            SensorAlert(
                metric="temperature",
                status=status,
                value=data.temperature_c,
                limit=thresholds.temperature_warning_c,
                message="Temperatura do spindle acima do recomendado.",
            )
        )
        overall_status = _max_status(overall_status, status)

    if data.torque_nm >= thresholds.torque_critical_nm:
        status = "critical"
        alerts.append(
            SensorAlert(
                metric="torque",
                status=status,
                value=data.torque_nm,
                limit=thresholds.torque_critical_nm,
                message="Torque do spindle em nivel critico.",
            )
        )
        overall_status = _max_status(overall_status, status)
    elif data.torque_nm >= thresholds.torque_warning_nm:
        status = "warning"
        alerts.append(
            SensorAlert(
                metric="torque",
                status=status,
                value=data.torque_nm,
                limit=thresholds.torque_warning_nm,
                message="Torque do spindle acima do esperado.",
            )
        )
        overall_status = _max_status(overall_status, status)

    if data.rotation_rpm < thresholds.min_rotation_rpm:
        status = "warning"
        alerts.append(
            SensorAlert(
                metric="rotation",
                status=status,
                value=float(data.rotation_rpm),
                limit=float(thresholds.min_rotation_rpm),
                message="Rotacao abaixo do minimo esperado para a operacao.",
            )
        )
        overall_status = _max_status(overall_status, status)

    if data.tool_wear_pct >= thresholds.tool_wear_critical_pct:
        status = "critical"
        alerts.append(
            SensorAlert(
                metric="tool_wear",
                status=status,
                value=data.tool_wear_pct,
                limit=thresholds.tool_wear_critical_pct,
                message="Desgaste da ferramenta em nivel critico.",
            )
        )
        overall_status = _max_status(overall_status, status)
    elif data.tool_wear_pct >= thresholds.tool_wear_warning_pct:
        status = "warning"
        alerts.append(
            SensorAlert(
                metric="tool_wear",
                status=status,
                value=data.tool_wear_pct,
                limit=thresholds.tool_wear_warning_pct,
                message="Desgaste da ferramenta acima do recomendado.",
            )
        )
        overall_status = _max_status(overall_status, status)

    return ThresholdCheckResult(
        machine_id=data.machine_id,
        overall_status=overall_status,
        alerts=alerts,
        sensor_data=data,
    )
