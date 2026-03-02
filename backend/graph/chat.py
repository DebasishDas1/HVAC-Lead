from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import SystemMessage
from langchain_groq import ChatGroq

from config.settings import settings
from schemas.state import ChatState

# ── Chat Setup ─────────────────────────────────────────────────────────────

llm = ChatGroq(
    model        = settings.GROQ_MODEL,
    groq_api_key = settings.GROQ_API_KEY,
    temperature  = 0.2,
)

async def chat_node(state: ChatState):
    """The qualifying assistant node."""
    messages = state["messages"]
    user_info = state["user_info"]
    
    system_msg = SystemMessage(content=(
        f"You are a helpful HVAC Lead Qualification assistant. Name: {user_info.get('name')}. "
        "Your goal is to qualify the lead by understanding their HVAC needs. "
        "Ask about the issue, urgency, and if they represent a home or business. "
        "Be friendly and concise. If the lead is clear about their need and urgency, "
        "conclude the session by saying they are qualified and someone will call them."
    ))
    
    response = await llm.ainvoke([system_msg] + messages)
    
    # Simple heuristic for qualification
    is_qualified = "qualified" in response.content.lower()
    
    return {"messages": [response], "is_qualified": is_qualified}

def build_chat_workflow():
    builder = StateGraph(ChatState)
    builder.add_node("chat", chat_node)
    builder.set_entry_point("chat")
    builder.add_edge("chat", END)
    return builder.compile(checkpointer=MemorySaver())
