from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.db.session import SessionLocal
from app.db.models import User, RefreshToken, LoginAttempt
from app.schemas.auth import (
    RegisterRequest, LoginRequest, TokenResponse, RefreshRequest
)
from app.core.security import hash_password, verify_password
from app.core.jwt import create_access_token, create_refresh_token
from app.core.jwt import SECRET_KEY, ALGORITHM

router = APIRouter(tags=["auth"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register", status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(
        (User.username.ilike(data.username)) | (User.email == data.email)
    ).first():
        raise HTTPException(status_code=409, detail="El nombre de usuario o email ya está registrado")

    user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "created_at": user.created_at
    }


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username.ilike(data.username)).first()

    success = user and verify_password(data.password, user.password_hash)

    db.add(LoginAttempt(
        username=data.username,
        ip_address="unknown",
        success=bool(success)
    ))
    db.commit()

    if not success:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    access_token = create_access_token(user.id, user.username)
    refresh_token, jti, exp = create_refresh_token(user.id)

    db.add(RefreshToken(
        jti=jti,
        user_id=user.id,
        expires_at=exp
    ))
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


@router.post("/refresh", response_model=TokenResponse)
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(data.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Token de actualización inválido")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Token de actualización inválido")

    token = db.query(RefreshToken).filter_by(jti=payload["jti"]).first()

    if not token:
        raise HTTPException(status_code=401, detail="Token de actualización inválido")

    if token.used:
        raise HTTPException(status_code=401, detail="Token de actualización ya utilizado")

    token.used = True
    db.commit()

    access = create_access_token(payload["sub"], "")
    refresh, jti, exp = create_refresh_token(payload["sub"])

    db.add(RefreshToken(
        jti=jti,
        user_id=payload["sub"],
        expires_at=exp
    ))
    db.commit()

    return {
        "access_token": access,
        "refresh_token": refresh
    }
