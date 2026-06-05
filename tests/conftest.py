import json
import pandas as pd
import pytest


class MockResponse:
    def __init__(self, content: str):
        self.content = content


class MockSchemaLLM:
    def invoke(self, messages):
        return MockResponse(
            json.dumps(
                {
                    "Survived": {
                        "role": "target",
                        "description": "Whether passenger survived",
                        "analytical_importance": "high",
                    },
                    "Pclass": {
                        "role": "categorical",
                        "description": "Passenger class",
                        "analytical_importance": "high",
                    },
                    "Sex": {
                        "role": "categorical",
                        "description": "Passenger gender",
                        "analytical_importance": "high",
                    },
                    "Age": {
                        "role": "numerical",
                        "description": "Passenger age",
                        "analytical_importance": "high",
                    },
                    "Fare": {
                        "role": "numerical",
                        "description": "Ticket fare",
                        "analytical_importance": "medium",
                    },
                }
            )
        )


class MockQueryLLM:
    def invoke(self, messages):
        code = """
results = {}
survival_rate = df["Survived"].mean()
survival_by_sex = df.groupby("Sex")["Survived"].mean().to_dict()

results["summary"] = f"Overall survival rate is {survival_rate:.2f}"
results["key_metrics"] = {
    "overall_survival_rate": round(float(survival_rate), 3),
    "survival_by_sex": survival_by_sex,
}
results["data_for_viz"] = {
    "survival_by_sex": survival_by_sex,
}
"""
        return MockResponse(code)


class MockReportLLM:
    def invoke(self, messages):
        return MockResponse(
            """
## Executive Summary
The dataset shows survival patterns by passenger attributes.

## Key Findings
- Survival varies by sex and class.
- Fare and age can be used for further analysis.

## Statistical Insights
The generated analysis computes survival rates and EDA metrics.

## Recommendations
Investigate class, sex, age, and fare together.
"""
        )


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "Survived": [0, 1, 1, 0, 1],
            "Pclass": [3, 1, 3, 1, 2],
            "Sex": ["male", "female", "female", "female", "male"],
            "Age": [22, 38, None, 35, 1000],
            "Fare": [7.25, 71.28, 7.92, None, 9999],
        }
    )


@pytest.fixture
def schema_info():
    return {
        "shape": {"rows": 5, "cols": 5},
        "columns": {
            "Survived": {
                "dtype": "int64",
                "null_pct": 0.0,
                "role": "target",
                "analytical_importance": "high",
            },
            "Pclass": {
                "dtype": "int64",
                "null_pct": 0.0,
                "role": "categorical",
                "analytical_importance": "high",
            },
            "Sex": {
                "dtype": "object",
                "null_pct": 0.0,
                "role": "categorical",
                "analytical_importance": "high",
            },
            "Age": {
                "dtype": "float64",
                "null_pct": 20.0,
                "role": "numerical",
                "analytical_importance": "high",
            },
            "Fare": {
                "dtype": "float64",
                "null_pct": 20.0,
                "role": "numerical",
                "analytical_importance": "medium",
            },
        },
        "high_null_cols": [],
        "target_hint": "Survived",
    }


@pytest.fixture
def base_state(sample_df):
    return {
        "user_query": "What factors affected passenger survival?",
        "raw_data": sample_df,
        "source": "unit_test",
        "schema_info": None,
        "cleaned_data": None,
        "query_plan": None,
        "analysis_results": None,
        "charts": None,
        "errors": [],
        "agent_logs": [],
        "final_report": None,
    }