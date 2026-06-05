from src.agents.cleaning_agent import DataCleaningAgent


def test_cleaning_agent_fills_nulls(base_state, schema_info):
    state = {
        **base_state,
        "schema_info": schema_info,
    }

    agent = DataCleaningAgent()
    result = agent.run(state)

    cleaned_df = result["cleaned_data"]

    assert cleaned_df is not None
    assert cleaned_df["Age"].isnull().sum() == 0
    assert cleaned_df["Fare"].isnull().sum() == 0
    assert len(result["agent_logs"]) > 0