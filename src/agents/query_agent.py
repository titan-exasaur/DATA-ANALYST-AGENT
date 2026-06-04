import textwrap

import pandas as pd
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from src.config.config_loader import load_config
from src.config.settings import get_settings
from src.graph.state import AnalystState


class QueryPlanningAgent:
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
        log = "[Query Planning Agent] Generating analysis plan..."
        print(log)

        try:
            user_query: str = state["user_query"]
            schema_info: dict = state["schema_info"]
            df: pd.DataFrame = state["cleaned_data"]

            col_summary = []

            for col, meta in schema_info["columns"].items():
                if col in df.columns:
                    col_summary.append(
                        f"- {col}: {meta.get('role', '?')} | "
                        f"dtype={meta.get('dtype', '?')} | "
                        f"nulls={meta.get('null_pct', 0)}% | "
                        f"{meta.get('description', '')}"
                    )

            col_summary_str = "\n".join(col_summary)

            system_prompt = textwrap.dedent("""
                You are a Python data analyst. Given a user's question and a DataFrame schema,
                write executable Python/Pandas code to answer the question.

                Rules:
                1. The DataFrame is available as variable `df`
                2. Store ALL results in a dict called `results`
                3. results must contain: "summary" (str), "key_metrics" (dict), "data_for_viz" (dict)
                4. Do NOT use plt.show(), fig.show(), input(), open(), eval(), exec(), os, subprocess
                5. Handle edge cases gracefully
                6. Return ONLY Python code, no markdown fences, no explanation
            """)

            user_prompt = f"""
            User question: {user_query}

            DataFrame columns:
            {col_summary_str}

            DataFrame shape: {df.shape[0]} rows × {df.shape[1]} columns

            Write the Pandas analysis code:
            """

            response = self.llm.invoke(
                [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt),
                ]
            )

            code = self._clean_code_response(response.content)

            log2 = (
                f"[Query Planning Agent] Generated "
                f"{len(code.splitlines())} lines of analysis code."
            )
            print(log2)

            return {
                **state,
                "query_plan": code,
                "agent_logs": state.get("agent_logs", []) + [log, log2],
            }

        except Exception as e:
            error_log = f"[Query Planning Agent] Failed: {str(e)}"
            print(error_log)

            return {
                **state,
                "errors": state.get("errors", []) + [error_log],
                "agent_logs": state.get("agent_logs", []) + [log, error_log],
            }

    def _clean_code_response(self, content: str) -> str:
        code = content.strip()

        if code.startswith("```"):
            lines = code.splitlines()

            if lines[0].startswith("```"):
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            code = "\n".join(lines)

        return code.strip()


query_agent = QueryPlanningAgent()


def query_planning_agent(state: AnalystState) -> AnalystState:
    return query_agent.run(state)