🚀 AI AGENT WORKFLOW ENGINE

A minimal yet powerful Agent Workflow Engine built using Python & FastAPI.

Workflows consist of nodes (Python functions) that mutate shared state and are connected as a directed graph.
Supports branching, looping, execution logging, real-time WebSocket streaming, and graph visualization.

<br>
✨ Key Features:

 Node registry (tools)

 Directed workflow graph (DAG)

 Shared mutable state

 Branching & loop control using _next

 Execution logging (timestamp, snapshots, duration)

 FastAPI endpoints for graph execution

 WebSocket live workflow streaming

 Graph visualization (GraphViz DOT output)

 Example summarization + counter + arithmetic workflows

 Fully in-memory — no external DB required

<br>
🧠 Architecture

 Client
    │
    ▼
 FastAPI  --->  GraphEngine  --->  ToolRegistry
                        │
                        ▼
                Nodes mutate shared state

Core Concepts:

Graph = nodes + edges + entrypoint

Engine executes nodes sequentially

_next enables conditional branching / looping

State is mutated and passed through each node

<br>
⚙️ Installation

git clone https://github.com/Aditya5529/ai-agent-workflow-engine.git

cd ai-agent-workflow-engine

pip install -r requirements.txt

<br>
▶️ Run Server

python -m uvicorn app.main:app --reload


Open API docs:

http://127.0.0.1:8000/docs

<br>
🧱 Project Structure

app/

 ├── main.py    # FastAPI endpoints + WebSockets + visualization
 
 ├── engine.py   # Core workflow execution engine
 
 ├── tools.py   # All node functions (registered tools)
 
 ├── models.py   # Pydantic models, Graph, Run logs
 
requirements.txt

README.md

<br>
🚧 Create a Workflow Graph

POST /graph/create

    {
    "name": "summary_workflow",
  
       "nodes": [
  
          "split_text",
          "generate_summaries",
          "merge_summaries",
          "refine_summary"
    ],
    "edges": {
    "split_text": "generate_summaries",
    "generate_summaries": "merge_summaries",
    "merge_summaries": "refine_summary"
    },
    "entrypoint": "split_text"
    }

<br>
▶️ Run the Workflow

POST /graph/run

    {
    "graph_id": "<your-graph-id>",
    "initial_state": {
    "text": "some long text...",
    "chunk_size": 30,
    "per_chunk_summary_words": 10,
    "max_summary_words": 25
    }
    }

<br>
📈 Inspect Execution Logs

<br>

GET /graph/state/{run_id}

Includes:

final_state.summary

node-by-node logs

timestamps

execution duration

state snapshots

<br>
🛰 Real-time WebSocket Streaming

Connect:

ws://127.0.0.1:8000/ws/run/<graph_id>


Example streamed events:

    {"event":"workflow_started","entrypoint":"split_text"}

    {"event":"node_started","node":"split_text"}

    {"event":"node_completed","node":"split_text","duration_ms":0.82}

    {"event":"workflow_done","final_state":{ ... }}


Useful for dashboards, live monitoring, agent UX.

<br>
🖼 Graph Visualization
GET /graph/visualize/{graph_id}

Returns DOT format:

    digraph workflow {
    "split_text" -> "generate_summaries";
    "generate_summaries" -> "merge_summaries";
    "merge_summaries" -> "refine_summary";
    }


Visualize via GraphViz:

https://dreampuf.github.io/GraphvizOnline/

<br>
🧪 Example Workflows

✅ 1. Summarization Workflow (Main Demo)

Already shown above.

✅ 2. Looping Counter Workflow

    Create:
    {
    "name": "counter_loop",
    "nodes": ["counter"],
    "edges": {},
    "entrypoint": "counter"
    }

    Run:
    {
    "graph_id": "<id>",
    "initial_state": {
    "count": 0,
    "limit": 5
    }
    }

Behavior:

Node runs repeatedly

Each run increments count

Loop stops when count == limit

✅ 3. Arithmetic Workflow Example

Add tools:

    def add_node(state):
    state["value"] = state.get("value", 0) + state.get("add", 1)
    return state

    def square_node(state):
    v = state.get("value", 0)
    state["value"] = v * v
    return state

    tool_registry.register("add", add_node)
    tool_registry.register("square", square_node)

    Create Graph:
    {
    "name": "math_pipeline",
    "nodes": ["add", "square"],
    "edges": { "add": "square" },
    "entrypoint": "add"
    }

    Run:
    {
    "graph_id": "<id>",
    "initial_state": { "value": 2, "add": 5 }
    }


Result:

value = (2 + 5)^2 = 49

<br>
🧩 Architecture Details

Feature	Supported

Node registry	✔

DAG workflow	✔

Shared state	✔

Looping via _next	✔

Branching	✔

Execution log	✔

WebSocket streaming	✔

Graph visualization	✔

In-memory store	✔

Nodes are simple:

    def my_node(state):
    state["x"] = 1
    return state


Register easily:

tool_registry.register("my_node", my_node)

<br>
📎 Built for Tredence AI Engineering Case Study

This project demonstrates:

Workflow engine design

Stateful agent execution

Graph-based reasoning

Real-time event streaming

Logging & monitoring

Summarization pipeline example

Extensible tool registry

<br>

📫 Author

Aditya Niraj Gupta

AI Engineering | Workflow Engines | Python | FastAPI
