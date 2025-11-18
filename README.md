# 📌 OTPi Backend (FastAPI + PostgreSQL)

간단한 **이메일 OTP 로그인 시스템**을 FastAPI로 구현한 백엔드 프로젝트입니다.
사용자는 이메일로 전송되는 OTP(일회용 비밀번호)를 입력해 로그인할 수 있으며,
로그인 성공 시 서버는 세션 토큰을 발급하고 `HttpOnly Cookie`로 내려줍니다.

> 프론트엔드가 헤더 처리를 하지 않아도 되는 **쿠키 기반 인증 방식**이라
> 초심자에게도 이해하기 쉬운 구조입니다.

---

## 🚀 Features

- ✔ 이메일 기반 OTP 로그인
- ✔ RFC 6238 기반 TOTP 구현 (pyotp 없이 직접 구현)
- ✔ FastAPI 기반 RESTful API
- ✔ PostgreSQL + SQLAlchemy ORM
- ✔ Docker Compose로 손쉽게 배포
- ✔ HttpOnly 쿠키 기반 세션 관리
- ✔ 한국(KST) 시간대 응답 변환

---

## 🛠 Tech Stack

- **Backend**: FastAPI, Uvicorn
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Auth**: TOTP(HMAC-SHA1, RFC6238)
- **Deploy**: Docker, Docker Compose
- **Config**: Pydantic Settings (.env 지원)

---

## 📁 Project Structure

```
OTPi-backend/
 ├─ backend/
 │   ├─ app.py
 │   ├─ models.py
 │   ├─ schemas.py
 │   ├─ database.py
 │   ├─ config.py
 │
 ├─ otpi/
 │   ├─ api.py      # OTP 생성/검증 + 이메일 전송
 │   ├─ totp.py     # TOTP 구현
 │
 ├─ Dockerfile
 ├─ docker-compose.yml
 ├─ requirements.txt
 ├─ README.md
 └─ .env
```

---

## ⚙️ Environment Variables (.env)

프로젝트 루트에 `.env` 파일 생성:

```
PROJECT_NAME=OTPi Backend
DEBUG=True

DATABASE_URL=postgresql+psycopg2://admin:admin@db:5432/otpi

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

OTP_SECRET=CHANGE_THIS
OTP_INTERVAL=120
OTP_DIGITS=6
```

🔐 `SMTP_PASSWORD`는 반드시 **Google App Password** 사용
