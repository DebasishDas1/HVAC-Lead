from pydantic import BaseModel


class LeadData(BaseModel):
    """Raw lead data as read from Google Sheets."""
    row_number:    int
    name:          str = "Not provided"
    email:         str = "Not provided"
    phone:         str = "Not provided"
    budget:        str = "Not specified"
    timeline:      str = "Not specified"
    property_type: str = "Not specified"
    location:      str = "Not specified"
    authority:     str = "Not specified"
    financing:     str = "Not specified"