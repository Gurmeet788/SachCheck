import logging
import re
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.claim import Claim
from app.models.claim_search import ClaimSearch

logger = logging.getLogger(__name__)


def normalize_claim_text(text: str) -> str:
    """
    Normalizes claim text for duplicate matching:
    - Converts to lowercase
    - Strips leading and trailing whitespace
    - Collapses multiple internal spaces into a single space
    """
    cleaned = text.lower().strip()
    return re.sub(r"\s+", " ", cleaned)


def check_or_record_claim(
    db: Session,
    claim_text: str,
    session_id: Optional[str] = None,
) -> Claim:
    """
    Finds or creates a claim based on normalized text, records a search entry,
    and handles transaction rollback safely upon failure.
    """
    normalized = normalize_claim_text(claim_text)
    original_display_text = claim_text.strip()

    try:
        # Check if a claim with the same normalized text already exists
        stmt = select(Claim).where(Claim.normalized_text == normalized)
        claim = db.scalars(stmt).first()

        now_utc = datetime.now(timezone.utc)

        if claim:
            # Existing claim found: update last checked timestamp and reuse
            claim.last_checked_at = now_utc
        else:
            # New claim: insert into claims table with status 'unverified'
            claim = Claim(
                claim_text=original_display_text,
                normalized_text=normalized,
                status="unverified",
                last_checked_at=now_utc,
            )
            db.add(claim)
            db.flush()  # Populates claim.id for foreign key reference

        # Record this search event for trending statistics
        search_record = ClaimSearch(
            claim_id=claim.id,
            session_id=session_id.strip() if session_id else None,
            searched_at=now_utc,
        )
        db.add(search_record)

        # Commit transaction safely
        db.commit()
        db.refresh(claim)
        return claim

    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("Database error while processing claim: %s", type(exc).__name__)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="A database error occurred while recording the claim.",
        )
    except Exception as exc:
        db.rollback()
        logger.error("Unexpected error while processing claim: %s", type(exc).__name__)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing the claim.",
        )
