"""
main.py — Real Estate Lead Scoring System (Optimized & Async)
============================================================
Entry point. Polls Google Sheets for new leads every N seconds
and runs them concurrently through the LangGraph scoring workflow.

Usage:
    python main.py
"""

import asyncio
import time

from config.settings import settings, logger
from services.sheets import SheetsClient
from schemas.lead import LeadData
from graph.workflow import build_workflow


async def process_lead(app, lead: LeadData) -> dict:
    """Run the full LangGraph workflow for a single lead asynchronously."""
    initial_state = {
        "lead":           lead,
        "lead_context":   "",
        "score_result":   None,
        "sheet_updated":  False,
        "notified":       False,
        "nurtured":       False,
        "error":          None,
        "retry_count":    0,
        "processing_log": [],
    }
    config = {"configurable": {"thread_id": f"lead-row-{lead.row_number}"}}
    # ainvoke is the async version of invoke
    return await app.ainvoke(initial_state, config=config)


async def main():
    # Validate all required env vars before starting
    settings.validate()

    logger.info("🚀 Real Estate Lead Scoring System — Starting (Async Optimized)")
    logger.info(f"   Model:    {settings.GROQ_MODEL}")
    logger.info(f"   Sheet:    {settings.GOOGLE_SHEET_NAME}")
    logger.info(f"   Interval: {settings.POLL_INTERVAL_SECONDS}s")

    app          = build_workflow()
    sheets       = SheetsClient()

    while True:
        try:
            logger.info("🔍 Polling for new unscored leads...")
            new_leads = await sheets.get_new_leads()

            if not new_leads:
                logger.info("   No new leads found.")
            else:
                logger.info(f"   Found {len(new_leads)} new lead(s) — processing concurrently...")
                
                # Process all new leads concurrently
                tasks = [process_lead(app, lead) for lead in new_leads]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        lead = new_leads[i]
                        logger.error(f"   ❌ Error processing lead '{lead.name}' (row {lead.row_number}): {result}")
                    else:
                        score = result.get("score_result")
                        if score:
                            logger.info(
                                f"   ✅ Done: {score.priority_level} "
                                f"({score.lead_score}/100)"
                            )

        except KeyboardInterrupt:
            logger.info("🛑 Shutting down gracefully.")
            break
        except Exception as e:
            logger.error(f"Polling loop error: {e}", exc_info=True)

        logger.info(f"💤 Sleeping {settings.POLL_INTERVAL_SECONDS}s...\n")
        await asyncio.sleep(settings.POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass