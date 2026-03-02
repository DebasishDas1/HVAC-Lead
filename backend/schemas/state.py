from typing import Optional, List, Annotated, Union
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage

from schemas.lead import LeadData
from schemas.score import LeadScore

class WorkflowState(TypedDict, total=False):
    """LangGraph state for lead scoring."""
    lead:           LeadData
    lead_context:   str
    score_result:   Optional[LeadScore]
    sheet_updated:  bool
    notified:       bool
    nurtured:       bool
    error:          Optional[str]
    retry_count:    int
    processing_log: list[str]

def merge_messages(left: List[BaseMessage], right: Union[List[BaseMessage], BaseMessage]) -> List[BaseMessage]:
    if isinstance(right, BaseMessage):
        return left + [right]
    return left + right

class ChatState(TypedDict):
    """LangGraph state for interactive chat."""
    messages: Annotated[List[BaseMessage], merge_messages]
    user_info: dict
    is_qualified: bool