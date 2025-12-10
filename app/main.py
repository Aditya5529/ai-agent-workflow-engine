from fastapi import FastAPI, HTTPException

from .engine import GraphEngine
from .models import (
    GraphCreateRequest,
    GraphCreateResponse,
    RunRequest,
    RunStateResponse,
    RunResult,
    GraphDefinition,
)

from .tools import tool_registry


app = FastAPI(title="Minimal Agent Workflow Engine")

engine = GraphEngine()


@app.get("/health")
def health():
    return {"status": "ok"}


# -----------------------------------------
# Create graph
# -----------------------------------------
@app.post("/graph/create", response_model=GraphCreateResponse)
def create_graph(req: GraphCreateRequest):

    # validate
    if req.entrypoint not in req.nodes:
        raise HTTPException(
            status_code=400,
            detail="entrypoint must be part of nodes list"
        )

    graph = GraphDefinition(
        name=req.name,
        nodes=req.nodes,
        edges=req.edges,
        entrypoint=req.entrypoint,
        description=req.description,
    )

    graph_id = engine.create_graph(graph)
    return GraphCreateResponse(graph_id=graph_id)


# -----------------------------------------
# Run graph
# -----------------------------------------
@app.post("/graph/run", response_model=RunResult)
def run_graph(req: RunRequest):
    try:
        result = engine.run_graph(req.graph_id, req.initial_state)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# -----------------------------------------
# Get run state
# -----------------------------------------
@app.get("/graph/state/{run_id}", response_model=RunStateResponse)
def get_run_state(run_id: str):
    try:
        run = engine.get_run(run_id)
        return RunStateResponse(
            run_id=run.id,
            graph_id=run.graph_id,
            started_at=run.started_at,
            finished_at=run.finished_at,
            final_state=run.final_state,
            log=run.log,
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="Run not found")


@app.get("/tools")
def list_tools():
    return tool_registry.list_tools()
