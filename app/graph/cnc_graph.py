import json
import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from app.graph.state import CNCState
from app.services.schemas import SensorDataRequest, ThresholdCheckRequest
from app.schemas.diagnosis import Diagnosis
from app.tools.check_sensor_thresholds import check_sensor_thresholds
from app.tools.get_sensor_data import get_sensor_data
from app.tools.search_machine_manual import search_machine_manual


load_dotenv()


def load_sensor_data_node(state: CNCState) -> CNCState:
    machine_id = state.get("machine_id", "CNC_001")

    sensor_data = get_sensor_data(
        SensorDataRequest(
            machine_id=machine_id,
            profile=state.get("sensor_profile"),
        )
    )

    return {
        "sensor_data": sensor_data.model_dump(mode="json"),
    }


def check_thresholds_node(state: CNCState) -> CNCState:
    sensor_data = state["sensor_data"]

    threshold_analysis = check_sensor_thresholds(
        ThresholdCheckRequest.model_validate({"sensor_data": sensor_data})
    )

    return {
        "threshold_analysis": threshold_analysis.model_dump(mode="json"),
    }


def retrieve_manual_context_node(state: CNCState) -> CNCState:
    user_issue = state.get("user_issue", "")
    sensor_data = state.get("sensor_data", {})
    threshold_analysis = state.get("threshold_analysis", {})

    alerts_text = " ".join(
        [
            item.get("message", "")
            for item in threshold_analysis.get("alerts", [])
        ]
    )

    rag_query = f"""
    CNC troubleshooting.
    User issue: {user_issue}
    Machine ID: {sensor_data.get("machine_id")}
    Temperature C: {sensor_data.get("temperature_c")}
    Torque Nm: {sensor_data.get("torque_nm")}
    Rotation RPM: {sensor_data.get("rotation_rpm")}
    Tool wear pct: {sensor_data.get("tool_wear_pct")}
    Sensor alerts: {alerts_text}
    Relevant terms: spindle overheating high temperature torque tool wear lubrication coolant bearing overload
    """

    manual_context = search_machine_manual(
        query=rag_query,
        n_results=5,
    )

    return {
        "rag_query": rag_query,
        "manual_context": manual_context,
    }


def generate_diagnosis_node(state: CNCState) -> CNCState:
    model_name = os.getenv("OPENAI_MODEL")

    if not model_name:
        raise ValueError("OPENAI_MODEL não encontrado no arquivo .env")

    llm = ChatOpenAI(model=model_name)

    structured_llm = llm.with_structured_output(Diagnosis)

    sensor_data = state.get("sensor_data", {})
    threshold_analysis = state.get("threshold_analysis", {})
    manual_context = state.get("manual_context", [])
    user_issue = state.get("user_issue", "")

    manual_context_text = []

    for i, item in enumerate(manual_context, start=1):
        manual_context_text.append(
            {
                "result": i,
                "source": item.get("source"),
                "page": item.get("page"),
                "content": item.get("content", "")[:1200],
            }
        )

    system_prompt = """
    Você é um agente de reasoning técnico para troubleshooting de manutenção de uma máquina CNC.

    Sua tarefa:
    1. Analisar os dados de sensores.
    2. Considerar violações de limites operacionais.
    3. Usar o contexto recuperado dos manuais.
    4. Gerar hipótese de causa raiz.
    5. Recomendar ações seguras para o operador.
    6. Indicar quando escalar para manutenção.

    Regras importantes:
    - Não invente fonte, página ou procedimento.
    - Se o manual não trouxer evidência suficiente, diga isso nas evidências.
    - Não recomende abrir painéis elétricos, mexer em partes energizadas ou executar reparos perigosos.
    - Para qualquer ação mecânica ou elétrica de risco, recomende acionar manutenção qualificada.
    - Baseie a resposta nas evidências fornecidas.
    - Responda em português do Brasil.
    """

    human_prompt = f"""
    Problema informado pelo operador:
    {user_issue}

    Dados atuais dos sensores:
    {json.dumps(sensor_data, ensure_ascii=False, indent=2)}

    Análise de thresholds:
    {json.dumps(threshold_analysis, ensure_ascii=False, indent=2)}

    Contexto recuperado dos manuais:
    {json.dumps(manual_context_text, ensure_ascii=False, indent=2)}

    Gere um diagnóstico estruturado.
    """

    diagnosis = structured_llm.invoke(
        [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt),
        ]
    )

    return {
        "diagnosis": diagnosis.model_dump(),
    }


def format_response_node(state: CNCState) -> CNCState:
    diagnosis = state["diagnosis"]
    sensor_data = state.get("sensor_data", {})
    threshold_analysis = state.get("threshold_analysis", {})
    manual_context = state.get("manual_context", [])

    sources = []
    for item in manual_context:
        source = item.get("source")
        page = item.get("page")

        if source and page:
            sources.append(f"{source}, página {page}")
        elif source:
            sources.append(source)

    unique_sources = list(dict.fromkeys(sources))

    alerts = threshold_analysis.get("alerts", [])

    alerts_text = "\n".join(
        [
            f"- {item['metric']}: {item['value']} | {item['status']} | {item['message']}"
            for item in alerts
        ]
    )

    root_causes_text = "\n".join(
        [f"{i}. {cause}" for i, cause in enumerate(diagnosis["probable_root_causes"], start=1)]
    )

    evidence_text = "\n".join(
        [f"- {evidence}" for evidence in diagnosis["evidence"]]
    )

    actions_text = "\n".join(
        [f"{i}. {action}" for i, action in enumerate(diagnosis["recommended_actions"], start=1)]
    )

    safety_text = "\n".join(
        [f"- {note}" for note in diagnosis["safety_notes"]]
    )

    sources_text = "\n".join(
        [f"- {source}" for source in unique_sources]
    )

    final_response = f"""
## Diagnóstico da máquina {sensor_data.get("machine_id")}

**Resumo do problema:**  
{diagnosis["problem_summary"]}

**Status:** {threshold_analysis.get("overall_status")}  
**Prioridade:** {diagnosis["priority"]}  
**Confiança:** {diagnosis["confidence"]:.0%}  
**Abrir ticket de manutenção:** {"Sim" if diagnosis["should_open_ticket"] else "Não"}

### Alertas detectados nos sensores
{alerts_text if alerts_text else "- Nenhum alerta detectado."}

### Causas prováveis
{root_causes_text}

### Evidências usadas
{evidence_text}

### Ações recomendadas ao operador
{actions_text}

### Notas de segurança
{safety_text}

### Fontes consultadas
{sources_text if sources_text else "- Nenhuma fonte recuperada do manual."}
"""

    return {
        "final_response": final_response.strip(),
    }


def build_cnc_graph():
    workflow = StateGraph(CNCState)

    workflow.add_node("load_sensor_data", load_sensor_data_node)
    workflow.add_node("check_thresholds", check_thresholds_node)
    workflow.add_node("retrieve_manual_context", retrieve_manual_context_node)
    workflow.add_node("generate_diagnosis", generate_diagnosis_node)
    workflow.add_node("format_response", format_response_node)

    workflow.add_edge(START, "load_sensor_data")
    workflow.add_edge("load_sensor_data", "check_thresholds")
    workflow.add_edge("check_thresholds", "retrieve_manual_context")
    workflow.add_edge("retrieve_manual_context", "generate_diagnosis")
    workflow.add_edge("generate_diagnosis", "format_response")
    workflow.add_edge("format_response", END)

    checkpointer = MemorySaver()

    return workflow.compile(checkpointer=checkpointer)
