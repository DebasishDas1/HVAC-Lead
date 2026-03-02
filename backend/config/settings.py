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
    GROQ_MODEL: str             = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

    # Google Sheets
    GOOGLE_SHEETS_ID: str       = os.getenv("GOOGLE_SHEETS_ID", "")
    GOOGLE_SHEET_NAME: str      = os.getenv("SHEET_TAB", "LeadIQ Realtor Leads")
    GOOGLE_SERVICE_ACCOUNT: str = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "credential/deba4-google-sheet-credential.json")

    # SendGrid
    SENDGRID_API_KEY: str       = os.getenv("SENDGRID_API_KEY", "")
    NURTURE_EMAIL_FROM: str     = os.getenv("NURTURE_EMAIL_FROM", "no-reply@youragency.com")

    # Polling & Concurrency
    POLL_INTERVAL_SECONDS: int  = int(os.getenv("POLL_INTERVAL_SECONDS", "60"))
    MAX_CONCURRENT_LEADS: int   = int(os.getenv("MAX_CONCURRENT_LEADS", "5"))

    # Chat
    MAX_TOKEN: int = int(os.getenv("MAX_TOKEN", "200"))

    def validate(self):
        """Warn if required keys are missing, but allow mock mode for development."""
        required_critical = {
            "GROQ_API_KEY":             self.GROQ_API_KEY,
        }
        required_sheets = {
            "GOOGLE_SHEETS_ID":         self.GOOGLE_SHEETS_ID,
            "GOOGLE_SERVICE_ACCOUNT_JSON": self.GOOGLE_SERVICE_ACCOUNT,
        }
        
        missing_critical = [k for k, v in required_critical.items() if not v]
        if missing_critical:
            raise EnvironmentError(f"CRITICAL: Missing required environment variables: {', '.join(missing_critical)}")

        missing_sheets = [k for k, v in required_sheets.items() if not v]
        if missing_sheets:
            logger.warning(
                f"⚠️ Missing Sheets environment variables: {', '.join(missing_sheets)}. "
                f"The system will run in MOCK MODE for Google Sheets."
            )
        
        if not self.SENDGRID_API_KEY:
             logger.warning("⚠️ SENDGRID_API_KEY missing. Nurture emails will be logged but not sent.")


settings = Settings()