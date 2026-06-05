import pandas as pd

from src.agents.viz_agent import VizAgent
from src.graph.state import AnalystState


def main():
    df = pd.DataFrame(
        {
            "Survived": [0, 1, 1, 0, 1, 0, 1, 0],
            "Pclass": [3, 1, 3, 1, 2, 3, 1, 2],
            "Sex": ["male", "female", "female", "female", "male", "male", "female", "male"],
            "Age": [22, 38, 26, 35, 35, 41, 19, 50],
            "Fare": [7.25, 71.28, 7.92, 53.1, 8.05, 12.5, 80.0, 30.0],
        }
    )

    schema_info = {
        "shape": {"rows": 8, "cols": 5},
        "columns": {
            "Survived": {
                "dtype": "int64",
                "null_pct": 0.0,
                "role": "target",
                "analytical_importance": "high",
            },
            "Pclass": {
                "dtype": "int64",
                "null_pct": 0.0,
                "role": "categorical",
                "analytical_importance": "high",
            },
            "Sex": {
                "dtype": "object",
                "null_pct": 0.0,
                "role": "categorical",
                "analytical_importance": "high",
            },
            "Age": {
                "dtype": "int64",
                "null_pct": 0.0,
                "role": "numerical",
                "analytical_importance": "high",
            },
            "Fare": {
                "dtype": "float64",
                "null_pct": 0.0,
                "role": "numerical",
                "analytical_importance": "medium",
            },
        },
        "high_null_cols": [],
        "target_hint": "Survived",
    }

    analysis_results = {
        "llm_results": {
            "summary": "Survival varies by sex and class.",
            "key_metrics": {},
            "data_for_viz": {},
        },
        "eda": {
            "value_counts": {
                "Sex": {
                    "male": 4,
                    "female": 4,
                },
                "Pclass": {
                    1: 3,
                    2: 2,
                    3: 3,
                },
            }
        },
    }

    state: AnalystState = {
        "user_query": "What factors affected passenger survival?",
        "raw_data": df,
        "source": "manual_test",
        "schema_info": schema_info,
        "cleaned_data": df,
        "query_plan": None,
        "analysis_results": analysis_results,
        "charts": None,
        "next_agent": None,
        "errors": [],
        "agent_logs": [],
        "final_report": None,
    }

    agent = VizAgent()
    result_state = agent.run(state)

    print("\n========== ERRORS ==========")
    print(result_state["errors"])

    print("\n========== AGENT LOGS ==========")
    for log in result_state["agent_logs"]:
        print(log)

    print("\n========== CHARTS GENERATED ==========")
    charts = result_state["charts"]

    print(f"Total charts: {len(charts)}")

    for index, chart in enumerate(charts, start=1):
        print(f"{index}. {chart['title']}")

    if charts:
        charts[0]["fig"].write_html("tests/results/sample_viz_chart.html")
        print("\nSaved first chart to: tests/results/sample_viz_chart.html")


if __name__ == "__main__":
    main()