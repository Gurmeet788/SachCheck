from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.claim import Claim
from app.models.claim_search import ClaimSearch
from app.models.fact_check import FactCheck


def test_empty_platform_statistics(client: TestClient):
    """
    When the database is empty, GET /stats must return zeros for all counts.
    """
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert data == {
        "total_claims": 0,
        "total_fact_checks": 0,
        "total_search_events": 0,
        "distinct_visitor_ids_24h": 0,
    }


def test_empty_trending_claims(client: TestClient):
    """
    When no claims or searches exist, GET /claims/trending must return an empty list.
    """
    response = client.get("/claims/trending")
    assert response.status_code == 200
    assert response.json() == []


def test_trending_ranking_and_visitor_deduplication(client: TestClient, db_session: Session):
    """
    Verify:
    - Same visitor searching multiple times counts as 1 distinct visitor for that claim.
    - Different visitors increase count.
    - Anonymous searches (no visitor ID) do not count as distinct visitors.
    - Searches older than 24 hours are excluded.
    - Claims are ranked by highest distinct visitor count descending.
    - Limit parameter restricts results.
    """
    now = datetime.now(timezone.utc)

    # Claim 1: Will have 3 distinct visitors (plus duplicate searches by the same visitor)
    claim1 = Claim(
        claim_text="Claim Alpha - High Interest",
        normalized_text="claim alpha - high interest",
        status="fact_checked",
        created_at=now,
    )
    # Claim 2: Will have 1 distinct visitor
    claim2 = Claim(
        claim_text="Claim Beta - Moderate Interest",
        normalized_text="claim beta - moderate interest",
        status="unverified",
        created_at=now,
    )
    # Claim 3: Only has anonymous searches and old searches -> should NOT appear in trending
    claim3 = Claim(
        claim_text="Claim Gamma - Expired or Anonymous Searches",
        normalized_text="claim gamma - expired or anonymous searches",
        status="unverified",
        created_at=now,
    )

    db_session.add_all([claim1, claim2, claim3])
    db_session.commit()

    # Searches for Claim 1:
    # Visitor A searches 5 times (should only count as 1 distinct visitor)
    for _ in range(5):
        db_session.add(ClaimSearch(claim_id=claim1.id, session_id="visitor-A", searched_at=now))
    # Visitor B searches once
    db_session.add(ClaimSearch(claim_id=claim1.id, session_id="visitor-B", searched_at=now))
    # Visitor C searches once
    db_session.add(ClaimSearch(claim_id=claim1.id, session_id="visitor-C", searched_at=now))
    # Anonymous search for Claim 1 (must not increment distinct visitors)
    db_session.add(ClaimSearch(claim_id=claim1.id, session_id=None, searched_at=now))

    # Searches for Claim 2:
    # Visitor D searches 3 times
    for _ in range(3):
        db_session.add(ClaimSearch(claim_id=claim2.id, session_id="visitor-D", searched_at=now))

    # Searches for Claim 3:
    # Search older than 24 hours (25 hours ago)
    old_time = now - timedelta(hours=25)
    db_session.add(ClaimSearch(claim_id=claim3.id, session_id="visitor-Old", searched_at=old_time))
    # Anonymous search
    db_session.add(ClaimSearch(claim_id=claim3.id, session_id=None, searched_at=now))
    db_session.add(ClaimSearch(claim_id=claim3.id, session_id="", searched_at=now))

    db_session.commit()

    # Query GET /claims/trending
    response = client.get("/claims/trending")
    assert response.status_code == 200
    trending = response.json()

    # Expecting 2 claims (claim1 with count 3, claim2 with count 1; claim3 excluded)
    assert len(trending) == 2

    # Verify ranking
    assert trending[0]["claim_id"] == claim1.id
    assert trending[0]["claim_text"] == "Claim Alpha - High Interest"
    assert trending[0]["status"] == "fact_checked"
    assert trending[0]["distinct_visitor_count"] == 3

    assert trending[1]["claim_id"] == claim2.id
    assert trending[1]["claim_text"] == "Claim Beta - Moderate Interest"
    assert trending[1]["status"] == "unverified"
    assert trending[1]["distinct_visitor_count"] == 1

    # Verify limit parameter
    limited_response = client.get("/claims/trending?limit=1")
    assert limited_response.status_code == 200
    limited_trending = limited_response.json()
    assert len(limited_trending) == 1
    assert limited_trending[0]["claim_id"] == claim1.id


def test_platform_stats_aggregation(client: TestClient, db_session: Session):
    """
    Verify /stats endpoint accurately calculates:
    - total_claims
    - total_fact_checks
    - total_search_events
    - distinct_visitor_ids_24h across all searches
    """
    now = datetime.now(timezone.utc)
    old_time = now - timedelta(hours=30)

    # 1. Add claims
    c1 = Claim(claim_text="Stats Claim 1", normalized_text="stats claim 1", status="fact_checked", created_at=now)
    c2 = Claim(claim_text="Stats Claim 2", normalized_text="stats claim 2", status="unverified", created_at=now)
    db_session.add_all([c1, c2])
    db_session.commit()

    # 2. Add fact checks
    fc1 = FactCheck(claim_id=c1.id, publisher="Snopes", rating="False", source_url="https://snopes.com/1", retrieved_at=now)
    fc2 = FactCheck(claim_id=c1.id, publisher="PolitiFact", rating="Pants on Fire", source_url="https://politifact.com/2", retrieved_at=now)
    db_session.add_all([fc1, fc2])

    # 3. Add search events
    # visitor-X searches c1
    db_session.add(ClaimSearch(claim_id=c1.id, session_id="visitor-X", searched_at=now))
    # visitor-X also searches c2 (should count as 1 distinct visitor overall)
    db_session.add(ClaimSearch(claim_id=c2.id, session_id="visitor-X", searched_at=now))
    # visitor-Y searches c1
    db_session.add(ClaimSearch(claim_id=c1.id, session_id="visitor-Y", searched_at=now))
    # Anonymous search (session_id is None)
    db_session.add(ClaimSearch(claim_id=c1.id, session_id=None, searched_at=now))
    # Old search (older than 24h)
    db_session.add(ClaimSearch(claim_id=c2.id, session_id="visitor-Z", searched_at=old_time))

    db_session.commit()

    # Execute request
    response = client.get("/stats")
    assert response.status_code == 200
    stats = response.json()

    assert stats["total_claims"] == 2
    assert stats["total_fact_checks"] == 2
    assert stats["total_search_events"] == 5
    # distinct_visitor_ids_24h within 24h: visitor-X, visitor-Y -> 2
    assert stats["distinct_visitor_ids_24h"] == 2


def test_trending_invalid_limit_query_param(client: TestClient):
    """Query parameter validation: limit < 1 or limit > 100 must fail with 422."""
    res_zero = client.get("/claims/trending?limit=0")
    assert res_zero.status_code == 422

    res_negative = client.get("/claims/trending?limit=-5")
    assert res_negative.status_code == 422

    res_too_large = client.get("/claims/trending?limit=101")
    assert res_too_large.status_code == 422
