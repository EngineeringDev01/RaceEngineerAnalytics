from __future__ import annotations

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import Base


class KPIModel(Base):
    __tablename__ = "kpis"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    race_session_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "race_sessions.id",
            ondelete="CASCADE",
        ),
        nullable=True,
        index=True,
    )

    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
    )

    value: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    unit: Mapped[str] = mapped_column(
        String(50),
        default="",
        nullable=False,
    )

    source_channel: Mapped[str] = mapped_column(
        String(150),
        default="",
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        default="",
        nullable=False,
    )