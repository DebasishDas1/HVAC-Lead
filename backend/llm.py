import os
from typing import List
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from .models import LLMStructuredOutput

load_dotenv()

# Initialize the LLM
# You can use "gpt-4o" or a faster model like "gpt-4o-mini"
llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0
)

# Bind structured output
structured_llm = llm.with_structured_output(LLMStructuredOutput)

SYSTEM_PROMPT = """
You are a professional, empathetic HVAC service coordinator. 
Your goal is to answer user questions about HVAC repair, installation, and maintenance, 
and qualify them for a service booking.

Conversation Guidelines:
1. Greet the user warmly by their name ({name}).
2. Provide technical but accessible advice for HVAC problems.
3. Be empathetic to their situation (e.g., if their AC is broken in summer).
4. Ask clarifying questions if the problem is vague.
5. Identify when the user is ready to book an appointment.

Qualification Criteria:
- User explicitly asks for a technician/visit.
- User agrees to a suggested service call.
- User provides enough detail about a problem that requires professional attention.

When the user is qualified:
- Set qualified: true
- Identify service_type (repair/install/maintenance)
- Determine urgency (low/medium/high)

Otherwise, keep qualified: false.
"""

def get_llm_response(name: str, messages: List[dict]) -> LLMStructuredOutput:
    """Sends messages to LLM and returns structured response."""
    
    # Format messages for LangChain
    formatted_messages = [SystemMessage(content=SYSTEM_PROMPT.format(name=name))]
    
    for msg in messages:
        if msg["role"] == "user":
            formatted_messages.append(HumanMessage(content=msg["content"]))
        else:
            formatted_messages.append(AIMessage(content=msg["content"]))
            
    return structured_llm.invoke(formatted_messages)
