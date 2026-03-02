import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from services.sheets import SheetsClient
from schemas.lead import LeadData
from schemas.score import LeadScore, ScoreBreakdown

@pytest.mark.asyncio
async def test_sheets_client_headers_caching():
    client = SheetsClient()
    client.sheets = MagicMock()
    
    mock_values = MagicMock()
    mock_values.get.return_value.execute.return_value = {"values": [["Name", "Email", "Lead Score"]]}
    client.sheets.values.return_value = mock_values
    
    # First call should fetch from API
    headers1 = await client._get_headers()
    assert headers1 == ["name", "email", "lead_score"]
    assert mock_values.get.call_count == 1
    
    # Second call should use cache
    headers2 = await client._get_headers()
    assert headers2 == ["name", "email", "lead_score"]
    assert mock_values.get.call_count == 1

@pytest.mark.asyncio
async def test_sheets_client_batch_update():
    client = SheetsClient()
    client.sheets = MagicMock()
    client._cached_headers = ["name", "email", "lead_score", "priority_level", "budget_score", "timeline_score", "authority_score", "financing_score", "engagement_score", "recommended_action", "agent_notes", "follow_up_timing", "disqualification_flags", "scored_at"]
    
    mock_values = MagicMock()
    client.sheets.values.return_value = mock_values
    
    lead = LeadData(row_number=2, name="Test")
    score = LeadScore(
        lead_score=85,
        priority_level="HOT",
        score_breakdown=ScoreBreakdown(budget_score=30, timeline_score=30, authority_score=10, financing_score=10, engagement_score=5),
        recommended_action="Call now",
        agent_notes="Strong lead",
        follow_up_timing="Immediately"
    )
    
    await client.update_lead_score(lead, score)
    
    assert mock_values.batchUpdate.call_count == 1
    call_args = mock_values.batchUpdate.call_args[1]
    body = call_args["body"]
    assert body["valueInputOption"] == "RAW"
    assert len(body["data"]) > 1
    assert any(d["range"] == f"{client.tab}!C2" for d in body["data"]) # lead_score col 3 -> C
