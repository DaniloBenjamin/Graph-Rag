from app.agents.base import ProductionAgent
from app.agents.graph_rag_cause_agent import GraphRAGCauseAgent
from app.agents.graph_rag_solution_agent import GraphRAGSolutionAgent
from app.agents.knowledge_agent import KnowledgeAgent
from app.agents.knowledge_harvesting_agent import KnowledgeHarvestingAgent
from app.agents.maintenance_agent import MaintenanceAgent
from app.agents.maintenance_ticket_agent import MaintenanceTicketAgent
from app.agents.mds_agent import MDSAgent
from app.agents.mds_analysis_agent import MDSAnalysisAgent
from app.agents.monitor_alerts_agent import MonitorAlertsAgent
from app.agents.rag_agent import RAGAgent
from app.agents.reasoning_recommender_agent import ReasoningRecommenderAgent
from app.agents.solver_agent import SolverAgent
from app.agents.troubleshoot_agent import TroubleshootAgent


mds_agent = MDSAgent()
monitor_alerts_agent = MonitorAlertsAgent()
mds_analysis_agent = MDSAnalysisAgent()
maintenance_agent = MaintenanceAgent()
graph_rag_cause_agent = GraphRAGCauseAgent()
graph_rag_solution_agent = GraphRAGSolutionAgent()
reasoning_recommender_agent = ReasoningRecommenderAgent()
rag_agent = RAGAgent()
solver_agent = SolverAgent()
troubleshoot_agent = TroubleshootAgent()
maintenance_ticket_agent = MaintenanceTicketAgent()
knowledge_agent = KnowledgeAgent()
knowledge_harvesting_agent = KnowledgeHarvestingAgent()


__all__ = [
    "ProductionAgent",
    "MDSAgent",
    "MonitorAlertsAgent",
    "MDSAnalysisAgent",
    "MaintenanceAgent",
    "GraphRAGCauseAgent",
    "GraphRAGSolutionAgent",
    "ReasoningRecommenderAgent",
    "RAGAgent",
    "SolverAgent",
    "TroubleshootAgent",
    "MaintenanceTicketAgent",
    "KnowledgeAgent",
    "KnowledgeHarvestingAgent",
    "mds_agent",
    "monitor_alerts_agent",
    "mds_analysis_agent",
    "maintenance_agent",
    "graph_rag_cause_agent",
    "graph_rag_solution_agent",
    "reasoning_recommender_agent",
    "rag_agent",
    "solver_agent",
    "troubleshoot_agent",
    "maintenance_ticket_agent",
    "knowledge_agent",
    "knowledge_harvesting_agent",
]
