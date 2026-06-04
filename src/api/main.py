import json
import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.agents.schema_agent import SchemaAgent
from src.agents.cleaning_agent import DataCleaningAgent
from src.agents.query_agent import QueryPlanningAgent
from src.agents.analysis_agent import AnalysisAgent
from src.agents.viz_agent import VizAgent
from src.agents.report_agent import ReportAgent
from src.graph.state import AnalystState
from src.data_ingestion.loader_factory import load_uploaded_file

BASE_DIR = Path(__file__).resolve().parents[2]
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(title="AI Data Analyst Agent")

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "src" / "static"),
    name="static",
)

templates = Jinja2Templates(directory=BASE_DIR / "src" / "templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )

@app.post("/analyse")
async def analyse(file: UploadFile = File(...), user_query: str = Form(...)):
    session_id = str(uuid.uuid4())
    file_path = UPLOAD_DIR / f"{session_id}_{file.filename}"

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    def event_stream():
        try:
            yield sse("File uploaded successfully")

            df = load_uploaded_file(str(file_path))

            state: AnalystState = {
                "user_query": user_query,
                "raw_data": df,
                "source": str(file_path),
                "schema_info": None,
                "cleaned_data": None,
                "query_plan": None,
                "analysis_results": None,
                "charts": None,
                "errors": [],
                "agent_logs": [],
                "final_report": None,
            }

            agents = [
                ("Schema Analysis Agent", SchemaAgent()),
                ("Data Cleaning Agent", DataCleaningAgent()),
                ("Query Planning Agent", QueryPlanningAgent()),
                ("Statistical Analysis Agent", AnalysisAgent()),
                ("Visualization Agent", VizAgent()),
                ("Report Agent", ReportAgent()),
            ]

            for agent_name, agent in agents:
                yield sse(f"{agent_name} started")
                state = agent.run(state)

                if state.get("errors"):
                    yield sse(f"{agent_name} failed")
                    yield sse_done(
                        {
                            "success": False,
                            "errors": state["errors"],
                            "report": state.get("final_report"),
                            "charts": [],
                        }
                    )
                    return

                yield sse(f"{agent_name} completed")

            chart_payload = []

            for chart in state.get("charts", []) or []:
                chart_payload.append(
                    {
                        "title": chart["title"],
                        "figure": chart["fig"].to_json(),
                    }
                )

            yield sse_done(
                {
                    "success": True,
                    "report": state["final_report"],
                    "errors": state.get("errors", []),
                    "charts": chart_payload,
                }
            )

        except Exception as e:
            yield sse_done(
                {
                    "success": False,
                    "errors": [str(e)],
                    "report": None,
                    "charts": [],
                }
            )

    return StreamingResponse(event_stream(), media_type="text/event-stream")


def sse(message: str) -> str:
    return f"data: {json.dumps({'type': 'status', 'message': message})}\n\n"


def sse_done(payload: dict) -> str:
    payload["type"] = "done"
    return f"data: {json.dumps(payload)}\n\n"