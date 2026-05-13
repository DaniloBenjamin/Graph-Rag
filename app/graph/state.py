from typing import Any, TypedDict


class CNCState(TypedDict, total=False):
    machine_id: str
    user_issue: str
    sensor_profile: str

    sensor_data: dict[str, Any]
    threshold_analysis: dict[str, Any]

    rag_query: str
    manual_context: list[dict[str, Any]]

    diagnosis: dict[str, Any]
    final_response: str
