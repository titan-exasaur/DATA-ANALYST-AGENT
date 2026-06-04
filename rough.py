#!/usr/bin/env python3
"""
AI Data Analyst Agent — Project Template Generator
Run: python generate_project.py
Creates the full project structure in ./ai-data-analyst/
"""

import os

ROOT = "ai-data-analyst"
files = {}

files[".env.example"] = """\
OPENAI_API_KEY=sk-...
AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com/
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_STORAGE_CONNECTION_STRING=
AZURE_STORAGE_CONTAINER_NAME=analyst-uploads
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=ai_analyst
APP_ENV=development
APP_PORT=8000
LOG_LEVEL=INFO
MAX_UPLOAD_SIZE_MB=50
ALLOWED_EXTENSIONS=csv,xlsx,xls
"""

files[".gitignore"] = """\
__pycache__/
*.py[cod]
.venv/
venv/
.env
.env.*
!.env.example
data/uploads/
data/outputs/
*.csv
*.xlsx
.ipynb_checkpoints/
.vscode/
.idea/
logs/
*.log
.coverage
htmlcov/
.pytest_cache/
dist/
build/
*.egg-info/
.DS_Store
"""

files["requirements.txt"] = """\
fastapi==0.115.0
uvicorn[standard]==0.30.6
python-multipart==0.0.9
jinja2==3.1.4
aiofiles==23.2.1
langgraph==0.2.28
langchain==0.3.1
langchain-openai==0.2.1
langchain-core==0.3.6
openai==1.51.0
pandas==2.2.3
numpy==1.26.4
plotly==5.24.1
openpyxl==3.1.5
azure-storage-blob==12.22.0
azure-identity==1.18.0
motor==3.5.1
pymongo==4.9.1
pydantic==2.9.2
pydantic-settings==2.5.2
python-dotenv==1.0.1
structlog==24.4.0
"""

files["requirements-dev.txt"] = """\
-r requirements.txt
pytest==8.3.3
pytest-asyncio==0.24.0
pytest-cov==5.0.0
httpx==0.27.2
pytest-mock==3.14.0
ruff==0.6.9
black==24.8.0
mypy==1.11.2
pre-commit==3.8.0
"""

files["pyproject.toml"] = """\
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.backends.legacy:build"

[project]
name = "ai-data-analyst"
version = "0.1.0"
description = "Multi-agent AI Data Analyst with LangGraph + Azure OpenAI"
readme = "README.md"
requires-python = ">=3.11"

[tool.ruff]
line-length = 100
target-version = "py311"
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.black]
line-length = 100
target-version = ["py311"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
addopts = "--cov=src --cov-report=term-missing --cov-fail-under=70"

[tool.mypy]
python_version = "3.11"
strict = false
ignore_missing_imports = true
"""

files["Dockerfile"] = """\
FROM python:3.11-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --upgrade pip && pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

FROM python:3.11-slim AS runtime
WORKDIR /app
RUN groupadd -r appuser && useradd -r -g appuser appuser
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels
COPY src/ ./src/
COPY pyproject.toml .
RUN chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \\
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
"""

files["docker-compose.yml"] = """\
version: "3.9"
services:
  app:
    build: { context: ., dockerfile: Dockerfile, target: runtime }
    container_name: ai_analyst_app
    ports: ["8000:8000"]
    env_file: [.env]
    environment: [MONGO_URI=mongodb://mongo:27017]
    depends_on:
      mongo: { condition: service_healthy }
    restart: unless-stopped
    networks: [analyst_net]

  mongo:
    image: mongo:7.0
    container_name: ai_analyst_mongo
    ports: ["27017:27017"]
    volumes: [mongo_data:/data/db]
    healthcheck:
      test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks: [analyst_net]

volumes:
  mongo_data:

networks:
  analyst_net:
    driver: bridge
"""

files["src/__init__.py"] = ""
files["src/config/__init__.py"] = ""
files["src/config/settings.py"] = """\
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from functools import lru_cache

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_env: str = Field(default="development")
    app_port: int = Field(default=8000)
    log_level: str = Field(default="INFO")
    max_upload_size_mb: int = Field(default=50)
    allowed_extensions: str = Field(default="csv,xlsx,xls")
    openai_api_key: str = Field(default="")
    azure_openai_endpoint: str = Field(default="")
    azure_openai_api_key: str = Field(default="")
    azure_openai_deployment: str = Field(default="gpt-4o")
    azure_storage_connection_string: str = Field(default="")
    azure_storage_container_name: str = Field(default="analyst-uploads")
    mongo_uri: str = Field(default="mongodb://localhost:27017")
    mongo_db_name: str = Field(default="ai_analyst")

    @property
    def allowed_ext_list(self) -> list[str]:
        return [e.strip() for e in self.allowed_extensions.split(",")]

@lru_cache
def get_settings() -> Settings:
    return Settings()
"""

files["src/graph/__init__.py"] = ""
files["src/graph/state.py"] = """\
from typing import TypedDict, Optional, List
import pandas as pd

class AnalystState(TypedDict):
    user_query: str
    raw_data: Optional[pd.DataFrame]
    file_id: Optional[str]
    schema_info: Optional[dict]
    cleaned_data: Optional[pd.DataFrame]
    query_plan: Optional[str]
    analysis_results: Optional[dict]
    charts: Optional[list]
    errors: List[str]
    agent_logs: List[str]
    final_report: Optional[str]
    session_id: Optional[str]
"""

files["src/graph/router.py"] = """\
from langgraph.graph import END
from src.graph.state import AnalystState

def supervisor_router(state: AnalystState) -> str:
    if state.get("schema_info") is None:      return "schema_analysis"
    if state.get("cleaned_data") is None:     return "data_cleaning"
    if state.get("query_plan") is None:       return "query_planning"
    if state.get("analysis_results") is None: return "statistical_analysis"
    if state.get("charts") is None:           return "visualization"
    if state.get("final_report") is None:     return "report"
    return END
"""

