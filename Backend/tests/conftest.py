import os
from typing import Generator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app

# In-memory SQLite engine configured for thread-safe testing
# StaticPool ensures all connections in the test process share the exact same in-memory DB
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Ensure safe testing environment variables are set."""
    os.environ["GOOGLE_FACT_CHECK_API_KEY"] = "test-google-factcheck-api-key"
    os.environ["GEMINI_API_KEY"] = "test-gemini-api-key"
    yield


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Creates fresh database schema in memory for each test function,
    yields a session, and drops all tables on teardown.
    Completely isolates tests from Supabase and from other tests.
    """
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    Provides a FastAPI TestClient with the get_db dependency overridden
    to use the isolated SQLite in-memory database.
    """
    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
