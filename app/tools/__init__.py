__all__ = [
    "check_sensor_thresholds",
    "get_sensor_data",
    "search_machine_manual",
]


def __getattr__(name: str):
    if name == "check_sensor_thresholds":
        from app.tools.check_sensor_thresholds import check_sensor_thresholds

        return check_sensor_thresholds
    if name == "get_sensor_data":
        from app.tools.get_sensor_data import get_sensor_data

        return get_sensor_data
    if name == "search_machine_manual":
        from app.tools.search_machine_manual import search_machine_manual

        return search_machine_manual
    raise AttributeError(f"module 'app.tools' has no attribute {name!r}")