files["src/graph/graph_builder.py"] = """\
from langgraph.graph import StateGraph, END
from src.graph.state import AnalystState
from src.graph.router import supervisor_router
from src.agents.schema_agent import SchemaAnalysisAgent
from src.agents.cleaning_agent import DataCleaningAgent
from src.agents.query_agent import QueryPlanningAgent
from src.agents.analysis_agent import StatisticalAnalysisAgent
from src.agents.viz_agent import VisualizationAgent
from src.agents.report_agent import ReportAgent

def build_graph(llm) -> StateGraph:
    graph = StateGraph(AnalystState)
    graph.add_node("supervisor",           lambda s: s)
    graph.add_node("schema_analysis",      SchemaAnalysisAgent(llm).run)
    graph.add_node("data_cleaning",        DataCleaningAgent().run)
    graph.add_node("query_planning",       QueryPlanningAgent(llm).run)
    graph.add_node("statistical_analysis", StatisticalAnalysisAgent().run)
    graph.add_node("visualization",        VisualizationAgent().run)
    graph.add_node("report",               ReportAgent(llm).run)
    graph.set_entry_point("supervisor")
    graph.add_conditional_edges("supervisor", supervisor_router, {
        "schema_analysis": "schema_analysis", "data_cleaning": "data_cleaning",
        "query_planning": "query_planning", "statistical_analysis": "statistical_analysis",
        "visualization": "visualization", "report": "report", END: END,
    })
    for node in ["schema_analysis","data_cleaning","query_planning",
                 "statistical_analysis","visualization","report"]:
        graph.add_edge(node, "supervisor")
    return graph.compile()
"""

files["src/agents/__init__.py"] = ""
files["src/agents/base_agent.py"] = """\
import structlog
from abc import ABC, abstractmethod
from src.graph.state import AnalystState

logger = structlog.get_logger(__name__)

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def run(self, state: AnalystState) -> AnalystState: ...

    def log(self, state: AnalystState, message: str) -> AnalystState:
        logger.info(message, agent=self.name)
        return {**state, "agent_logs": state.get("agent_logs", []) + [f"[{self.name}] {message}"]}

    def error(self, state: AnalystState, message: str) -> AnalystState:
        logger.error(message, agent=self.name)
        return {**state, "errors": state.get("errors", []) + [f"[{self.name}] {message}"]}
"""

files["src/agents/schema_agent.py"] = """\
import json
from src.agents.base_agent import BaseAgent
from src.graph.state import AnalystState
from langchain_core.messages import SystemMessage, HumanMessage

class SchemaAnalysisAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__("SchemaAnalysisAgent")
        self.llm = llm

    def run(self, state: AnalystState) -> AnalystState:
        state = self.log(state, "Starting schema analysis")
        df = state["raw_data"]
        stats = {col: {"dtype": str(df[col].dtype), "null_pct": round(df[col].isnull().mean()*100,2),
                        "unique_count": int(df[col].nunique()), "sample_values": df[col].dropna().head(3).tolist()}
                 for col in df.columns}
        response = self.llm.invoke([
            SystemMessage(content="You are a data schema analyst. Return ONLY valid JSON where each key is a column name and value has: role (categorical|numerical|temporal|id|target|text), description (str), analytical_importance (high|medium|low)."),
            HumanMessage(content=f"User query: {state['user_query']}\\n\\nColumn stats:\\n{json.dumps(stats, indent=2, default=str)}")
        ])
        try:
            raw = response.content.strip()
            if raw.startswith("```"): raw = "\\n".join(raw.split("\\n")[1:-1])
            llm_meta = json.loads(raw)
        except json.JSONDecodeError:
            llm_meta = {}
        schema_info = {
            "shape": {"rows": df.shape[0], "cols": df.shape[1]},
            "columns": {col: {**stats[col], **(llm_meta.get(col, {}))} for col in df.columns},
            "high_null_cols": [c for c, s in stats.items() if s["null_pct"] > 20],
            "target_hint": next((c for c, m in llm_meta.items() if m.get("role") == "target"), None),
        }
        state = self.log(state, f"Schema done. Target: {schema_info['target_hint']}")
        return {**state, "schema_info": schema_info}
"""

files["src/agents/cleaning_agent.py"] = """\
import numpy as np
import pandas as pd
from src.agents.base_agent import BaseAgent
from src.graph.state import AnalystState

class DataCleaningAgent(BaseAgent):
    def __init__(self):
        super().__init__("DataCleaningAgent")

    def run(self, state: AnalystState) -> AnalystState:
        state = self.log(state, "Starting data cleaning")
        df = state["raw_data"].copy()
        schema = state["schema_info"]
        steps = []
        for col, meta in schema["columns"].items():
            null_pct, role, dtype = meta["null_pct"], meta.get("role","unknown"), meta["dtype"]
            if null_pct > 50:
                df.drop(columns=[col], inplace=True, errors="ignore")
                steps.append(f"Dropped '{col}' — {null_pct}% nulls"); continue
            if col not in df.columns: continue
            if null_pct > 0:
                if role == "numerical" or dtype in ("float64","int64","float32","int32"):
                    fill = df[col].median(); df[col].fillna(fill, inplace=True)
                    steps.append(f"Filled '{col}' with median={fill:.2f}")
                elif role in ("categorical","text"):
                    fill = df[col].mode()[0] if not df[col].mode().empty else "Unknown"
                    df[col].fillna(fill, inplace=True); steps.append(f"Filled '{col}' with mode='{fill}'")
            if role == "temporal" and "datetime" not in dtype:
                try: df[col] = pd.to_datetime(df[col], errors="coerce"); steps.append(f"Cast '{col}' to datetime")
                except: pass
            if role == "numerical" and col in df.columns:
                Q1,Q3 = df[col].quantile(0.25), df[col].quantile(0.75); IQR=Q3-Q1
                lo,hi = Q1-3*IQR, Q3+3*IQR; n = int(((df[col]<lo)|(df[col]>hi)).sum())
                if n: df[col]=df[col].clip(lo,hi); steps.append(f"Capped {n} outliers in '{col}'")
        state = self.log(state, f"Cleaning done — {len(steps)} steps")
        return {**state, "cleaned_data": df}
"""

