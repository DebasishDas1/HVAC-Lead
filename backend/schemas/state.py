from typing import Optional
from typing_extensions import TypedDict

from schemas.lead import LeadData
from schemas.score import LeadScore


class WorkflowState(TypedDict, total=False):
    """
    LangGraph state passed between all nodes.
    Use TypedDict (not Pydantic BaseModel) for LangGraph compatibility.
    """
    lead:           LeadData
    lead_context:   str
    score_result:   Optional[LeadScore]
    sheet_updated:  bool
    notified:       bool
    nurtured:       bool
    error:          Optional[str]
    retry_count:    int
    processing_log: list[str]