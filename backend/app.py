# main.py
import secrets
from datetime import datetime, timezone

from backend.models import User
from backend.schemas import (OTPRequest, OTPVerifyRequest, RegisterRequest,
                             UserResponse)
from fastapi import Cookie, Depends, FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from otpi import OTPi
from sqlalchemy.orm import Session

from .config import settings
from .database import Base, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    debug=settings.DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_current_user(
    db: Session = Depends(get_db),
    token: str | None = Cookie(default=None),
):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="로그인이 필요합니다.",
        )

    user = db.query(User).filter(User.token == token).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 세션입니다.",
        )

    return user

@app.get("/me", response_model=UserResponse, tags=["auth"])
def me(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/", tags=["health"])
def root():
    return {"message": "OTP Backend is running."}


@app.post("/register", response_model=UserResponse, tags=["auth"])
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        return existing

    secret = OTPi.generate_secret()

    user = User(
        name=payload.name,
        email=payload.email,
        secret=secret,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user

@app.post("/request-otp", tags=["auth"])
def request_otp(
    payload: OTPRequest,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="등록되지 않은 이메일입니다.",
        )

    if not (settings.SMTP_USER and settings.SMTP_PASSWORD and settings.SMTP_HOST):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SMTP 설정이 누락되어 있습니다. 서버의 .env 파일을 확인하세요.",
        )

    otpi = OTPi(
        secret=user.secret,
        interval=settings.OTP_INTERVAL,
        digits=settings.OTP_DIGITS,
        smtp_host=settings.SMTP_HOST,
        smtp_port=settings.SMTP_PORT,
        smtp_user=settings.SMTP_USER,
        smtp_password=settings.SMTP_PASSWORD,
    )

    try:
        otpi.send_otp(payload.email)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"이메일 전송에 실패했습니다: {e}",
        )

    return {
        "message": "OTP가 이메일로 발송되었습니다.",
        "email": payload.email,
    }


@app.post("/verify-otp", tags=["auth"])
def verify_otp(
    payload: OTPVerifyRequest,
    res: Response,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="등록되지 않은 이메일입니다.",
        )

    otpi = OTPi(
        secret=user.secret,
        interval=settings.OTP_INTERVAL,
        digits=settings.OTP_DIGITS,
        smtp_host=settings.SMTP_HOST,
        smtp_port=settings.SMTP_PORT,
        smtp_user=settings.SMTP_USER,
        smtp_password=settings.SMTP_PASSWORD,
    )

    is_valid = otpi.verify_code(payload.code)

    if not is_valid:
        return {
            "message": "OTP 인증 실패",
            "email": payload.email,
            "login": False,
        }

    token = secrets.token_hex(32)
    user.token = token
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()

    res.set_cookie(
        key="token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
    )

    return {
        "message": "OTP 인증 성공",
        "email": user.email,
        "name": user.name,
        "token": token,
        "login": True,
    }

@app.post("/logout", tags=["auth"])
def logout(
    res: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_user.token = None
    db.commit()

    res.delete_cookie("token")

    return {"message": "로그아웃 되었습니다."}