files["src/agents/query_agent.py"] = """\
import textwrap
from src.agents.base_agent import BaseAgent
from src.graph.state import AnalystState
from langchain_core.messages import SystemMessage, HumanMessage

class QueryPlanningAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__("QueryPlanningAgent")
        self.llm = llm

    def run(self, state: AnalystState) -> AnalystState:
        state = self.log(state, "Generating query plan")
        df, schema = state["cleaned_data"], state["schema_info"]
        col_lines = "\\n".join(f"  - {c}: {m.get('role','?')} | {m['dtype']} | {m.get('description','')}"
                               for c, m in schema["columns"].items() if c in df.columns)
        system = textwrap.dedent("""
            You are a Python data analyst. Write executable Pandas code to answer the user's question.
            Rules: 1) DataFrame is `df`. 2) Store all results in `results` dict with keys: summary (str), key_metrics (dict), data_for_viz (dict). 3) No plt.show() or fig.show(). 4) Return ONLY raw Python, no markdown fences.
        """)
        response = self.llm.invoke([
            SystemMessage(content=system),
            HumanMessage(content=f"Question: {state['user_query']}\\n\\nColumns:\\n{col_lines}\\n\\nShape: {df.shape[0]} rows × {df.shape[1]} cols")
        ])
        code = response.content.strip()
        if code.startswith("```"):
            lines = code.split("\\n"); code = "\\n".join(lines[1:-1] if lines[-1].strip()=="```" else lines[1:])
        state = self.log(state, f"Query plan generated — {len(code.splitlines())} lines")
        return {**state, "query_plan": code}
"""

files["src/agents/analysis_agent.py"] = """\
import numpy as np
import pandas as pd
from src.agents.base_agent import BaseAgent
from src.graph.state import AnalystState

class StatisticalAnalysisAgent(BaseAgent):
    def __init__(self):
        super().__init__("StatisticalAnalysisAgent")

    def run(self, state: AnalystState) -> AnalystState:
        state = self.log(state, "Running statistical analysis")
        df, code, schema = state["cleaned_data"], state["query_plan"], state["schema_info"]
        errors, results = list(state.get("errors", [])), {}
        ns = {"df": df.copy(), "pd": pd, "np": np, "results": {}}
        try:
            exec(code, ns); results["llm_results"] = ns.get("results", {})
        except Exception as exc:
            errors.append(f"Code exec error: {exc}"); results["llm_results"] = {"error": str(exc), "summary": "Execution failed"}
        numeric_df = df.select_dtypes(include=[np.number])
        cat_cols = [c for c,m in schema["columns"].items() if m.get("role")=="categorical" and c in df.columns]
        eda = {}
        if not numeric_df.empty: eda["describe"] = numeric_df.describe().round(3).to_dict()
        if numeric_df.shape[1] > 1:
            corr = numeric_df.corr()
            pairs = [{"col_a": corr.columns[i], "col_b": corr.columns[j], "correlation": round(corr.iloc[i,j],3)}
                     for i in range(len(corr.columns)) for j in range(i+1,len(corr.columns)) if not np.isnan(corr.iloc[i,j])]
            pairs.sort(key=lambda x: abs(x["correlation"]), reverse=True); eda["top_correlations"] = pairs[:10]
        eda["value_counts"] = {col: df[col].value_counts().head(10).to_dict() for col in cat_cols[:5]}
        target = schema.get("target_hint")
        if target and target in df.columns:
            eda["target_distribution"] = df[target].value_counts(normalize=True).round(3).to_dict()
        results["eda"] = eda
        state = self.log(state, "Statistical analysis complete")
        return {**state, "analysis_results": results, "errors": errors}
"""

