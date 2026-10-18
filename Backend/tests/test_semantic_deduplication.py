"""
Tests for gemini_classification_service.classify_claim_pair and the
automatic semantic deduplication in POST /claims/check.

All external HTTP calls (Gemini API, Google Fact Check API) and the
embedding generator are mocked – no real API keys are required.
All database operations run against the isolated in-memory SQLite defined
in conftest.py; the real Supabase database is never touched.
"""
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import httpx


# ────────────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────────────

def _gemini_classify_response(relationship: str, reason: str = "test reason") -> MagicMock:
    """Builds a mock httpx.Response that mimics a valid Gemini classification reply."""
    body = json.dumps({"relationship": relationship, "reason": reason})
    response = MagicMock(spec=httpx.Response)
    response.status_code = 200
    response.json.return_value = {
        "candidates": [
            {"content": {"parts": [{"text": body}]}}
        ]
    }
    return response


def _gemini_error_response(status_code: int = 500) -> MagicMock:
    response = MagicMock(spec=httpx.Response)
    response.status_code = status_code
    return response


# ────────────────────────────────────────────────────────────────────────────
# Unit tests – classify_claim_pair
# ────────────────────────────────────────────────────────────────────────────

class TestClassifyClaimPair:
    """Direct unit tests for classify_claim_pair without going through the HTTP stack."""

    @pytest.mark.asyncio
    async def test_equivalent_claims_returns_equivalent(self):
        from app.services.gemini_classification_service import classify_claim_pair

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.post = AsyncMock(return_value=_gemini_classify_response("EQUIVALENT"))

        result = await classify_claim_pair(
            claim_a="Pakistan won the cricket match",
            claim_b="The cricket match was won by Pakistan",
            client=mock_client,
        )
        assert result == "EQUIVALENT"

    @pytest.mark.asyncio
    async def test_contradictory_claims_returns_contradictory(self):
        from app.services.gemini_classification_service import classify_claim_pair

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.post = AsyncMock(return_value=_gemini_classify_response("CONTRADICTORY"))

        result = await classify_claim_pair(
            claim_a="Pakistan did not win the cricket match",
            claim_b="Pakistan won the cricket match",
            client=mock_client,
        )
        assert result == "CONTRADICTORY"

    @pytest.mark.asyncio
    async def test_related_claims_returns_related(self):
        from app.services.gemini_classification_service import classify_claim_pair

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.post = AsyncMock(return_value=_gemini_classify_response("RELATED"))

        result = await classify_claim_pair(
            claim_a="Pakistan scored 300 runs",
            claim_b="Pakistan won the cricket match",
            client=mock_client,
        )
        assert result == "RELATED"

    @pytest.mark.asyncio
    async def test_uncertain_label_returned_on_ambiguous(self):
        from app.services.gemini_classification_service import classify_claim_pair

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.post = AsyncMock(return_value=_gemini_classify_response("UNCERTAIN"))

        result = await classify_claim_pair(
            claim_a="x",
            claim_b="y",
            client=mock_client,
        )
        assert result == "UNCERTAIN"

    @pytest.mark.asyncio
    async def test_api_error_status_returns_uncertain(self):
        from app.services.gemini_classification_service import classify_claim_pair

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.post = AsyncMock(return_value=_gemini_error_response(500))

        result = await classify_claim_pair(
            claim_a="The earth is flat",
            claim_b="The earth is round",
            client=mock_client,
        )
        assert result == "UNCERTAIN"

    @pytest.mark.asyncio
    async def test_timeout_returns_uncertain(self):
        from app.services.gemini_classification_service import classify_claim_pair

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.post = AsyncMock(side_effect=httpx.TimeoutException("timeout"))

        result = await classify_claim_pair(
            claim_a="The earth is flat",
            claim_b="The earth is a globe",
            client=mock_client,
        )
        assert result == "UNCERTAIN"

    @pytest.mark.asyncio
    async def test_network_error_returns_uncertain(self):
        from app.services.gemini_classification_service import classify_claim_pair

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.post = AsyncMock(
            side_effect=httpx.ConnectError("connection refused")
        )

        result = await classify_claim_pair(
            claim_a="Vaccines cause autism",
            claim_b="Vaccines do not cause autism",
            client=mock_client,
        )
        assert result == "UNCERTAIN"

    @pytest.mark.asyncio
    async def test_malformed_json_returns_uncertain(self):
        from app.services.gemini_classification_service import classify_claim_pair

        bad_response = MagicMock(spec=httpx.Response)
        bad_response.status_code = 200
        bad_response.json.return_value = {
            "candidates": [
                {"content": {"parts": [{"text": "not json {{{{"}]}}
            ]
        }
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.post = AsyncMock(return_value=bad_response)

        result = await classify_claim_pair("A", "B", client=mock_client)
        assert result == "UNCERTAIN"

    @pytest.mark.asyncio
    async def test_invalid_label_returns_uncertain(self):
        from app.services.gemini_classification_service import classify_claim_pair

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.post = AsyncMock(
            return_value=_gemini_classify_response("DEFINITELY_SAME")
        )

        result = await classify_claim_pair("A", "B", client=mock_client)
        assert result == "UNCERTAIN"

    @pytest.mark.asyncio
    async def test_missing_api_key_returns_uncertain(self, monkeypatch):
        from app.services.gemini_classification_service import classify_claim_pair
        from app.core.config import settings

        monkeypatch.setattr(settings, "GEMINI_API_KEY", "")

        result = await classify_claim_pair(
            claim_a="The moon is made of cheese",
            claim_b="The moon is a rocky satellite",
        )
        assert result == "UNCERTAIN"

    @pytest.mark.asyncio
    async def test_empty_inputs_return_uncertain(self):
        from app.services.gemini_classification_service import classify_claim_pair

        result = await classify_claim_pair("", "Some claim")
        assert result == "UNCERTAIN"

        result = await classify_claim_pair("Some claim", "")
        assert result == "UNCERTAIN"


