import json

import pandas as pd

from src.agents.schema_agent import SchemaAgent
from src.agents.query_agent import QueryPlanningAgent
from src.agents.report_agent import ReportAgent
from src.agents.cleaning_agent import DataCleaningAgent
from src.agents.analysis_agent import AnalysisAgent
from src.agents.viz_agent import VizAgent
from src.graph.state import AnalystState


class MockResponse:
    def __init__(self, content: str):
        self.content = content


class MockSchemaLLM:
    def invoke(self, messages):
        content = json.dumps(
            {
                "Survived": {
                    "role": "target",
                    "description": "Whether the passenger survived",
                    "analytical_importance": "high",
                },
                "Pclass": {
                    "role": "categorical",
                    "description": "Passenger class",
                    "analytical_importance": "high",
                },
                "Sex": {
                    "role": "categorical",
                    "description": "Passenger gender",
                    "analytical_importance": "high",
                },
                "Age": {
                    "role": "numerical",
                    "description": "Passenger age",
                    "analytical_importance": "high",
                },
                "Fare": {
                    "role": "numerical",
                    "description": "Ticket fare",
                    "analytical_importance": "medium",
                },
            }
        )

        return MockResponse(content)


class MockQueryLLM:
    def invoke(self, messages):
        code = """
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
        return MockResponse(code)


class MockReportLLM:
    def invoke(self, messages):
        report = """
## Executive Summary

The dataset shows that survival varies strongly by passenger sex and class.

## Key Findings

- Overall survival rate is computed from the uploaded dataset.
- Female passengers show higher survival than male passengers.
- Passenger class appears to influence survival outcomes.

## Statistical Insights

The analysis compares survival rates across categorical groups and computes basic EDA statistics.

## Recommendations

Investigate survival patterns further using sex, class, fare, and age together.
"""
        return MockResponse(report)


def main():
    df = pd.DataFrame(
        {
            "Survived": [0, 1, 1, 0, 1, 0, 1, 0],
            "Pclass": [3, 1, 3, 1, 2, 3, 1, 2],
            "Sex": ["male", "female", "female", "female", "male", "male", "female", "male"],
            "Age": [22, 38, 26, None, 35, 41, 19, 50],
            "Fare": [7.25, 71.28, 7.92, 53.1, 8.05, 12.5, 80.0, 30.0],
        }
    )

    state: AnalystState = {
        "user_query": "What factors affected passenger survival?",
        "raw_data": df,
        "source": "manual_graph_test",
        "schema_info": None,
        "cleaned_data": None,
        "query_plan": None,
        "analysis_results": None,
        "charts": None,
        "errors": [],
        "agent_logs": [],
        "final_report": None,
    }

    schema_agent = SchemaAgent(llm=MockSchemaLLM())
    cleaning_agent = DataCleaningAgent()
    query_agent = QueryPlanningAgent(llm=MockQueryLLM())
    analysis_agent = AnalysisAgent()
    viz_agent = VizAgent()
    report_agent = ReportAgent(llm=MockReportLLM())

    state = schema_agent.run(state)
    state = cleaning_agent.run(state)
    state = query_agent.run(state)
    state = analysis_agent.run(state)
    state = viz_agent.run(state)
    state = report_agent.run(state)

    print("\n========== ERRORS ==========")
    print(state["errors"])

    print("\n========== AGENT LOGS ==========")
    for log in state["agent_logs"]:
        print(log)

    print("\n========== FINAL REPORT ==========")
    print(state["final_report"])

    print("\n========== CHART COUNT ==========")
    print(len(state["charts"] or []))


if __name__ == "__main__":
    main()