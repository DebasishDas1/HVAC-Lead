import os
import logging
from dotenv import load_dotenv

load_dotenv()

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("LeadScoring")


# ── Settings object ───────────────────────────────────────────────────────────
class Settings:
    # Groq
    GROQ_API_KEY: str           = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str             = "llama-3.1-8b-instant"

    # Google Sheets
    GOOGLE_SHEETS_ID: str       = os.getenv("GOOGLE_SHEETS_ID", "")
    GOOGLE_SHEET_NAME: str      = os.getenv("SHEET_TAB", "LeadIQ Realtor Leads")
    GOOGLE_SERVICE_ACCOUNT: str = "credential/deba4-google-sheet-credential.json"

    # SendGrid
    SENDGRID_API_KEY: str       = os.getenv("SENDGRID_API_KEY", "")
    NURTURE_EMAIL_FROM: str     = os.getenv("NURTURE_EMAIL_FROM", "no-reply@youragency.com")

    # Polling
    POLL_INTERVAL_SECONDS: int  = int(os.getenv("POLL_INTERVAL_SECONDS", "60"))

    def validate(self):
        """Warn if required keys are missing, but allow mock mode for development."""
        required = {
            "GROQ_API_KEY":             self.GROQ_API_KEY,
            "GOOGLE_SHEETS_ID":         self.GOOGLE_SHEETS_ID,
            "GOOGLE_SERVICE_ACCOUNT_JSON": self.GOOGLE_SERVICE_ACCOUNT,
            "SENDGRID_API_KEY":         self.SENDGRID_API_KEY,
        }
        missing = [k for k, v in required.items() if not v]
        if missing:
            logger.warning(
                f"⚠️ Missing environment variables: {', '.join(missing)}. "
                f"The system will run with reduced functionality (Mock Mode)."
            )


settings = Settings()