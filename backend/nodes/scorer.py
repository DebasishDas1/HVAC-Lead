import json
from langchain_groq import ChatGroq
from langchain_core.output_parsers import PydanticOutputParser

from config.settings import settings, logger
from schemas.score import LeadScore, ScoreBreakdown
from schemas.state import WorkflowState
from graph.prompts import scoring_prompt

# ── LLM Setup (Groq) ──────────────────────────────────────────────────────────
llm = ChatGroq(
    model        = settings.GROQ_MODEL,
    groq_api_key = settings.GROQ_API_KEY,
    temperature  = 0,
)

output_parser = PydanticOutputParser(pydantic_object=LeadScore)

# Chain: prompt → Groq → Pydantic validation
scoring_chain = scoring_prompt | llm | output_parser

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
    """
    Node 2 — Call Groq LLM to score the lead.
    Retries up to 2 times on failure, then applies a safe fallback.
    """
    log         = state.get("processing_log", [])
    retry_count = state.get("retry_count", 0)
    MAX_RETRIES = 2

    try:
        result = await scoring_chain.ainvoke({"lead_context": state["lead_context"]})
        log.append(f"Scored: {result.lead_score}/100 → {result.priority_level}")
        return {
            **state,
            "score_result":   result,
            "error":          None,
            "processing_log": log,
        }

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Scoring attempt {retry_count + 1} failed: {error_msg}")

        if retry_count < MAX_RETRIES:
            log.append(f"Retry {retry_count + 1}/{MAX_RETRIES}: {error_msg}")
            return {
                **state,
                "retry_count":    retry_count + 1,
                "error":          error_msg,
                "processing_log": log,
            }
        else:
            # Max retries exhausted — use fallback
            fallback = _fallback_score(error_msg)
            log.append(f"Fallback score applied after {MAX_RETRIES} retries")
            logger.warning(f"Using fallback score for row {state['lead'].row_number}")
            return {
                **state,
                "score_result":   fallback,
                "error":          None,
                "processing_log": log,
            }