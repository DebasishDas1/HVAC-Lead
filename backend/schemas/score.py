from typing import Literal
from pydantic import BaseModel, Field, model_validator


class ScoreBreakdown(BaseModel):
    budget_score:     int = Field(..., ge=0, le=30,  description="Budget clarity score (0-30)")
    timeline_score:   int = Field(..., ge=0, le=30,  description="Timeline urgency score (0-30)")
    authority_score:  int = Field(..., ge=0, le=15,  description="Decision authority score (0-15)")
    financing_score:  int = Field(..., ge=0, le=15,  description="Financing readiness score (0-15)")
    engagement_score: int = Field(..., ge=0, le=10,  description="Engagement quality score (0-10)")

    @model_validator(mode="after")
    def validate_total(self) -> "ScoreBreakdown":
        total = (
            self.budget_score + self.timeline_score +
            self.authority_score + self.financing_score + self.engagement_score
        )
        if total > 100:
            raise ValueError(f"Sub-scores sum to {total}, exceeds 100")
        return self


class LeadScore(BaseModel):
    lead_score:             int   = Field(..., ge=0, le=100)
    priority_level:         Literal["HOT", "WARM", "COLD"]
    score_breakdown:        ScoreBreakdown
    recommended_action:     str   = Field(..., description="Specific next action for agent")
    agent_notes:            str   = Field(..., description="Context and warnings for the agent")
    follow_up_timing:       str   = Field(..., description="Exact timing e.g. 'within 60 seconds'")
    disqualification_flags: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def sync_priority(self) -> "LeadScore":
        """Ensure priority_level always matches lead_score numerically."""
        if self.lead_score >= 80:
            self.priority_level = "HOT"
        elif self.lead_score >= 50:
            self.priority_level = "WARM"
        else:
            self.priority_level = "COLD"
        return self