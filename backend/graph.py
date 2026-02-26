import datetime
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, END
from models import HVACState, LLMStructuredOutput, Lead
from llm import get_llm_response

from services.google_sheets_mock import save_lead_mock

# Node functions
def chat_node(state: HVACState):
    """Handles the conversation with the LLM."""
    print(f"--- [CHATTING] ---")
    
    # Call LLM
    result: LLMStructuredOutput = get_llm_response(state.name, state.messages)
    
    # Update state
    state.ai_response = result.response
    state.is_qualified = result.qualified
    state.service_type = result.service_type
    state.urgency_level = result.urgency
    
    # Add AI response to transcript history
    state.messages.append({"role": "assistant", "content": result.response})
    
    return state

async def save_lead_node(state: HVACState):
    """Final node called when a lead is qualified."""
    print(f"--- [SAVING LEAD] ---")
    
    # Build transcript
    transcript = "\n".join([f"{m['role']}: {m['content']}" for m in state.messages])
    
    lead = Lead(
        name=state.name,
        email=state.email,
        phone=state.phone,
        transcript=transcript,
        timestamp=str(datetime.datetime.now()),
        service_type=state.service_type,
        urgency=state.urgency_level
    )
    
    # Call our mock service
    await save_lead_mock(lead)
    
    state.ai_response = f"{state.ai_response}\n\nOur team has received your request and will contact you shortly to schedule your service."
    
    return state

def qualification_router(state: HVACState):
    """Determines if we should save the lead or continue chatting."""
    if state.is_qualified:
        return "save_lead"
    return END

# Graph Construction
workflow = StateGraph(HVACState)

# Add Nodes
workflow.add_node("chat", chat_node)
workflow.add_node("save_lead", save_lead_node)

# Define conditional logic properly
workflow.add_conditional_edges(
    "chat",
    qualification_router,
    {
        "save_lead": "save_lead",
        END: END
    }
)

workflow.add_edge("save_lead", END)

# Initial entry
workflow.set_entry_point("chat")

# Compile
graph = workflow.compile()
