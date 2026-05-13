import random

from app.services.schemas import SensorData, SensorDataRequest


SENSOR_PROFILES: dict[str, dict[str, float | int]] = {
    "normal": {
        "temperature_c": 58.0,
        "torque_nm": 92.0,
        "rotation_rpm": 9200,
        "tool_wear_pct": 38.0,
    },
    "overheating": {
        "temperature_c": 88.0,
        "torque_nm": 118.0,
        "rotation_rpm": 8800,
        "tool_wear_pct": 55.0,
    },
    "overload": {
        "temperature_c": 76.0,
        "torque_nm": 151.0,
        "rotation_rpm": 6500,
        "tool_wear_pct": 72.0,
    },
    "tool_wear": {
        "temperature_c": 73.0,
        "torque_nm": 134.0,
        "rotation_rpm": 8100,
        "tool_wear_pct": 91.0,
    },
}


def get_sensor_data(request: SensorDataRequest) -> SensorData:
    """
    Retorna leituras simuladas de sensores da CNC.
    """
    profile_name = request.profile or "normal"
    profile = SENSOR_PROFILES.get(profile_name, SENSOR_PROFILES["normal"])

    return SensorData(
        machine_id=request.machine_id,
        temperature_c=round(float(profile["temperature_c"]) + random.uniform(-2.0, 2.0), 1),
        torque_nm=round(float(profile["torque_nm"]) + random.uniform(-4.0, 4.0), 1),
        rotation_rpm=max(0, int(profile["rotation_rpm"]) + random.randint(-150, 150)),
        tool_wear_pct=min(
            100.0,
            max(0.0, round(float(profile["tool_wear_pct"]) + random.uniform(-3.0, 3.0), 1)),
        ),
    )
