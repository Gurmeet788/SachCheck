from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.stats import PlatformStatsResponse
from app.services.trending_service import get_platform_stats

router = APIRouter(tags=["stats"])


@router.get(
    "/stats",
    response_model=PlatformStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get platform aggregate statistics",
)
def get_stats(
    db: Session = Depends(get_db),
):
    """
    Returns platform-wide aggregate counts:
    - Total claims registered
    - Total external fact-check records stored
    - Total raw search lookups logged
    - Distinct visitor IDs in the last 24 hours (clearly labeled as
      pseudonymous client identifiers rather than unique people).
    """
    return get_platform_stats(db=db)
