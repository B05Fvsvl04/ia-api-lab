import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    jti: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        nullable=False,
        index=True
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    issued_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    used: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    used_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    user = relationship("User")
