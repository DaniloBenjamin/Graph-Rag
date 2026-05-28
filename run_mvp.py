from app.graph.cnc_graph import build_cnc_graph
from app.services.langfuse_service import (
    get_langfuse_callback_handler,
    shutdown_langfuse,
)


def main():
    graph = build_cnc_graph()

    initial_state = {
        "machine_id": "CNC_001",
        "sensor_profile": "overheating",
        "user_issue": "A máquina apresentou alerta de temperatura alta no spindle e parece estar com torque elevado.",
    }

    config = {
        "configurable": {
            "thread_id": "cnc-troubleshooting-demo-001"
        },
        "metadata": {
            "langfuse_session_id": "cnc-troubleshooting-demo-001",
            "langfuse_tags": ["cnc", "mvp", "troubleshooting"],
        },
    }

    langfuse_handler = get_langfuse_callback_handler()
    if langfuse_handler:
        config["callbacks"] = [langfuse_handler]

    try:
        result = graph.invoke(initial_state, config=config)
        print(result["final_response"])
    finally:
        shutdown_langfuse()


if __name__ == "__main__":
    main()
