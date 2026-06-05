from src.agents.viz_agent import VizAgent


def test_viz_agent_generates_charts(base_state, schema_info, sample_df):
    analysis_results = {
        "llm_results": {
            "summary": "Test summary",
            "key_metrics": {},
            "data_for_viz": {},
        },
        "eda": {
            "value_counts": {
                "Sex": {
                    "male": 2,
                    "female": 3,
                }
            }
        },
    }

    state = {
        **base_state,
        "schema_info": schema_info,
        "cleaned_data": sample_df.fillna(0),
        "analysis_results": analysis_results,
    }

    agent = VizAgent()
    result = agent.run(state)

    assert result["charts"] is not None
    assert len(result["charts"]) > 0
    assert "title" in result["charts"][0]
    assert "fig" in result["charts"][0]