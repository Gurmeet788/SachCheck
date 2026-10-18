from unittest.mock import AsyncMock, patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.claim import Claim
from app.models.claim_search import ClaimSearch
from app.schemas.claim import GeminiReport
from app.services.claim_service import check_or_record_claim, normalize_claim_text


# ============================================================================
# Unit Tests for normalize_claim_text
# ============================================================================

def test_normalize_leading_articles_equivalent():
    """Verify 'The earth is flat', 'earth is flat', and other article variations normalize identically."""
    assert normalize_claim_text("The earth is flat") == "earth is flat"
    assert normalize_claim_text("earth is flat") == "earth is flat"
    assert normalize_claim_text("A secret base exists on Mars") == "secret base exists on mars"
    assert normalize_claim_text("secret base exists on Mars") == "secret base exists on mars"
    assert normalize_claim_text("An asteroid will impact the planet") == "asteroid will impact the planet"
    assert normalize_claim_text("asteroid will impact the planet") == "asteroid will impact the planet"


def test_normalize_does_not_strip_non_article_words():
    """
    Ensure words merely starting with 'the', 'a', or 'an' (or inside the sentence)
    are NOT erroneously stripped.
    """
    assert normalize_claim_text("Theme park was closed") == "theme park was closed"
    assert normalize_claim_text("There is an earthquake") == "there is an earthquake"
    assert normalize_claim_text("Theater tickets are free") == "theater tickets are free"
    assert normalize_claim_text("Theology studies religion") == "theology studies religion"
    assert normalize_claim_text("Anonymous sources confirmed the report") == "anonymous sources confirmed the report"
    assert normalize_claim_text("Apple released a new device") == "apple released a new device"
    # Internal 'the' must be preserved
    assert normalize_claim_text("Visiting the White House") == "visiting the white house"


def test_normalize_capitalization_and_whitespace():
    """Handle all variations of casing and internal/surrounding whitespace."""
    assert normalize_claim_text("THE EARTH IS FLAT") == "earth is flat"
    assert normalize_claim_text("   The   \t  earth   \n   is   flat   ") == "earth is flat"
    assert normalize_claim_text("Earth   Is   Flat") == "earth is flat"


def test_normalize_harmless_trailing_punctuation_and_quotes():
    """Strip harmless trailing punctuation and surrounding quotes without affecting internal punctuation."""
    assert normalize_claim_text("The earth is flat.") == "earth is flat"
    assert normalize_claim_text("The earth is flat!") == "earth is flat"
    assert normalize_claim_text("The earth is flat?") == "earth is flat"
    assert normalize_claim_text("The earth is flat...") == "earth is flat"
    assert normalize_claim_text("The earth is flat!?!") == "earth is flat"
    assert normalize_claim_text("The earth is flat;") == "earth is flat"
    assert normalize_claim_text("The earth is flat, ") == "earth is flat"
    assert normalize_claim_text('"The earth is flat"') == "earth is flat"
    assert normalize_claim_text("'The earth is flat.'") == "earth is flat"
    assert normalize_claim_text("“The earth is flat.”") == "earth is flat"
    assert normalize_claim_text("‘The earth is flat!’") == "earth is flat"


def test_normalize_preserves_internal_punctuation():
    """Internal punctuation crucial to claim meaning (hyphens, decimals, apostrophes) must be kept."""
    assert normalize_claim_text("COVID-19 was created in a lab.") == "covid-19 was created in a lab"
    assert normalize_claim_text("Inflation reached 8.5% in the U.S.") == "inflation reached 8.5% in the u.s"
    assert normalize_claim_text("It's a proven scientific fact.") == "it's a proven scientific fact"


def test_normalize_genuinely_different_claims_remain_distinct():
    """
    Ensure claims with different semantics, negations, or topics
    produce distinct normalized outputs and are never conflated.
    """
    norm_flat = normalize_claim_text("The earth is flat")
    norm_round = normalize_claim_text("The earth is round")
    norm_not_flat = normalize_claim_text("The earth is not flat")

    assert norm_flat == "earth is flat"
    assert norm_round == "earth is round"
    assert norm_not_flat == "earth is not flat"

    assert norm_flat != norm_round
    assert norm_flat != norm_not_flat
    assert norm_round != norm_not_flat

    # Medical / scientific distinctions
    assert (
        normalize_claim_text("Vaccines cause autism")
        != normalize_claim_text("Vaccines do not cause autism")
    )
    assert (
        normalize_claim_text("Drinking water cures headaches")
        != normalize_claim_text("Drinking saltwater cures headaches")
    )


# ============================================================================
# Service Layer Tests for check_or_record_claim
# ============================================================================

def test_check_or_record_claim_treats_the_earth_is_flat_and_earth_is_flat_as_duplicates(
    db_session: Session,
):
    """
    Requirement:
    Treat 'The earth is flat' and 'earth is flat' as duplicates.
    Preserve the original claim text of the first submission.
    Log separate search records for each submission.
    """
    claim1 = check_or_record_claim(db_session, "The earth is flat", session_id="v-1")
    assert claim1.id is not None
    assert claim1.claim_text == "The earth is flat"
    assert claim1.normalized_text == "earth is flat"

    claim2 = check_or_record_claim(db_session, "earth is flat", session_id="v-2")
    # Same claim record reused
    assert claim2.id == claim1.id
    # Original claim text preserved
    assert claim2.claim_text == "The earth is flat"

    # Only 1 row in claims table
    all_claims = db_session.scalars(select(Claim)).all()
    assert len(all_claims) == 1

    # Both search events recorded
    searches = db_session.scalars(
        select(ClaimSearch).where(ClaimSearch.claim_id == claim1.id)
    ).all()
    assert len(searches) == 2
    assert {s.session_id for s in searches} == {"v-1", "v-2"}


