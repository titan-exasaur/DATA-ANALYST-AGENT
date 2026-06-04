import pandas as pd

from src.graph.state import AnalystState


class DataCleaningAgent:
    def run(self, state: AnalystState) -> AnalystState:
        log = "[Cleaning Agent] Starting data cleaning..."
        print(log)

        try:
            df: pd.DataFrame = state["raw_data"].copy()
            schema_info: dict = state["schema_info"]

            cleaning_steps = []

            for col, meta in schema_info["columns"].items():
                if col not in df.columns:
                    continue

                null_pct = meta.get("null_pct", 0)
                role = meta.get("role", "unknown")
                dtype = meta.get("dtype", "")

                if null_pct > 50:
                    df = df.drop(columns=[col])
                    cleaning_steps.append(
                        f"Dropped '{col}' — {null_pct}% nulls"
                    )
                    continue

                if null_pct > 0:
                    if role == "numerical" or dtype in [
                        "float64",
                        "int64",
                        "float32",
                        "int32",
                    ]:
                        fill_val = df[col].median()
                        df[col] = df[col].fillna(fill_val)
                        cleaning_steps.append(
                            f"Filled '{col}' nulls with median ({fill_val})"
                        )

                    elif role in ["categorical", "text"]:
                        mode_value = df[col].mode()
                        fill_val = mode_value.iloc[0] if not mode_value.empty else "Unknown"
                        df[col] = df[col].fillna(fill_val)
                        cleaning_steps.append(
                            f"Filled '{col}' nulls with mode ('{fill_val}')"
                        )

                if role == "temporal":
                    df[col] = pd.to_datetime(df[col], errors="coerce")
                    cleaning_steps.append(f"Cast '{col}' to datetime")

                if role == "numerical":
                    q1 = df[col].quantile(0.25)
                    q3 = df[col].quantile(0.75)
                    iqr = q3 - q1

                    lower = q1 - 3 * iqr
                    upper = q3 + 3 * iqr

                    outlier_count = ((df[col] < lower) | (df[col] > upper)).sum()

                    if outlier_count > 0:
                        df[col] = df[col].clip(lower, upper)
                        cleaning_steps.append(
                            f"Capped {outlier_count} outliers in '{col}'"
                        )

            log2 = f"[Cleaning Agent] Done. {len(cleaning_steps)} cleaning steps applied."
            print(log2)

            return {
                **state,
                "cleaned_data": df,
                "agent_logs": state.get("agent_logs", []) + [log, log2] + cleaning_steps,
            }

        except Exception as e:
            error_log = f"[Cleaning Agent] Failed: {str(e)}"
            print(error_log)

            return {
                **state,
                "errors": state.get("errors", []) + [error_log],
                "agent_logs": state.get("agent_logs", []) + [log, error_log],
            }


cleaning_agent = DataCleaningAgent()
def data_cleaning_agent(state: AnalystState) -> AnalystState:
    return cleaning_agent.run(state)