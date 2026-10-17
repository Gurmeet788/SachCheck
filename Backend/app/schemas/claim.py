from typing import Optional
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


class ClaimCheckResponse(BaseModel):
    claim_id: int
    claim_text: str
    status: str
    message: str

    model_config = ConfigDict(from_attributes=True)
