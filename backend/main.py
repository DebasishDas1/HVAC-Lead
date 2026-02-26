import os
import uuid
from typing import Dict
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import ChatRequest, ChatResponse, HVACState
from graph import graph

app = FastAPI(title="HVAC Lead Qualification API")

# CORS setup for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store (In production, use Redis or a DB)
sessions: Dict[str, dict] = {}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    session_id = request.sessionId
    
    # Initialize or retrieve session state
    if session_id not in sessions:
        sessions[session_id] = {
            "messages": [],
            "is_qualified": False
        }
    
    session_data = sessions[session_id]
    
    # If the user is already qualified, we don't need to process further
    # but we might want to let them keep talking or just return a static message.
    if session_data["is_qualified"]:
        return ChatResponse(
            response="Our team will contact you shortly to schedule your service.",
            qualified=True
        )

    # Append user message
    session_data["messages"].append({"role": "user", "content": request.message})
    
    # Prepare state for LangGraph
    # We use a dict for the graph input as it's often more flexible with LangGraph's TypedDict/State
    initial_state = {
        "session_id": session_id,
        "name": request.user.name,
        "email": request.user.email,
        "phone": request.user.phone,
        "messages": session_data["messages"],
        "ai_response": None,
        "is_qualified": False,
        "service_type": None,
        "urgency_level": None
    }
    
    try:
        # Run the graph
        final_output = graph.invoke(initial_state)
        
        # Update session data
        sessions[session_id]["messages"] = final_output["messages"]
        sessions[session_id]["is_qualified"] = final_output["is_qualified"]
        
        return ChatResponse(
            response=final_output["ai_response"],
            qualified=final_output["is_qualified"]
        )
        
    except Exception as e:
        print(f"Error processing chat: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
