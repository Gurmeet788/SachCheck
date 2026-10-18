import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.claim import Claim
from app.schemas.claim import GeminiReport
from app.services.claim_service import check_or_record_claim
from app.services.embedding_service import (
    check_negation_mismatch,
    compute_cosine_distance,
    contains_negation,
    generate_claim_embedding,
    search_semantic_candidates,
)


# ============================================================================
# Unit Tests for compute_cosine_distance
# ============================================================================

def test_compute_cosine_distance_identical_and_orthogonal():
    """Verify mathematical cosine distance properties."""
    vec1 = [1.0, 0.0, 0.0]
    vec2 = [1.0, 0.0, 0.0]
    vec3 = [0.0, 1.0, 0.0]
    vec4 = [-1.0, 0.0, 0.0]

    # Identical vectors: distance = 0.0
    assert compute_cosine_distance(vec1, vec2) == pytest.approx(0.0)

    # Orthogonal vectors: distance = 1.0
    assert compute_cosine_distance(vec1, vec3) == pytest.approx(1.0)

    # Opposite vectors: distance = 2.0
    assert compute_cosine_distance(vec1, vec4) == pytest.approx(2.0)


# ============================================================================
# Unit Tests for generate_claim_embedding
# ============================================================================

@pytest.mark.asyncio
async def test_generate_claim_embedding_success():
    """Verify successful 768-dimensional vector generation."""
    mock_values = [0.05] * 768
    mock_embedding = MagicMock()
    mock_embedding.values = mock_values

    mock_response = MagicMock()
    mock_response.embeddings = [mock_embedding]

    mock_client = MagicMock()
    mock_client.aio.models.embed_content = AsyncMock(return_value=mock_response)

    vector = await generate_claim_embedding("Test claim text", client=mock_client)
    assert vector is not None
    assert len(vector) == 768
    assert vector[0] == pytest.approx(0.05)


@pytest.mark.asyncio
async def test_generate_claim_embedding_missing_api_key():
    """Missing API key returns None safely without throwing."""
    with patch.object(settings, "GEMINI_API_KEY", ""):
        vector = await generate_claim_embedding("Any claim text")
        assert vector is None


@pytest.mark.asyncio
async def test_generate_claim_embedding_timeout():
    """Async timeout returns None gracefully without failing the request."""
    mock_client = MagicMock()
    mock_client.aio.models.embed_content = AsyncMock(side_effect=asyncio.TimeoutError())

    with patch.object(settings, "GEMINI_API_KEY", "dummy-key"):
        vector = await generate_claim_embedding("Slow claim", client=mock_client)
        assert vector is None


@pytest.mark.asyncio
async def test_generate_claim_embedding_empty_response():
    """Empty response from model returns None safely."""
    mock_response = MagicMock()
    mock_response.embeddings = []
    mock_client = MagicMock()
    mock_client.aio.models.embed_content = AsyncMock(return_value=mock_response)

    with patch.object(settings, "GEMINI_API_KEY", "dummy-key"):
        vector = await generate_claim_embedding("Claim with empty response", client=mock_client)
        assert vector is None


# ============================================================================
# Tests for Candidate Search & Defense Against Auto-Merging
# ============================================================================

def test_search_semantic_candidates_ranking(db_session: Session):
    """Verify semantic candidate discovery ranks by cosine distance."""
    # Seed claims with synthetic vectors
    c1 = Claim(
        claim_text="Base reference claim",
        normalized_text="base reference claim",
        embedding=[0.1] * 768,
        status="unverified",
    )
    c2 = Claim(
        claim_text="Very similar claim",
        normalized_text="very similar claim",
        embedding=[0.1] * 768,  # identical vector -> distance 0.0
        status="fact_checked",
    )
    c3 = Claim(
        claim_text="Different claim",
        normalized_text="different claim",
        embedding=[-0.1] * 768,  # opposite vector -> distance 2.0
        status="unverified",
    )
    c4 = Claim(
        claim_text="Claim without embedding",
        normalized_text="claim without embedding",
        embedding=None,  # should be skipped
        status="unverified",
    )
    db_session.add_all([c1, c2, c3, c4])
    db_session.commit()

    candidates = search_semantic_candidates(
        db=db_session,
        target_vector=[0.1] * 768,
        threshold=0.5,
        limit=5,
    )

    # c1 and c2 should match threshold, c3 is opposite (dist=2), c4 has no embedding
    assert len(candidates) == 2
    assert candidates[0].similarity_score == pytest.approx(1.0)
    assert candidates[0].claim_id in {c1.id, c2.id}


