from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import Base


class RaceSessionModel(Base):
    __tablename__ = "race_sessions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
    )

    session_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    source_file: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    source_system: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )