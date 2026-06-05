from src.agents.report_agent import ReportAgent
from tests.conftest import MockReportLLM


def test_report_agent_generates_final_report(base_state, schema_info, sample_df):
    analysis_results = {
        "llm_results": {
            "summary": "Overall survival rate is 0.60",
            "key_metrics": {"overall_survival_rate": 0.6},
            "data_for_viz": {},
        },
        "eda": {
            "top_correlations": [],
            "target_distribution": {1: 0.6, 0: 0.4},
            "value_counts": {},
        },
    }

    state = {
        **base_state,
        "schema_info": schema_info,
        "cleaned_data": sample_df.fillna(0),
        "analysis_results": analysis_results,
        "charts": [{"title": "Test Chart", "fig": None}],
        "agent_logs": ["Schema done", "Analysis done"],
    }

    agent = ReportAgent(llm=MockReportLLM())
    result = agent.run(state)

    assert result["final_report"] is not None
    assert "AI Data Analysis Report" in result["final_report"]
    assert "Executive Summary" in result["final_report"]
    assert result["errors"] == []