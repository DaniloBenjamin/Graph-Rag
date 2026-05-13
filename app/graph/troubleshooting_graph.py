from langgraph.graph import END, StateGraph

from app.services.diagnosis_service import build_manual_query, generate_diagnosis
from app.services.schemas import (
    DiagnosisRequest,
    DiagnosisResult,
    ManualContextItem,
    SensorDataRequest,
    ThresholdCheckRequest,
    TroubleshootingState,
)
from app.tools.check_sensor_thresholds import check_sensor_thresholds
from app.tools.get_sensor_data import get_sensor_data


def load_sensor_data(state: TroubleshootingState) -> dict:
    request = state.request
    sensor_data = get_sensor_data(
        SensorDataRequest(
            machine_id=request.machine_id,
            profile=request.sensor_profile,
        )
    )

    return {"sensor_data": sensor_data}


def check_thresholds(state: TroubleshootingState) -> dict:
    if state.sensor_data is None:
        raise ValueError("sensor_data ausente. Execute load_sensor_data antes de check_thresholds.")

    threshold_result = check_sensor_thresholds(
        ThresholdCheckRequest(sensor_data=state.sensor_data)
    )

    return {"threshold_result": threshold_result}


def retrieve_manual_context(state: TroubleshootingState) -> dict:
    if state.threshold_result is None:
        raise ValueError("threshold_result ausente. Execute check_thresholds antes de retrieve_manual_context.")

    query = build_manual_query(
        symptom=state.request.symptom,
        alerts=state.threshold_result.alerts,
    )

    from app.tools.search_machine_manual import search_machine_manual

    results = search_machine_manual(
        query=query,
        n_results=state.request.n_manual_results,
    )

    manual_context = [ManualContextItem.model_validate(item) for item in results]
    return {"manual_context": manual_context}


def generate_diagnosis_node(state: TroubleshootingState) -> dict:
    if state.threshold_result is None:
        raise ValueError("threshold_result ausente. Execute check_thresholds antes de generate_diagnosis.")

    diagnosis = generate_diagnosis(
        threshold_result=state.threshold_result,
        manual_context=state.manual_context,
        symptom=state.request.symptom,
    )

    return {"diagnosis": diagnosis}


def build_troubleshooting_graph():
    graph = StateGraph(TroubleshootingState)

    graph.add_node("load_sensor_data", load_sensor_data)
    graph.add_node("check_thresholds", check_thresholds)
    graph.add_node("retrieve_manual_context", retrieve_manual_context)
    graph.add_node("generate_diagnosis", generate_diagnosis_node)

    graph.set_entry_point("load_sensor_data")
    graph.add_edge("load_sensor_data", "check_thresholds")
    graph.add_edge("check_thresholds", "retrieve_manual_context")
    graph.add_edge("retrieve_manual_context", "generate_diagnosis")
    graph.add_edge("generate_diagnosis", END)

    return graph.compile()


troubleshooting_graph = build_troubleshooting_graph()


def run_troubleshooting(request: DiagnosisRequest) -> DiagnosisResult:
    initial_state = TroubleshootingState(request=request)
    result = troubleshooting_graph.invoke(initial_state)
    final_state = TroubleshootingState.model_validate(result)

    if final_state.diagnosis is None:
        raise RuntimeError("Fluxo finalizou sem gerar diagnostico.")

    return final_state.diagnosis


if __name__ == "__main__":
    diagnosis = run_troubleshooting(
        DiagnosisRequest(
            machine_id="CNC-001",
            symptom="spindle high temperature",
            sensor_profile="overheating",
        )
    )
    print(diagnosis.model_dump_json(indent=2))
