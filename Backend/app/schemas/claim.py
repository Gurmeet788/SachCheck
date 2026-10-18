from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ClaimCheckRequest(BaseModel):
    claim_text: str = Field(
        ...,
        max_length=2000,
        description="The statement or claim text to check.",
    )
    session_id: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Optional tracking identifier for client sessions.",
    )

    @field_validator("claim_text")
    @classmethod
    def validate_claim_text(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Claim text cannot be empty or whitespace only.")
        return value.strip()


class FactCheckItem(BaseModel):
    id: int
    claim_id: int
    publisher: str
    rating: str
    source_url: str
    published_at: Optional[datetime] = None
    retrieved_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class GeminiReport(BaseModel):
    summary: str = Field(
        ...,
        description="Concise summary of findings strictly based on the retrieved evidence.",
    )
    evidence_analysis: str = Field(
        ...,
        description="Detailed analysis of what the evidence articles state and publisher ratings.",
    )
    limitations: str = Field(
        ...,
        description="Known gaps, scope limitations, or context missing in the retrieved evidence.",
    )
    suggested_correction: str = Field(
        ...,
        description="Fact-based correction or clarification of the claim based on the evidence.",
    )
    evidence_sufficient: bool = Field(
        ...,
        description="Indicates whether external evidence was sufficient to evaluate the claim.",
    )

    model_config = ConfigDict(from_attributes=True)


class ClaimCheckResponse(BaseModel):
    claim_id: int
    claim_text: str
    status: str
    message: str
    fact_checks: List[FactCheckItem] = Field(default_factory=list)
    report: Optional[GeminiReport] = None

    model_config = ConfigDict(from_attributes=True)


class TrendingClaimItem(BaseModel):
    claim_id: int = Field(..., description="Unique claim identifier.")
    claim_text: str = Field(..., description="The claim statement text.")
    status: str = Field(..., description="Current verification status of the claim.")
    distinct_visitor_count: int = Field(
        ...,
        description="Count of distinct visitor/browser identifiers that searched this claim in the last 24 hours.",
    )

    model_config = ConfigDict(from_attributes=True)



