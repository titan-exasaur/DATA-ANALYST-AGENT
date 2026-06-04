import pandas as pd

from src.agents.schema_agent import SchemaAgent
from src.agents.cleaning_agent import DataCleaningAgent
from src.agents.query_agent import QueryPlanningAgent
from src.agents.analysis_agent import AnalysisAgent
from src.agents.viz_agent import VizAgent
from src.agents.report_agent import ReportAgent
from src.graph.state import AnalystState


def main():
    df = pd.DataFrame(
        {
            "Survived": [0, 1, 1, 0, 1, 0],
            "Pclass": [3, 1, 3, 1, 2, 3],
            "Sex": ["male", "female", "female", "female", "male", "male"],
            "Age": [22, 38, 26, None, 35, 41],
            "Fare": [7.25, 71.28, 7.92, 53.1, 8.05, 12.5],
        }
    )

    state: AnalystState = {
        "user_query": "What factors affected passenger survival?",
        "raw_data": df,
        "source": "real_llm_test",
        "schema_info": None,
        "cleaned_data": None,
        "query_plan": None,
        "analysis_results": None,
        "charts": None,
        "errors": [],
        "agent_logs": [],
        "final_report": None,
    }

    state = SchemaAgent().run(state)
    state = DataCleaningAgent().run(state)
    state = QueryPlanningAgent().run(state)
    state = AnalysisAgent().run(state)
    state = VizAgent().run(state)
    state = ReportAgent().run(state)

    print("\n========== ERRORS ==========")
    print(state["errors"])

    print("\n========== FINAL REPORT ==========")
    print(state["final_report"])

    print("\n========== CHARTS GENERATED ==========")
    print(len(state["charts"] or []))


if __name__ == "__main__":
    main()