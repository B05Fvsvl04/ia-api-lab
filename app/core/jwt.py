import os
import uuid
from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = os.environ["JWT_SECRET"]
ALGORITHM = "HS256"


def create_access_token(user_id: str, username: str) -> str:
    payload = {
        "sub": user_id,
        "username": username,
        "type": "access",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=30),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(user_id: str) -> tuple[str, str, datetime]:
    jti = str(uuid.uuid4())
    exp = datetime.utcnow() + timedelta(days=7)
    payload = {
        "sub": user_id,
        "jti": jti,
        "type": "refresh",
        "iat": datetime.utcnow(),
        "exp": exp,
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token, jti, exp
