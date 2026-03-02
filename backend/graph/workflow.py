from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from schemas.state import WorkflowState
from nodes.prepare import prepare_lead_context
from nodes.scorer import score_lead
from nodes.updater import update_sheet
from nodes.nurture import nurture_cold_lead
from nodes.logger import log_completion


# =============================================================================
# ROUTING FUNCTIONS
# =============================================================================

def should_retry(state: WorkflowState) -> str:
    """After score_lead: retry if there's an error and retries remain."""
    if state.get("error") and state.get("retry_count", 0) < 2:
        return "retry"
    return "continue"


def route_by_priority(state: WorkflowState) -> str:
    """After update_sheet: branch based on lead priority level."""
    level = state["score_result"].priority_level
    return {"HOT": "hot", "WARM": "warm", "COLD": "cold"}[level]


# =============================================================================
# GRAPH ASSEMBLY
# =============================================================================

def build_workflow():
    """
    Compile and return the LangGraph StateGraph.
    Works with both synchronous and asynchronous nodes.
    """
    graph = StateGraph(WorkflowState)

    # ── Register nodes ────────────────────────────────────────────────────────
    graph.add_node("prepare_context", prepare_lead_context)
    graph.add_node("score_lead",      score_lead)
    graph.add_node("update_sheet",    update_sheet)
    graph.add_node("nurture_cold",    nurture_cold_lead)
    graph.add_node("log_completion",  log_completion)

    # ── Entry point ───────────────────────────────────────────────────────────
    graph.set_entry_point("prepare_context")

    # ── Edges ─────────────────────────────────────────────────────────────────
    graph.add_edge("prepare_context", "score_lead")

    # Retry loop: score_lead → (retry → score_lead) or (continue → update_sheet)
    graph.add_conditional_edges(
        "score_lead",
        should_retry,
        {"retry": "score_lead", "continue": "update_sheet"},
    )

    # Priority routing: update_sheet → HOT | WARM | COLD branch
    # HOT and WARM now go straight to log_completion
    graph.add_conditional_edges(
        "update_sheet",
        route_by_priority,
        {"hot": "log_completion", "warm": "log_completion", "cold": "nurture_cold"},
    )

    # COLD branch converges at log_completion
    graph.add_edge("nurture_cold", "log_completion")
    graph.add_edge("log_completion", END)

    return graph.compile(checkpointer=MemorySaver())