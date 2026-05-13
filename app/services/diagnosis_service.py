from app.services.schemas import (
    DiagnosisResult,
    ManualContextItem,
    SensorAlert,
    ThresholdCheckResult,
)


CAUSES_BY_METRIC = {
    "temperature": [
        "falha ou baixa eficiencia de lubrificacao",
        "problema de refrigeracao/coolant",
        "rolamento do spindle com atrito elevado",
    ],
    "torque": [
        "sobrecarga de corte",
        "parametros de avanco ou profundidade agressivos",
        "ferramenta perdendo capacidade de corte",
    ],
    "rotation": [
        "queda de desempenho no acionamento do spindle",
        "limite operacional imposto por protecao da maquina",
        "carga mecanica acima do esperado",
    ],
    "tool_wear": [
        "ferramenta no fim da vida util",
        "condicao de corte inadequada para o material",
        "necessidade de troca ou reafiacao da ferramenta",
    ],
}


ACTION_BY_METRIC = {
    "temperature": "Verificar lubrificacao, fluxo de coolant e sinais de aquecimento nos rolamentos.",
    "torque": "Reduzir avanco/profundidade temporariamente e inspecionar carga do spindle.",
    "rotation": "Confirmar comando de RPM, carga mecanica e alarmes do inversor/drive.",
    "tool_wear": "Inspecionar a ferramenta e substituir se o desgaste visual confirmar a leitura.",
}


def _unique(items: list[str]) -> list[str]:
    return list(dict.fromkeys(items))


def build_manual_query(symptom: str, alerts: list[SensorAlert]) -> str:
    alert_terms = " ".join(alert.metric for alert in alerts)
    return f"{symptom} {alert_terms} spindle cnc troubleshooting".strip()


def generate_diagnosis(
    threshold_result: ThresholdCheckResult,
    manual_context: list[ManualContextItem],
    symptom: str,
) -> DiagnosisResult:
    alerts = threshold_result.alerts

    if not alerts:
        return DiagnosisResult(
            machine_id=threshold_result.machine_id,
            status="normal",
            summary="Sensores dentro dos limites simulados. Nenhuma anomalia critica foi detectada.",
            probable_causes=[],
            recommended_actions=[
                "Continuar monitoramento e comparar novas leituras com o historico da maquina."
            ],
            alerts=[],
            manual_context=manual_context,
        )

    causes: list[str] = []
    actions: list[str] = []

    for alert in alerts:
        causes.extend(CAUSES_BY_METRIC.get(alert.metric, []))
        action = ACTION_BY_METRIC.get(alert.metric)
        if action:
            actions.append(action)

    if manual_context:
        actions.append("Consultar os trechos recuperados do manual antes de liberar a maquina para producao.")

    summary = (
        f"Diagnostico inicial para '{symptom}': status {threshold_result.overall_status}. "
        f"Foram encontrados {len(alerts)} alerta(s) nos sensores simulados."
    )

    return DiagnosisResult(
        machine_id=threshold_result.machine_id,
        status=threshold_result.overall_status,
        summary=summary,
        probable_causes=_unique(causes),
        recommended_actions=_unique(actions),
        alerts=alerts,
        manual_context=manual_context,
    )
