from src.agents.schema_agent import SchemaAgent
from src.agents.cleaning_agent import DataCleaningAgent
from src.agents.query_agent import QueryPlanningAgent
from src.agents.analysis_agent import AnalysisAgent
from src.agents.viz_agent import VizAgent
from src.agents.report_agent import ReportAgent

from tests.conftest import MockSchemaLLM, MockQueryLLM, MockReportLLM


def test_full_agent_pipeline_with_mock_llms(base_state):
    state = base_state

    state = SchemaAgent(llm=MockSchemaLLM()).run(state)
    state = DataCleaningAgent().run(state)
    state = QueryPlanningAgent(llm=MockQueryLLM()).run(state)
    state = AnalysisAgent().run(state)
    state = VizAgent().run(state)
    state = ReportAgent(llm=MockReportLLM()).run(state)

    assert state["schema_info"] is not None
    assert state["cleaned_data"] is not None
    assert state["query_plan"] is not None
    assert state["analysis_results"] is not None
    assert state["charts"] is not None
    assert state["final_report"] is not None
    assert state["errors"] == []