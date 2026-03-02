from datetime import datetime
from schemas.state import WorkflowState

async def prepare_lead_context(state: WorkflowState) -> WorkflowState:
    """
    Format raw LeadData into a readable context string for the LLM.
    """
    lead = state["lead"]

    context = (
        f"Lead Information:\n"
        f"{'─' * 40}\n"
        f"Full Name:          {lead.name}\n"
        f"Email Address:      {lead.email}\n"
        f"Phone Number:       {lead.phone}\n"
        f"Stated Budget:      {lead.budget}\n"
        f"Purchase Timeline:  {lead.timeline}\n"
        f"Property Type:      {lead.property_type}\n"
        f"Preferred Location: {lead.location}\n"
        f"Decision Authority: {lead.authority}\n"
        f"Financing Status:   {lead.financing}\n"
        f"Submitted At:       {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n"
    )

    log = state.get("processing_log", [])
    log.append(f"Context prepared for '{lead.name}' (row {lead.row_number})")

    return {
        **state,
        "lead_context":   context,
        "processing_log": log,
    }