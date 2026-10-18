import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

import httpx
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.claim import Claim
from app.models.fact_check import FactCheck

logger = logging.getLogger(__name__)


class FactCheckOutcome(str, Enum):
    MATCHES_FOUND = "matches_found"
    NO_MATCHES = "no_matches"
    SERVICE_TIMEOUT = "service_timeout"
    SERVICE_ERROR = "service_error"
    NOT_CONFIGURED = "not_configured"


@dataclass
class FactCheckArticle:
    publisher: str
    rating: str
    source_url: str
    published_at: Optional[datetime] = None


@dataclass
class FactCheckFetchResult:
    outcome: FactCheckOutcome
    articles: List[FactCheckArticle]
    error_message: Optional[str] = None


def parse_review_date(date_str: Optional[str]) -> Optional[datetime]:
    """
    Parses ISO 8601 / RFC 3339 date strings commonly returned by
    the Google Fact Check Tools API into a timezone-aware datetime.
    """
    if not date_str or not isinstance(date_str, str):
        return None
    cleaned = date_str.strip()
    if not cleaned:
        return None
    try:
        # Replaces trailing Z with +00:00 for full ISO compatibility
        return datetime.fromisoformat(cleaned.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        try:
            return datetime.strptime(cleaned[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except Exception:
            logger.debug("Unable to parse reviewDate string: %s", date_str)
            return None


async def fetch_google_fact_checks(
    query: str,
    client: Optional[httpx.AsyncClient] = None,
) -> FactCheckFetchResult:
    """
    Asynchronously queries the Google Fact Check Tools API claims:search endpoint.
    Handles network errors, timeouts, and HTTP errors gracefully while keeping API keys private.
    """
    api_key = settings.GOOGLE_FACT_CHECK_API_KEY
    if not api_key:
        logger.warning("GOOGLE_FACT_CHECK_API_KEY is not configured.")
        return FactCheckFetchResult(
            outcome=FactCheckOutcome.NOT_CONFIGURED,
            articles=[],
            error_message="Fact-checking API key is not configured.",
        )

    endpoint_url = settings.GOOGLE_FACT_CHECK_API_URL
    timeout = httpx.Timeout(settings.FACT_CHECK_TIMEOUT_SECONDS, connect=5.0)
    params = {
        "query": query,
        "key": api_key,
    }

    try:
        # Allow passing an injected client (useful for unit tests / connection pooling)
        if client is not None:
            response = await client.get(endpoint_url, params=params)
        else:
            async with httpx.AsyncClient(timeout=timeout) as async_client:
                response = await async_client.get(endpoint_url, params=params)

        if response.status_code == 200:
            data = response.json()
            raw_claims = data.get("claims", [])
            articles: List[FactCheckArticle] = []
            seen_urls: Set[str] = set()

            for claim_item in raw_claims:
                reviews = claim_item.get("claimReview", [])
                for review in reviews:
                    url = (review.get("url") or "").strip()
                    if not url or url in seen_urls:
                        continue
                    seen_urls.add(url)

                    # Extract publisher display name or host site
                    pub_info = review.get("publisher") or {}
                    publisher = (pub_info.get("name") or pub_info.get("site") or "Unknown Publisher").strip()
                    # Enforce max 255 chars for database column
                    publisher = publisher[:255]

                    # Extract textual rating
                    rating = (review.get("textualRating") or "Not Specified").strip()
                    # Enforce max 100 chars for database column
                    rating = rating[:100]

                    published_at = parse_review_date(review.get("reviewDate"))

                    articles.append(
                        FactCheckArticle(
                            publisher=publisher,
                            rating=rating,
                            source_url=url,
                            published_at=published_at,
                        )
                    )

            if articles:
                return FactCheckFetchResult(
                    outcome=FactCheckOutcome.MATCHES_FOUND,
                    articles=articles,
                )
            return FactCheckFetchResult(
                outcome=FactCheckOutcome.NO_MATCHES,
                articles=[],
            )

        # Distinguish non-200 responses without exposing the API key in logs
        logger.error(
            "Google Fact Check API returned error HTTP status code: %s",
            response.status_code,
        )
        return FactCheckFetchResult(
            outcome=FactCheckOutcome.SERVICE_ERROR,
            articles=[],
            error_message=f"Fact check service returned HTTP status {response.status_code}.",
        )

    except httpx.TimeoutException:
        logger.warning("Google Fact Check API request timed out after %s seconds.", settings.FACT_CHECK_TIMEOUT_SECONDS)
        return FactCheckFetchResult(
            outcome=FactCheckOutcome.SERVICE_TIMEOUT,
            articles=[],
            error_message="External fact-check service timed out.",
        )
    except httpx.RequestError as exc:
        logger.error("Network communication error with Google Fact Check API: %s", type(exc).__name__)
        return FactCheckFetchResult(
            outcome=FactCheckOutcome.SERVICE_ERROR,
            articles=[],
            error_message="Network communication error with external fact-check service.",
        )
    except Exception as exc:
        logger.error("Unexpected error querying Google Fact Check API: %s", type(exc).__name__)
        return FactCheckFetchResult(
            outcome=FactCheckOutcome.SERVICE_ERROR,
            articles=[],
            error_message="An unexpected error occurred while querying external fact check service.",
        )


async def verify_and_sync_fact_checks(
    db: Session,
    claim: Claim,
    client: Optional[httpx.AsyncClient] = None,
) -> Tuple[List[FactCheck], str]:
    """
    Coordinates verification with the Google Fact Check Tools API:
    - Queries the API with the claim text.
    - Prevents duplicate fact-check records for the same claim and source URL.
    - Saves new fact-check results into the fact_checks table.
    - Updates claim status to 'fact_checked' when articles exist.
    - Retains 'unverified' status on a successful no-match or when the service fails/times out.
    - Distinguishes service failures from successful no-matches in human-readable messages.
    - Returns all source-backed fact check records associated with the claim and the outcome message.
    """
    fetch_result = await fetch_google_fact_checks(claim.claim_text, client=client)

    try:
        now_utc = datetime.now(timezone.utc)
        claim.last_checked_at = now_utc

        if fetch_result.outcome == FactCheckOutcome.MATCHES_FOUND:
            # Query existing source URLs for this claim to prevent duplicates
            existing_urls_stmt = select(FactCheck.source_url).where(FactCheck.claim_id == claim.id)
            existing_urls: Set[str] = set(db.scalars(existing_urls_stmt).all())

            new_records_count = 0
            for article in fetch_result.articles:
                if article.source_url not in existing_urls:
                    fact_check = FactCheck(
                        claim_id=claim.id,
                        publisher=article.publisher,
                        rating=article.rating,
                        source_url=article.source_url,
                        published_at=article.published_at,
                    )
                    db.add(fact_check)
                    existing_urls.add(article.source_url)
                    new_records_count += 1

            # Update status to fact_checked since articles exist
            claim.status = "fact_checked"
            db.commit()
            db.refresh(claim)

            message = (
                f"Fact-check articles found. Added {new_records_count} new record(s)."
                if new_records_count > 0
                else "Fact-check articles found. Records are already up to date."
            )

        elif fetch_result.outcome == FactCheckOutcome.NO_MATCHES:
            # Check if this claim previously had fact checks attached
            existing_records_stmt = select(FactCheck).where(FactCheck.claim_id == claim.id)
            existing_records = list(db.scalars(existing_records_stmt).all())

            if existing_records:
                claim.status = "fact_checked"
                message = "Search completed. No additional fact-check articles found for this claim."
            else:
                claim.status = "unverified"
                message = "Search completed successfully. No fact-check articles found for this claim."

            db.commit()
            db.refresh(claim)

        elif fetch_result.outcome == FactCheckOutcome.SERVICE_TIMEOUT:
            # Distinguish timeout from successful no-match; retain current/unverified status
            existing_records_stmt = select(FactCheck).where(FactCheck.claim_id == claim.id)
            existing_records = list(db.scalars(existing_records_stmt).all())
            if not existing_records:
                claim.status = "unverified"

            db.commit()
            db.refresh(claim)
            message = "External fact-check service timed out. Claim recorded with status unverified."

        elif fetch_result.outcome == FactCheckOutcome.NOT_CONFIGURED:
            # Distinguish missing config from successful no-match
            existing_records_stmt = select(FactCheck).where(FactCheck.claim_id == claim.id)
            existing_records = list(db.scalars(existing_records_stmt).all())
            if not existing_records:
                claim.status = "unverified"

            db.commit()
            db.refresh(claim)
            message = "External fact-check service is not configured. Claim recorded with status unverified."

        else:  # FactCheckOutcome.SERVICE_ERROR
            # Distinguish service failure from successful no-match; retain current/unverified status
            existing_records_stmt = select(FactCheck).where(FactCheck.claim_id == claim.id)
            existing_records = list(db.scalars(existing_records_stmt).all())
            if not existing_records:
                claim.status = "unverified"

            db.commit()
            db.refresh(claim)
            message = "External fact-check service is temporarily unavailable. Claim recorded with status unverified."

        # Fetch all fact check records linked to this claim to return full details
        results_stmt = (
            select(FactCheck)
            .where(FactCheck.claim_id == claim.id)
            .order_by(FactCheck.id.asc())
        )
        all_fact_checks = list(db.scalars(results_stmt).all())
        return all_fact_checks, message

    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("Database error while synchronizing fact checks: %s", type(exc).__name__)
        raise
