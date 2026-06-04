import json
import textwrap

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from src.config.config_loader import load_config
from src.config.settings import get_settings
from src.graph.state import AnalystState


class ReportAgent:
    def __init__(self, llm=None):
        config = load_config()
        settings = get_settings()

        llm_config = config["llm"]

        self.llm = llm or ChatOpenAI(
            model=llm_config["model"],
            temperature=llm_config["temperature"],
            api_key=settings.openai_api_key,
        )

    def run(self, state: AnalystState) -> AnalystState:
        log = "[Report Agent] Generating final report..."
        print(log)

        try:
            user_query: str = state["user_query"]
            schema_info: dict = state["schema_info"]
            analysis_results: dict = state["analysis_results"]
            charts: list = state.get("charts", [])
            agent_logs: list = state.get("agent_logs", [])
            errors: list = state.get("errors", [])

            eda = analysis_results.get("eda", {})
            llm_results = analysis_results.get("llm_results", {})

            top_corrs = eda.get("top_correlations", [])[:5]
            corr_str = "\n".join(
                [
                    f"- {item['col_a']} to {item['col_b']}: r={item['correlation']}"
                    for item in top_corrs
                ]
            )

            target_dist = eda.get("target_distribution", {})

            context = f"""
            Dataset shape: {schema_info["shape"]}
            User question: {user_query}
            Target variable: {schema_info.get("target_hint", "none identified")}
            Target distribution: {json.dumps(target_dist, default=str)[:300]}
            Top correlations:
            {corr_str}
            Analysis summary: {str(llm_results.get("summary", ""))[:400]}
            Key metrics: {json.dumps(llm_results.get("key_metrics", {}), default=str)[:400]}
            Number of charts generated: {len(charts)}
            """

            system_prompt = textwrap.dedent("""
                You are a senior data scientist writing a concise analysis report.

                Given dataset statistics, write a structured report with these sections:

                ## Executive Summary
                ## Key Findings
                ## Statistical Insights
                ## Recommendations

                Be specific with numbers. Be direct. Max 400 words.
            """)

            narrative_response = self.llm.invoke(
                [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=context),
                ]
            )

            report = f"""
# AI Data Analysis Report

**Query:** {user_query}  
**Dataset:** {schema_info["shape"]["rows"]} rows x {schema_info["shape"]["cols"]} columns  
**Agents Executed:** Schema -> Cleaning -> Query Planning -> Statistical Analysis -> Visualization -> Report

---

{narrative_response.content}

---

## Charts Generated

{chr(10).join(["- " + chart["title"] for chart in charts]) if charts else "- None"}

## Agent Execution Log

{chr(10).join(["- " + item for item in agent_logs[-10:]])}

## Errors Encountered

{chr(10).join(["- " + item for item in errors]) if errors else "- None"}
"""

            log2 = "[Report Agent] Report generated successfully."
            print(log2)

            return {
                **state,
                "final_report": report,
                "agent_logs": agent_logs + [log, log2],
            }

        except Exception as e:
            error_log = f"[Report Agent] Failed: {str(e)}"
            print(error_log)

            return {
                **state,
                "errors": state.get("errors", []) + [error_log],
                "agent_logs": state.get("agent_logs", []) + [log, error_log],
            }


report_agent_instance = ReportAgent()


def report_agent(state: AnalystState) -> AnalystState:
    return report_agent_instance.run(state)