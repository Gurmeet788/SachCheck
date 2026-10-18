import logging
from datetime import datetime, timedelta, timezone
from typing import List

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.models.claim import Claim
from app.models.claim_search import ClaimSearch
from app.models.fact_check import FactCheck
from app.schemas.claim import TrendingClaimItem
from app.schemas.stats import PlatformStatsResponse

logger = logging.getLogger(__name__)


def get_trending_claims(
    db: Session,
    limit: int = 10,
    hours: int = 24,
) -> List[TrendingClaimItem]:
    """
    Retrieves claims searched during the specified time window (default 24h),
    ranked by the number of distinct visitor/browser identifiers.

    Guarantees:
    - Multiple searches of the same claim by the same visitor ID count as 1.
    - Searches without a visitor ID are excluded from distinct visitor counts.
    - Searches older than the cutoff window (24h) are excluded.
    - Execution is delegated completely to database aggregation (COUNT DISTINCT),
      avoiding loading raw records into memory.
    - Empty database returns an empty list.
    """
    now_utc = datetime.now(timezone.utc)
    cutoff = now_utc - timedelta(hours=hours)

    stmt = (
        select(
            Claim.id.label("claim_id"),
            Claim.claim_text.label("claim_text"),
            Claim.status.label("status"),
            func.count(func.distinct(ClaimSearch.session_id)).label("distinct_visitor_count"),
        )
        .join(Claim, ClaimSearch.claim_id == Claim.id)
        .where(
            ClaimSearch.searched_at >= cutoff,
            ClaimSearch.session_id.isnot(None),
            ClaimSearch.session_id != "",
        )
        .group_by(Claim.id, Claim.claim_text, Claim.status)
        .order_by(
            desc("distinct_visitor_count"),
            desc(func.max(ClaimSearch.searched_at)),
            Claim.id.desc(),
        )
        .limit(limit)
    )

    rows = db.execute(stmt).all()

    return [
        TrendingClaimItem(
            claim_id=row.claim_id,
            claim_text=row.claim_text,
            status=row.status,
            distinct_visitor_count=row.distinct_visitor_count,
        )
        for row in rows
    ]


def get_platform_stats(
    db: Session,
    hours: int = 24,
) -> PlatformStatsResponse:
    """
    Calculates platform-wide aggregate statistics:
    - Total claims registered
    - Total fact-check records stored
    - Total raw search events logged
    - Distinct visitor IDs active in the last 24 hours (clearly labeled as
      pseudonymous client identifiers rather than unique people).
    """
    now_utc = datetime.now(timezone.utc)
    cutoff = now_utc - timedelta(hours=hours)

    total_claims = db.scalar(select(func.count(Claim.id))) or 0
    total_fact_checks = db.scalar(select(func.count(FactCheck.id))) or 0
    total_search_events = db.scalar(select(func.count(ClaimSearch.id))) or 0

    distinct_visitors_stmt = (
        select(func.count(func.distinct(ClaimSearch.session_id)))
        .where(
            ClaimSearch.searched_at >= cutoff,
            ClaimSearch.session_id.isnot(None),
            ClaimSearch.session_id != "",
        )
    )
    distinct_visitor_ids_24h = db.scalar(distinct_visitors_stmt) or 0

    return PlatformStatsResponse(
        total_claims=total_claims,
        total_fact_checks=total_fact_checks,
        total_search_events=total_search_events,
        distinct_visitor_ids_24h=distinct_visitor_ids_24h,
    )