def test_check_or_record_claim_equivalent_variations(db_session: Session):
    """Multiple equivalent variations map to the same claim record."""
    variations = [
        "The earth is flat.",
        "  the   earth   is   flat!  ",
        "THE EARTH IS FLAT",
        '"earth is flat?"',
        "“The earth is flat...”",
    ]

    claim_ids = set()
    for text in variations:
        c = check_or_record_claim(db_session, text, session_id="session-var")
        claim_ids.add(c.id)

    # Exactly one claim record created
    assert len(claim_ids) == 1
    # 5 searches logged
    all_searches = db_session.scalars(select(ClaimSearch)).all()
    assert len(all_searches) == len(variations)


def test_check_or_record_claim_genuinely_different_claims_create_separate_records(
    db_session: Session,
):
    """Genuinely different claims must create separate database records."""
    c1 = check_or_record_claim(db_session, "The earth is flat")
    c2 = check_or_record_claim(db_session, "The earth is round")
    c3 = check_or_record_claim(db_session, "The earth is not flat")

    assert c1.id != c2.id
    assert c1.id != c3.id
    assert c2.id != c3.id

    assert c1.claim_text == "The earth is flat"
    assert c2.claim_text == "The earth is round"
    assert c3.claim_text == "The earth is not flat"

    all_claims = db_session.scalars(select(Claim)).all()
    assert len(all_claims) == 3


def test_check_or_record_claim_handles_concurrency_race_condition(db_session: Session):
    """
    Test that when an IntegrityError is raised during flush (simulating a concurrent
    transaction inserting the exact same normalized claim in parallel), the function
    catches the error, rolls back, queries the committed claim, and logs the search event.
    """
    # 1. Create a claim committed by another transaction
    committed_claim = Claim(
        claim_text="Concurrent claim statement",
        normalized_text="concurrent claim statement",
        status="unverified",
    )
    db_session.add(committed_claim)
    db_session.commit()

    query_count = 0

    class MockScalars:
        def first(self):
            nonlocal query_count
            query_count += 1
            if query_count == 1:
                return None  # First check found nothing (concurrent race)
            # Second check after rollback finds the committed claim
            return committed_claim

    original_flush = db_session.flush
    flush_called = False

    def simulated_flush():
        nonlocal flush_called
        if not flush_called:
            flush_called = True
            raise IntegrityError("duplicate key", params=None, orig=None)
        return original_flush()

    with (
        patch.object(db_session, "scalars", return_value=MockScalars()),
        patch.object(db_session, "flush", side_effect=simulated_flush),
    ):
        resolved_claim = check_or_record_claim(db_session, "  the concurrent claim statement.  ")
        assert resolved_claim.id == committed_claim.id



# ============================================================================
# End-to-End API Tests on POST /claims/check & Trending Integration
# ============================================================================

def test_api_deduplication_and_trending_count(client: TestClient):
    """
    End-to-end integration test:
    1. Check 'The earth is flat' with visitor 1.
    2. Check 'earth is flat' with visitor 2.
    3. Check 'THE EARTH IS FLAT.' with visitor 3.
    4. Assert all return the same claim_id and original claim_text.
    5. Assert GET /claims/trending ranks this single claim with distinct_visitor_count = 3.
    """
    dummy_report = GeminiReport(
        summary="Summary",
        evidence_analysis="Analysis",
        limitations="None",
        suggested_correction="Correction",
        evidence_sufficient=False,
    )

    with (
        patch("app.api.claims.verify_and_sync_fact_checks", new_callable=AsyncMock) as mock_fact_check,
        patch("app.api.claims.generate_gemini_report", new_callable=AsyncMock) as mock_gemini,
    ):
        mock_fact_check.return_value = ([], "No articles found.")
        mock_gemini.return_value = dummy_report

        # Request 1: "The earth is flat"
        res1 = client.post(
            "/claims/check",
            json={"claim_text": "The earth is flat"},
            headers={"X-Visitor-ID": "visitor-alpha"},
        )
        assert res1.status_code == 200
        data1 = res1.json()
        claim_id = data1["claim_id"]
        assert data1["claim_text"] == "The earth is flat"

        # Request 2: "earth is flat" (omitting leading 'The')
        res2 = client.post(
            "/claims/check",
            json={"claim_text": "earth is flat"},
            headers={"X-Visitor-ID": "visitor-beta"},
        )
        assert res2.status_code == 200
        data2 = res2.json()
        assert data2["claim_id"] == claim_id
        # Preserves original text
        assert data2["claim_text"] == "The earth is flat"

        # Request 3: "THE EARTH IS FLAT." (all caps + trailing punctuation)
        res3 = client.post(
            "/claims/check",
            json={"claim_text": "THE EARTH IS FLAT."},
            headers={"X-Visitor-ID": "visitor-gamma"},
        )
        assert res3.status_code == 200
        data3 = res3.json()
        assert data3["claim_id"] == claim_id
        assert data3["claim_text"] == "The earth is flat"

        # Check trending claims: should have 1 trending claim with distinct_visitor_count = 3
        trending_res = client.get("/claims/trending")
        assert trending_res.status_code == 200
        trending = trending_res.json()
        assert len(trending) == 1
        assert trending[0]["claim_id"] == claim_id
        assert trending[0]["claim_text"] == "The earth is flat"
        assert trending[0]["distinct_visitor_count"] == 3
