import uuid
from datetime import datetime

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    username: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        unique=True,
        index=True
    )

    email: Mapped[str] = mapped_column(
        String(254),
        nullable=False,
        unique=True,
        index=True
    )

    password_hash: Mapped[str] = mapped_column(
        String(128),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
