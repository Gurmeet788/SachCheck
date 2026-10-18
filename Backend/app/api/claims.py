from typing import List, Optional

from fastapi import APIRouter, Depends, Header, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.claim import (
    ClaimCheckRequest,
    ClaimCheckResponse,
    TrendingClaimItem,
)
from app.services.claim_service import check_or_record_claim
from app.services.fact_check_service import verify_and_sync_fact_checks
from app.services.gemini_report_service import generate_gemini_report
from app.services.trending_service import get_trending_claims

router = APIRouter(prefix="/claims", tags=["claims"])


@router.post(
    "/check",
    response_model=ClaimCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Check or record a claim statement",
)
async def check_claim(
    payload: ClaimCheckRequest,
    x_visitor_id: Optional[str] = Header(
        default=None,
        alias="X-Visitor-ID",
        description="Optional opaque, pseudonymous client/browser identifier.",
    ),
    db: Session = Depends(get_db),
):
    """
    Submits a claim statement:
    - Reuses existing claims matching normalized text.
    - Saves new claims with initial status 'unverified'.
    - Stores X-Visitor-ID (or payload.session_id) as an opaque pseudonymous visitor identifier.
    - Requests without a visitor ID are logged as raw search events without incrementing distinct visitor counts.
    - Asynchronously queries the Google Fact Check Tools API.
    - Saves parsed fact-check articles (publisher, rating, URL, review date).
    - Updates claim status to 'fact_checked' if articles exist, or retains 'unverified'.
    - Synthesizes an objective, source-grounded report using Gemini without inventing facts.
    - Returns claim details, retrieved source-backed results, and Gemini report.
    """
    # Prefer X-Visitor-ID header; fallback to payload.session_id
    effective_session_id = None
    if x_visitor_id and x_visitor_id.strip():
        effective_session_id = x_visitor_id.strip()[:255]
    elif payload.session_id and payload.session_id.strip():
        effective_session_id = payload.session_id.strip()[:255]

    claim = check_or_record_claim(
        db=db,
        claim_text=payload.claim_text,
        session_id=effective_session_id,
    )

    fact_checks, message = await verify_and_sync_fact_checks(
        db=db,
        claim=claim,
    )

    report = await generate_gemini_report(
        claim_text=claim.claim_text,
        fact_checks=fact_checks,
    )

    return ClaimCheckResponse(
        claim_id=claim.id,
        claim_text=claim.claim_text,
        status=claim.status,
        message=message,
        fact_checks=fact_checks,
        report=report,
    )


@router.get(
    "/trending",
    response_model=List[TrendingClaimItem],
    status_code=status.HTTP_200_OK,
    summary="Get trending claims ranked by distinct visitor IDs in the last 24 hours",
)
def get_trending(
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of trending claims to return (1-100).",
    ),
    db: Session = Depends(get_db),
):
    """
    Returns claims searched during the last 24 hours, ranked by the number of distinct visitor IDs.
    - Multiple searches by the same visitor ID count as 1 distinct visitor for that claim.
    - Different visitor IDs increase the trending count.
    - Searches without a visitor ID are recorded as raw search events but not counted as distinct visitors.
    - Visitor IDs are pseudonymous client identifiers and do not represent verified unique people.
    - Aggregation is performed directly in the database.
    """
    return get_trending_claims(db=db, limit=limit)



