from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.claim import Claim
from app.models.fact_check import FactCheck
from app.services.fact_check_service import (
    FactCheckArticle,
    FactCheckFetchResult,
    FactCheckOutcome,
    fetch_google_fact_checks,
    parse_review_date,
    verify_and_sync_fact_checks,
)


def test_parse_review_date_rfc3339():
    dt = parse_review_date("2026-08-21T00:00:00Z")
    assert dt is not None
    assert dt.year == 2026
    assert dt.month == 8
    assert dt.day == 21


def test_parse_review_date_date_only():
    dt = parse_review_date("2026-08-21")
    assert dt is not None
    assert dt.year == 2026
    assert dt.month == 8
    assert dt.day == 21


def test_parse_review_date_invalid_or_empty():
    assert parse_review_date(None) is None
    assert parse_review_date("") is None
    assert parse_review_date("not-a-valid-date") is None


@pytest.mark.asyncio
async def test_fetch_with_matches():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "claims": [
            {
                "text": "The moon is made of green cheese",
                "claimReview": [
                    {
                        "publisher": {"name": "Science Checker", "site": "sciencechecker.org"},
                        "url": "https://sciencechecker.org/moon-cheese",
                        "textualRating": "False",
                        "reviewDate": "2026-05-10T12:00:00Z",
                    }
                ],
            }
        ]
    }

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response

    with patch.object(settings, "GOOGLE_FACT_CHECK_API_KEY", "test-key"):
        result = await fetch_google_fact_checks("moon cheese", client=mock_client)
        assert result.outcome == FactCheckOutcome.MATCHES_FOUND
        assert len(result.articles) == 1
        assert result.articles[0].publisher == "Science Checker"
        assert result.articles[0].rating == "False"
        assert result.articles[0].source_url == "https://sciencechecker.org/moon-cheese"


@pytest.mark.asyncio
async def test_fetch_no_matches():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response

    with patch.object(settings, "GOOGLE_FACT_CHECK_API_KEY", "test-key"):
        result = await fetch_google_fact_checks("nonexistent topic", client=mock_client)
        assert result.outcome == FactCheckOutcome.NO_MATCHES
        assert len(result.articles) == 0


@pytest.mark.asyncio
async def test_fetch_timeout_handling():
    mock_client = AsyncMock()
    mock_client.get.side_effect = httpx.ReadTimeout("Request timed out")

    with patch.object(settings, "GOOGLE_FACT_CHECK_API_KEY", "test-key"):
        result = await fetch_google_fact_checks("slow query", client=mock_client)
        assert result.outcome == FactCheckOutcome.SERVICE_TIMEOUT
        assert len(result.articles) == 0
        assert "timed out" in result.error_message


@pytest.mark.asyncio
async def test_fetch_http_error_handling():
    mock_response = MagicMock()
    mock_response.status_code = 503

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response

    with patch.object(settings, "GOOGLE_FACT_CHECK_API_KEY", "test-key"):
        result = await fetch_google_fact_checks("server error query", client=mock_client)
        assert result.outcome == FactCheckOutcome.SERVICE_ERROR
        assert "503" in result.error_message


@pytest.mark.asyncio
async def test_fetch_missing_api_key():
    with patch.object(settings, "GOOGLE_FACT_CHECK_API_KEY", ""):
        result = await fetch_google_fact_checks("any query")
        assert result.outcome == FactCheckOutcome.NOT_CONFIGURED


@pytest.mark.asyncio
async def test_verify_and_sync_fact_checks_service(db_session: Session):
    """
    Test direct service integration with isolated SQLite database:
    - Inserts new fact-checks
    - Updates claim status to fact_checked
    - Avoids duplicate records for the same source_url
    """
    claim = Claim(
        claim_text="Service verification claim",
        normalized_text="service verification claim",
        status="unverified",
    )
    db_session.add(claim)
    db_session.commit()
    db_session.refresh(claim)

    fake_result = FactCheckFetchResult(
        outcome=FactCheckOutcome.MATCHES_FOUND,
        articles=[
            FactCheckArticle(
                publisher="P1",
                rating="False",
                source_url="https://p1.org/review-1",
                published_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            ),
            FactCheckArticle(
                publisher="P2",
                rating="Mostly False",
                source_url="https://p2.org/review-2",
                published_at=datetime(2026, 1, 2, tzinfo=timezone.utc),
            ),
        ],
    )

    with patch("app.services.fact_check_service.fetch_google_fact_checks", new=AsyncMock(return_value=fake_result)):
        records, message = await verify_and_sync_fact_checks(db_session, claim)
        assert len(records) == 2
        assert claim.status == "fact_checked"
        assert "Added 2 new record(s)" in message

        # Run again with the same articles to test deduplication
        records_repeat, msg_repeat = await verify_and_sync_fact_checks(db_session, claim)
        assert len(records_repeat) == 2
        assert "already up to date" in msg_repeat


def test_check_claim_api_success_with_mocked_articles(client: TestClient):
    fake_articles = [
        FactCheckArticle(
            publisher="Test Fact Checker",
            rating="Mostly False",
            source_url="https://factcheck.example.com/claim-1",
            published_at=datetime(2026, 1, 15, tzinfo=timezone.utc),
        ),
    ]

    with patch(
        "app.services.fact_check_service.fetch_google_fact_checks",
        new=AsyncMock(return_value=FactCheckFetchResult(
            outcome=FactCheckOutcome.MATCHES_FOUND,
            articles=fake_articles,
        )),
    ):
        response = client.post(
            "/claims/check",
            json={
                "claim_text": "Unit Test Claim: Humans only use 10% of their brains",
                "session_id": "test-session-123",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "fact_checked"
        assert "Fact-check articles found" in data["message"]
        assert len(data["fact_checks"]) >= 1
        first_fc = data["fact_checks"][0]
        assert first_fc["publisher"] == "Test Fact Checker"
        assert first_fc["rating"] == "Mostly False"
        assert first_fc["source_url"] == "https://factcheck.example.com/claim-1"


def test_check_claim_api_no_match(client: TestClient):
    with patch(
        "app.services.fact_check_service.fetch_google_fact_checks",
        new=AsyncMock(return_value=FactCheckFetchResult(
            outcome=FactCheckOutcome.NO_MATCHES,
            articles=[],
        )),
    ):
        response = client.post(
            "/claims/check",
            json={
                "claim_text": "Random Unverified Claim XYZ 987654321",
                "session_id": "test-session-456",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unverified"
        assert "No fact-check articles found" in data["message"]
        assert len(data["fact_checks"]) == 0


def test_check_claim_api_service_timeout(client: TestClient):
    with patch(
        "app.services.fact_check_service.fetch_google_fact_checks",
        new=AsyncMock(return_value=FactCheckFetchResult(
            outcome=FactCheckOutcome.SERVICE_TIMEOUT,
            articles=[],
            error_message="External fact-check service timed out.",
        )),
    ):
        response = client.post(
            "/claims/check",
            json={
                "claim_text": "Timeout Test Claim Statement",
                "session_id": "test-session-timeout",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unverified"
        assert "timed out" in data["message"].lower()
