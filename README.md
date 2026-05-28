# MVP de Troubleshooting de CNC com LangGraph

Este projeto é um MVP de agente para troubleshooting de máquinas CNC. A ideia é combinar leituras simuladas de sensores, regras simples de thresholds, recuperação de contexto em manuais técnicos via ChromaDB local e geração de um diagnóstico estruturado com LLM.

O objetivo não é substituir um técnico de manutenção, mas demonstrar um fluxo inicial de apoio à decisão: o operador informa um problema, o sistema consulta dados operacionais simulados, verifica condições críticas, busca trechos relevantes do manual e produz uma resposta com causas prováveis, evidências, ações recomendadas e notas de segurança.

## O Que Este MVP Faz

- Simula dados de sensores de uma CNC, como temperatura do spindle, torque, rotação e desgaste da ferramenta.
- Verifica se as leituras ultrapassam limites operacionais configurados.
- Consulta uma base local de manuais usando ChromaDB e embeddings da OpenAI.
- Executa um fluxo LangGraph com etapas separadas e rastreáveis.
- Usa Pydantic para estruturar entradas, saídas, estado do grafo e diagnóstico.
- Gera uma resposta final em português com foco em manutenção segura.

## Arquitetura

A organização principal do projeto é:

```text
app/
  graph/
    cnc_graph.py              # Fluxo LangGraph principal do MVP
    state.py                  # Estado compartilhado do grafo
    troubleshooting_graph.py  # Fluxo mais simples e modular

  schemas/
    diagnosis.py              # Schema Pydantic da resposta estruturada do LLM

  services/
    diagnosis_service.py      # Regras auxiliares para diagnóstico
    schemas.py                # Schemas Pydantic de sensores, thresholds e resultado

  tools/
    get_sensor_data.py        # Tool de dados simulados de sensores
    check_sensor_thresholds.py # Tool de análise de thresholds
    search_machine_manual.py  # Tool RAG usando ChromaDB local
```

O arquivo `run_mvp.py` executa uma demonstração ponta a ponta.

## Fluxo LangGraph

O grafo principal executa os seguintes passos:

1. `load_sensor_data`
   Carrega dados simulados da CNC a partir de um perfil, por exemplo `normal`, `overheating`, `overload` ou `tool_wear`.

2. `check_thresholds`
   Analisa temperatura, torque, rotação e desgaste da ferramenta contra limites definidos.

3. `retrieve_manual_context`
   Monta uma query com o problema informado, dados de sensores e alertas detectados, depois busca contexto relevante no manual indexado no ChromaDB.

4. `generate_diagnosis`
   Usa um modelo de linguagem com saída estruturada para gerar diagnóstico técnico.

5. `format_response`
   Formata o resultado final para leitura do operador ou técnico.

## Exemplo de Entrada

```python
initial_state = {
    "machine_id": "CNC_001",
    "sensor_profile": "overheating",
    "user_issue": "A máquina apresentou alerta de temperatura alta no spindle e parece estar com torque elevado.",
}
```

## Exemplo de Saída

A resposta final inclui:

- resumo do problema;
- status operacional;
- prioridade;
- confiança do diagnóstico;
- indicação sobre abrir ticket de manutenção;
- alertas detectados nos sensores;
- causas prováveis;
- evidências usadas;
- ações recomendadas;
- notas de segurança;
- fontes consultadas no manual.

## Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as chaves necessárias:

```env
OPENAI_API_KEY=...
OPENAI_MODEL=...
```

O modelo configurado em `OPENAI_MODEL` é usado na etapa de geração do diagnóstico. A chave `OPENAI_API_KEY` também é usada para gerar embeddings na busca semântica dos manuais.

### Langfuse: Prompt Management e Tracing

Opcionalmente, instale o SDK do Langfuse:

```powershell
pip install langfuse
```

Depois adicione as variáveis abaixo ao `.env`:

```env
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_BASE_URL=https://cloud.langfuse.com

# Opcional. Se não informado, usa cnc-troubleshooting-system.
LANGFUSE_CNC_SYSTEM_PROMPT=cnc-troubleshooting-system

# Opcional. Se não informado, Langfuse usa o label production.
LANGFUSE_PROMPT_LABEL=production

# Opcional. Se true, falha quando o prompt não puder ser carregado.
LANGFUSE_PROMPT_REQUIRED=false
```

No Langfuse, crie um prompt de texto chamado `cnc-troubleshooting-system` com o conteúdo do system prompt. Quando as variáveis estiverem presentes, o MVP busca esse prompt no Langfuse e registra o trace da execução do LangGraph/LangChain. Se o Langfuse não estiver configurado, o projeto continua usando o prompt local em `app/services/langfuse_service.py`.

## Como Executar

Com o ambiente virtual ativado e as dependências instaladas:

```powershell
.\.venv\Scripts\python.exe run_mvp.py
```

Ou, se o Python do ambiente já estiver ativo:

```powershell
python run_mvp.py
```

## Observações

- Os dados de sensores são simulados e servem apenas para demonstrar o fluxo.
- A busca no manual depende da base ChromaDB local em `vector_store/chroma`.
- O diagnóstico gerado deve ser tratado como apoio à decisão, não como ordem automática de manutenção.
- Ações envolvendo partes elétricas, spindle, rolamentos, sensores internos ou componentes energizados devem ser executadas apenas por manutenção qualificada.

## Próximos Passos Possíveis

- Conectar sensores reais ou histórico de telemetria.
- Adicionar códigos de alarme reais da CNC.
- Criar uma API com FastAPI para expor o grafo.
- Adicionar interface web para operadores.
- Registrar execuções em banco de dados.
- Adicionar testes automatizados para tools e nodes do LangGraph.
- Melhorar o roteamento do grafo com decisões condicionais.
## Trilha Para Caso Real / Azure Foundry

O projeto tambem possui um scaffold separado para a arquitetura real de agentes. Veja `docs/real_case_architecture.md` e execute `python run_real_case.py` para testar a simulacao local.
