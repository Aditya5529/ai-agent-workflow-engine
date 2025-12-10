from typing import Callable, Dict, Any


class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register(self, name, func):
        self.tools[name] = func

    def get(self, name):
        if name not in self.tools:
            raise KeyError(f"Tool '{name}' not registered")
        return self.tools[name]

    def list_tools(self):
        return list(self.tools.keys())
    


tool_registry = ToolRegistry()
# ===== Option B: Summarization + Refinement nodes =====

def split_text_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Split input text into rough-sized chunks.
    Expects: state["text"], state.get("chunk_size", 300)
    """
    text: str = state.get("text", "")
    chunk_size: int = int(state.get("chunk_size", 300))

    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[i:i + chunk_size]))

    state["chunks"] = chunks
    return state


def generate_summaries_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create simple per-chunk summaries (first N words).
    """
    chunks = state.get("chunks", [])
    per_chunk_limit = int(state.get("per_chunk_summary_words", 50))

    summaries = []
    for chunk in chunks:
        words = chunk.split()
        summary = " ".join(words[:per_chunk_limit])
        summaries.append(summary)

    state["chunk_summaries"] = summaries
    return state


def merge_summaries_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge chunk summaries into a single draft summary.
    """
    summaries = state.get("chunk_summaries", [])
    state["summary"] = " ".join(summaries)
    return state


def refine_summary_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Trim summary until under max_words, used in a loop.
    """
    max_words = int(state.get("max_summary_words", 120))
    summary = state.get("summary", "")
    words = summary.split()

    if len(words) > max_words:
        # simple heuristic: keep only first max_words
        new_summary = " ".join(words[:max_words])
        state["summary"] = new_summary

    # Decide next step for the engine (loop or stop)
    if len(state["summary"].split()) > max_words:
        state["_next"] = "refine_summary"  # loop
    else:
        state["_next"] = None              # allow engine to stop

    # optional quality metric
    state["summary_word_count"] = len(state["summary"].split())
    return state


# Register tools on import
tool_registry.register("split_text", split_text_node)
tool_registry.register("generate_summaries", generate_summaries_node)
tool_registry.register("merge_summaries", merge_summaries_node)
tool_registry.register("refine_summary", refine_summary_node)
