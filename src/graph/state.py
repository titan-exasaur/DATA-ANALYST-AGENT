import pandas as pd
from typing import List, Optional, TypedDict

class AnalystState(TypedDict):
    """
    Shared state passed between all agents in the LangGraph graph.
    Every agent reads from and writes to this state.
    """
    # ── Input ──
    user_query: str                        # Natural language question from user
    raw_data: Optional[pd.DataFrame]       # Original uploaded dataframe
    source: Optional[str]               # Path to CSV/Excel (if file-based)

    # ── Intermediate State ──
    schema_info: Optional[dict]            # Output of Schema Analysis Agent
    cleaned_data: Optional[pd.DataFrame]  # Output of Data Cleaning Agent
    query_plan: Optional[str]             # Output of Query Planning Agent (code)
    analysis_results: Optional[dict]      # Output of Statistical Analysis Agent
    charts: Optional[list]                # Output of Visualization Agent (Plotly figs)

    # ── Control Flow ──
    next_agent: Optional[str]             # Supervisor routing decision
    errors: List[str]                     # Accumulated errors across agents
    agent_logs: List[str]                 # Step-by-step execution trace

    # ── Output -─
    final_report: Optional[str]           # Markdown report from Report Agent

    print("AnalystState TypedDict defined ")
