import os
from typing import List
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from models import LLMStructuredOutput
from langchain_groq import ChatGroq

load_dotenv()

# Initialize LLM2 (Ollama)
llm2 = ChatOllama(
    model="qwen3:1.7b",
    temperature=0,
)

llm3 = ChatGroq(
    model="llama-3.1-8b-instant",
    groq_api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

# Bind structured output
structured_llm2 = llm2.with_structured_output(LLMStructuredOutput)
structured_llm3 = llm3.with_structured_output(LLMStructuredOutput)

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

    formatted_messages = [
        HumanMessage(content=SYSTEM_PROMPT.format(name=name))
    ]

    for msg in messages:
        if msg["role"] == "user":
            formatted_messages.append(HumanMessage(content=msg["content"]))
        else:
            formatted_messages.append(AIMessage(content=msg["content"]))

    try:
        return structured_llm3.invoke(formatted_messages)

    except Exception as e:
        print("⚠️ Gemini failed, falling back to Ollama:", e)
        return structured_llm3.invoke(formatted_messages)