from src.agents.schema_agent import SchemaAgent
from tests.conftest import MockSchemaLLM


def test_schema_agent_generates_schema_info(base_state):
    agent = SchemaAgent(llm=MockSchemaLLM())

    result = agent.run(base_state)

    assert result["schema_info"] is not None
    assert result["schema_info"]["shape"]["rows"] == 5
    assert result["schema_info"]["target_hint"] == "Survived"
    assert "Age" in result["schema_info"]["columns"]
    assert result["errors"] == []