files["src/agents/viz_agent.py"] = """\
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from src.agents.base_agent import BaseAgent
from src.graph.state import AnalystState

class VisualizationAgent(BaseAgent):
    def __init__(self):
        super().__init__("VisualizationAgent")

    def run(self, state: AnalystState) -> AnalystState:
        state = self.log(state, "Generating visualizations")
        df, schema, eda = state["cleaned_data"], state["schema_info"], state["analysis_results"].get("eda",{})
        charts = []
        num_cols = [c for c,m in schema["columns"].items() if m.get("role")=="numerical" and c in df.columns and m.get("analytical_importance") in ("high","medium")][:4]
        if num_cols:
            rows = (len(num_cols)+1)//2
            fig = make_subplots(rows=rows, cols=2, subplot_titles=[f"Distribution: {c}" for c in num_cols])
            for i,col in enumerate(num_cols):
                fig.add_trace(go.Histogram(x=df[col],name=col,nbinsx=30,marker_color="#636EFA",showlegend=False), row=i//2+1, col=i%2+1)
            fig.update_layout(title_text="Numerical Distributions", height=300*rows, template="plotly_white")
            charts.append({"title": "Numerical Distributions", "fig_json": fig.to_json()})
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.shape[1] > 2:
            corr = numeric_df.corr().round(2)
            fig = go.Figure(go.Heatmap(z=corr.values,x=corr.columns.tolist(),y=corr.index.tolist(),colorscale="RdBu_r",zmid=0,text=corr.values.round(2),texttemplate="%{text}"))
            fig.update_layout(title="Correlation Matrix", height=500, template="plotly_white")
            charts.append({"title": "Correlation Heatmap", "fig_json": fig.to_json()})
        target = schema.get("target_hint")
        cat_cols = [c for c,m in schema["columns"].items() if m.get("role")=="categorical" and c in df.columns and c!=target and m.get("analytical_importance")=="high"][:3]
        if target and target in df.columns and cat_cols:
            fig = make_subplots(rows=1,cols=len(cat_cols),subplot_titles=[f"{target} by {c}" for c in cat_cols])
            for i,col in enumerate(cat_cols):
                grp = df.groupby(col)[target].mean().reset_index()
                fig.add_trace(go.Bar(x=grp[col].astype(str),y=grp[target],name=col,showlegend=False),row=1,col=i+1)
            fig.update_layout(title_text=f"{target} Rate by Category",height=400,template="plotly_white")
            charts.append({"title": f"{target} Rate by Category", "fig_json": fig.to_json()})
        state = self.log(state, f"Generated {len(charts)} charts")
        return {**state, "charts": charts}
"""

files["src/agents/report_agent.py"] = """\
import json, textwrap
from src.agents.base_agent import BaseAgent
from src.graph.state import AnalystState
from langchain_core.messages import SystemMessage, HumanMessage

class ReportAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__("ReportAgent")
        self.llm = llm

    def run(self, state: AnalystState) -> AnalystState:
        state = self.log(state, "Generating final report")
        schema, results = state["schema_info"], state["analysis_results"]
        eda, llm_r = results.get("eda",{}), results.get("llm_results",{})
        corr_str = "\\n".join(f"  - {c['col_a']} ↔ {c['col_b']}: r={c['correlation']}" for c in eda.get("top_correlations",[])[:5])
        context = (f"Dataset shape: {schema['shape']}\\nUser question: {state['user_query']}\\nTarget: {schema.get('target_hint')}\\n"
                   f"Target distribution: {json.dumps(eda.get('target_distribution',{}),default=str)[:300]}\\nTop correlations:\\n{corr_str}\\n"
                   f"Analysis summary: {str(llm_r.get('summary',''))[:400]}\\nKey metrics: {json.dumps(llm_r.get('key_metrics',{}),default=str)[:400]}")
        narrative = self.llm.invoke([
            SystemMessage(content=textwrap.dedent("""You are a senior data scientist. Write a concise report with sections: ## Executive Summary, ## Key Findings, ## Statistical Insights, ## Recommendations. Be specific with numbers. Max 400 words.""")),
            HumanMessage(content=context)
        ])
        report = (f"# AI Data Analysis Report\\n\\n**Query:** {state['user_query']}  \\n"
                  f"**Shape:** {schema['shape']['rows']} rows × {schema['shape']['cols']} cols  \\n\\n---\\n\\n"
                  f"{narrative.content}\\n\\n---\\n\\n## Agent Log\\n" +
                  "\\n".join(f"- {l}" for l in state.get("agent_logs",[])[-10:]))
        state = self.log(state, "Report complete")
        return {**state, "final_report": report}
"""

files["src/db/__init__.py"] = ""
files["src/db/repositories/__init__.py"] = ""
files["src/db/client.py"] = """\
import motor.motor_asyncio
from src.config.settings import get_settings
_client = None

def get_client():
    global _client
    if _client is None:
        _client = motor.motor_asyncio.AsyncIOMotorClient(get_settings().mongo_uri)
    return _client

def get_db():
    return get_client()[get_settings().mongo_db_name]
"""

files["src/db/models.py"] = """\
from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, Field

class FileMetadata(BaseModel):
    filename: str; blob_url: str; size_bytes: int; extension: str
    schema_snapshot: Optional[dict] = None
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SessionMetadata(BaseModel):
    file_id: str; user_query: str; status: str = "running"
    agent_logs: List[str] = []; errors: List[str] = []
    report_md: Optional[str] = None; chart_count: int = 0
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
"""

files["src/db/repositories/file_repo.py"] = """\
from bson import ObjectId
from src.db.client import get_db
from src.db.models import FileMetadata

COLLECTION = "files"

async def save_file_metadata(data: FileMetadata) -> str:
    result = await get_db()[COLLECTION].insert_one(data.model_dump())
    return str(result.inserted_id)

async def get_file_metadata(file_id: str) -> dict | None:
    doc = await get_db()[COLLECTION].find_one({"_id": ObjectId(file_id)})
    if doc: doc["_id"] = str(doc["_id"])
    return doc

async def patch_schema_snapshot(file_id: str, schema_snapshot: dict) -> None:
    await get_db()[COLLECTION].update_one({"_id": ObjectId(file_id)}, {"$set": {"schema_snapshot": schema_snapshot}})
"""

files["src/db/repositories/session_repo.py"] = """\
from datetime import datetime, timezone
from bson import ObjectId
from src.db.client import get_db
from src.db.models import SessionMetadata

COLLECTION = "sessions"

async def create_session(data: SessionMetadata) -> str:
    result = await get_db()[COLLECTION].insert_one(data.model_dump())
    return str(result.inserted_id)

async def update_session(session_id: str, update: dict) -> None:
    update["completed_at"] = datetime.now(timezone.utc)
    await get_db()[COLLECTION].update_one({"_id": ObjectId(session_id)}, {"$set": update})

async def get_session(session_id: str) -> dict | None:
    doc = await get_db()[COLLECTION].find_one({"_id": ObjectId(session_id)})
    if doc: doc["_id"] = str(doc["_id"])
    return doc

