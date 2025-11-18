# backend/config.py
import os

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

class Settings(BaseModel):
    PROJECT_NAME: str = "OTP Backend"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    DATABASE_URL: str = os.getenv("DATABASE_URL")

    SMTP_HOST: str | None = os.getenv("SMTP_HOST")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str | None = os.getenv("SMTP_USER")
    SMTP_PASSWORD: str | None = os.getenv("SMTP_PASSWORD")

    OTP_INTERVAL: int = int(os.getenv("OTP_INTERVAL", "90"))
    OTP_DIGITS: int = int(os.getenv("OTP_DIGITS", "6"))
settings = Settings()
