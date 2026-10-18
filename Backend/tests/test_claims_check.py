from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.claim import Claim
from app.models.claim_search import ClaimSearch
from app.schemas.claim import GeminiReport


def test_create_new_claim_basic(client: TestClient, db_session: Session):
    """
    Test submitting a new claim:
    - Creates a new claim with initial status unverified.
    - Records a search event.
    - Matches expected ClaimCheckResponse structure.
    """
    with (
        patch("app.api.claims.verify_and_sync_fact_checks", new_callable=AsyncMock) as mock_fact_check,
        patch("app.api.claims.generate_gemini_report", new_callable=AsyncMock) as mock_gemini,
    ):
        mock_fact_check.return_value = ([], "Search completed successfully. No fact-check articles found.")
        mock_gemini.return_value = GeminiReport(
            summary="Insufficient evidence found.",
            evidence_analysis="No articles found.",
            limitations="No indexed data.",
            suggested_correction="Verify with official sources.",
            evidence_sufficient=False,
        )

        response = client.post(
            "/claims/check",
            json={"claim_text": "Drinking saltwater cures all known headaches", "session_id": "sess-alpha-1"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["claim_id"] is not None
        assert data["claim_text"] == "Drinking saltwater cures all known headaches"
        assert data["status"] == "unverified"
        assert data["fact_checks"] == []
        assert data["report"]["evidence_sufficient"] is False

        # Verify database record
        saved_claim = db_session.scalar(select(Claim).where(Claim.id == data["claim_id"]))
        assert saved_claim is not None
        assert saved_claim.claim_text == "Drinking saltwater cures all known headaches"

        # Verify search event
        searches = db_session.scalars(select(ClaimSearch).where(ClaimSearch.claim_id == saved_claim.id)).all()
        assert len(searches) == 1
        assert searches[0].session_id == "sess-alpha-1"


def test_duplicate_claims_reuse_existing_claim_id(client: TestClient, db_session: Session):
    """
    Submitting the same claim (with differences only in case or leading/trailing whitespace)
    must reuse the existing claim record and not create duplicate claims.
    Each search should be appended to the claim_searches table.
    """
    with (
        patch("app.api.claims.verify_and_sync_fact_checks", new_callable=AsyncMock) as mock_fact_check,
        patch("app.api.claims.generate_gemini_report", new_callable=AsyncMock) as mock_gemini,
    ):
        mock_fact_check.return_value = ([], "No articles found.")
        mock_gemini.return_value = GeminiReport(
            summary="Insufficient evidence.",
            evidence_analysis="No articles.",
            limitations="None.",
            suggested_correction="None.",
            evidence_sufficient=False,
        )

        # First submission
        res1 = client.post(
            "/claims/check",
            json={"claim_text": "The moon is made of green cheese"},
            headers={"X-Visitor-ID": "visitor-001"},
        )
        assert res1.status_code == 200
        claim_id_1 = res1.json()["claim_id"]

        # Second submission of identical statement with different casing & whitespace
        res2 = client.post(
            "/claims/check",
            json={"claim_text": "  THE MOON IS MADE OF GREEN CHEESE  "},
            headers={"X-Visitor-ID": "visitor-002"},
        )
        assert res2.status_code == 200
        claim_id_2 = res2.json()["claim_id"]

        # Claim ID must be identical (reused)
        assert claim_id_1 == claim_id_2

        # Verify database contains only 1 Claim row
        all_claims = db_session.scalars(select(Claim)).all()
        assert len(all_claims) == 1

        # Verify database contains 2 ClaimSearch events
        all_searches = db_session.scalars(
            select(ClaimSearch).where(ClaimSearch.claim_id == claim_id_1)
        ).all()
        assert len(all_searches) == 2
        visitor_ids = {s.session_id for s in all_searches}
        assert visitor_ids == {"visitor-001", "visitor-002"}


def test_visitor_id_header_precedence_over_body(client: TestClient, db_session: Session):
    """
    X-Visitor-ID header must take precedence over payload session_id if both are provided.
    """
    with (
        patch("app.api.claims.verify_and_sync_fact_checks", new_callable=AsyncMock) as mock_fact_check,
        patch("app.api.claims.generate_gemini_report", new_callable=AsyncMock) as mock_gemini,
    ):
        mock_fact_check.return_value = ([], "No articles.")
        mock_gemini.return_value = GeminiReport(
            summary="S", evidence_analysis="E", limitations="L", suggested_correction="C", evidence_sufficient=False
        )

        response = client.post(
            "/claims/check",
            json={"claim_text": "Header precedence claim", "session_id": "body-session-id"},
            headers={"X-Visitor-ID": "header-visitor-id"},
        )
        assert response.status_code == 200

        search = db_session.scalar(select(ClaimSearch))
        assert search is not None
        assert search.session_id == "header-visitor-id"


def test_missing_visitor_id_records_search_without_error(client: TestClient, db_session: Session):
    """
    Requests without any visitor ID (missing X-Visitor-ID and missing session_id)
    must still be logged as a raw search event with session_id=None.
    """
    with (
        patch("app.api.claims.verify_and_sync_fact_checks", new_callable=AsyncMock) as mock_fact_check,
        patch("app.api.claims.generate_gemini_report", new_callable=AsyncMock) as mock_gemini,
    ):
        mock_fact_check.return_value = ([], "No articles.")
        mock_gemini.return_value = GeminiReport(
            summary="S", evidence_analysis="E", limitations="L", suggested_correction="C", evidence_sufficient=False
        )

        response = client.post(
            "/claims/check",
            json={"claim_text": "Anonymous search without visitor ID"},
        )
        assert response.status_code == 200

        search = db_session.scalar(select(ClaimSearch))
        assert search is not None
        assert search.session_id is None


def test_empty_and_whitespace_claim_text_rejected(client: TestClient):
    """
    Validation error (422) must be returned when claim_text is empty or whitespace only.
    """
    res1 = client.post("/claims/check", json={"claim_text": ""})
    assert res1.status_code == 422

    res2 = client.post("/claims/check", json={"claim_text": "     "})
    assert res2.status_code == 422


def test_missing_claim_text_rejected(client: TestClient):
    """
    Validation error (422) must be returned when claim_text field is missing.
    """
    response = client.post("/claims/check", json={})
    assert response.status_code == 422
