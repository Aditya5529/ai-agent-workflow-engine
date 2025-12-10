from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from uuid import uuid4
from datetime import datetime


# ---------- Core graph models ----------

class GraphDefinition(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    nodes: List[str]                     # node names (must exist in tool registry)
    edges: Dict[str, str]               # simple mapping: current_node -> next_node
    entrypoint: str                     # starting node name
    description: Optional[str] = None


class GraphCreateRequest(BaseModel):
    name: str
    nodes: List[str]
    edges: Dict[str, str]
    entrypoint: str
    description: Optional[str] = None


class GraphCreateResponse(BaseModel):
    graph_id: str


# ---------- Run / execution models ----------

class RunRequest(BaseModel):
    graph_id: str
    initial_state: Dict[str, Any] = Field(default_factory=dict)


class NodeExecutionLog(BaseModel):
    node: str
    timestamp: datetime
    state_snapshot: Dict[str, Any]
    duration_ms: float = 0.0
    


class RunResult(BaseModel):
    run_id: str
    final_state: Dict[str, Any]
    log: List[NodeExecutionLog]


class RunRecord(BaseModel):
    id: str
    graph_id: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    final_state: Optional[Dict[str, Any]] = None
    log: List[NodeExecutionLog] = Field(default_factory=list)


class RunStateResponse(BaseModel):
    run_id: str
    graph_id: str
    started_at: datetime
    finished_at: Optional[datetime]
    final_state: Optional[Dict[str, Any]]
    log: List[NodeExecutionLog]


# ---------- In-memory stores ----------

GRAPHS: Dict[str, GraphDefinition] = {}
RUNS: Dict[str, RunRecord] = {}
