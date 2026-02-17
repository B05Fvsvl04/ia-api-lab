from datetime import datetime

from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class LoginAttempt(Base):
    __tablename__ = "login_attempts"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    username: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True
    )

    ip_address: Mapped[str] = mapped_column(
        String(45),
        nullable=False,
        index=True
    )

    success: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )
