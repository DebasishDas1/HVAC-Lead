from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class LeadUser(BaseModel):
    name: str
    email: str
    phone: str

class ChatRequest(BaseModel):
    sessionId: str
    user: LeadUser
    message: str

class ChatResponse(BaseModel):
    response: str
    qualified: bool

class LLMStructuredOutput(BaseModel):
    """The structured output returned by the LLM."""
    response: str = Field(description="The professional response to the user's message.")
    qualified: bool = Field(description="Whether the user is ready to book a service.")
    service_type: Optional[Literal["repair", "install", "maintenance"]] = Field(description="The type of HVAC service requested.")
    urgency: Optional[Literal["low", "medium", "high"]] = Field(description="The urgency of the service.")

class Lead(BaseModel):
    """The lead object to be saved to 'Google Sheets'."""
    name: str
    email: str
    phone: str
    transcript: str
    timestamp: str
    status: str = "Qualified"
    service_type: Optional[str]
    urgency: Optional[str]

class HVACState(BaseModel):
    """The state maintained in LangGraph."""
    session_id: str
    name: str
    email: str
    phone: str
    messages: List[dict] = []
    ai_response: Optional[str] = None
    is_qualified: bool = False
    service_type: Optional[str] = None
    urgency_level: Optional[str] = None
