import logging
from typing import Generator, Tuple
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

logger = logging.getLogger(__name__)

# SQLAlchemy 2.x Engine using psycopg PostgreSQL driver
engine = create_engine(
    settings.sync_database_url,
    pool_pre_ping=True,
    echo=False,
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency yielding a SQLAlchemy session.
    Guarantees the session is closed after request lifecycle.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> Tuple[bool, str]:
    """
    Executes a 'SELECT 1' test query to verify database connectivity.
    Masks credentials and provides safe, descriptive error messages.
    """
    safe_target = engine.url.render_as_string(hide_password=True)
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            scalar_result = result.scalar()
            if scalar_result == 1:
                return True, f"Database connectivity check passed (target: {safe_target})."
            return False, f"Unexpected response from database: {scalar_result}"
    except SQLAlchemyError as exc:
        # Extract safe high-level error description without exposing passwords
        error_type = type(exc).__name__
        orig_msg = str(getattr(exc, "orig", exc))
        # Mask any potential password leakage in raw error text
        if settings.sync_database_url in orig_msg:
            orig_msg = orig_msg.replace(settings.sync_database_url, safe_target)
        
        logger.error("Database connection failure [%s]: %s", error_type, orig_msg)
        return (
            False,
            f"Database connection error [{error_type}] when connecting to {safe_target}. "
            "Please verify host reachability, SSL configuration, and credentials.",
        )
    except Exception as exc:
        logger.error("Unexpected database error: %s", type(exc).__name__)
        return (
            False,
            f"Unexpected error while attempting to connect to {safe_target}.",
        )


if __name__ == "__main__":
    success, message = check_db_connection()
    status_label = "OK" if success else "FAILED"
    print(f"[{status_label}] {message}")
