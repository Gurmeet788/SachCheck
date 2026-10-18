import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.schemas.claim import FactCheckItem, GeminiReport
from app.services.fact_check_service import FactCheckArticle, FactCheckFetchResult, FactCheckOutcome
from app.services.gemini_report_service import (
    build_fallback_report,
    build_insufficient_evidence_report,
    format_evidence_block,
    generate_gemini_report,
)


@pytest.fixture
def sample_fact_checks():
    return [
        FactCheckItem(
            id=1,
            claim_id=10,
            publisher="Lead Stories",
            rating="False",
            source_url="https://leadstories.com/hoax-alert/sample",
            published_at=datetime(2026, 4, 1, 10, 0, tzinfo=timezone.utc),
        )
    ]


@pytest.mark.asyncio
async def test_empty_fact_checks_returns_insufficient_evidence_without_api_call():
    """If there are no fact-check records, do not invoke Gemini; return honest insufficient report."""
    mock_client = AsyncMock()

    report = await generate_gemini_report(
        claim_text="Aliens built the pyramids yesterday",
        fact_checks=[],
        client=mock_client,
    )

    mock_client.post.assert_not_called()
    assert report.evidence_sufficient is False
    assert "Insufficient external evidence" in report.summary
    assert "No published fact-check articles" in report.evidence_analysis


@pytest.mark.asyncio
async def test_successful_gemini_report_generation(sample_fact_checks):
    """Tests successful structured JSON parsing from Gemini API."""
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": json.dumps({
                                "summary": "The claim is refuted by Lead Stories.",
                                "evidence_analysis": "Lead Stories investigated and rated the claim as False.",
                                "limitations": "Only one fact-checking source was indexed.",
                                "suggested_correction": "The claim is inaccurate based on available reporting.",
                                "evidence_sufficient": True,
                            })
                        }
                    ]
                }
            }
        ]
    }
    mock_client.post.return_value = mock_response

    with patch.object(settings, "GEMINI_API_KEY", "test-gemini-key"):
        report = await generate_gemini_report(
            claim_text="Sample fake claim",
            fact_checks=sample_fact_checks,
            client=mock_client,
        )

        assert report.evidence_sufficient is True
        assert report.summary == "The claim is refuted by Lead Stories."
        assert report.suggested_correction == "The claim is inaccurate based on available reporting."


@pytest.mark.asyncio
async def test_gemini_timeout_handling(sample_fact_checks):
    """Tests graceful handling when Gemini API request times out."""
    mock_client = AsyncMock()
    mock_client.post.side_effect = httpx.ReadTimeout("Read timed out")

    with patch.object(settings, "GEMINI_API_KEY", "test-gemini-key"):
        report = await generate_gemini_report(
            claim_text="Sample claim with timeout",
            fact_checks=sample_fact_checks,
            client=mock_client,
        )

        assert report.evidence_sufficient is True
        assert "temporarily unavailable" in report.summary
        assert "request timeout" in report.evidence_analysis


@pytest.mark.asyncio
async def test_gemini_http_error_handling(sample_fact_checks):
    """Tests graceful handling when Gemini API returns 500 or 503."""
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.status_code = 503
    mock_client.post.return_value = mock_response

    with patch.object(settings, "GEMINI_API_KEY", "test-gemini-key"):
        report = await generate_gemini_report(
            claim_text="Sample claim with server error",
            fact_checks=sample_fact_checks,
            client=mock_client,
        )

        assert report.evidence_sufficient is True
        assert "temporarily unavailable" in report.summary
        assert "503" in report.evidence_analysis


@pytest.mark.asyncio
async def test_gemini_malformed_json_handling(sample_fact_checks):
    """Tests handling when model outputs non-JSON or malformed syntax."""
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": "Not valid JSON at all"}]}}]
    }
    mock_client.post.return_value = mock_response

    with patch.object(settings, "GEMINI_API_KEY", "test-gemini-key"):
        report = await generate_gemini_report(
            claim_text="Sample claim with malformed json",
            fact_checks=sample_fact_checks,
            client=mock_client,
        )

        assert report.evidence_sufficient is True
        assert "temporarily unavailable" in report.summary


