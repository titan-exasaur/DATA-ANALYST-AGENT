import pandas as pd

from src.agents.cleaning_agent import DataCleaningAgent
from src.graph.state import AnalystState


def main():
    df = pd.DataFrame(
        {
            "Age": [22, 38, None, 35, 1000],
            "Sex": ["male", "female", None, "female", "male"],
            "Cabin": [None, None, None, "C85", None],
            "Fare": [7.25, 71.28, 8.05, None, 9999],
            "Embarked": ["S", "C", "S", None, "Q"],
            "Date": ["2024-01-01", "2024-01-02", None, "2024-01-04", "bad-date"],
        }
    )

    schema_info = {
        "shape": {"rows": 5, "cols": 6},
        "columns": {
            "Age": {
                "dtype": "float64",
                "null_pct": 20.0,
                "role": "numerical",
            },
            "Sex": {
                "dtype": "object",
                "null_pct": 20.0,
                "role": "categorical",
            },
            "Cabin": {
                "dtype": "object",
                "null_pct": 80.0,
                "role": "categorical",
            },
            "Fare": {
                "dtype": "float64",
                "null_pct": 20.0,
                "role": "numerical",
            },
            "Embarked": {
                "dtype": "object",
                "null_pct": 20.0,
                "role": "categorical",
            },
            "Date": {
                "dtype": "object",
                "null_pct": 20.0,
                "role": "temporal",
            },
        },
        "high_null_cols": ["Cabin"],
        "target_hint": None,
    }

    state: AnalystState = {
        "user_query": "Analyze passenger survival patterns",
        "raw_data": df,
        "source": "manual_test",
        "schema_info": schema_info,
        "cleaned_data": None,
        "query_plan": None,
        "analysis_results": None,
        "charts": None,
        "next_agent": None,
        "errors": [],
        "agent_logs": [],
        "final_report": None,
    }

    agent = DataCleaningAgent()
    result_state = agent.run(state)

    print("\n========== ERRORS ==========")
    print(result_state["errors"])

    print("\n========== AGENT LOGS ==========")
    for log in result_state["agent_logs"]:
        print(log)

    print("\n========== CLEANED DATA ==========")
    print(result_state["cleaned_data"])

    print("\n========== CLEANED DTYPES ==========")
    print(result_state["cleaned_data"].dtypes)


if __name__ == "__main__":
    main()