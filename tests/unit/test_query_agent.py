from src.agents.query_agent import QueryPlanningAgent
from tests.conftest import MockQueryLLM


def test_query_agent_generates_code(base_state, schema_info, sample_df):
    state = {
        **base_state,
        "schema_info": schema_info,
        "cleaned_data": sample_df.fillna(0),
    }

    agent = QueryPlanningAgent(llm=MockQueryLLM())
    result = agent.run(state)

    assert result["query_plan"] is not None
    assert "results" in result["query_plan"]
    assert "survival_rate" in result["query_plan"]
    assert result["errors"] == []