@pytest.mark.asyncio
async def test_missing_api_key(sample_fact_checks):
    """Tests handling when GEMINI_API_KEY is blank."""
    with patch.object(settings, "GEMINI_API_KEY", ""):
        report = await generate_gemini_report(
            claim_text="Any claim",
            fact_checks=sample_fact_checks,
        )
        assert "API key not configured" in report.evidence_analysis


def test_format_evidence_block_delimiters(sample_fact_checks):
    """Tests that evidence is wrapped in <untrusted_evidence> tags for prompt injection defense."""
    text = format_evidence_block("Test Claim", sample_fact_checks)
    assert text.startswith("<untrusted_evidence>")
    assert text.endswith("</untrusted_evidence>")
    assert "Lead Stories" in text
    assert "False" in text
    assert "https://leadstories.com/hoax-alert/sample" in text


def test_claims_check_endpoint_with_evidence_includes_report(client: TestClient):
    """Verifies POST /claims/check returns report alongside claim and fact_checks."""
    fake_article = FactCheckArticle(
        publisher="PolitiFact",
        rating="False",
        source_url="https://politifact.com/factchecks/2026/sample-claim-1",
        published_at=datetime(2026, 2, 20, tzinfo=timezone.utc),
    )

    fake_report = GeminiReport(
        summary="PolitiFact evaluated this claim as False.",
        evidence_analysis="PolitiFact found no basis for the assertion.",
        limitations="Based on a single review.",
        suggested_correction="The assertion is unproven and false.",
        evidence_sufficient=True,
    )

    with patch(
        "app.services.fact_check_service.fetch_google_fact_checks",
        new=AsyncMock(return_value=FactCheckFetchResult(
            outcome=FactCheckOutcome.MATCHES_FOUND,
            articles=[fake_article],
        )),
    ), patch(
        "app.api.claims.generate_gemini_report",
        new=AsyncMock(return_value=fake_report),
    ):
        response = client.post(
            "/claims/check",
            json={"claim_text": "Vaccines contain microchips", "session_id": "test-gemini-session-1"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "claim_id" in data
        assert data["status"] == "fact_checked"
        assert "fact_checks" in data
        assert "report" in data
        assert data["report"] is not None
        assert data["report"]["summary"] == "PolitiFact evaluated this claim as False."
        assert data["report"]["evidence_sufficient"] is True


def test_claims_check_endpoint_no_evidence_returns_honest_report(client: TestClient):
    """Verifies POST /claims/check with no evidence returns honest insufficient report."""
    with patch(
        "app.services.fact_check_service.fetch_google_fact_checks",
        new=AsyncMock(return_value=FactCheckFetchResult(
            outcome=FactCheckOutcome.NO_MATCHES,
            articles=[],
        )),
    ):
        response = client.post(
            "/claims/check",
            json={"claim_text": "Obscure Unmatched Claim 998877", "session_id": "test-gemini-session-2"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unverified"
        assert "report" in data
        assert data["report"] is not None
        assert data["report"]["evidence_sufficient"] is False
        assert "Insufficient external evidence" in data["report"]["summary"]


def test_claims_check_endpoint_gemini_failure_gracefully_handled(client: TestClient):
    """Verifies endpoint does not crash when Gemini fails."""
    fallback = build_fallback_report(fact_checks_exist=True, failure_reason="service error 500")

    with patch(
        "app.services.fact_check_service.fetch_google_fact_checks",
        new=AsyncMock(return_value=FactCheckFetchResult(
            outcome=FactCheckOutcome.MATCHES_FOUND,
            articles=[FactCheckArticle(
                publisher="Snopes",
                rating="Unproven",
                source_url="https://snopes.com/claim-500",
                published_at=None,
            )],
        )),
    ), patch(
        "app.api.claims.generate_gemini_report",
        new=AsyncMock(return_value=fallback),
    ):
        response = client.post(
            "/claims/check",
            json={"claim_text": "Claim testing gemini failure", "session_id": "test-gemini-session-3"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "report" in data
        assert "temporarily unavailable" in data["report"]["summary"]
