from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.db.session import SessionLocal
from app.db.models import User
from app.schemas.profile import ProfileResponse, ProfileUpdateRequest
from app.core.security import hash_password
from app.core.jwt import SECRET_KEY, ALGORITHM

router = APIRouter(tags=["profile"])
security = HTTPBearer()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    try:
        payload = jwt.decode(creds.credentials, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="No autenticado")

    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="No autenticado")

    user = db.query(User).get(payload["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="No autenticado")

    return user


@router.get("/profile", response_model=ProfileResponse)
def get_profile(user: User = Depends(get_current_user)):
    return user


@router.put("/profile", response_model=ProfileResponse)
def update_profile(
    data: ProfileUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if data.email:
        if db.query(User).filter(User.email == data.email, User.id != user.id).first():
            raise HTTPException(status_code=409, detail="El email ya está registrado")
        user.email = data.email

    if data.password:
        user.password_hash = hash_password(data.password)

    db.commit()
    db.refresh(user)
    return user
