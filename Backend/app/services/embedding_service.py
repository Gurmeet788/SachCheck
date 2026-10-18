import asyncio
import logging
import math
from dataclasses import dataclass
from typing import List, Optional, Sequence

from google import genai
from google.genai import types
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.claim import Claim

import re

logger = logging.getLogger(__name__)

# Regex matching English negation tokens and common contractions (supporting both straight ' and curly ’ apostrophes)
# Note: This is a conservative lexical heuristic, not a complete natural language inference contradiction detector.
NEGATION_PATTERN = re.compile(
    r"\b(?:not|no|never|neither|nor|none|cannot|can['’]?t|won['’]?t|don['’]?t|didn['’]?t|doesn['’]?t|isn['’]?t|aren['’]?t|wasn['’]?t|weren['’]?t|hasn['’]?t|haven['’]?t|hadn['’]?t|couldn['’]?t|shouldn['’]?t|wouldn['’]?t)\b",
    re.IGNORECASE,
)


def contains_negation(text: Optional[str]) -> bool:
    """
    Conservative heuristic check for presence of lexical negation markers or contractions
    (e.g., 'not', 'never', "didn't", "won't", "cannot").

    Disclaimer: This is a lexical token heuristic, not a full semantic contradiction detector.
    """
    if not text:
        return False
    return bool(NEGATION_PATTERN.search(text))


def check_negation_mismatch(text_a: Optional[str], text_b: Optional[str]) -> bool:
    """
    Returns True if one statement contains a negation token while the other does not.
    Returns False if both are positive or both contain negation tokens.
    """
    if not text_a or not text_b:
        return False
    return contains_negation(text_a) != contains_negation(text_b)


@dataclass
class SemanticCandidate:
    claim_id: int
    claim_text: str
    status: str
    cosine_distance: float
    similarity_score: float
    has_negation_mismatch: bool = False


def compute_cosine_distance(vec_a: Sequence[float], vec_b: Sequence[float]) -> float:
    """
    Computes mathematical cosine distance between two vectors:
    distance = 1.0 - cosine_similarity
    Result is bounded between 0.0 (identical direction) and 2.0 (opposite direction).
    """
    if len(vec_a) != len(vec_b) or not vec_a:
        return 1.0

    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))

    if norm_a == 0.0 or norm_b == 0.0:
        return 1.0

    similarity = dot / (norm_a * norm_b)
    # Clamp for floating point rounding discrepancies
    similarity = max(-1.0, min(1.0, similarity))
    return 1.0 - similarity


async def generate_claim_embedding(
    text: str,
    client: Optional[genai.Client] = None,
) -> Optional[List[float]]:
    """
    Asynchronously generates a 768-dimensional semantic embedding using
    the verified google-genai SDK and gemini-embedding-001.

    Guarantees:
    - Never exposes or logs the GEMINI_API_KEY.
    - If the API key is missing or the external API fails/times out, logs the error
      and safely returns None so the claim ingestion never crashes or false-merges.
    - Validates output dimensionality matches settings.EMBEDDING_DIMENSION (768).
    """
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        logger.warning("GEMINI_API_KEY is not configured; skipping embedding generation.")
        return None

    cleaned_text = text.strip()
    if not cleaned_text:
        return None

    try:
        genai_client = client or genai.Client(api_key=api_key)

        embed_config = types.EmbedContentConfig(
            task_type="SEMANTIC_SIMILARITY",
            output_dimensionality=settings.EMBEDDING_DIMENSION,
        )

        # Apply timeout protection
        coro = genai_client.aio.models.embed_content(
            model=settings.GEMINI_EMBEDDING_MODEL,
            contents=cleaned_text,
            config=embed_config,
        )
        response = await asyncio.wait_for(coro, timeout=settings.EMBEDDING_TIMEOUT_SECONDS)

        if not response.embeddings or not response.embeddings[0].values:
            logger.warning("Gemini embedding model returned empty embedding payload.")
            return None

        vector = list(response.embeddings[0].values)
        if len(vector) != settings.EMBEDDING_DIMENSION:
            logger.error(
                "Gemini embedding dimension mismatch: expected %d, got %d",
                settings.EMBEDDING_DIMENSION,
                len(vector),
            )
            return None

        return vector

    except asyncio.TimeoutError:
        logger.warning(
            "Gemini embedding request timed out after %.1f seconds.",
            settings.EMBEDDING_TIMEOUT_SECONDS,
        )
        return None
    except Exception as exc:
        logger.error("Error generating claim embedding [%s]: %s", type(exc).__name__, str(exc))
        return None


