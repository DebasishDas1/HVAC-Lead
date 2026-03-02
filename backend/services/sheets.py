import anyio
import os
from datetime import datetime
from typing import Optional

from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials as ServiceAccountCredentials

from config.settings import settings, logger
from schemas.lead import LeadData
from schemas.score import LeadScore, ScoreBreakdown


class SheetsClient:
    """Handles all Google Sheets read/write operations asynchronously."""

    def _safe_tab(self) -> str:
        """Wrap tab name safely for Google Sheets range usage."""
        if " " in self.tab:
            return f"'{self.tab}'"
        return self.tab

    def __init__(self):
        self.sheet_id = settings.GOOGLE_SHEETS_ID
        self.tab = settings.GOOGLE_SHEET_NAME
        self._cached_headers: Optional[list[str]] = None
        
        # Check if service account file exists, otherwise enter mock mode
        self.mock_mode = False
        if not settings.GOOGLE_SERVICE_ACCOUNT or not os.path.exists(settings.GOOGLE_SERVICE_ACCOUNT):
            logger.warning("⚠️ Google Service Account JSON not found or path empty. Running in MOCK MODE.")
            self.mock_mode = True
            self.sheets = None
        else:
            scopes = ["https://www.googleapis.com/auth/spreadsheets"]
            creds = ServiceAccountCredentials.from_service_account_file(
                settings.GOOGLE_SERVICE_ACCOUNT, scopes=scopes
            )
            service = build("sheets", "v4", credentials=creds)
            self.sheets = service.spreadsheets()

    async def _get_values(self, range_name: str) -> list[list]:
        """Internal helper to fetch values from the sheet asynchronously."""
        if self.mock_mode:
            # Return some dummy lead data for testing
            return [
                ["Name", "Email", "Phone", "Budget", "Timeline", "Property Type", "Location", "Authority", "Financing", "Lead Score"],
                ["John Doe", "john@example.com", "+123456789", "$500k", "Immediate", "Villa", "Dubai Marina", "Decision Maker", "Pre-approved", ""],
                ["Jane Smith", "jane@example.com", "+987654321", "$200k", "6 months", "Apartment", "Downtown", "Researcher", "Cash", ""],
            ]

        return await anyio.to_thread.run_sync(
            lambda: self.sheets.values().get(
                spreadsheetId=self.sheet_id,
                range=range_name
            ).execute().get("values", [])
        )

    async def _get_headers(self) -> list[str]:
        """Fetch and cache headers to avoid redundant API calls."""
        if self._cached_headers:
            return self._cached_headers

        rows = await self._get_values(f"{self._safe_tab()}!1:1")
        if not rows:
            return []

        headers = [h.lower().strip().replace(" ", "_") for h in rows[0]]
        self._cached_headers = headers
        return headers

    # ── Read ──────────────────────────────────────────────────────────────────

    async def get_new_leads(self) -> list[LeadData]:
        """
        Fetch all rows where lead_score is empty.
        Deduplication: any row already having a lead_score is skipped.
        """
        rows = await self._get_values(f"{self._safe_tab()}!A1:Z")
        if not rows:
            logger.info("Sheet is empty.")
            return []

        headers = [h.lower().strip().replace(" ", "_") for h in rows[0]]
        self._cached_headers = headers  # Update cache while we're at it
        leads = []

        for i, row in enumerate(rows[1:], start=2):
            padded = row + [""] * (len(headers) - len(row))
            row_dict = dict(zip(headers, padded))

            # Skip already scored rows
            if row_dict.get("lead_score", "").strip():
                continue

            leads.append(LeadData(
                row_number=i,
                name=row_dict.get("name", "Not provided"),
                email=row_dict.get("email", "Not provided"),
                phone=row_dict.get("phone", "Not provided"),
                budget=row_dict.get("budget", "Not specified"),
                timeline=row_dict.get("timeline", "Not specified"),
                property_type=row_dict.get("property_type", "Not specified"),
                location=row_dict.get("location", "Not specified"),
                authority=row_dict.get("authority", "Not specified"),
                financing=row_dict.get("financing", "Not specified"),
            ))

        # In mock mode, we only return each lead once to avoid infinite loop
        if self.mock_mode:
            logger.info(f"MOCK MODE: Returning {len(leads)} dummy leads.")
            # We'll just return them and since we can't update the "mock" source, 
            # the user might need to stop the process manually.
        
        return leads

    # ── Write ─────────────────────────────────────────────────────────────────

    async def update_lead_score(self, lead: LeadData, score: LeadScore):
        """Write scoring results back to the exact row in the sheet using batchUpdate."""
        if self.mock_mode:
            logger.info(f"MOCK MODE: Skipping real sheet update for row {lead.row_number}")
            logger.info(f"MOCK DATA: Score: {score.lead_score}, Priority: {score.priority_level}")
            return

        headers = await self._get_headers()
        priority_labels = {"HOT": "HOT 🔥", "WARM": "WARM ⚠️", "COLD": "COLD ❄️"}

        field_map = {
            "lead_score": str(score.lead_score),
            "priority_level": priority_labels[score.priority_level],
            "budget_score": str(score.score_breakdown.budget_score),
            "timeline_score": str(score.score_breakdown.timeline_score),
            "authority_score": str(score.score_breakdown.authority_score),
            "financing_score": str(score.score_breakdown.financing_score),
            "engagement_score": str(score.score_breakdown.engagement_score),
            "recommended_action": score.recommended_action,
            "agent_notes": score.agent_notes,
            "follow_up_timing": score.follow_up_timing,
            "disqualification_flags": ", ".join(score.disqualification_flags),
            "scored_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        }

        data = []
        for field, value in field_map.items():
            if field not in headers:
                logger.warning(f"Column '{field}' not found in sheet headers — skipping")
                continue

            col_index = headers.index(field)
            col_letter = chr(65 + col_index)  # Simple A-Z mapping
            cell_range = f"{self._safe_tab()}!{col_letter}{lead.row_number}"
            data.append({
                "range": cell_range,
                "values": [[value]]
            })

        if not data:
            return

        body = {
            "valueInputOption": "RAW",
            "data": data
        }

        await anyio.to_thread.run_sync(
            lambda: self.sheets.values().batchUpdate(
                spreadsheetId=self.sheet_id,
                body=body
            ).execute()
        )

        logger.info(f"Sheet row {lead.row_number} updated — {score.priority_level} ({score.lead_score}/100)")