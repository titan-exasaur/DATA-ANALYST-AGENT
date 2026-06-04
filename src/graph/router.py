from langgraph.graph import END
from src.graph.state import AnalystState


class SupervisorRouter:
    def router(self, state: AnalystState) -> str:
        """
        LangGraph conditional edge router.
        """

        if state.get("errors"):
            return END

        if state.get("schema_info") is None:
            return "schema_analysis"

        if state.get("cleaned_data") is None:
            return "data_cleaning"

        if state.get("query_plan") is None:
            return "query_planning"

        if state.get("analysis_results") is None:
            return "statistical_analysis"

        if state.get("charts") is None:
            return "visualization"

        if state.get("final_report") is None:
            return "report"

        return END