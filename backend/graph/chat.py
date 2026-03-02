from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import SystemMessage, AIMessage
from langchain_groq import ChatGroq

from config.settings import settings
from schemas.state import ChatState
from schemas.chat import QualificationResult
from store.lead_cache import lead_store

# ── Chat Setup ─────────────────────────────────────────────────────────────

llm = ChatGroq(
    model=settings.GROQ_MODEL,
    groq_api_key=settings.GROQ_API_KEY,
    temperature=0.4,
    max_tokens=settings.MAX_TOKEN,
    max_retries=3
)

async def chat_node(state: ChatState):
    messages = state["messages"]
    user_info = state["user_info"]

    session_id = user_info.get("email") or user_info.get("phone")
    namespace = ("lead_cache",)

    # Use namespace tuple in aget
    item = await lead_store.aget(namespace, session_id)
    memory = item.value if item else {}

    SYSTEM_PROMPT = """
    You are a friendly HVAC Lead Qualification assistant.
    Your goal is to qualify the lead by understanding their HVAC needs.
    Ask about the issue, urgency, and if they represent a home or business.
    Be concise and professional.

    If the lead is clear about their need and urgency, conclude the session by saying:
    "Qualified. Someone will contact you shortly."

    Return your response in JSON format with the following fields:
    - reply: The message to send to the user.
    - problem: The HVAC problem (e.g., "AC not cooling", "furnace broken").
    - urgency: Urgency level (e.g., "urgent", "not urgent").
    - property_type: "home" or "business".
    """

    response = await llm.with_structured_output(QualificationResult).ainvoke(
        [SYSTEM_PROMPT] + messages
    )

    # 🔄 Merge new info into memory
    memory.update({
        "problem": response.problem or memory.get("problem"),
        "urgency": response.urgency or memory.get("urgency"),
        "property_type": response.property_type or memory.get("property_type"),
    })

    # 🎯 Qualification Logic (deterministic)
    is_qualified = all([
        memory.get("problem"),
        memory.get("urgency"),
        memory.get("property_type"),
    ])

    memory["is_qualified"] = is_qualified

    # 💾 Persist into LangGraph Store
    await lead_store.aput(namespace, session_id, memory)

    return {
        "messages": [AIMessage(content=response.reply)],
        "is_qualified": is_qualified,
        "lead_memory": memory
    }


def build_chat_workflow():
    builder = StateGraph(ChatState)

    builder.add_node("chat", chat_node)

    builder.set_entry_point("chat")
    builder.add_edge("chat", END)

    return builder.compile(
        checkpointer=MemorySaver(),
        store=lead_store
    )