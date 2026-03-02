import asyncio
from config.settings import logger, settings
from services.sheets import sheets_service
from graph.workflow import workflow
from schemas.state import WorkflowState

async def process_leads():
    """Main polling loop to process new leads."""
    logger.info("Starting Lead Scoring Backend...")
    
    while True:
        try:
            # 1. Fetch new leads
            new_leads = await sheets_service.get_new_leads()
            
            if not new_leads:
                logger.info(f"No new leads found. Waiting {settings.POLL_INTERVAL_SECONDS}s...")
            else:
                logger.info(f"Found {len(new_leads)} new leads. Processing...")
                
                for lead in new_leads:
                    # 2. Initialize State
                    initial_state: WorkflowState = {
                        "lead": lead,
                        "formatted_context": None,
                        "score": None,
                        "notifications_sent": [],
                        "nurture_sent": False,
                        "status": "started",
                        "error": None
                    }
                    
                    # 3. Run Workflow
                    logger.info(f"Running workflow for lead: {lead.id}")
                    await workflow.ainvoke(initial_state)
            
            # 4. Wait for next poll
            await asyncio.sleep(settings.POLL_INTERVAL_SECONDS)
            
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            await asyncio.sleep(10)  # Wait a bit before retrying on error

if __name__ == "__main__":
    try:
        asyncio.run(process_leads())
    except KeyboardInterrupt:
        logger.info("Backend stopped by user.")
