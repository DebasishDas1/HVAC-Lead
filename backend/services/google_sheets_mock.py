import asyncio
from models import Lead

async def save_lead_mock(lead: Lead):
    """Mock function to simulate saving to Google Sheets or CRM."""
    # Simulate API latency
    await asyncio.sleep(1)
    
    print(f"\n--- [SAVE LEAD MOCK] ---")
    print(f"Name: {lead.name}")
    print(f"Email: {lead.email}")
    print(f"Phone: {lead.phone}")
    print(f"Type: {lead.service_type}")
    print(f"Urgency: {lead.urgency}")
    print(f"Status: {lead.status}")
    print(f"Transcript Snippet: {lead.transcript[:100]}...")
    print(f"------------------------\n")
    return True
