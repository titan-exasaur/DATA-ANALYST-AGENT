import json
import textwrap

import pandas as pd
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from src.config.config_loader import load_config
from src.config.settings import get_settings
from src.graph.state import AnalystState


class SchemaAgent:
    def __init__(self, llm=None):
        config = load_config()

        llm_config = config["llm"]

        self.llm = llm
        self.llm_config = llm_config

        self.sample_values_count = config["schema_agent"]["sample_values_count"]
        self.high_null_threshold_pct = config["schema_agent"]["high_null_threshold_pct"]

    def _get_llm(self):
        if self.llm is None:
            settings = get_settings()

            self.llm = ChatOpenAI(
                model=self.llm_config["model"],
                temperature=self.llm_config["temperature"],
                api_key=settings.openai_api_key,
            )

        return self.llm

    def run(self, state: AnalystState) -> AnalystState:
        log = "[Schema Agent] Starting schema analysis..."
        print(log)

        try:
            df: pd.DataFrame = state["raw_data"]
            user_query: str = state["user_query"]

            schema_stats = {}

            for col in df.columns:
                schema_stats[col] = {
                    "dtype": str(df[col].dtype),
                    "null_pct": round(df[col].isnull().mean() * 100, 2),
                    "unique_count": int(df[col].nunique()),
                    "sample_values": df[col]
                    .dropna()
                    .head(self.sample_values_count)
                    .tolist(),
                }

            schema_json_str = json.dumps(schema_stats, indent=2, default=str)

            system_prompt = textwrap.dedent("""
                You are a data schema analyst. Given column statistics from a DataFrame,
                return a JSON object where each key is a column name and the value is:
                {
                    "role": one of [categorical, numerical, temporal, id, target, text],
                    "description": "brief one-line description of what this column likely represents",
                    "analytical_importance": one of [high, medium, low]
                }

                Return ONLY valid JSON. No markdown. No explanation.
            """)

            user_prompt = f"""
            User's question: {user_query}

            Column statistics:
            {schema_json_str}
            """

            response = self._get_llm().invoke(
                [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt),
                ]
            )

            llm_classifications = self._parse_json_response(response.content)

            schema_info = {
                "shape": {
                    "rows": df.shape[0],
                    "cols": df.shape[1],
                },
                "columns": {},
                "high_null_cols": [],
                "target_hint": None,
            }

            for col in df.columns:
                classification = llm_classifications.get(col, {})

                schema_info["columns"][col] = {
                    **schema_stats[col],
                    **classification,
                }

                if schema_stats[col]["null_pct"] > self.high_null_threshold_pct:
                    schema_info["high_null_cols"].append(col)

                if classification.get("role") == "target":
                    schema_info["target_hint"] = col

            log2 = (
                f" [Schema Agent] Done. "
                f"Shape: {df.shape}, "
                f"High-null cols: {schema_info['high_null_cols']}, "
                f"Target hint: {schema_info['target_hint']}"
            )

            print(log2)

            return {
                **state,
                "schema_info": schema_info,
                "agent_logs": state.get("agent_logs", []) + [log, log2],
            }

        except Exception as e:
            error_log = f"❌ [Schema Agent] Failed: {str(e)}"
            print(error_log)

            return {
                **state,
                "errors": state.get("errors", []) + [error_log],
                "agent_logs": state.get("agent_logs", []) + [log, error_log],
            }

    def _parse_json_response(self, content: str) -> dict:
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            start = content.find("{")
            end = content.rfind("}") + 1

            if start == -1 or end == 0:
                return {}

            return json.loads(content[start:end])




def schema_analysis_agent(state: AnalystState) -> AnalystState:
    return SchemaAgent().run(state)