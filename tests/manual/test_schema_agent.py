import pandas as pd

from src.agents.schema_agent import SchemaAgent
from src.graph.state import AnalystState


def main():
    df = pd.DataFrame(
        {
            "PassengerId": [1, 2, 3, 4, 5],
            "Survived": [0, 1, 1, 0, 1],
            "Pclass": [3, 1, 3, 1, 2],
            "Name": [
                "Braund, Mr. Owen",
                "Cumings, Mrs. John",
                "Heikkinen, Miss. Laina",
                "Futrelle, Mrs. Jacques",
                "Allen, Mr. William",
            ],
            "Sex": ["male", "female", "female", "female", "male"],
            "Age": [22, 38, 26, None, 35],
            "Fare": [7.25, 71.28, 7.92, 53.1, 8.05],
        }
    )

    state: AnalystState = {
        "user_query": "Analyze survival patterns in the Titanic dataset",
        "raw_data": df,
        "source": "manual_test",
        "schema_info": None,
        "cleaned_data": None,
        "query_plan": None,
        "analysis_results": None,
        "charts": None,
        "next_agent": None,
        "errors": [],
        "agent_logs": [],
        "final_report": None,
    }

    agent = SchemaAgent()
    result_state = agent.run(state)

    print("\n========== ERRORS ==========")
    print(result_state["errors"])

    print("\n========== AGENT LOGS ==========")
    for log in result_state["agent_logs"]:
        print(log)

    print("\n========== SCHEMA INFO ==========")
    print(result_state["schema_info"])


if __name__ == "__main__":
    main()