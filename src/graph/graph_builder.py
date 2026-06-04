from langgraph.graph import END, StateGraph

from src.graph.state import AnalystState
from src.graph.router import SupervisorRouter

from src.agents.schema_agent import schema_analysis_agent
from src.agents.cleaning_agent import data_cleaning_agent
from src.agents.query_agent import query_planning_agent
from src.agents.analysis_agent import statistical_analysis_agent
from src.agents.viz_agent import visualization_agent
from src.agents.report_agent import report_agent


def build_analyst_graph():
    """
    Assembles the full multi-agent LangGraph graph.
    """

    router = SupervisorRouter()

    graph = StateGraph(AnalystState)

    graph.add_node("schema_analysis", schema_analysis_agent)
    graph.add_node("data_cleaning", data_cleaning_agent)
    graph.add_node("query_planning", query_planning_agent)
    graph.add_node("statistical_analysis", statistical_analysis_agent)
    graph.add_node("visualization", visualization_agent)
    graph.add_node("report", report_agent)

    graph.add_node("supervisor", lambda state: state)

    graph.set_entry_point("supervisor")

    graph.add_conditional_edges(
        "supervisor",
        router.router,
        {
            "schema_analysis": "schema_analysis",
            "data_cleaning": "data_cleaning",
            "query_planning": "query_planning",
            "statistical_analysis": "statistical_analysis",
            "visualization": "visualization",
            "report": "report",
            END: END,
        },
    )

    for node in [
        "schema_analysis",
        "data_cleaning",
        "query_planning",
        "statistical_analysis",
        "visualization",
        "report",
    ]:
        graph.add_edge(node, "supervisor")

    return graph.compile()