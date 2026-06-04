import numpy as np
import pandas as pd

from src.graph.state import AnalystState


class AnalysisAgent:
    def run(self, state: AnalystState) -> AnalystState:
        log = "[Statistical Analysis Agent] Executing analysis plan..."
        print(log)

        try:
            df: pd.DataFrame = state["cleaned_data"]
            code: str = state["query_plan"]
            schema_info: dict = state["schema_info"]

            analysis_results = {}
            errors = list(state.get("errors", []))

            exec_namespace = {
                "df": df.copy(),
                "pd": pd,
                "np": np,
                "results": {},
            }

            try:
                exec(code, exec_namespace)
                analysis_results["llm_results"] = exec_namespace.get("results", {})
                print("LLM-generated code executed successfully")

            except Exception as e:
                err = f"Code execution error: {str(e)}"
                print(f"⚠️ {err}")
                errors.append(err)

                analysis_results["llm_results"] = {
                    "error": str(e),
                    "summary": "Code execution failed",
                    "key_metrics": {},
                    "data_for_viz": {},
                }

            numeric_df = df.select_dtypes(include=[np.number])

            cat_cols = [
                col
                for col, meta in schema_info["columns"].items()
                if meta.get("role") == "categorical" and col in df.columns
            ]

            eda = {}

            if not numeric_df.empty:
                eda["describe"] = numeric_df.describe().round(3).to_dict()

            if numeric_df.shape[1] > 1:
                corr_matrix = numeric_df.corr()
                corr_pairs = []

                for i in range(len(corr_matrix.columns)):
                    for j in range(i + 1, len(corr_matrix.columns)):
                        col_a = corr_matrix.columns[i]
                        col_b = corr_matrix.columns[j]
                        val = corr_matrix.iloc[i, j]

                        if not np.isnan(val):
                            corr_pairs.append(
                                {
                                    "col_a": col_a,
                                    "col_b": col_b,
                                    "correlation": round(float(val), 3),
                                }
                            )

                corr_pairs.sort(
                    key=lambda item: abs(item["correlation"]),
                    reverse=True,
                )

                eda["top_correlations"] = corr_pairs[:10]

            eda["value_counts"] = {}

            for col in cat_cols[:5]:
                eda["value_counts"][col] = (
                    df[col]
                    .value_counts()
                    .head(10)
                    .to_dict()
                )

            target = schema_info.get("target_hint")

            if target and target in df.columns:
                eda["target_distribution"] = (
                    df[target]
                    .value_counts(normalize=True)
                    .round(3)
                    .to_dict()
                )

            analysis_results["eda"] = eda

            log2 = (
                f"[Statistical Analysis Agent] Done. "
                f"EDA stats computed for {numeric_df.shape[1]} numeric cols, "
                f"{len(cat_cols)} categorical cols."
            )

            print(log2)

            return {
                **state,
                "analysis_results": analysis_results,
                "errors": errors,
                "agent_logs": state.get("agent_logs", []) + [log, log2],
            }

        except Exception as e:
            error_log = f"[Statistical Analysis Agent] Failed: {str(e)}"
            print(error_log)

            return {
                **state,
                "errors": state.get("errors", []) + [error_log],
                "agent_logs": state.get("agent_logs", []) + [log, error_log],
            }


analysis_agent = AnalysisAgent()


def statistical_analysis_agent(state: AnalystState) -> AnalystState:
    return analysis_agent.run(state)