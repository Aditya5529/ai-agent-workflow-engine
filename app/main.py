from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect

from .engine import GraphEngine
from .models import (
    GraphCreateRequest,
    GraphCreateResponse,
    RunRequest,
    RunStateResponse,
    RunResult,
    GraphDefinition,
    GRAPHS,
    RUNS
)
from .tools import tool_registry
import asyncio


app = FastAPI(title="Minimal Agent Workflow Engine")

engine = GraphEngine()


# -----------------------------------------
# Health Check
# -----------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


# -----------------------------------------
# Create Graph
# -----------------------------------------
@app.post("/graph/create", response_model=GraphCreateResponse)
def create_graph(req: GraphCreateRequest):

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
# Run Graph (Standard Execution)
# -----------------------------------------
@app.post("/graph/run", response_model=RunResult)
def run_graph(req: RunRequest):
    try:
        return engine.run_graph(req.graph_id, req.initial_state)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# -----------------------------------------
# Get Run State (Logs + Final State)
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


# -----------------------------------------
# List Available Tools
# -----------------------------------------
@app.get("/tools")
def list_tools():
    return tool_registry.list_tools()


# -----------------------------------------
# WebSocket: Real-Time Workflow Streaming
# -----------------------------------------
@app.websocket("/ws/run/{graph_id}")
async def websocket_run(websocket: WebSocket, graph_id: str):
    await websocket.accept()

    async def sender(msg):
        import json
        await websocket.send_text(json.dumps(msg))

    try:
        # run the sync graph engine in a thread so WebSocket stays responsive
        loop = asyncio.get_event_loop()

        def run_sync():
            engine.run_graph_stream(
                graph_id,
                initial_state={},
                callback=lambda m: asyncio.run_coroutine_threadsafe(sender(m), loop)
            )

        # start graph execution in background
        await loop.run_in_executor(None, run_sync)

    except WebSocketDisconnect:
        print("WebSocket disconnected")

    finally:
        await websocket.close()


# -----------------------------------------
# List All Graphs
# -----------------------------------------
@app.get("/graphs")
def list_graphs():
    return GRAPHS


# -----------------------------------------
# List All Runs
# -----------------------------------------
@app.get("/runs")
def list_runs():
    return RUNS


# -----------------------------------------
# Graph Visualization (DOT Format)
# -----------------------------------------
@app.get("/graph/visualize/{graph_id}")
def visualize_graph(graph_id: str):
    if graph_id not in GRAPHS:
        raise HTTPException(status_code=404, detail="Graph not found")

    graph = GRAPHS[graph_id]

    dot = "digraph workflow {\n"
    for src, dst in graph.edges.items():
        dot += f'    "{src}" -> "{dst}";\n'
    dot += "}"

    return {"dot": dot}
 