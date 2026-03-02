"""
main.py — Real Estate Lead Scoring System (Optimized & Async)
============================================================
FastAPI Entry Point. Orchestrates background workers and chat API.
"""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage

from config.settings import settings, logger
from services.poller import lead_polling_loop
from graph.chat import build_chat_workflow
from schemas.chat import ChatRequest, ChatResponse

chat_app = build_chat_workflow()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Run polling loop in background
    settings.validate()
    polling_task = asyncio.create_task(lead_polling_loop())
    yield
    # Shutdown: Cancel background task
    polling_task.cancel()
    try:
        await polling_task
    except asyncio.CancelledError:
        logger.info("🧵 Background lead polling loop stopped.")

app = FastAPI(
    title="HVAC Lead AI",
    description="FastAPI service for lead scoring and interactive qualification.",
    version="1.2.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Endpoints ───────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/evac_lead_chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """Handle interactive chat with the lead."""
    config = {"configurable": {"thread_id": req.sessionId}}
    
    # Run the chat workflow
    input_state = {
        "messages": [HumanMessage(content=req.message)],
        "user_info": req.user.dict(),
        "is_qualified": False
    }
    
    final_state = await chat_app.ainvoke(input_state, config=config)
    last_message = final_state["messages"][-1]
    
    return ChatResponse(
        response=last_message.content,
        qualified=final_state.get("is_qualified", False)
    )

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting HVAC Lead AI Server...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)