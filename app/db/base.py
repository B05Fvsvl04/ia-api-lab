from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

from app.db.models.user import User
from app.db.models.refresh_token import RefreshToken
from app.db.models.login_attempt import LoginAttempt
