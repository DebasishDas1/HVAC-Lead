import anyio
import os
import re
from datetime import datetime
from typing import Optional

from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials as ServiceAccountCredentials

from config.settings import settings, logger
from schemas.lead import LeadData
from schemas.score import LeadScore


class SheetsClient:
    """Handles all Google Sheets read/write operations asynchronously."""

    def _safe_tab(self) -> str:
        """Wrap tab name safely for Google Sheets range usage."""
        # Quote if it contains spaces or special characters
        if re.search(r"[^a-zA-Z0-9]", self.tab):
            return f"'{self.tab}'"
        return self.tab

    def __init__(self):
        self.sheet_id = settings.GOOGLE_SHEETS_ID
        self.tab = settings.GOOGLE_SHEET_NAME
        self._cached_headers: Optional[list[str]] = None
        
        # Check if service account file exists, otherwise enter mock mode
        self.mock_mode = False
        if not settings.GOOGLE_SERVICE_ACCOUNT or not os.path.exists(settings.GOOGLE_SERVICE_ACCOUNT):
            logger.warning(f"⚠️ Google Service Account JSON not found at '{settings.GOOGLE_SERVICE_ACCOUNT}'. Running in MOCK MODE.")
            self.mock_mode = True
            self.sheets = None
        else:
            try:
                scopes = ["https://www.googleapis.com/auth/spreadsheets"]
                creds = ServiceAccountCredentials.from_service_account_file(
                    settings.GOOGLE_SERVICE_ACCOUNT, scopes=scopes
                )
                service = build("sheets", "v4", credentials=creds)
                self.sheets = service.spreadsheets()
                logger.info("✅ Google Sheets API client initialized.")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Google Sheets API: {e}")
                self.mock_mode = True
                self.sheets = None

    async def _get_values(self, range_name: str) -> list[list]:
        """Internal helper to fetch values from the sheet asynchronously with retry logic."""
        if self.mock_mode:
            return [
                ["Name", "Email", "Phone", "Budget", "Timeline", "Property Type", "Location", "Authority", "Financing", "Lead Score"],
                ["John Doe", "john@example.com", "+123456789", "$500k", "Immediate", "Villa", "Dubai Marina", "Decision Maker", "Pre-approved", ""],
                ["Jane Smith", "jane@example.com", "+987654321", "$200k", "6 months", "Apartment", "Downtown", "Researcher", "Cash", ""],
            ]

        for attempt in range(3):
            try:
                return await anyio.to_thread.run_sync(
                    lambda: self.sheets.values().get(
                        spreadsheetId=self.sheet_id,
                        range=range_name
                    ).execute().get("values", [])
                )
            except Exception as e:
                if attempt == 2:
                    logger.error(f"Final attempt failed fetching values from {range_name}: {e}")
                    raise
                logger.warning(f"Retry {attempt + 1} fetching values from {range_name}...")
                await anyio.sleep(1)

    async def _get_headers(self) -> list[str]:
        """Fetch and cache headers to avoid redundant API calls."""
        if self._cached_headers:
            return self._cached_headers

        rows = await self._get_values(f"{self._safe_tab()}!1:1")
        if not rows:
            logger.warning(f"No headers found in tab '{self.tab}'")
            return []

        # Normalize headers: lowercase, strip, replace spaces with underscores
        headers = [h.lower().strip().replace(" ", "_").replace("-", "_") for h in rows[0]]
        self._cached_headers = headers
        return headers

    async def get_new_leads(self) -> list[LeadData]:
        """
        Fetch all rows where lead_score is empty.
        Uses robust column mapping based on header strings.
        """
        rows = await self._get_values(f"{self._safe_tab()}!A1:Z")
        if not rows:
            logger.info("Sheet is empty or tab not found.")
            return []

        headers = await self._get_headers()
        leads = []

        # Re-check columns to ensure we have what we need
        required = ["name", "email", "lead_score"]
        missing = [r for r in required if r not in headers]
        if missing:
            logger.error(f"❌ Missing required columns in sheet: {', '.join(missing)}")
            return []

        for i, row in enumerate(rows[1:], start=2):
            # Pad row to match header length
            padded = row + [""] * (len(headers) - len(row))
            row_dict = dict(zip(headers, padded))

            # Skip already scored rows (check 'lead_score')
            if row_dict.get("lead_score", "").strip():
                continue

            leads.append(LeadData(
                row_number=i,
                name=row_dict.get("name") or row_dict.get("full_name", "Not provided"),
                email=row_dict.get("email") or row_dict.get("email_address", "Not provided"),
                phone=row_dict.get("phone") or row_dict.get("phone_number", "Not provided"),
                budget=row_dict.get("budget") or row_dict.get("stated_budget", "Not specified"),
                timeline=row_dict.get("timeline") or row_dict.get("purchase_timeline", "Not specified"),
                property_type=row_dict.get("property_type", "Not specified"),
                location=row_dict.get("location") or row_dict.get("preferred_location", "Not specified"),
                authority=row_dict.get("authority") or row_dict.get("decision_authority", "Not specified"),
                financing=row_dict.get("financing") or row_dict.get("financing_status", "Not specified"),
            ))

        if self.mock_mode:
            logger.info(f"MOCK MODE: Returning {len(leads)} dummy leads.")
        
        return leads

    async def update_lead_score(self, lead: LeadData, score: LeadScore):
        """Write scoring results back to the exact row in the sheet using batchUpdate."""
        if self.mock_mode:
            logger.info(f"MOCK MODE: Skipping real sheet update for row {lead.row_number}")
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
                continue

            col_index = headers.index(field)
            col_letter = self._get_column_letter(col_index)
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

    def _get_column_letter(self, index: int) -> str:
        """Convert a 0-indexed column number to a Google Sheets column letter (A, B, ..., Z, AA, ...)."""
        letter = ""
        while index >= 0:
            letter = chr(65 + (index % 26)) + letter
            index = (index // 26) - 1
        return letter