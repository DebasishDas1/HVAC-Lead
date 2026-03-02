import json
from langchain_groq import ChatGroq
from langchain_core.output_parsers import PydanticOutputParser

from config.settings import settings, logger
from schemas.score import LeadScore, ScoreBreakdown
from schemas.state import WorkflowState
from graph.prompts import scoring_prompt
from store.lead_cache import lead_store, lead_key

MAX_RETRIES = 2

# ── LLM Setup (Groq) ──────────────────────────────────────────────────────────
llm = ChatGroq(
    model=settings.GROQ_MODEL,
    groq_api_key=settings.GROQ_API_KEY,
    temperature=0,
    max_tokens=settings.MAX_TOKEN
)

# Use with_structured_output for better reliability with Groq
scoring_chain = scoring_prompt | llm.with_structured_output(LeadScore)

ALLOWED_KEYS = (
    "budget",
    "timeline",
    "authority",
    "financing",
    "location",
    "property",
    "urgency"
)

def compress_context(ctx: str) -> str:
    lines = ctx.lower().split("\n")
    return "\n".join(
        l for l in lines if any(k in l for k in ALLOWED_KEYS)
    )[:400]

# ── Fallback score used after max retries ─────────────────────────────────────
def _fallback_score(error_msg: str) -> LeadScore:
    return LeadScore(
        lead_score          = 25,
        priority_level      = "COLD",
        score_breakdown     = ScoreBreakdown(
            budget_score=5, timeline_score=5,
            authority_score=5, financing_score=5, engagement_score=5
        ),
        recommended_action  = "Manual review required — AI scoring failed",
        agent_notes         = f"Scoring error: {error_msg}. Please score manually.",
        follow_up_timing    = "Review within 24 hours",
        disqualification_flags = ["AI scoring failed — manual review needed"],
    )

# ── Node ──────────────────────────────────────────────────────────────────────
async def score_lead(state: WorkflowState) -> WorkflowState:
    lead = state["lead"]
    key = lead_key(lead)
    namespace = ("lead_cache",)
    log = state.get("processing_log", [])

    item = await lead_store.aget(namespace, key)
    if item:
        cached = item.value
        logger.info(f"⚡ Cache hit for {lead.email}")
        return {**state, "score_result": cached, "error": None}

    context = compress_context(state["lead_context"])

    for attempt in range(2):  # internal retry
        try:
            result = await scoring_chain.ainvoke({
                "lead_context": context
            })

            log.append(f"Scored: {result.lead_score}/100 → {result.priority_level}")

            # cache only real results
            await lead_store.aput(namespace, key, result.dict() if hasattr(result, "dict") else result)

            return {
                **state,
                "score_result": result,
                "error": None,
                "processing_log": log,
            }

        except Exception as e:
            error_msg = str(e)
            logger.warning(f"Scoring retry {attempt+1} failed: {error_msg}")

    # fallback only after retries
    fallback = _fallback_score(error_msg)
    log.append("Fallback score applied")

    return {
        **state,
        "score_result": fallback,
        "error": None,
        "processing_log": log,
    }