# ────────────────────────────────────────────────────────────────────────────
# Integration tests – POST /claims/check semantic deduplication
# ────────────────────────────────────────────────────────────────────────────

class TestSemanticDeduplicationInCheckEndpoint:
    """
    Tests that verify the full deduplication pipeline inside POST /claims/check.

    Strategy:
    - generate_claim_embedding is mocked (autouse fixture in conftest.py returns [0.01]*768).
    - search_semantic_candidates is mocked per test to control which candidates are found.
    - classify_claim_pair is mocked per test to control the Gemini classification result.
    - verify_and_sync_fact_checks and generate_gemini_report are mocked globally.
    """

    @pytest.fixture(autouse=True)
    def mock_external_services(self):
        """Mock fact-check and Gemini report services for all tests in this class."""
        with (
            patch(
                "app.api.claims.verify_and_sync_fact_checks",
                new_callable=AsyncMock,
                return_value=([], "No fact checks found."),
            ),
            patch(
                "app.api.claims.generate_gemini_report",
                new_callable=AsyncMock,
                return_value=None,
            ),
        ):
            yield

    def test_new_claim_no_candidates_creates_new_record(self, client):
        """No existing candidates → new claim is created."""
        with patch(
            "app.api.claims.search_semantic_candidates",
            return_value=[],
        ):
            resp1 = client.post("/claims/check", json={"claim_text": "The sun is a star"})
            assert resp1.status_code == 200
            claim_id_1 = resp1.json()["claim_id"]

            resp2 = client.post("/claims/check", json={"claim_text": "Water is wet"})
            assert resp2.status_code == 200
            claim_id_2 = resp2.json()["claim_id"]

        # Different claims → different IDs
        assert claim_id_1 != claim_id_2

    def test_exact_normalized_duplicate_reuses_id_without_classification(self, client):
        """
        Exact normalisation match must reuse the canonical ID without calling
        the Gemini classifier at all.
        """
        with patch("app.api.claims.search_semantic_candidates", return_value=[]):
            resp1 = client.post(
                "/claims/check", json={"claim_text": "The earth is round"}
            )
            assert resp1.status_code == 200
            canonical_id = resp1.json()["claim_id"]

        with (
            patch("app.api.claims.search_semantic_candidates", return_value=[]),
            patch(
                "app.api.claims.classify_claim_pair",
                new_callable=AsyncMock,
            ) as mock_classify,
        ):
            resp2 = client.post(
                "/claims/check", json={"claim_text": "earth is round"}
            )
            assert resp2.status_code == 200
            assert resp2.json()["claim_id"] == canonical_id
            # Classifier must NOT be called for exact normalisation matches
            mock_classify.assert_not_called()

    def test_semantic_equivalent_claim_reuses_canonical_id(self, client):
        """
        When Gemini classifies the pair as EQUIVALENT, the existing canonical claim
        ID should be returned for the paraphrased submission.
        """
        from app.services.embedding_service import SemanticCandidate

        # First, create the canonical claim
        with patch("app.api.claims.search_semantic_candidates", return_value=[]):
            resp1 = client.post(
                "/claims/check",
                json={"claim_text": "The cricket match was won by Pakistan"},
            )
            assert resp1.status_code == 200
            canonical_id = resp1.json()["claim_id"]
            canonical_text = resp1.json()["claim_text"]

        # Now submit a paraphrase; mock a high-similarity candidate + EQUIVALENT verdict
        fake_candidate = SemanticCandidate(
            claim_id=canonical_id,
            claim_text=canonical_text,
            status="unverified",
            cosine_distance=0.01,
            similarity_score=0.99,
            has_negation_mismatch=False,
        )

        with (
            patch(
                "app.api.claims.search_semantic_candidates",
                return_value=[fake_candidate],
            ),
            patch(
                "app.api.claims.classify_claim_pair",
                new_callable=AsyncMock,
                return_value="EQUIVALENT",
            ),
        ):
            resp2 = client.post(
                "/claims/check",
                json={"claim_text": "Pakistan won the cricket match"},
            )
            assert resp2.status_code == 200
            data = resp2.json()
            # Must return the canonical ID, not a new one
            assert data["claim_id"] == canonical_id
            # Must preserve the original canonical claim text
            assert data["claim_text"] == canonical_text

    def test_contradictory_claim_creates_new_record(self, client):
        """
        CONTRADICTORY classification must NOT merge the claims; a new record is created.
        """
        from app.services.embedding_service import SemanticCandidate

        with patch("app.api.claims.search_semantic_candidates", return_value=[]):
            resp1 = client.post(
                "/claims/check",
                json={"claim_text": "Pakistan won the cricket match"},
            )
            canonical_id = resp1.json()["claim_id"]
            canonical_text = resp1.json()["claim_text"]

        fake_candidate = SemanticCandidate(
            claim_id=canonical_id,
            claim_text=canonical_text,
            status="unverified",
            cosine_distance=0.08,
            similarity_score=0.92,
            has_negation_mismatch=True,
        )

        with (
            patch(
                "app.api.claims.search_semantic_candidates",
                return_value=[fake_candidate],
            ),
            patch(
                "app.api.claims.classify_claim_pair",
                new_callable=AsyncMock,
                return_value="CONTRADICTORY",
            ),
        ):
            resp2 = client.post(
                "/claims/check",
                json={"claim_text": "Pakistan did not win the cricket match"},
            )
            assert resp2.status_code == 200
            new_id = resp2.json()["claim_id"]
            # Must be a different claim row
            assert new_id != canonical_id

    def test_related_claim_creates_new_record(self, client):
        """RELATED classification must NOT merge; a separate claim is recorded."""
        from app.services.embedding_service import SemanticCandidate

        with patch("app.api.claims.search_semantic_candidates", return_value=[]):
            resp1 = client.post(
                "/claims/check",
                json={"claim_text": "Pakistan won the cricket match"},
            )
            canonical_id = resp1.json()["claim_id"]
            canonical_text = resp1.json()["claim_text"]

        fake_candidate = SemanticCandidate(
            claim_id=canonical_id,
            claim_text=canonical_text,
            status="unverified",
            cosine_distance=0.10,
            similarity_score=0.90,
            has_negation_mismatch=False,
        )

        with (
            patch(
                "app.api.claims.search_semantic_candidates",
                return_value=[fake_candidate],
            ),
            patch(
                "app.api.claims.classify_claim_pair",
                new_callable=AsyncMock,
                return_value="RELATED",
            ),
        ):
            resp2 = client.post(
                "/claims/check",
                json={"claim_text": "Pakistan scored 300 runs in the match"},
            )
            assert resp2.status_code == 200
            assert resp2.json()["claim_id"] != canonical_id

    def test_uncertain_classification_creates_new_record(self, client):
        """UNCERTAIN classification must NOT merge; safe fallback creates a new record."""
        from app.services.embedding_service import SemanticCandidate

        with patch("app.api.claims.search_semantic_candidates", return_value=[]):
            resp1 = client.post(
                "/claims/check",
                json={"claim_text": "Vaccines are safe"},
            )
            canonical_id = resp1.json()["claim_id"]
            canonical_text = resp1.json()["claim_text"]

        fake_candidate = SemanticCandidate(
            claim_id=canonical_id,
            claim_text=canonical_text,
            status="unverified",
            cosine_distance=0.09,
            similarity_score=0.91,
            has_negation_mismatch=False,
        )

        with (
            patch(
                "app.api.claims.search_semantic_candidates",
                return_value=[fake_candidate],
            ),
            patch(
                "app.api.claims.classify_claim_pair",
                new_callable=AsyncMock,
                return_value="UNCERTAIN",
            ),
        ):
            resp2 = client.post(
                "/claims/check",
                json={"claim_text": "Vaccines may cause side effects"},
            )
            assert resp2.status_code == 200
            assert resp2.json()["claim_id"] != canonical_id

    def test_classification_api_error_creates_new_record_safely(self, client):
        """
        If classify_claim_pair raises an exception (simulated by returning UNCERTAIN),
        the endpoint must not crash and must safely create a new claim.
        """
        from app.services.embedding_service import SemanticCandidate

        with patch("app.api.claims.search_semantic_candidates", return_value=[]):
            resp1 = client.post(
                "/claims/check",
                json={"claim_text": "Vaccines are safe"},
            )
            canonical_id = resp1.json()["claim_id"]
            canonical_text = resp1.json()["claim_text"]

        fake_candidate = SemanticCandidate(
            claim_id=canonical_id,
            claim_text=canonical_text,
            status="unverified",
            cosine_distance=0.05,
            similarity_score=0.95,
            has_negation_mismatch=False,
        )

        with (
            patch(
                "app.api.claims.search_semantic_candidates",
                return_value=[fake_candidate],
            ),
            patch(
                "app.api.claims.classify_claim_pair",
                new_callable=AsyncMock,
                # classify_claim_pair always returns UNCERTAIN on any internal error
                return_value="UNCERTAIN",
            ),
        ):
            resp2 = client.post(
                "/claims/check",
                json={"claim_text": "Vaccines may cause side effects"},
            )
            assert resp2.status_code == 200

    def test_low_similarity_candidate_skips_classification(self, client):
        """
        Candidates with similarity below CLASSIFICATION_SIMILARITY_FLOOR must be
        skipped; classify_claim_pair must not be called for them.
        """
        from app.services.embedding_service import SemanticCandidate
        from app.services.gemini_classification_service import CLASSIFICATION_SIMILARITY_FLOOR

        with patch("app.api.claims.search_semantic_candidates", return_value=[]):
            resp1 = client.post(
                "/claims/check",
                json={"claim_text": "The moon is made of cheese"},
            )
            canonical_id = resp1.json()["claim_id"]
            canonical_text = resp1.json()["claim_text"]

        # Candidate just below the floor
        low_sim_candidate = SemanticCandidate(
            claim_id=canonical_id,
            claim_text=canonical_text,
            status="unverified",
            cosine_distance=1.0 - (CLASSIFICATION_SIMILARITY_FLOOR - 0.01),
            similarity_score=CLASSIFICATION_SIMILARITY_FLOOR - 0.01,
            has_negation_mismatch=False,
        )

        with (
            patch(
                "app.api.claims.search_semantic_candidates",
                return_value=[low_sim_candidate],
            ),
            patch(
                "app.api.claims.classify_claim_pair",
                new_callable=AsyncMock,
                return_value="EQUIVALENT",  # Would merge if called – must NOT be called
            ) as mock_classify,
        ):
            resp2 = client.post(
                "/claims/check",
                json={"claim_text": "Astronauts landed on the moon"},
            )
            assert resp2.status_code == 200
            mock_classify.assert_not_called()

    def test_embedding_failure_creates_claim_without_vector(self, client):
        """
        If embedding generation fails (returns None), the claim is saved with
        embedding=NULL and no classification is attempted.
        """
        with (
            patch(
                "app.api.claims.generate_claim_embedding",
                new_callable=AsyncMock,
                return_value=None,
            ),
            patch(
                "app.api.claims.classify_claim_pair",
                new_callable=AsyncMock,
            ) as mock_classify,
        ):
            resp = client.post(
                "/claims/check",
                json={"claim_text": "Climate change is real"},
            )
            assert resp.status_code == 200
            assert resp.json()["claim_id"] is not None
            mock_classify.assert_not_called()

    def test_multiple_equivalent_submissions_count_as_one_unique_claim(self, client):
        """
        Three different phrasings of the same claim (all classified EQUIVALENT)
        must all map to the same canonical claim_id. Each submission records a
        separate search event (for statistics) but does not inflate claim count.
        """
        from app.services.embedding_service import SemanticCandidate

        # Create canonical claim
        with patch("app.api.claims.search_semantic_candidates", return_value=[]):
            resp1 = client.post(
                "/claims/check",
                json={
                    "claim_text": "The earth orbits the sun",
                    "session_id": "visitor-alpha",
                },
            )
            assert resp1.status_code == 200
            canonical_id = resp1.json()["claim_id"]
            canonical_text = resp1.json()["claim_text"]

        fake_candidate = SemanticCandidate(
            claim_id=canonical_id,
            claim_text=canonical_text,
            status="unverified",
            cosine_distance=0.005,
            similarity_score=0.995,
            has_negation_mismatch=False,
        )

        paraphrases = [
            ("Earth goes around the sun", "visitor-beta"),
            ("Sun is orbited by the Earth", "visitor-gamma"),
        ]

        for paraphrase_text, visitor in paraphrases:
            with (
                patch(
                    "app.api.claims.search_semantic_candidates",
                    return_value=[fake_candidate],
                ),
                patch(
                    "app.api.claims.classify_claim_pair",
                    new_callable=AsyncMock,
                    return_value="EQUIVALENT",
                ),
            ):
                resp = client.post(
                    "/claims/check",
                    json={"claim_text": paraphrase_text, "session_id": visitor},
                )
                assert resp.status_code == 200
                assert resp.json()["claim_id"] == canonical_id, (
                    f"Expected canonical id {canonical_id}, got {resp.json()['claim_id']} "
                    f"for '{paraphrase_text}'"
                )
