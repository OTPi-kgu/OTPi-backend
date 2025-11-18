from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from pydantic import BaseModel, EmailStr, validator

KST = ZoneInfo("Asia/Seoul")


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr


class OTPRequest(BaseModel):
    email: EmailStr


class OTPVerifyRequest(BaseModel):
    code: str
    email: EmailStr


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime
    last_login_at: datetime | None

    @validator("created_at", "last_login_at", pre=False)
    def convert_to_kst(cls, v: datetime | None):
        if v is None:
            return v
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        return v.astimezone(KST)

    class Config:
        orm_mode = True
