# schemas.py
from datetime import datetime

from pydantic import BaseModel, EmailStr


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
    last_login_at: datetime | None = None


class Config:
   from_attributes = True