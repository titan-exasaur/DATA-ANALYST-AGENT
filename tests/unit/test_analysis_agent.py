from src.agents.analysis_agent import AnalysisAgent


def test_analysis_agent_executes_query_plan(base_state, schema_info, sample_df):
    query_plan = """
results = {}
survival_rate = df["Survived"].mean()
results["summary"] = f"Overall survival rate is {survival_rate:.2f}"
results["key_metrics"] = {"overall_survival_rate": round(float(survival_rate), 3)}
results["data_for_viz"] = {}
"""

    state = {
        **base_state,
        "schema_info": schema_info,
        "cleaned_data": sample_df.fillna(0),
        "query_plan": query_plan,
    }

    agent = AnalysisAgent()
    result = agent.run(state)

    assert result["analysis_results"] is not None
    assert "llm_results" in result["analysis_results"]
    assert "eda" in result["analysis_results"]
    assert result["analysis_results"]["llm_results"]["key_metrics"]["overall_survival_rate"] == 0.6