from langgraph.store.memory import InMemoryStore
from config.settings import logger

# Initialize without namespace in constructor
lead_store = InMemoryStore()

# Consistent namespace tuple
CACHE_NAMESPACE = ("lead_cache",)

def lead_key(lead):
    return f"lead::{lead.email.lower().strip()}"

async def cache_lead(lead):
    """Cache lead before processing."""
    # aput(namespace, key, value)
    await lead_store.aput(CACHE_NAMESPACE, lead_key(lead), lead.dict() if hasattr(lead, "dict") else lead)
    logger.info(f"✅ Cached lead: {lead.email}")

async def get_cached_lead(lead):
    """Get cached lead."""
    # aget(namespace, key)
    item = await lead_store.aget(CACHE_NAMESPACE, lead_key(lead))
    return item.value if item else None

async def delete_cached_lead(lead):
    """Delete cached lead."""
    # adelete(namespace, key)
    await lead_store.adelete(CACHE_NAMESPACE, lead_key(lead))
    logger.info(f"✅ Deleted cached lead: {lead.email}")