def test_claims_with_opposing_meaning_are_not_automatically_merged(
    client: TestClient, db_session: Session
):
    """
    CRITICAL REQUIREMENT:
    Claims with opposing meaning (e.g. 'Pakistan won the match' vs 'Pakistan lost the match')
    must NEVER be merged automatically into a single claim ID, even if their semantic
    similarity score is high.
    """
    dummy_report = GeminiReport(
        summary="S", evidence_analysis="E", limitations="L", suggested_correction="C", evidence_sufficient=False
    )
    # High similarity synthetic vectors (0.95 similarity)
    vec_won = [0.1] * 768
    vec_lost = [0.1] * 768

    with (
        patch("app.api.claims.verify_and_sync_fact_checks", new_callable=AsyncMock) as mock_fc,
        patch("app.api.claims.generate_gemini_report", new_callable=AsyncMock) as mock_gem,
        patch("app.api.claims.generate_claim_embedding", new_callable=AsyncMock) as mock_embed,
    ):
        mock_fc.return_value = ([], "No articles.")
        mock_gem.return_value = dummy_report
        mock_embed.side_effect = [vec_won, vec_lost]

        res1 = client.post("/claims/check", json={"claim_text": "Pakistan won the cricket match"})
        assert res1.status_code == 200
        id1 = res1.json()["claim_id"]

        res2 = client.post("/claims/check", json={"claim_text": "Pakistan lost the cricket match"})
        assert res2.status_code == 200
        id2 = res2.json()["claim_id"]

        # MUST be separate claims!
        assert id1 != id2
        assert db_session.scalar(select(Claim.claim_text).where(Claim.id == id1)) == "Pakistan won the cricket match"
        assert db_session.scalar(select(Claim.claim_text).where(Claim.id == id2)) == "Pakistan lost the cricket match"


def test_claims_with_negation_are_not_automatically_merged(
    client: TestClient, db_session: Session
):
    """
    CRITICAL REQUIREMENT:
    Statements with negation ('Vaccines cause autism' vs 'Vaccines do not cause autism')
    must NEVER be merged into a single claim ID.
    """
    dummy_report = GeminiReport(
        summary="S", evidence_analysis="E", limitations="L", suggested_correction="C", evidence_sufficient=False
    )
    with (
        patch("app.api.claims.verify_and_sync_fact_checks", new_callable=AsyncMock) as mock_fc,
        patch("app.api.claims.generate_gemini_report", new_callable=AsyncMock) as mock_gem,
        patch("app.api.claims.generate_claim_embedding", new_callable=AsyncMock) as mock_embed,
    ):
        mock_fc.return_value = ([], "No articles.")
        mock_gem.return_value = dummy_report
        mock_embed.side_effect = [[0.2] * 768, [0.2] * 768]

        res1 = client.post("/claims/check", json={"claim_text": "Vaccines cause autism"})
        res2 = client.post("/claims/check", json={"claim_text": "Vaccines do not cause autism"})

        assert res1.status_code == 200
        assert res2.status_code == 200
        assert res1.json()["claim_id"] != res2.json()["claim_id"]


