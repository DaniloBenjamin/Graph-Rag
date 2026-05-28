from app.graph.production_graph import run_production_troubleshooting
from app.schemas.production_state import IncidentRequest


if __name__ == "__main__":
    final_state = run_production_troubleshooting(
        IncidentRequest(
            incident_id="INC-2026-0001",
            machine_id="CNC_001",
            alarm_code="SPINDLE_TEMP_HIGH",
            symptom="Spindle temperature alarm with elevated load during machining.",
            operator_id="operator_123",
            sensor_profile="overheating",
        )
    )

    print(final_state.model_dump_json(indent=2))