async def list_sessions(limit: int = 20) -> list[dict]:
    docs = await get_db()[COLLECTION].find().sort("started_at", -1).limit(limit).to_list(length=limit)
    for d in docs: d["_id"] = str(d["_id"])
    return docs
"""

files["src/storage/__init__.py"] = ""
files["src/storage/blob_client.py"] = """\
import uuid
from azure.storage.blob.aio import BlobServiceClient
from src.config.settings import get_settings

async def upload_file(file_bytes: bytes, filename: str) -> str:
    settings = get_settings()
    blob_name = f"{uuid.uuid4()}_{filename}"
    async with BlobServiceClient.from_connection_string(settings.azure_storage_connection_string) as client:
        container = client.get_container_client(settings.azure_storage_container_name)
        await container.upload_blob(name=blob_name, data=file_bytes, overwrite=True)
    return f"https://<account>.blob.core.windows.net/{settings.azure_storage_container_name}/{blob_name}"

async def download_file(blob_url: str) -> bytes:
    settings = get_settings()
    blob_name = blob_url.split("/")[-1]
    async with BlobServiceClient.from_connection_string(settings.azure_storage_connection_string) as client:
        container = client.get_container_client(settings.azure_storage_container_name)
        stream = await container.download_blob(blob_name)
        return await stream.readall()
"""

files["src/api/__init__.py"] = ""
files["src/api/routes/__init__.py"] = ""
files["src/api/main.py"] = """\
import structlog, logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from src.config.settings import get_settings
from src.api.routes import upload, analyse, sessions

settings = get_settings()
logging.basicConfig(level=settings.log_level)
logger = structlog.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up", env=settings.app_env); yield; logger.info("Shutting down")