def test_claims_with_different_numbers_dates_and_scores_are_not_merged(
    client: TestClient, db_session: Session
):
    """
    CRITICAL REQUIREMENT:
    Claims differing in numbers, dates, or scores must remain separate records:
    - 'COVID cases rose by 5% in 2024' vs 'COVID cases rose by 50% in 2026'
    - 'The team scored 3 goals' vs 'The team scored 0 goals'
    """
    dummy_report = GeminiReport(
        summary="S", evidence_analysis="E", limitations="L", suggested_correction="C", evidence_sufficient=False
    )
    with (
        patch("app.api.claims.verify_and_sync_fact_checks", new_callable=AsyncMock) as mock_fc,
        patch("app.api.claims.generate_gemini_report", new_callable=AsyncMock) as mock_gem,
        patch("app.api.claims.generate_claim_embedding", new_callable=AsyncMock) as mock_embed,
    ):
        mock_fc.return_value = ([], "No articles.")
        mock_gem.return_value = dummy_report
        mock_embed.return_value = [0.15] * 768

        r1 = client.post("/claims/check", json={"claim_text": "COVID cases rose by 5% in 2024"})
        r2 = client.post("/claims/check", json={"claim_text": "COVID cases rose by 50% in 2026"})
        assert r1.json()["claim_id"] != r2.json()["claim_id"]

        r3 = client.post("/claims/check", json={"claim_text": "The team scored 3 goals"})
        r4 = client.post("/claims/check", json={"claim_text": "The team scored 0 goals"})
        assert r3.json()["claim_id"] != r4.json()["claim_id"]


def test_embedding_failure_safely_saves_claim_with_null_vector(
    client: TestClient, db_session: Session
):
    """
    When embedding generation fails, claim check must still succeed,
    saving the claim with embedding=NULL and never crashing or false-matching.
    """
    dummy_report = GeminiReport(
        summary="S", evidence_analysis="E", limitations="L", suggested_correction="C", evidence_sufficient=False
    )
    with (
        patch("app.api.claims.verify_and_sync_fact_checks", new_callable=AsyncMock) as mock_fc,
        patch("app.api.claims.generate_gemini_report", new_callable=AsyncMock) as mock_gem,
        patch("app.api.claims.generate_claim_embedding", new_callable=AsyncMock, return_value=None),
    ):
        mock_fc.return_value = ([], "No articles.")
        mock_gem.return_value = dummy_report

        res = client.post("/claims/check", json={"claim_text": "Claim testing null vector storage"})
        assert res.status_code == 200
        claim_id = res.json()["claim_id"]

        saved_claim = db_session.scalar(select(Claim).where(Claim.id == claim_id))
        assert saved_claim is not None
        assert saved_claim.embedding is None


# ============================================================================
# Tests for Candidate Inspection Endpoint
# ============================================================================

def test_candidate_discovery_endpoint_in_dev_and_prod_guard(client: TestClient, db_session: Session):
    """
    Verify POST /claims/candidates:
    - Works in development environment.
    - Rejects unauthenticated calls in production environment with 403 Forbidden.
    """
    # Seed an existing claim with vector
    c = Claim(
        claim_text="Original indexed statement",
        normalized_text="original indexed statement",
        embedding=[0.1] * 768,
        status="unverified",
    )
    db_session.add(c)
    db_session.commit()

    with patch("app.api.claims.generate_claim_embedding", new_callable=AsyncMock, return_value=[0.1] * 768):
        # 1. In development: succeeds without auth
        with patch.object(settings, "ENVIRONMENT", "development"):
            res = client.post("/claims/candidates", json={"query_text": "Search query statement"})
            assert res.status_code == 200
            data = res.json()
            assert data["candidates_count"] >= 1
            assert data["candidates"][0]["claim_id"] == c.id
            assert data["candidates"][0]["similarity_score"] == pytest.approx(1.0)

        # 2. In production without auth: 403 Forbidden
        with patch.object(settings, "ENVIRONMENT", "production"):
            res_prod = client.post("/claims/candidates", json={"query_text": "Search query statement"})
            assert res_prod.status_code == 403

        # 3. In production with valid auth header: 200 OK
        with patch.object(settings, "ENVIRONMENT", "production"):
            res_auth = client.post(
                "/claims/candidates",
                json={"query_text": "Search query statement"},
                headers={"Authorization": f"Bearer {settings.SECRET_KEY}"},
            )
            assert res_auth.status_code == 200


# ============================================================================
# Tests for Negation Heuristics & Contractions
# ============================================================================