def search_semantic_candidates(
    db: Session,
    target_vector: Sequence[float],
    threshold: Optional[float] = None,
    limit: int = 5,
    exclude_claim_id: Optional[int] = None,
    query_text: Optional[str] = None,
) -> List[SemanticCandidate]:
    """
    Searches for candidate claims with existing non-null embeddings based on cosine distance.
    - On PostgreSQL: Executes native pgvector <=> operator directly in the database.
    - On SQLite (in-memory test suite): Computes exact cosine distance in Python.
    - Robust tuple unpacking: extracts (claim_obj, dist) directly from database rows.
    - Negation mismatch heuristic: checks if candidate polarity diverges from query_text.
    - Returns candidates ranked by highest similarity (lowest cosine distance).
    - NOTE: Semantic similarity identifies CANDIDATES for evaluation; it does NOT
      auto-merge claims into a single ID.
    """
    if not target_vector:
        return []

    min_similarity = (
        threshold
        if threshold is not None
        else settings.EMBEDDING_SIMILARITY_THRESHOLD
    )
    # Cosine distance = 1.0 - cosine_similarity
    max_distance = max(0.0, 1.0 - min_similarity)

    dialect_name = db.get_bind().dialect.name

    if dialect_name == "postgresql":
        # Native PostgreSQL + pgvector query
        distance_col = Claim.embedding.cosine_distance(target_vector).label("distance")
        stmt = (
            select(Claim, distance_col)
            .where(Claim.embedding.isnot(None))
            .where(distance_col <= max_distance)
        )
        if exclude_claim_id is not None:
            stmt = stmt.where(Claim.id != exclude_claim_id)

        stmt = stmt.order_by("distance").limit(limit)
        results = db.execute(stmt).all()

        candidates: List[SemanticCandidate] = []
        # Robust tuple unpacking across drivers: (claim_obj, dist)
        for claim_obj, dist in results:
            dist_val = float(dist)
            has_mismatch = (
                check_negation_mismatch(query_text, claim_obj.claim_text)
                if query_text
                else False
            )
            candidates.append(
                SemanticCandidate(
                    claim_id=claim_obj.id,
                    claim_text=claim_obj.claim_text,
                    status=claim_obj.status,
                    cosine_distance=dist_val,
                    similarity_score=round(1.0 - dist_val, 4),
                    has_negation_mismatch=has_mismatch,
                )
            )
        return candidates

    else:
        # SQLite test environment fallback: fetch claims with non-null embeddings and compute
        stmt = select(Claim).where(Claim.embedding.isnot(None))
        if exclude_claim_id is not None:
            stmt = stmt.where(Claim.id != exclude_claim_id)

        claims = db.scalars(stmt).all()
        candidates: List[SemanticCandidate] = []

        for claim in claims:
            if not claim.embedding:
                continue
            dist = compute_cosine_distance(target_vector, claim.embedding)
            if dist <= max_distance:
                has_mismatch = (
                    check_negation_mismatch(query_text, claim.claim_text)
                    if query_text
                    else False
                )
                candidates.append(
                    SemanticCandidate(
                        claim_id=claim.id,
                        claim_text=claim.claim_text,
                        status=claim.status,
                        cosine_distance=dist,
                        similarity_score=round(1.0 - dist, 4),
                        has_negation_mismatch=has_mismatch,
                    )
                )

        # Sort ascending by distance (descending by similarity)
        candidates.sort(key=lambda c: c.cosine_distance)
        return candidates[:limit]
