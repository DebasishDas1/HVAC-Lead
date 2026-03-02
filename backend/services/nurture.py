import sendgrid
from sendgrid.helpers.mail import Mail

from config.settings import settings, logger
from schemas.lead import LeadData
from schemas.score import LeadScore


class NurtureEmailService:
    """Sends COLD lead nurture emails via SendGrid."""

    def __init__(self):
        self.sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)

    def send_cold_nurture(self, lead: LeadData, score: LeadScore):
        if lead.email in ("Not provided", ""):
            logger.warning(f"No email for '{lead.name}' (row {lead.row_number}) — skipping nurture")
            return

        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; color: #333;">
          <div style="background: #1a1a2e; padding: 24px; border-radius: 8px 8px 0 0;">
            <h1 style="color: #c9a84c; margin: 0; font-size: 22px;">
              Dubai Luxury Properties
            </h1>
            <p style="color: #aaa; margin: 4px 0 0;">Handpicked for you</p>
          </div>

          <div style="padding: 24px; border: 1px solid #eee; border-top: none; border-radius: 0 0 8px 8px;">
            <p>Dear {lead.name},</p>
            <p>
              Thank you for your interest in Dubai luxury real estate.
              We've noted your preferences and have curated properties
              that may be a great match.
            </p>

            <h3 style="color: #c9a84c;">Your Preferences:</h3>
            <table style="width:100%; border-collapse: collapse;">
              <tr>
                <td style="padding: 8px; border-bottom: 1px solid #eee; color: #666; width: 40%;">Property Type</td>
                <td style="padding: 8px; border-bottom: 1px solid #eee;">{lead.property_type}</td>
              </tr>
              <tr>
                <td style="padding: 8px; border-bottom: 1px solid #eee; color: #666;">Preferred Location</td>
                <td style="padding: 8px; border-bottom: 1px solid #eee;">{lead.location}</td>
              </tr>
              <tr>
                <td style="padding: 8px; color: #666;">Budget Range</td>
                <td style="padding: 8px;">{lead.budget}</td>
              </tr>
            </table>

            <p style="margin-top: 24px;">
              When you're ready to take the next step, our specialists are available
              7 days a week for a no-obligation consultation.
            </p>

            <div style="text-align: center; margin: 32px 0;">
              <a href="https://youragency.com/book?ref={lead.row_number}"
                 style="background: #c9a84c; color: white; padding: 14px 32px;
                        text-decoration: none; border-radius: 4px; font-weight: bold;">
                Schedule a Free Consultation
              </a>
            </div>

            <hr style="border: none; border-top: 1px solid #eee;"/>
            <p style="color: #bbb; font-size: 11px; margin-top: 16px;">
              You received this because you enquired about our properties.<br/>
              Lead ref: {lead.row_number} | Score: {score.lead_score}/100
            </p>
          </div>
        </body>
        </html>
        """

        message = Mail(
            from_email   = settings.NURTURE_EMAIL_FROM,
            to_emails    = lead.email,
            subject      = "Dubai Luxury Properties — We Found Your Match",
            html_content = html_body,
        )

        try:
            response = self.sg.send(message)
            logger.info(
                f"Nurture email sent → {lead.email} "
                f"(status {response.status_code})"
            )
        except Exception as e:
            logger.error(f"SendGrid error for {lead.email}: {e}")