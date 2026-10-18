"""Business logic and services package."""
from app.services.claim_service import check_or_record_claim, normalize_claim_text
from app.services.fact_check_service import (
    FactCheckOutcome,
    fetch_google_fact_checks,
    verify_and_sync_fact_checks,
)

from app.services.embedding_service import (
    SemanticCandidate,
    check_negation_mismatch,
    compute_cosine_distance,
    contains_negation,
    generate_claim_embedding,
    search_semantic_candidates,
)
from app.services.gemini_classification_service import (
    CLASSIFICATION_SIMILARITY_FLOOR,
    classify_claim_pair,
)
from app.services.gemini_report_service import generate_gemini_report
from app.services.trending_service import get_platform_stats, get_trending_claims

__all__ = [
    "check_or_record_claim",
    "normalize_claim_text",
    "fetch_google_fact_checks",
    "verify_and_sync_fact_checks",
    "FactCheckOutcome",
    "generate_gemini_report",
    "get_trending_claims",
    "get_platform_stats",
    "generate_claim_embedding",
    "search_semantic_candidates",
    "SemanticCandidate",
    "compute_cosine_distance",
    "contains_negation",
    "check_negation_mismatch",
    "classify_claim_pair",
    "CLASSIFICATION_SIMILARITY_FLOOR",
]


