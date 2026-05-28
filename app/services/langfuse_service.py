import os
from dataclasses import dataclass
from typing import Any


DEFAULT_CNC_SYSTEM_PROMPT = """
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


@dataclass
class PromptConfig:
    content: str
    langfuse_prompt: Any | None = None


def is_langfuse_configured() -> bool:
    return bool(
        os.getenv("LANGFUSE_PUBLIC_KEY")
        and os.getenv("LANGFUSE_SECRET_KEY")
        and os.getenv("LANGFUSE_BASE_URL")
    )


def get_cnc_system_prompt() -> PromptConfig:
    if not is_langfuse_configured():
        return PromptConfig(content=DEFAULT_CNC_SYSTEM_PROMPT)

    try:
        from langfuse import get_client

        langfuse = get_client()
        prompt_name = os.getenv(
            "LANGFUSE_CNC_SYSTEM_PROMPT",
            "cnc-troubleshooting-system",
        )
        prompt_label = os.getenv("LANGFUSE_PROMPT_LABEL")

        kwargs = {"label": prompt_label} if prompt_label else {}
        langfuse_prompt = langfuse.get_prompt(prompt_name, **kwargs)

        return PromptConfig(
            content=langfuse_prompt.compile(),
            langfuse_prompt=langfuse_prompt,
        )
    except Exception as exc:
        if os.getenv("LANGFUSE_PROMPT_REQUIRED", "").lower() == "true":
            raise

        print(
            "Langfuse prompt indisponível; usando prompt local. "
            f"Motivo: {exc}"
        )
        return PromptConfig(content=DEFAULT_CNC_SYSTEM_PROMPT)


def get_langfuse_callback_handler():
    if not is_langfuse_configured():
        return None

    try:
        from langfuse.langchain import CallbackHandler

        return CallbackHandler()
    except Exception as exc:
        print(
            "Langfuse tracing indisponível; executando sem callback. "
            f"Motivo: {exc}"
        )
        return None


def shutdown_langfuse() -> None:
    if not is_langfuse_configured():
        return

    try:
        from langfuse import get_client

        get_client().shutdown()
    except Exception:
        pass
