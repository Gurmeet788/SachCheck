from pydantic import BaseModel, ConfigDict, Field


class PlatformStatsResponse(BaseModel):
    total_claims: int = Field(
        ...,
        description="Total number of registered claims in the system.",
    )
    total_fact_checks: int = Field(
        ...,
        description="Total number of external fact-check records stored.",
    )
    total_search_events: int = Field(
        ...,
        description="Total raw search lookups logged.",
    )
    distinct_visitor_ids_24h: int = Field(
        ...,
        description="Distinct visitor/browser identifiers active in the last 24 hours (pseudonymous client IDs, not verified unique people).",
    )

    model_config = ConfigDict(from_attributes=True)
