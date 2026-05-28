# CNC Troubleshooting Agents - Real Case Architecture

This document describes how the current local MVP evolves into a production-oriented
agent ecosystem for Azure AI Foundry.

## Target Runtime

- Platform: Azure AI Foundry hosted/container agent.
- Model deployment: GPT-4.1 through an Azure OpenAI deployment, referenced by deployment name.
- Orchestration: LangGraph inside the container image.
- Local mode: deterministic/simulated adapters so development can continue without Azure access.
- Production mode: replace local adapters with MDS, monitoring, GraphRAG, CMMS and knowledge-base connectors.

## Current MVP vs Real Case

The MVP currently does four useful things:

1. Simulates CNC sensor readings.
2. Checks thresholds.
3. Retrieves local manual context.
4. Produces a structured diagnosis.

The real case keeps those capabilities, but separates them into deployable agent
responsibilities with explicit state contracts. This makes each integration replaceable
without changing the whole orchestration graph.

## Agent Ecosystem Mapping

| Agent | Stage | Production responsibility | Local implementation |
| --- | --- | --- | --- |
| MDS Agent | 1 | Pull alarm context, equipment hierarchy, line, shift and recurrence flags from MDS. | `mds_agent` returns simulated equipment context. |
| Monitor Alerts Agent | 1 | Surface correlated alarms and anomaly scores. | `monitor_alerts_agent` uses threshold checks over simulated sensor data. |
| MDS Analysis Agent | 2 | Slice trends and detect sensor anomalies over the incident window. | `mds_analysis_agent` returns representative trend summaries. |
| Maintenance Agent | 2 | Retrieve historical maintenance records for affected equipment. | `maintenance_agent` returns a sample prior work order. |
| GraphRAG Cause Agent | 2 | Query FMEA, prior incidents and asset graph for cause hypotheses. | `graph_rag_cause_agent` returns placeholder graph evidence. |
| GraphRAG Solution Agent | 2 | Query SOP and resolution graph for validated solution patterns. | `graph_rag_solution_agent` returns placeholder SOP evidence. |
| Reasoning & Recommender Agent | 2 | Synthesize outputs into ranked, confidence-scored causes. | `reasoning_recommender_agent` ranks causes deterministically. |
| RAG Agent | 3 | Retrieve SOPs, OEM manuals and diagrams for the selected cause. | `rag_agent` returns placeholder document context. |
| Solver Agent | 3 | Generate the safe step-by-step troubleshooting plan. | `solver_agent` creates an operator-safe plan. |
| Troubleshoot Agent | 3 | Run branching operator loop and capture per-step outcomes. | `troubleshoot_agent` prepares the loop; UI/API will provide outcomes. |
| Maintenance Ticket Agent | 4 | Assemble pre-filled CMMS payload from accumulated state. | `maintenance_ticket_agent` creates a CMMS draft. |
| Knowledge Agent | 5 | Validate and structure captured knowledge. | `knowledge_agent` creates a lesson-learned draft. |
| Knowledge Harvesting Agent | 5 | Route lesson learned through admin approval. | `knowledge_harvesting_agent` marks capture as pending approval. |

## Code Entry Points

- MVP graph: `app/graph/cnc_graph.py`
- Production-ready graph: `app/graph/production_graph.py`
- Agent implementations: `app/agents/production_agents.py`
- Shared production state contracts: `app/schemas/production_state.py`
- Local real-case runner: `run_real_case.py`
- Foundry metadata placeholder: `.foundry/agent-metadata.yaml`

## Production State

The `ProductionTroubleshootingState` object is the cross-agent contract. It keeps:

- incident request;
- equipment context;
- correlated alerts;
- MDS trend slices;
- maintenance records;
- GraphRAG cause and solution evidence;
- ranked causes;
- retrieved SOP/manual documents;
- troubleshooting plan and step outcomes;
- CMMS ticket draft;
- knowledge capture draft;
- audit log.

This is intentionally broader than the MVP state so every later integration has a stable
place to write its output.

## Azure Foundry Deployment Shape

Recommended first production packaging:

1. Deploy one hosted/container agent named `cnc-troubleshooting-orchestrator`.
2. Keep the sub-agents as internal Python modules inside the same image.
3. Expose one primary invocation path that accepts an incident request and returns the accumulated state or an operator-facing response.
4. Add service connectors behind each agent module.
5. Split individual sub-agents into separate hosted agents only if independent scaling, ownership, security boundaries or release cycles require it.

This keeps the first real implementation simpler while preserving the architecture names
and responsibilities.

## GPT-4.1 Configuration

Use an Azure OpenAI model deployment named clearly, for example:

```env
AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com/
AZURE_OPENAI_API_KEY=<secret>
AZURE_OPENAI_DEPLOYMENT=gpt-4.1
AZURE_OPENAI_API_VERSION=<tenant-approved-api-version>
```

In code, prefer referencing the deployment name instead of hard-coding the base model.
For local development, keep the existing `OPENAI_MODEL` path until the Azure client is
added.

## Integration Backlog

1. Replace `mds_agent` with an MDS client.
2. Replace `monitor_alerts_agent` with monitoring/alarm correlation service calls.
3. Replace `mds_analysis_agent` with trend and anomaly services over the incident window.
4. Replace `maintenance_agent` with a CMMS or maintenance history connector.
5. Replace GraphRAG placeholders with graph queries over FMEA, SOPs and prior incidents.
6. Replace `rag_agent` placeholder with the existing Chroma path locally and Azure AI Search in production.
7. Add FastAPI or Foundry invocation adapter for operator UI integration.
8. Add persistence for incident state, step outcomes and audit log.
9. Add evaluation datasets under `.foundry/datasets/` for smoke, safety and regression checks.

## Safety Rules To Preserve

- Operator-facing steps must remain visual, procedural and safe.
- Anything involving electrical panels, spindle internals, energized parts, guarded areas or protected mechanical assemblies must escalate to qualified maintenance.
- Every cause recommendation should include evidence references and confidence.
- Knowledge harvesting should require human/admin approval before updating the production knowledge base.