def test_contains_negation_contractions_and_words():
    """Verify conservative negation token detection across words and contractions."""
    # Positive statements (must return False)
    assert contains_negation("Pakistan won the cricket match") is False
    assert contains_negation("The earth is round") is False
    assert contains_negation("Economic growth reached 5% in 2026") is False
    assert contains_negation("Drinking water improves health") is False

    # Negative words (must return True)
    assert contains_negation("Pakistan did not win the cricket match") is True
    assert contains_negation("There is no evidence supporting the assertion") is True
    assert contains_negation("Scientists never verified this outcome") is True
    assert contains_negation("Government cannot confirm the report") is True

    # Common contractions with standard straight apostrophes
    assert contains_negation("Pakistan didn't win the cricket match") is True
    assert contains_negation("The team won't participate in the tournament") is True
    assert contains_negation("The statement isn't accurate") is True
    assert contains_negation("Officials aren't commenting on the matter") is True
    assert contains_negation("They haven't discovered new evidence") is True
    assert contains_negation("He couldn't substantiate the allegation") is True

    # Common contractions with curly apostrophes (smart quotes)
    assert contains_negation("Pakistan didn’t win the cricket match") is True
    assert contains_negation("The team won’t participate") is True
    assert contains_negation("The claim isn’t factual") is True


def test_check_negation_mismatch_combinations():
    """Verify check_negation_mismatch across positive/negative combinations."""
    pos1 = "The cricket match was won by Pakistan"
    pos2 = "Pakistan won the cricket match"
    neg1 = "Pakistan did not win the cricket match"
    neg2 = "Pakistan didn't win the cricket match"

    # Positive vs Negative (mismatch expected)
    assert check_negation_mismatch(pos1, neg1) is True
    assert check_negation_mismatch(pos2, neg2) is True
    assert check_negation_mismatch(neg1, pos2) is True

    # Two Positive claims (no mismatch)
    assert check_negation_mismatch(pos1, pos2) is False

    # Two Negative claims (no mismatch)
    assert check_negation_mismatch(neg1, neg2) is False


def test_search_semantic_candidates_populates_negation_mismatch_flag(db_session: Session):
    """
    Verify search_semantic_candidates flags has_negation_mismatch=True
    when query is positive and candidate is negative, even with high vector similarity.
    """
    # Seed DB with a negative claim having a vector
    c_neg = Claim(
        claim_text="Pakistan did not win the cricket match",
        normalized_text="pakistan did not win the cricket match",
        embedding=[0.1] * 768,
        status="unverified",
    )
    c_pos = Claim(
        claim_text="The cricket match was won by Pakistan",
        normalized_text="cricket match was won by pakistan",
        embedding=[0.1] * 768,
        status="unverified",
    )
    db_session.add_all([c_neg, c_pos])
    db_session.commit()

    # Query with a positive statement
    query_text = "Pakistan won the cricket match"
    candidates = search_semantic_candidates(
        db=db_session,
        target_vector=[0.1] * 768,
        query_text=query_text,
        threshold=0.5,
    )

    assert len(candidates) == 2
    cand_neg = next(c for c in candidates if c.claim_id == c_neg.id)
    cand_pos = next(c for c in candidates if c.claim_id == c_pos.id)

    # Negative candidate must be flagged with negation mismatch
    assert cand_neg.has_negation_mismatch is True
    # Positive candidate must NOT be flagged
    assert cand_pos.has_negation_mismatch is False


def test_candidate_endpoint_returns_has_negation_mismatch(client: TestClient, db_session: Session):
    """
    Integration test for POST /claims/candidates:
    Verifies that the API returns has_negation_mismatch: true when comparing
    a positive query against an opposing negative candidate.
    """
    c = Claim(
        claim_text="Pakistan didn't win the cricket match",
        normalized_text="pakistan didn't win the cricket match",
        embedding=[0.1] * 768,
        status="unverified",
    )
    db_session.add(c)
    db_session.commit()

    with patch("app.api.claims.generate_claim_embedding", new_callable=AsyncMock, return_value=[0.1] * 768):
        response = client.post(
            "/claims/candidates",
            json={"query_text": "Pakistan won the cricket match"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["candidates_count"] >= 1
        candidate_item = data["candidates"][0]
        assert candidate_item["claim_id"] == c.id
        assert candidate_item["has_negation_mismatch"] is True

