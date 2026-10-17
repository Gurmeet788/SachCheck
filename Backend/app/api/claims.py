from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.claim import ClaimCheckRequest, ClaimCheckResponse
from app.services.claim_service import check_or_record_claim

router = APIRouter(prefix="/claims", tags=["claims"])


@router.post(
    "/check",
    response_model=ClaimCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Check or record a claim statement",
)
def check_claim(
    payload: ClaimCheckRequest,
    db: Session = Depends(get_db),
):
    """
    Submits a claim statement:
    - Reuses existing claims matching normalized text.
    - Saves new claims with status 'unverified'.
    - Logs each lookup in claim_searches for trending analytics.
    """
    claim = check_or_record_claim(
        db=db,
        claim_text=payload.claim_text,
        session_id=payload.session_id,
    )

    return ClaimCheckResponse(
        claim_id=claim.id,
        claim_text=claim.claim_text,
        status=claim.status,
        message="Claim registered. External fact-checking verification is not yet integrated.",
    )
