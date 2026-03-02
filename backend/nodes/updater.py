from config.settings import logger
from services.sheets import SheetsClient
from schemas.state import WorkflowState

_sheets = None

def get_sheets_client():
    global _sheets
    if _sheets is None:
        _sheets = SheetsClient()
    return _sheets

async def update_sheet(state: WorkflowState) -> WorkflowState:
    """
    Node 3 — Write scoring results back to the Google Sheet row.
    """
    sheets = get_sheets_client()
    log = state.get("processing_log", [])

    try:
        await sheets.update_lead_score(state["lead"], state["score_result"])
        log.append("Sheet updated successfully")
        return {**state, "sheet_updated": True, "processing_log": log}

    except Exception as e:
        logger.error(f"Sheet update failed: {e}")
        log.append(f"Sheet update FAILED: {e}")
        return {
            **state,
            "sheet_updated":  False,
            "error":          f"Sheet update failed: {str(e)}",
            "processing_log": log,
        }