app = FastAPI(title="AI Data Analyst Agent", version="0.1.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="src/static"), name="static")
templates = Jinja2Templates(directory="src/templates")
app.include_router(upload.router,  prefix="/api/v1", tags=["upload"])
app.include_router(analyse.router, prefix="/api/v1", tags=["analyse"])
app.include_router(sessions.router,prefix="/api/v1", tags=["sessions"])

@app.get("/health")
async def health(): return {"status": "ok", "env": settings.app_env}

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
"""

files["src/api/routes/upload.py"] = """\
import io, pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException
from src.config.settings import get_settings
from src.storage.blob_client import upload_file
from src.db.models import FileMetadata
from src.db.repositories.file_repo import save_file_metadata

router, settings = APIRouter(), get_settings()

@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    ext = file.filename.split(".")[-1].lower()
    if ext not in settings.allowed_ext_list:
        raise HTTPException(400, f"Extension .{ext} not allowed")
    content = await file.read()
    if len(content) > settings.max_upload_size_mb * 1024 * 1024:
        raise HTTPException(413, f"File exceeds {settings.max_upload_size_mb}MB")
    try:
        df = pd.read_csv(io.BytesIO(content)) if ext=="csv" else pd.read_excel(io.BytesIO(content))
        shape = {"rows": df.shape[0], "cols": df.shape[1], "columns": df.columns.tolist()}
    except Exception as exc:
        raise HTTPException(422, f"Could not parse file: {exc}")
    blob_url = await upload_file(content, file.filename)
    file_id = await save_file_metadata(FileMetadata(filename=file.filename, blob_url=blob_url, size_bytes=len(content), extension=ext))
    return {"file_id": file_id, "filename": file.filename, "shape": shape}
"""

files["src/api/routes/analyse.py"] = """\
import io, asyncio, pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from src.config.settings import get_settings
from src.graph.graph_builder import build_graph
from src.graph.state import AnalystState
from src.storage.blob_client import download_file
from src.db.repositories.file_repo import get_file_metadata, patch_schema_snapshot
from src.db.repositories.session_repo import create_session, update_session
from src.db.models import SessionMetadata

router, settings = APIRouter(), get_settings()

class AnalyseRequest(BaseModel):
    file_id: str; user_query: str

@router.post("/analyse")
async def analyse(req: AnalyseRequest):
    file_meta = await get_file_metadata(req.file_id)
    if not file_meta: raise HTTPException(404, "file_id not found")
    raw_bytes = await download_file(file_meta["blob_url"])
    ext = file_meta["extension"]
    try:
        df = pd.read_csv(io.BytesIO(raw_bytes)) if ext=="csv" else pd.read_excel(io.BytesIO(raw_bytes))
    except Exception as exc:
        raise HTTPException(422, f"Failed to read file: {exc}")
    llm = ChatOpenAI(model=settings.azure_openai_deployment, api_key=settings.openai_api_key, temperature=0)
    graph = build_graph(llm)
    session_id = await create_session(SessionMetadata(file_id=req.file_id, user_query=req.user_query))
    initial: AnalystState = {"user_query": req.user_query, "raw_data": df, "file_id": req.file_id,
        "schema_info": None, "cleaned_data": None, "query_plan": None,
        "analysis_results": None, "charts": None, "errors": [], "agent_logs": [], "final_report": None, "session_id": session_id}
    final = await asyncio.get_event_loop().run_in_executor(None, graph.invoke, initial)
    await update_session(session_id, {"status": "completed" if not final["errors"] else "failed",
        "agent_logs": final["agent_logs"], "errors": final["errors"],
        "report_md": final["final_report"], "chart_count": len(final.get("charts") or [])})
    if final.get("schema_info"): await patch_schema_snapshot(req.file_id, final["schema_info"])
    return {"session_id": session_id, "final_report": final["final_report"],
            "charts": [{"title": c["title"], "fig_json": c["fig_json"]} for c in (final.get("charts") or [])],
            "errors": final["errors"], "agent_logs": final["agent_logs"]}
"""

files["src/api/routes/sessions.py"] = """\
from fastapi import APIRouter, HTTPException
from src.db.repositories.session_repo import list_sessions, get_session

router = APIRouter()

@router.get("/sessions")
async def get_sessions(limit: int = 20): return await list_sessions(limit=limit)

@router.get("/sessions/{session_id}")
async def get_session_detail(session_id: str):
    doc = await get_session(session_id)
    if not doc: raise HTTPException(404, "Session not found")
    return doc
"""

files["src/static/css/style.css"] = """\
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#0f1117;--surface:#1a1d27;--border:#2a2d3a;--accent:#636efa;--accent-hover:#7c8bff;--text:#e8eaf0;--text-muted:#8b8fa8;--success:#00cc96;--error:#ef553b;--radius:8px;--font:'Inter',system-ui,sans-serif}
body{background:var(--bg);color:var(--text);font-family:var(--font);min-height:100vh;display:flex;flex-direction:column;align-items:center;padding:2rem 1rem}
.container{width:100%;max-width:900px}
h1{font-size:1.8rem;font-weight:700;margin-bottom:.25rem}
.subtitle{color:var(--text-muted);margin-bottom:2rem;font-size:.95rem}
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:1.5rem;margin-bottom:1.5rem}
.card h2{font-size:1rem;font-weight:600;margin-bottom:1rem;color:var(--accent)}
input[type=file],textarea,input[type=text]{width:100%;background:var(--bg);border:1px solid var(--border);border-radius:var(--radius);color:var(--text);padding:.75rem 1rem;font-size:.95rem;font-family:var(--font);outline:none;transition:border-color .2s}
input[type=file]:focus,textarea:focus{border-color:var(--accent)}
textarea{resize:vertical;min-height:80px}
.btn{display:inline-flex;align-items:center;gap:.5rem;background:var(--accent);color:#fff;border:none;border-radius:var(--radius);padding:.75rem 1.5rem;font-size:.95rem;font-weight:600;cursor:pointer;transition:background .2s,transform .1s}
.btn:hover{background:var(--accent-hover)}.btn:active{transform:scale(.98)}.btn:disabled{opacity:.5;cursor:not-allowed}
.status{padding:.5rem 1rem;border-radius:var(--radius);font-size:.875rem;margin-top:1rem}
.status.success{background:rgba(0,204,150,.1);color:var(--success)}.status.error{background:rgba(239,85,59,.1);color:var(--error)}.status.loading{background:rgba(99,110,250,.1);color:var(--accent)}
.report-box{background:var(--bg);border:1px solid var(--border);border-radius:var(--radius);padding:1.25rem;white-space:pre-wrap;font-size:.875rem;line-height:1.7;max-height:500px;overflow-y:auto}
"""

files["src/static/js/app.js"] = """\
let fileId=null;
async function uploadFile(){
  const input=document.getElementById('fileInput'),statusEl=document.getElementById('uploadStatus');
  if(!input.files.length)return alert('Select a file first');
  const form=new FormData();form.append('file',input.files[0]);
  statusEl.textContent='Uploading...';statusEl.className='status loading';statusEl.style.display='block';
  try{
    const res=await fetch('/api/v1/upload',{method:'POST',body:form});
    const data=await res.json();
    if(!res.ok)throw new Error(data.detail||'Upload failed');
    fileId=data.file_id;
    statusEl.textContent=`✅ Uploaded: ${data.filename} (${data.shape.rows} rows × ${data.shape.cols} cols)`;
    statusEl.className='status success';
    document.getElementById('analyseSection').style.display='block';
  }catch(err){statusEl.textContent=`❌ ${err.message}`;statusEl.className='status error';}
}
async function runAnalysis(){
  const query=document.getElementById('queryInput').value.trim();
  const statusEl=document.getElementById('analyseStatus'),reportEl=document.getElementById('reportBox'),chartsEl=document.getElementById('chartsBox');
  if(!fileId)return alert('Upload a file first');
  if(!query)return alert('Enter a question');
  statusEl.textContent='⏳ Running 6-agent pipeline... (30–60s)';statusEl.className='status loading';
  reportEl.textContent='';chartsEl.innerHTML='';
  try{
    const res=await fetch('/api/v1/analyse',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({file_id:fileId,user_query:query})});
    const data=await res.json();
    if(!res.ok)throw new Error(data.detail||'Analysis failed');
    statusEl.textContent=`✅ Done — Session: ${data.session_id}`;statusEl.className='status success';
    reportEl.textContent=data.final_report||'(no report)';
    if(data.charts&&data.charts.length){
      data.charts.forEach((c,i)=>{
        const div=document.createElement('div');div.id=`chart-${i}`;div.style.marginBottom='1.5rem';chartsEl.appendChild(div);
        const fig=JSON.parse(c.fig_json);Plotly.react(div.id,fig.data,fig.layout);
      });
    }
  }catch(err){statusEl.textContent=`❌ ${err.message}`;statusEl.className='status error';}
}
"""

files["src/templates/index.html"] = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
  <title>AI Data Analyst Agent</title>
  <link rel="stylesheet" href="/static/css/style.css">
  <script src="https://cdn.plot.ly/plotly-2.35.0.min.js"></script>
</head>
<body>
  <div class="container">
    <h1>🤖 AI Data Analyst Agent</h1>
    <p class="subtitle">Multi-agent LangGraph system · Azure OpenAI · MongoDB</p>
    <div class="card">
      <h2>1 · Upload Dataset</h2>
      <input type="file" id="fileInput" accept=".csv,.xlsx,.xls"><br><br>
      <button class="btn" onclick="uploadFile()">⬆ Upload</button>
      <div id="uploadStatus" class="status" style="display:none"></div>
    </div>
    <div class="card" id="analyseSection" style="display:none">
      <h2>2 · Ask a Question</h2>
      <textarea id="queryInput" placeholder="e.g. What factors most influenced survival on the Titanic?"></textarea><br><br>
      <button class="btn" onclick="runAnalysis()">🚀 Run Analysis</button>
      <div id="analyseStatus" class="status"></div>
    </div>
    <div class="card" id="reportCard" style="display:none">
      <h2>3 · Report</h2>
      <div id="reportBox" class="report-box"></div>
    </div>
    <div id="chartsBox"></div>
  </div>
  <script src="/static/js/app.js"></script>
  <script>
    const obs=new MutationObserver(()=>{if(document.getElementById('reportBox').textContent)document.getElementById('reportCard').style.display='block';});
    obs.observe(document.getElementById('reportBox'),{childList:true,characterData:true,subtree:true});
  </script>
</body>
</html>
"""

