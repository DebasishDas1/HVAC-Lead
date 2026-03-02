from pydantic import BaseModel
from typing import List, Optional

class UserInfo(BaseModel):
    name: str
    email: str
    phone: str

class ChatRequest(BaseModel):
    sessionId: str
    user: UserInfo
    message: str

class ChatResponse(BaseModel):
    response: str
    qualified: bool

class QualificationResult(BaseModel):
    reply: str
    problem: Optional[str] = None
    urgency: Optional[str] = None
    property_type: Optional[str] = None
