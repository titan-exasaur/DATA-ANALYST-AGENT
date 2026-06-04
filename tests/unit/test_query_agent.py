import pandas as pd

from src.agents.query_agent import QueryPlanningAgent
from src.graph.state import AnalystState


def main():
    df = pd.DataFrame(
        {
            "Survived": [0, 1, 1, 0, 1],
            "Pclass": [3, 1, 3, 1, 2],
            "Sex": ["male", "female", "female", "female", "male"],
            "Age": [22, 38, 26, 35, 35],
            "Fare": [7.25, 71.28, 7.92, 53.1, 8.05],
        }
    )

    schema_info = {
        "shape": {"rows": 5, "cols": 5},
        "columns": {
            "Survived": {
                "dtype": "int64",
                "null_pct": 0.0,
                "role": "target",
                "description": "Whether the passenger survived",
            },
            "Pclass": {
                "dtype": "int64",
                "null_pct": 0.0,
                "role": "categorical",
                "description": "Passenger class",
            },
            "Sex": {
                "dtype": "object",
                "null_pct": 0.0,
                "role": "categorical",
                "description": "Passenger gender",
            },
            "Age": {
                "dtype": "int64",
                "null_pct": 0.0,
                "role": "numerical",
                "description": "Passenger age",
            },
            "Fare": {
                "dtype": "float64",
                "null_pct": 0.0,
                "role": "numerical",
                "description": "Ticket fare",
            },
        },
        "high_null_cols": [],
        "target_hint": "Survived",
    }

    state: AnalystState = {
        "user_query": "What factors affected passenger survival?",
        "raw_data": df,
        "source": "manual_test",
        "schema_info": schema_info,
        "cleaned_data": df,
        "query_plan": None,
        "analysis_results": None,
        "charts": None,
        "next_agent": None,
        "errors": [],
        "agent_logs": [],
        "final_report": None,
    }

    agent = QueryPlanningAgent()
    result_state = agent.run(state)

    print("\n========== ERRORS ==========")
    print(result_state["errors"])

    print("\n========== AGENT LOGS ==========")
    for log in result_state["agent_logs"]:
        print(log)

    print("\n========== GENERATED QUERY PLAN ==========")
    print(result_state["query_plan"])


if __name__ == "__main__":
    main()