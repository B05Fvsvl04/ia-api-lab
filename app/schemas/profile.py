from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class ProfileResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime


class ProfileUpdateRequest(BaseModel):
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)
