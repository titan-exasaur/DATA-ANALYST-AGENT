from langgraph.graph import END

from src.graph.router import SupervisorRouter


def test_router_starts_with_schema(base_state):
    router = SupervisorRouter()

    assert router.router(base_state) == "schema_analysis"


def test_router_goes_to_cleaning(base_state, schema_info):
    router = SupervisorRouter()

    state = {
        **base_state,
        "schema_info": schema_info,
    }

    assert router.router(state) == "data_cleaning"


def test_router_goes_to_end_on_error(base_state):
    router = SupervisorRouter()

    state = {
        **base_state,
        "errors": ["Something failed"],
    }

    assert router.router(state) == END