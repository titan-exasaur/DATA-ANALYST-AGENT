import pandas as pd
import plotly.graph_objects as go

from src.agents.report_agent import ReportAgent
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
            "summary": "Overall survival rate is 0.60. Female passengers had higher survival.",
            "key_metrics": {
                "overall_survival_rate": 0.6,
                "female_survival_rate": 1.0,
                "male_survival_rate": 0.5,
            },
            "data_for_viz": {},
        },
        "eda": {
            "top_correlations": [
                {
                    "col_a": "Fare",
                    "col_b": "Survived",
                    "correlation": 0.42,
                },
                {
                    "col_a": "Pclass",
                    "col_b": "Survived",
                    "correlation": -0.35,
                },
            ],
            "target_distribution": {
                1: 0.6,
                0: 0.4,
            },
            "value_counts": {
                "Sex": {
                    "female": 3,
                    "male": 2,
                }
            },
        },
    }

    charts = [
        {
            "title": "Survival by Sex",
            "fig": go.Figure(
                data=[
                    go.Bar(
                        x=["female", "male"],
                        y=[1.0, 0.5],
                    )
                ]
            ),
        }
    ]

    state: AnalystState = {
        "user_query": "What factors affected passenger survival?",
        "raw_data": df,
        "source": "manual_test",
        "schema_info": schema_info,
        "cleaned_data": df,
        "query_plan": None,
        "analysis_results": analysis_results,
        "charts": charts,
        "next_agent": None,
        "errors": [],
        "agent_logs": [
            "[Schema Agent] Done.",
            "[Cleaning Agent] Done.",
            "[Query Planning Agent] Done.",
            "[Statistical Analysis Agent] Done.",
            "[Visualization Agent] Done.",
        ],
        "final_report": None,
    }

    agent = ReportAgent()
    result_state = agent.run(state)

    print("\n========== ERRORS ==========")
    print(result_state["errors"])

    print("\n========== AGENT LOGS ==========")
    for log in result_state["agent_logs"]:
        print(log)

    print("\n========== FINAL REPORT ==========")
    print(result_state["final_report"])


if __name__ == "__main__":
    main()