files["tests/__init__.py"] = ""
files["tests/unit/__init__.py"] = ""
files["tests/integration/__init__.py"] = ""
files["tests/conftest.py"] = """\
import pytest
import pandas as pd
from unittest.mock import MagicMock
from langchain_core.messages import AIMessage

@pytest.fixture
def sample_df():
    return pd.DataFrame({"PassengerId":[1,2,3,4,5],"Survived":[0,1,1,0,1],"Pclass":[3,1,3,1,3],
        "Name":["Braund","Cumings","Heikkinen","Futrelle","Allen"],"Sex":["male","female","female","female","male"],
        "Age":[22.0,38.0,None,35.0,35.0],"Fare":[7.25,71.28,7.925,53.1,8.05]})

@pytest.fixture
def mock_llm():
    llm=MagicMock()
    llm.invoke.return_value=AIMessage(content='{"Survived":{"role":"target","description":"Survival","analytical_importance":"high"},"Pclass":{"role":"categorical","description":"Class","analytical_importance":"high"},"Age":{"role":"numerical","description":"Age","analytical_importance":"high"},"Fare":{"role":"numerical","description":"Fare","analytical_importance":"medium"},"Sex":{"role":"categorical","description":"Gender","analytical_importance":"high"},"Name":{"role":"text","description":"Name","analytical_importance":"low"},"PassengerId":{"role":"id","description":"ID","analytical_importance":"low"}}')
    return llm

@pytest.fixture
def base_state(sample_df):
    return {"user_query":"Analyse survival rates by gender and class","raw_data":sample_df,"file_id":"test_file_id",
            "schema_info":None,"cleaned_data":None,"query_plan":None,"analysis_results":None,"charts":None,
            "errors":[],"agent_logs":[],"final_report":None,"session_id":None}
"""

files["tests/unit/test_schema_agent.py"] = """\
from src.agents.schema_agent import SchemaAnalysisAgent

def test_schema_agent_populates_schema_info(base_state,mock_llm,sample_df):
    result=SchemaAnalysisAgent(mock_llm).run(base_state)
    assert result["schema_info"] is not None
    assert result["schema_info"]["shape"]["rows"]==5
    assert "PassengerId" in result["schema_info"]["columns"]

def test_schema_agent_identifies_target(base_state,mock_llm):
    result=SchemaAnalysisAgent(mock_llm).run(base_state)
    assert result["schema_info"]["target_hint"]=="Survived"

def test_schema_agent_logs_steps(base_state,mock_llm):
    result=SchemaAnalysisAgent(mock_llm).run(base_state)
    assert len(result["agent_logs"])>=1
"""

files["tests/unit/test_cleaning_agent.py"] = """\
from src.agents.cleaning_agent import DataCleaningAgent

def test_cleaning_fills_numeric_nulls(base_state,sample_df):
    schema_info={"shape":{"rows":5,"cols":7},"high_null_cols":[],"target_hint":"Survived","columns":{
        "Age":{"dtype":"float64","null_pct":20.0,"role":"numerical","unique_count":4,"sample_values":[22.0]},
        **{c:{"dtype":"object","null_pct":0.0,"role":"categorical","unique_count":2,"sample_values":[]}
           for c in ["Sex","Name","PassengerId","Survived","Pclass","Fare"]}}}
    result=DataCleaningAgent().run({**base_state,"schema_info":schema_info})
    assert result["cleaned_data"]["Age"].isnull().sum()==0

def test_cleaning_drops_high_null_column(base_state,sample_df):
    import pandas as pd
    df=sample_df.copy(); df["HighNull"]=[None,None,None,None,1.0]
    schema_info={"shape":{"rows":5,"cols":8},"high_null_cols":["HighNull"],"target_hint":"Survived","columns":{
        "HighNull":{"dtype":"float64","null_pct":80.0,"role":"numerical","unique_count":1,"sample_values":[1.0]},
        **{c:{"dtype":"object","null_pct":0.0,"role":"categorical","unique_count":2,"sample_values":[]}
           for c in ["Sex","Name","PassengerId","Survived","Pclass","Fare","Age"]}}}
    result=DataCleaningAgent().run({**base_state,"raw_data":df,"schema_info":schema_info})
    assert "HighNull" not in result["cleaned_data"].columns
"""

files["tests/unit/test_router.py"] = """\
from langgraph.graph import END
from src.graph.router import supervisor_router

def test_routes_to_schema_when_no_schema(base_state): assert supervisor_router(base_state)=="schema_analysis"
def test_routes_to_cleaning_after_schema(base_state,sample_df):
    assert supervisor_router({**base_state,"schema_info":{"shape":{},"columns":{},"target_hint":None}})=="data_cleaning"
def test_routes_to_end_when_all_complete(base_state,sample_df):
    assert supervisor_router({**base_state,"schema_info":{},"cleaned_data":sample_df,"query_plan":"results={}","analysis_results":{},"charts":[],"final_report":"# Report"})==END
"""

