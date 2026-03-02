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
from schemas.lead import LeadData

# ── Initialization ──────────────────────────────────────────────────────────

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

# ── FastAPI App Setup ───────────────────────────────────────────────────────

app = FastAPI(
    title="HVAC Lead AI",
    description="FastAPI service for lead scoring and interactive qualification.",
    version="1.3.1",
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
    
    qualified = final_state.get("is_qualified", False)
    
    if qualified:
        # Finalize lead scoring and update sheet in background
        asyncio.create_task(finalize_chat_lead(req, final_state["messages"]))
        
    return ChatResponse(
        response=last_message.content,
        qualified=qualified
    )

async def finalize_chat_lead(req: ChatRequest, messages: list):
    """Scores the lead based on chat history and saves to relevant tab with exponential backoff."""
    MAX_ATTEMPTS = 5
    base_delay = 60  # Start with 60s delay if rate limited
    
    for attempt in range(MAX_ATTEMPTS):
        try:
            from nodes.scorer import scoring_chain
            from services.sheets import SheetsClient
            
            # 1. Prepare context for scoring
            history = "\n".join([f"{m.type}: {m.content}" for m in messages])
            context = (
                f"User Profile:\n"
                f"Name: {req.user.name}\n"
                f"Email: {req.user.email}\n"
                f"Phone: {req.user.phone}\n\n"
                f"Chat History:\n{history}"
            )
            
            # 2. Score lead
            logger.info(f"Finalizing scoring for chat lead: {req.user.name} (Attempt {attempt + 1})")
            scoring_result = await scoring_chain.ainvoke({"lead_context": context})
            
            # 3. Save to Excel (Google Sheets)
            sheets = SheetsClient()
            tab_mapping = {
                "HOT": "HOT Leads",
                "WARM": "WARM Leads",
                "COLD": "COLD Leads"
            }
            target_tab = tab_mapping.get(scoring_result.priority_level, "COLD Leads")
            
            # Prepare LeadData for appending
            lead = LeadData(
                row_number=0, # Appending
                name=req.user.name,
                email=req.user.email,
                phone=req.user.phone
            )
            
            await sheets.append_lead_to_tab(lead, scoring_result, target_tab)
            logger.info(f"✅ Chat lead {req.user.name} finalized and saved to {target_tab}")
            return  # Success!

        except Exception as e:
            error_msg = str(e)
            is_rate_limit = "rate_limit_exceeded" in error_msg.lower() or "429" in error_msg
            
            if is_rate_limit and attempt < MAX_ATTEMPTS - 1:
                delay = base_delay * (2 ** attempt)
                logger.warning(f"⚠️ Groq Rate Limit hit for {req.user.name}. Retrying in {delay}s... (Attempt {attempt + 1}/{MAX_ATTEMPTS})")
                await asyncio.sleep(delay)
            else:
                logger.error(f"❌ Error finalizing chat lead {req.user.name} after {attempt + 1} attempts: {e}", exc_info=True)
                break

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting HVAC Lead AI Server...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)