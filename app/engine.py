from typing import Dict, Any, Optional
from uuid import uuid4
from datetime import datetime

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
        self.graphs = GRAPHS           # global graph store
        self.runs = RUNS               # global run store


    # ----------------------------------------------------
    # create graph (stores it in memory)
    # ----------------------------------------------------
    def create_graph(self, graph: GraphDefinition) -> str:
        self.graphs[graph.id] = graph
        return graph.id


    # ----------------------------------------------------
    # run a single node
    # ----------------------------------------------------
    def _run_single_node(
        self,
        graph: GraphDefinition,
        node_name: str,
        state: Dict[str, Any],
        run_record: RunRecord,
    ) -> Optional[str]:
        """
        Execute node function and return next node name (or None).
        """

        # get function from registry
        tool = tool_registry.get(node_name)

        # execute (function updates & returns state)
        state = tool(state)

        # log snapshot
        run_record.log.append(
            NodeExecutionLog(
                node=node_name,
                timestamp=datetime.utcnow(),
                state_snapshot=state.copy(),
            )
        )

        # branch or loop based on state["_next"]
        if "_next" in state:
            return state["_next"]

        # otherwise follow graph edges
        return graph.edges.get(node_name)


    # ----------------------------------------------------
    # run full graph until no next node
    # ----------------------------------------------------
    def run_graph(self, graph_id: str, initial_state: Dict[str, Any]) -> RunResult:

        if graph_id not in self.graphs:
            raise KeyError(f"Graph '{graph_id}' not found")

        graph = self.graphs[graph_id]

        # every run has unique ID
        run_id = str(uuid4())
        run_record = RunRecord(
            id=run_id,
            graph_id=graph_id,
            started_at=datetime.utcnow(),
        )
        self.runs[run_id] = run_record

        state = dict(initial_state)   # avoid mutating caller input
        current_node = graph.entrypoint

        visited = 0
        max_steps = 200                # safety to avoid infinite loop

        while current_node is not None and visited < max_steps:

            if current_node not in graph.nodes:
                raise ValueError(f"Undefined node: {current_node}")

            next_node = self._run_single_node(
                graph,
                current_node,
                state,
                run_record
            )
            current_node = next_node
            visited += 1

        # finish run record
        run_record.finished_at = datetime.utcnow()
        run_record.final_state = state

        return RunResult(
            run_id=run_id,
            final_state=state,
            log=run_record.log
        )


    # ----------------------------------------------------
    # fetch run status + state
    # ----------------------------------------------------
    def get_run(self, run_id: str) -> RunRecord:
        if run_id not in self.runs:
            raise KeyError(f"Run '{run_id}' not found")
        return self.runs[run_id]
