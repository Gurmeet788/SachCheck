from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.claim_search import ClaimSearch
    from app.models.fact_check import FactCheck


class Claim(Base):
    __tablename__ = "claims"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    claim_text: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_text: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="unverified",
        server_default="unverified",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    last_checked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    fact_checks: Mapped[List["FactCheck"]] = relationship(
        "FactCheck",
        back_populates="claim",
        cascade="all, delete-orphan",
    )
    searches: Mapped[List["ClaimSearch"]] = relationship(
        "ClaimSearch",
        back_populates="claim",
        cascade="all, delete-orphan",
    )
