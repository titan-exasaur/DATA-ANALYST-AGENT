import pandas as pd

from src.agents.analysis_agent import AnalysisAgent
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

    query_plan = """
results = {}

survival_rate = df["Survived"].mean()

survival_by_sex = df.groupby("Sex")["Survived"].mean().to_dict()
survival_by_class = df.groupby("Pclass")["Survived"].mean().to_dict()

results["summary"] = f"Overall survival rate is {survival_rate:.2f}"
results["key_metrics"] = {
    "overall_survival_rate": round(float(survival_rate), 3),
    "survival_by_sex": survival_by_sex,
    "survival_by_class": survival_by_class,
}
results["data_for_viz"] = {
    "survival_by_sex": survival_by_sex,
    "survival_by_class": survival_by_class,
}
"""

    schema_info = {
        "shape": {"rows": 5, "cols": 5},
        "columns": {
            "Survived": {
                "dtype": "int64",
                "null_pct": 0.0,
                "role": "target",
            },
            "Pclass": {
                "dtype": "int64",
                "null_pct": 0.0,
                "role": "categorical",
            },
            "Sex": {
                "dtype": "object",
                "null_pct": 0.0,
                "role": "categorical",
            },
            "Age": {
                "dtype": "int64",
                "null_pct": 0.0,
                "role": "numerical",
            },
            "Fare": {
                "dtype": "float64",
                "null_pct": 0.0,
                "role": "numerical",
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
        "query_plan": query_plan,
        "analysis_results": None,
        "charts": None,
        "next_agent": None,
        "errors": [],
        "agent_logs": [],
        "final_report": None,
    }

    agent = AnalysisAgent()
    result_state = agent.run(state)

    print("\n========== ERRORS ==========")
    print(result_state["errors"])

    print("\n========== AGENT LOGS ==========")
    for log in result_state["agent_logs"]:
        print(log)

    print("\n========== ANALYSIS RESULTS ==========")
    print(result_state["analysis_results"])


if __name__ == "__main__":
    main()