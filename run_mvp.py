from app.graph.cnc_graph import build_cnc_graph


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
        }
    }

    result = graph.invoke(initial_state, config=config)

    print(result["final_response"])


if __name__ == "__main__":
    main()
