import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.claim import Claim
from app.schemas.claim import (
    ClaimCheckRequest,
    ClaimCheckResponse,
    SemanticCandidateItem,
    SemanticCandidateSearchRequest,
    SemanticCandidateSearchResponse,
    TrendingClaimItem,
)
from app.services.claim_service import check_or_record_claim, normalize_claim_text
from app.services.embedding_service import generate_claim_embedding, search_semantic_candidates
from app.services.fact_check_service import verify_and_sync_fact_checks
from app.services.gemini_classification_service import (
    CLASSIFICATION_SIMILARITY_FLOOR,
    classify_claim_pair,
)
from app.services.gemini_report_service import generate_gemini_report
from app.services.trending_service import get_trending_claims

logger = logging.getLogger(__name__)

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

    **Deduplication pipeline (in order):**
    1. Authoritative exact normalisation lookup — reuses existing claim if normalised text matches.
    2. If no exact match: generates 768-dim semantic embedding via gemini-embedding-001.
    3. Searches existing non-null embeddings using pgvector cosine distance.
    4. For each high-similarity candidate (score ≥ CLASSIFICATION_SIMILARITY_FLOOR), calls Gemini
       to classify the pair as EQUIVALENT / CONTRADICTORY / RELATED / UNCERTAIN.
    5. Reuses the canonical claim ID **only** when Gemini returns EQUIVALENT.
       Contradictory, related, uncertain, and error cases are kept as separate claims.
    6. Embedding failures log an error and save the claim with embedding=NULL.

    **Other behaviour:**
    - Stores X-Visitor-ID header (fallback: payload.session_id) as pseudonymous identifier.
    - Queries Google Fact Check Tools API and saves publisher articles.
    - Synthesises an objective Gemini report from retrieved evidence.
    """
    # Prefer X-Visitor-ID header; fallback to payload.session_id
    effective_session_id = None
    if x_visitor_id and x_visitor_id.strip():
        effective_session_id = x_visitor_id.strip()[:255]
    elif payload.session_id and payload.session_id.strip():
        effective_session_id = payload.session_id.strip()[:255]

    # ── Step 1: Authoritative exact normalization lookup ──────────────────────
    normalized = normalize_claim_text(payload.claim_text)
    stmt = (
        select(Claim)
        .where(Claim.normalized_text == normalized)
        .order_by(Claim.id.asc())
    )
    existing_claim = db.scalars(stmt).first()

    # ── Steps 2-5: Semantic deduplication (only when no exact match exists) ───
    embedding: Optional[List[float]] = None
    canonical_claim: Optional[Claim] = None  # set only on confirmed EQUIVALENT

    if not existing_claim:
        embedding = await generate_claim_embedding(payload.claim_text)
        if embedding:
            candidates = search_semantic_candidates(db=db, target_vector=embedding)
            for candidate in candidates:
                # Only classify pairs that pass the similarity floor; avoids wasting
                # API quota on weak matches that are unlikely to be EQUIVALENT.
                if candidate.similarity_score < CLASSIFICATION_SIMILARITY_FLOOR:
                    continue

                relationship = await classify_claim_pair(
                    claim_a=payload.claim_text,
                    claim_b=candidate.claim_text,
                )

                logger.info(
                    "Semantic dedup: new='%s' vs candidate[%d]='%s' → %s (score=%.4f)",
                    payload.claim_text[:50],
                    candidate.claim_id,
                    candidate.claim_text[:50],
                    relationship,
                    candidate.similarity_score,
                )

                if relationship == "EQUIVALENT":
                    # Retrieve the canonical Claim ORM object
                    canonical_claim = db.get(Claim, candidate.claim_id)
                    if canonical_claim is not None:
                        logger.info(
                            "Claim reused via semantic EQUIVALENT: canonical id=%d for new text='%s'",
                            canonical_claim.id,
                            payload.claim_text[:60],
                        )
                        break  # Use the first EQUIVALENT; stop checking further candidates

    # ── Step 6: Record the claim (exact duplicate, semantic duplicate, or new) ─
    if existing_claim is not None:
        # Exact normalisation match — use check_or_record_claim in the normal path
        # (it will find it again and just record a new search event)
        canonical_claim = None  # let check_or_record_claim handle it

    if canonical_claim is not None:
        # Semantic duplicate confirmed EQUIVALENT — record search against canonical claim
        # but do NOT create a new claim row
        claim = check_or_record_claim(
            db=db,
            claim_text=canonical_claim.claim_text,  # preserve canonical text
            session_id=effective_session_id,
            embedding=None,  # embedding already exists on canonical
        )
    else:
        # New claim (exact or no match) — normal ingestion path
        claim = check_or_record_claim(
            db=db,
            claim_text=payload.claim_text,
            session_id=effective_session_id,
            embedding=embedding,
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
    """
    return get_trending_claims(db=db, limit=limit)


@router.post(
    "/candidates",
    response_model=SemanticCandidateSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Search semantic candidate claims using pgvector (Testing/Inspection)",
)
async def find_candidates_endpoint(
    payload: SemanticCandidateSearchRequest,
    authorization: Optional[str] = Header(
        default=None,
        description="Admin token required in production environments.",
    ),
    db: Session = Depends(get_db),
):
    """
    Testable semantic candidate discovery endpoint:
    - Generates 768-dim embedding for query_text.
    - Searches existing non-null embeddings using pgvector cosine distance.
    - Returns candidate claim IDs, texts, and similarity scores.
    - Protected: Restricted in production environments to avoid unauthenticated administrative exposure.
    """
    if settings.ENVIRONMENT == "production":
        expected_secret = f"Bearer {settings.SECRET_KEY}"
        if not authorization or authorization.strip() != expected_secret:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Candidate inspection endpoint is restricted in production.",
            )

    embedding = await generate_claim_embedding(payload.query_text)
    if not embedding:
        return SemanticCandidateSearchResponse(
            query_text=payload.query_text,
            candidates_count=0,
            candidates=[],
        )

    candidates = search_semantic_candidates(
        db=db,
        target_vector=embedding,
        threshold=payload.threshold,
        limit=payload.limit,
        query_text=payload.query_text,
    )

    return SemanticCandidateSearchResponse(
        query_text=payload.query_text,
        candidates_count=len(candidates),
        candidates=[
            SemanticCandidateItem(
                claim_id=c.claim_id,
                claim_text=c.claim_text,
                status=c.status,
                similarity_score=c.similarity_score,
                cosine_distance=c.cosine_distance,
                has_negation_mismatch=c.has_negation_mismatch,
            )
            for c in candidates
        ],
    )


