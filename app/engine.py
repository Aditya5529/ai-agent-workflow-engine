from typing import Dict, Any, Optional, Callable
from uuid import uuid4
from datetime import datetime
import time

from .models import (
    GraphDefinition,
    GRAPHS,
    RUNS,
    RunRecord,
    NodeExecutionLog,
    RunResult,
)
from .tools import tool_registry

 
class GraphEngine:

    def __init__(self):
        self.graphs = GRAPHS
        self.runs = RUNS

    # -------------------------------------------------------------
    # Create Graph
    # -------------------------------------------------------------
    def create_graph(self, graph: GraphDefinition) -> str:
        self.graphs[graph.id] = graph
        return graph.id
    
    def get_run(self, run_id: str):
        if run_id not in self.runs:
            raise KeyError(f"Run ID '{run_id}' not found")
        return self.runs[run_id]

    # -------------------------------------------------------------
    # Internal node execution
    # -------------------------------------------------------------
    def _run_single_node(
        self,
        graph: GraphDefinition,
        node_name: str,
        state: Dict[str, Any],
        run_record: RunRecord,
    ) -> Optional[str]:

        tool = tool_registry.get(node_name)

        start = time.time()
        state = tool(state)  # node execution
        duration = round((time.time() - start) * 1000, 3)

        # Log execution
        run_record.log.append(
            NodeExecutionLog(
                node=node_name,
                timestamp=datetime.utcnow(),
                state_snapshot=state.copy(),
                duration_ms=duration
            )
        )

        if "_next" in state:
            return state["_next"]

        return graph.edges.get(node_name)

    # -------------------------------------------------------------
    # Full Workflow Execution (Standard)
    # -------------------------------------------------------------
    def run_graph(self, graph_id: str, initial_state: Dict[str, Any]) -> RunResult:

        if graph_id not in self.graphs:
            raise KeyError(f"Graph '{graph_id}' not found")

        graph = self.graphs[graph_id]

        run_id = str(uuid4())
        run_record = RunRecord(
            id=run_id,
            graph_id=graph_id,
            started_at=datetime.utcnow(),
        )
        self.runs[run_id] = run_record

        state = dict(initial_state)
        current_node = graph.entrypoint
        visited = 0
        max_steps = 200

        while current_node is not None and visited < max_steps:

            if current_node not in graph.nodes:
                raise ValueError(f"Undefined node: {current_node}")

            next_node = self._run_single_node(graph, current_node, state, run_record)
            current_node = next_node
            visited += 1

        run_record.finished_at = datetime.utcnow()
        run_record.final_state = state

        return RunResult(
            run_id=run_id,
            final_state=state,
            log=run_record.log
        )

    # -------------------------------------------------------------
    # Streaming Version (WebSockets)
    # -------------------------------------------------------------
    def run_graph_stream(
        self,
        graph_id: str,
        initial_state: Dict[str, Any],
        callback: Callable[[Dict[str, Any]], None]
    ) -> RunResult:

        if graph_id not in self.graphs:
            raise KeyError(f"Graph '{graph_id}' not found")

        graph = self.graphs[graph_id]

        state = dict(initial_state)
        current_node = graph.entrypoint
        steps = 0

        callback({"event": "workflow_started", "entrypoint": current_node})

        while current_node is not None:

            callback({"event": "node_started", "node": current_node})

            tool = tool_registry.get(current_node)

            start = time.time()
            state = tool(state)
            duration = round((time.time() - start) * 1000, 3)

            callback({
                "event": "node_completed",
                "node": current_node,
                "duration_ms": duration,
                "state": state.copy()
            })

            if "_next" in state:
                current_node = state["_next"]
            else:
                current_node = graph.edges.get(current_node)

            steps += 1
            if steps > 200:
                callback({"event": "error", "message": "Max steps exceeded"})
                break

        callback({"event": "workflow_done", "final_state": state})
        return RunResult(run_id="stream", final_state=state, log=[])