files["tests/integration/test_graph_pipeline.py"] = """\
from src.graph.graph_builder import build_graph

def test_full_pipeline_completes(base_state,mock_llm,sample_df):
    from langchain_core.messages import AIMessage
    orig=mock_llm.invoke
    def smart(msgs):
        c=str(msgs[-1].content)
        if "results" in c.lower() or "pandas" in c.lower():
            return AIMessage(content='results={"summary":"test","key_metrics":{},"data_for_viz":{}}')
        return orig(msgs)
    mock_llm.invoke=smart
    result=build_graph(mock_llm).invoke(base_state)
    assert result["final_report"] is not None
    assert result["schema_info"] is not None
    assert result["cleaned_data"] is not None
"""

files[".github/workflows/ci.yml"] = """\
name: CI
on:
  push: { branches: [main, develop] }
  pull_request: { branches: [main] }
jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11", cache: pip }
      - run: pip install --upgrade pip && pip install -r requirements-dev.txt
      - run: ruff check src/ tests/
      - run: black --check src/ tests/
      - run: pytest tests/unit -v --cov=src --cov-report=xml
        env: { OPENAI_API_KEY: dummy, MONGO_URI: mongodb://localhost:27017, AZURE_STORAGE_CONNECTION_STRING: dummy }
      - uses: codecov/codecov-action@v4
        with: { file: coverage.xml, fail_ci_if_error: false }
  docker-build:
    runs-on: ubuntu-latest
    needs: lint-and-test
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t ai-data-analyst:ci .
      - run: |
          docker run -d -p 8000:8000 -e OPENAI_API_KEY=dummy -e MONGO_URI=mongodb://localhost:27017 -e AZURE_STORAGE_CONNECTION_STRING=dummy --name test_app ai-data-analyst:ci
          sleep 10 && curl -f http://localhost:8000/health || (docker logs test_app && exit 1)
          docker stop test_app
"""

files[".github/workflows/cd.yml"] = """\
name: CD
on:
  push:
    branches: [main]
    tags: ["v*.*.*"]
env:
  REGISTRY: ${{ secrets.ACR_LOGIN_SERVER }}
  IMAGE_NAME: ai-data-analyst
  CONTAINER_APP: ai-data-analyst-app
  RESOURCE_GROUP: rg-ai-analyst
jobs:
  build-and-push:
    runs-on: ubuntu-latest
    outputs:
      image_tag: ${{ steps.meta.outputs.version }}
    steps:
      - uses: actions/checkout@v4
      - uses: azure/docker-login@v1
        with: { login-server: "${{ secrets.ACR_LOGIN_SERVER }}", username: "${{ secrets.ACR_USERNAME }}", password: "${{ secrets.ACR_PASSWORD }}" }
      - id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=sha,prefix=sha-
            type=semver,pattern={{version}}
            type=raw,value=latest,enable=${{ github.ref == 'refs/heads/main' }}
      - uses: docker/build-push-action@v5
        with:
          context: . 
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          cache-from: type=registry,ref=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:buildcache
          cache-to: type=registry,ref=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:buildcache,mode=max
  deploy:
    runs-on: ubuntu-latest
    needs: build-and-push
    environment: production
    steps:
      - uses: azure/login@v2
        with: { creds: "${{ secrets.AZURE_CREDENTIALS }}" }
      - uses: azure/container-apps-deploy-action@v2
        with:
          resourceGroup: ${{ env.RESOURCE_GROUP }}
          containerAppName: ${{ env.CONTAINER_APP }}
          imageToDeploy: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ needs.build-and-push.outputs.image_tag }}
      - run: sleep 15 && curl -f https://${{ env.CONTAINER_APP }}.azurecontainerapps.io/health
"""

files["infra/azure/deploy.sh"] = """\
#!/bin/bash
set -euo pipefail
RESOURCE_GROUP="rg-ai-analyst"; LOCATION="eastus"; ACR_NAME="aiadataanalystacr"
ACA_ENV="ai-analyst-env"; APP_NAME="ai-data-analyst-app"
az group create --name $RESOURCE_GROUP --location $LOCATION
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true
az containerapp env create --name $ACA_ENV --resource-group $RESOURCE_GROUP --location $LOCATION
az containerapp create --name $APP_NAME --resource-group $RESOURCE_GROUP --environment $ACA_ENV \\
  --image mcr.microsoft.com/azuredocs/containerapps-helloworld:latest \\
  --target-port 8000 --ingress external --min-replicas 1 --max-replicas 5 --cpu 1.0 --memory 2.0Gi
echo "✅ Done. Set GitHub secrets: ACR_LOGIN_SERVER, ACR_USERNAME, ACR_PASSWORD, AZURE_CREDENTIALS"
"""

# ── README with full Mermaid diagrams ─────────────────────────────────────────
files["README.md"] = open("/mnt/user-data/outputs/ai-data-analyst/README.md").read()

# ── WRITE ALL FILES ────────────────────────────────────────────────────────────
created = 0
for rel_path, content in files.items():
    full_path = os.path.join(ROOT, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w") as f:
        f.write(content)
    created += 1

print(f"\n✅  Created {created} files in ./{ROOT}/")
print("\nNext steps:")
print("  1. cp .env.example .env   (fill in your keys)")
print("  2. docker-compose up --build")
print("  3. open http://localhost:8000")
print("  4. git init && git remote add origin <your-repo>")
print("  5. git push origin main  → triggers CI/CD automatically")