from typing import Any

from langgraph.graph import END, StateGraph

from app.agents import (
    ProductionAgent,
    graph_rag_cause_agent,
    graph_rag_solution_agent,
    knowledge_agent,
    knowledge_harvesting_agent,
    maintenance_agent,
    maintenance_ticket_agent,
    mds_agent,
    mds_analysis_agent,
    monitor_alerts_agent,
    rag_agent,
    reasoning_recommender_agent,
    solver_agent,
    troubleshoot_agent,
)
from app.schemas.production_state import (
    IncidentRequest,
    ProductionTroubleshootingState,
)


def _node(agent: ProductionAgent):
    def wrapped(state: dict[str, Any]) -> dict[str, Any]:
        validated_state = ProductionTroubleshootingState.model_validate(state)
        return agent.run(validated_state)

    return wrapped


def build_production_troubleshooting_graph():
    graph = StateGraph(ProductionTroubleshootingState)

    graph.add_node("mds_agent", _node(mds_agent))
    graph.add_node("monitor_alerts_agent", _node(monitor_alerts_agent))
    graph.add_node("mds_analysis_agent", _node(mds_analysis_agent))
    graph.add_node("maintenance_agent", _node(maintenance_agent))
    graph.add_node("graph_rag_cause_agent", _node(graph_rag_cause_agent))
    graph.add_node("graph_rag_solution_agent", _node(graph_rag_solution_agent))
    graph.add_node("reasoning_recommender_agent", _node(reasoning_recommender_agent))
    graph.add_node("rag_agent", _node(rag_agent))
    graph.add_node("solver_agent", _node(solver_agent))
    graph.add_node("troubleshoot_agent", _node(troubleshoot_agent))
    graph.add_node("maintenance_ticket_agent", _node(maintenance_ticket_agent))
    graph.add_node("knowledge_agent", _node(knowledge_agent))
    graph.add_node("knowledge_harvesting_agent", _node(knowledge_harvesting_agent))

    graph.set_entry_point("mds_agent")

    graph.add_edge("mds_agent", "monitor_alerts_agent")
    graph.add_edge("monitor_alerts_agent", "mds_analysis_agent")
    graph.add_edge("mds_analysis_agent", "maintenance_agent")
    graph.add_edge("maintenance_agent", "graph_rag_cause_agent")
    graph.add_edge("graph_rag_cause_agent", "graph_rag_solution_agent")
    graph.add_edge("graph_rag_solution_agent", "reasoning_recommender_agent")
    graph.add_edge("reasoning_recommender_agent", "rag_agent")
    graph.add_edge("rag_agent", "solver_agent")
    graph.add_edge("solver_agent", "troubleshoot_agent")
    graph.add_edge("troubleshoot_agent", "maintenance_ticket_agent")
    graph.add_edge("maintenance_ticket_agent", "knowledge_agent")
    graph.add_edge("knowledge_agent", "knowledge_harvesting_agent")
    graph.add_edge("knowledge_harvesting_agent", END)

    return graph.compile()


production_troubleshooting_graph = build_production_troubleshooting_graph()


def run_production_troubleshooting(
    request: IncidentRequest,
) -> ProductionTroubleshootingState:
    initial_state = ProductionTroubleshootingState(request=request)
    result = production_troubleshooting_graph.invoke(initial_state.model_dump())
    return ProductionTroubleshootingState.model_validate(result)
