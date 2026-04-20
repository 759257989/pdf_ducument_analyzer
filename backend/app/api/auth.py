from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app.auth import create_token, current_user, hash_password, verify_password
from app.db import User, get_db

router = APIRouter()


class AuthIn(BaseModel):
    username: str = Field(min_length=2, max_length=32)
    password: str = Field(min_length=6, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password_bcrypt_bytes_limit(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must be at most 72 bytes for bcrypt")
        return value


class AuthOut(BaseModel):
    token: str
    username: str


@router.post("/auth/register", response_model=AuthOut)
def register(body: AuthIn, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(400, "Username already taken")
    user = User(id=uuid4().hex, username=body.username,
                password_hash=hash_password(body.password))
    db.add(user); db.commit(); db.refresh(user)
    return AuthOut(token=create_token(user.id), username=user.username)


@router.post("/auth/login", response_model=AuthOut)
def login(body: AuthIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == body.username).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(401, "Invalid username or password")
    return AuthOut(token=create_token(user.id), username=user.username)


@router.get("/auth/me")
def me(user: User = Depends(current_user)):
    return {"username": user.username}