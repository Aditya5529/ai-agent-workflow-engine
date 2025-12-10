AI Agent Workflow Engine

Minimal Agent Workflow Engine implemented using Python & FastAPI.
Workflows consist of nodes (Python functions) that operate over shared state and form directed graphs. Supports branching, looping, execution logging, and API-based workflow execution.

✨ Key Features

Node registry
Directed workflow graph
Shared mutable state
Branching & loop control (_next)
Execution logging
FastAPI endpoints
Example summarization workflow
No external DB required
Fully in-memory

🧠 Architecture

 Client ---> FastAPI ---> GraphEngine ---> ToolRegistry

Graph = nodes + edges + entrypoint
Engine executes nodes sequentially
_next enables branching/looping
State mutated at each node

Installation:
git clone https://github.com/Aditya5529/ai-agent-workflow-engine.git
cd ai-agent-workflow-engine
pip install -r requirements.txt

Run server:

python -m uvicorn app.main:app --reload

Open docs:

http://127.0.0.1:8000/docs


🚧 Create a graph

POST /graph/create

{
  "name": "summary",
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

▶️ Run the workflow

POST /graph/run

{
  "graph_id": "<your-id>",
  "initial_state": {
    "text": "some long text...",
    "chunk_size": 30,
    "per_chunk_summary_words": 10,
    "max_summary_words": 25
  }
}

📈 Inspect run

GET /graph/state/{run_id}

Example output contains:

final_state.summary
state evolution
execution log

🧩 Architecture Details
Feature	Supported
Node registry	✔
DAG workflow	✔
Shared state	✔
Looping	✔
Branching	✔
Execution log	✔

Nodes are simple Python functions:

def my_node(state):
    state["x"] = 1
    return state


Register easily:

tool_registry.register("my_node", my_node)

📌 Project Structure
app/
 ├── main.py
 ├── engine.py
 ├── tools.py
 ├── models.py
requirements.txt
README.md

🧱 Why this design?

Simple and extensible
Clear state management
Supports loops without complex orchestration
Easy to add new nodes
Demonstrates core agent principles

📎 Built for Tredence AI Engineering 
Case Study

Implements:
workflow engine
stateful agents
dynamic graphs
REST execution
example summarization pipeline

📫 Author

Aditya Niraj Gupta 
