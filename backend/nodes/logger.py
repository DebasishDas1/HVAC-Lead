from config.settings import logger
from schemas.state import WorkflowState

async def log_completion(state: WorkflowState) -> WorkflowState:
    """Node 5 — Log the final processing summary."""
    lead  = state["lead"]
    score = state["score_result"]

    logger.info(
        f"✅ DONE | '{lead.name}' (row {lead.row_number}) | "
        f"Score: {score.lead_score}/100 | {score.priority_level} | "
        f"Sheet: {'✓' if state.get('sheet_updated') else '✗'} | "
        f"Nurtured: {'✓' if state.get('nurtured') else '–'}"
    )

    for entry in state.get("processing_log", []):
        logger.debug(f"  • {entry}")

    return state