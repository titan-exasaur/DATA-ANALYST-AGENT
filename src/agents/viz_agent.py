import numpy as np
import pandas as pd

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.graph.state import AnalystState


class VizAgent:
    def run(self, state: AnalystState) -> AnalystState:
        log = "[Visualization Agent] Generating charts..."
        print(log)

        try:
            df: pd.DataFrame = state["cleaned_data"]
            schema_info: dict = state["schema_info"]
            analysis_results: dict = state["analysis_results"]

            charts = []

            num_cols = [
                col
                for col, meta in schema_info["columns"].items()
                if meta.get("role") == "numerical"
                and col in df.columns
                and meta.get("analytical_importance") in ["high", "medium"]
            ][:4]

            if num_cols:
                rows = (len(num_cols) + 1) // 2

                fig = make_subplots(
                    rows=rows,
                    cols=2,
                    subplot_titles=[f"Distribution: {col}" for col in num_cols],
                )

                for i, column_name in enumerate(num_cols):
                    row = i // 2 + 1
                    col_idx = i % 2 + 1

                    fig.add_trace(
                        go.Histogram(
                            x=df[column_name],
                            name=column_name,
                            nbinsx=30,
                            showlegend=False,
                        ),
                        row=row,
                        col=col_idx,
                    )

                fig.update_layout(
                    title_text="Numerical Feature Distributions",
                    height=300 * rows,
                    template="plotly_white",
                )

                charts.append({"title": "Numerical Distributions", "fig": fig})

            numeric_df = df.select_dtypes(include=[np.number])

            if numeric_df.shape[1] > 2:
                corr = numeric_df.corr().round(2)

                fig = go.Figure(
                    go.Heatmap(
                        z=corr.values,
                        x=corr.columns.tolist(),
                        y=corr.index.tolist(),
                        zmid=0,
                        text=corr.values.round(2),
                        texttemplate="%{text}",
                        colorbar_title="Correlation",
                    )
                )

                fig.update_layout(
                    title="Feature Correlation Matrix",
                    height=500,
                    template="plotly_white",
                )

                charts.append({"title": "Correlation Heatmap", "fig": fig})

            target = schema_info.get("target_hint")

            cat_cols = [
                col
                for col, meta in schema_info["columns"].items()
                if meta.get("role") == "categorical"
                and col in df.columns
                and col != target
                and meta.get("analytical_importance") == "high"
            ][:3]

            if target and target in df.columns and cat_cols:
                fig = make_subplots(
                    rows=1,
                    cols=len(cat_cols),
                    subplot_titles=[f"{target} by {col}" for col in cat_cols],
                )

                for i, column_name in enumerate(cat_cols):
                    grouped = df.groupby(column_name)[target].mean().reset_index()

                    fig.add_trace(
                        go.Bar(
                            x=grouped[column_name].astype(str),
                            y=grouped[target],
                            name=column_name,
                        ),
                        row=1,
                        col=i + 1,
                    )

                fig.update_layout(
                    title_text=f"{target} Rate by Categorical Features",
                    height=400,
                    template="plotly_white",
                    showlegend=False,
                )

                charts.append({"title": f"{target} Rate by Category", "fig": fig})

            value_counts_data = analysis_results.get("eda", {}).get("value_counts", {})

            if value_counts_data:
                top_cat = list(value_counts_data.keys())[0]
                counts = value_counts_data[top_cat]

                fig = go.Figure(
                    go.Bar(
                        x=list(counts.keys()),
                        y=list(counts.values()),
                        text=list(counts.values()),
                        textposition="outside",
                    )
                )

                fig.update_layout(
                    title=f"Value Counts: {top_cat}",
                    height=400,
                    template="plotly_white",
                    xaxis_title=top_cat,
                    yaxis_title="Count",
                )

                charts.append({"title": f"Value Counts: {top_cat}", "fig": fig})

            log2 = f"[Visualization Agent] Generated {len(charts)} charts."
            print(log2)

            return {
                **state,
                "charts": charts,
                "agent_logs": state.get("agent_logs", []) + [log, log2],
            }

        except Exception as e:
            error_log = f"[Visualization Agent] Failed: {str(e)}"
            print(error_log)

            return {
                **state,
                "errors": state.get("errors", []) + [error_log],
                "agent_logs": state.get("agent_logs", []) + [log, error_log],
            }


viz_agent = VizAgent()


def visualization_agent(state: AnalystState) -> AnalystState:
    return viz_agent.run(state)