import logging
import re
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.claim import Claim
from app.models.claim_search import ClaimSearch

logger = logging.getLogger(__name__)

# Punctuation characters to strip from ends of claims
SURROUNDING_QUOTES = "\"'“”‘’`«»"
TRAILING_PUNCTUATION_PATTERN = re.compile(r"[\s.!?,\'\";:…–—~\"“”‘’`«»]+$")
LEADING_ARTICLE_PATTERN = re.compile(r"^(?:the|a|an)\s+", re.IGNORECASE)


def normalize_claim_text(text: str) -> str:
    """
    Normalizes claim text for duplicate matching:
    - Strips leading and trailing whitespace and surrounding quotes
    - Converts to lowercase
    - Collapses multiple internal spaces into a single space
    - Strips harmless trailing punctuation (.,!?;:…'\"“”‘’`~–—)
    - Strips leading grammatical articles ('the', 'a', 'an')
    - Preserves semantic words, negations, internal punctuation, and meaning
    """
    if not text:
        return ""

    # 1. Strip surrounding whitespace and quotation marks
    cleaned = text.strip().strip(SURROUNDING_QUOTES)

    # 2. Convert to lowercase
    cleaned = cleaned.lower()

    # 3. Collapse multiple whitespace characters into a single space
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    # 4. Strip harmless trailing punctuation and quotes
    cleaned = TRAILING_PUNCTUATION_PATTERN.sub("", cleaned)

    # 5. Remove leading grammatical article ('the', 'a', 'an') if followed by a space
    # (e.g. "The earth is flat" and "earth is flat" both normalize to "earth is flat")
    normalized = LEADING_ARTICLE_PATTERN.sub("", cleaned)

    # If removing the leading article leaves nothing (e.g. input was just "A"), fallback to cleaned
    if not normalized:
        normalized = cleaned

    return normalized.strip()


def check_or_record_claim(
    db: Session,
    claim_text: str,
    session_id: Optional[str] = None,
    embedding: Optional[List[float]] = None,
) -> Claim:
    """
    Finds or creates a claim based on normalized text, records a search entry,
    and handles transaction rollback safely upon failure.

    Concurrency & Uniqueness:
    - Queries using normalized_text with order_by(Claim.id.asc()) to consistently
      reuse the canonical (earliest) record if historical duplicates exist.
    - Handles concurrent race conditions: catches IntegrityError during flush,
      rolls back, and re-fetches the newly created record.
    - Preserves the original claim_text of the initial submission.
    - Stores 768-dim semantic embedding vector on new claims if available.
    """
    normalized = normalize_claim_text(claim_text)
    original_display_text = claim_text.strip()
    now_utc = datetime.now(timezone.utc)

    try:
        # Check if a claim with the same normalized text already exists
        # Order by Claim.id.asc() ensures canonical consistency
        stmt = (
            select(Claim)
            .where(Claim.normalized_text == normalized)
            .order_by(Claim.id.asc())
        )
        claim = db.scalars(stmt).first()

        if claim:
            # Existing claim found: update last checked timestamp and reuse
            claim.last_checked_at = now_utc
            if claim.embedding is None and embedding is not None:
                claim.embedding = embedding
        else:
            # New claim: insert into claims table with status 'unverified'
            claim = Claim(
                claim_text=original_display_text,
                normalized_text=normalized,
                embedding=embedding,
                status="unverified",
                last_checked_at=now_utc,
            )
            db.add(claim)
            try:
                db.flush()  # Populates claim.id for foreign key reference
            except IntegrityError:
                # Concurrent race condition: another transaction committed the same normalized claim
                db.rollback()
                claim = db.scalars(stmt).first()
                if not claim:
                    raise
                claim.last_checked_at = now_utc

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

    except HTTPException:
        raise
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

