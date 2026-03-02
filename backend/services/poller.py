import asyncio
from config.settings import settings, logger
from services.sheets import SheetsClient
from schemas.lead import LeadData
from graph.workflow import build_workflow

async def process_lead(app_workflow, lead: LeadData, semaphore: asyncio.Semaphore) -> dict:
    """Run the full LangGraph workflow for a single lead asynchronously."""
    async with semaphore:
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
        return await app_workflow.ainvoke(initial_state, config=config)

async def lead_polling_loop():
    """Background loop that polls Google Sheets for new leads."""
    logger.info("🧵 Background lead polling loop started.")
    
    app_workflow = build_workflow()
    sheets       = SheetsClient()
    semaphore    = asyncio.Semaphore(settings.MAX_CONCURRENT_LEADS)

    while True:
        try:
            logger.info("🔍 Polling Google Sheets for unscored leads...")
            new_leads = await sheets.get_new_leads()

            if not new_leads:
                logger.info("   No new leads found.")
            else:
                logger.info(f"   Found {len(new_leads)} new lead(s) — processing concurrently...")
                tasks = [process_lead(app_workflow, lead, semaphore) for lead in new_leads]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                success_count = 0
                error_count = 0
                for i, result in enumerate(results):
                    lead = new_leads[i]
                    if isinstance(result, Exception):
                        logger.error(f"   ❌ Error processing lead '{lead.name}' (row {lead.row_number}): {result}")
                        error_count += 1
                    else:
                        score = result.get("score_result")
                        if score:
                            logger.info(
                                f"   ✅ Done: {score.priority_level} "
                                f"({score.lead_score}/100) | '{lead.name}' (row {lead.row_number})"
                            )
                            success_count += 1
                logger.info(f"   Batch complete: {success_count} success, {error_count} failed.")

        except Exception as e:
            logger.error(f"Polling loop error: {e}", exc_info=True)

        await asyncio.sleep(settings.POLL_INTERVAL_SECONDS)
