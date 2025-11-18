# otpi/api.py
import smtplib
from email.mime.text import MIMEText
from typing import Optional

from .totp import TOTP


class OTPi:
    def __init__(
        self,
        secret: bytes | str,
        interval: int = 90,
        digits: int = 6,
        smtp_host: str = "smtp.gmail.com",
        smtp_port: int = 587,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        from_email: Optional[str] = None,
    ):
        self.secret = secret
        self.interval = interval
        self.digits = digits
        self._totp = TOTP(self.secret, digits=self.digits, interval=self.interval)

        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.from_email = from_email or smtp_user

    @staticmethod
    def generate_secret(length: int = 20) -> bytes:
        """
        새 사용자용 랜덤 시크릿 생성 (DB에 그대로 bytes로 저장하는 용도)
        """
        return TOTP.generate_secret(length=length)
    
    def get_code(self) -> str:
        """
        현재 시간 기준 OTP 코드 생성
        """
        return self._totp.generate_code()

    def verify_code(self, code: str) -> bool:
        """
        OTP 코드 검증
        """
        return self._totp.verify_code(code)

    def _build_email_message(self, to_email: str, code: str) -> MIMEText:
        subject = "로그인 인증 코드 안내"
        if self.interval % 60 == 0:
            valid_text = f"{self.interval // 60}분"
        else:
            valid_text = f"{self.interval}초"

        body = f"""안녕하세요.

요청하신 로그인 인증 코드는 다음과 같습니다:

    {code}

이 코드는 {valid_text} 동안만 유효합니다.
본인이 요청한 것이 아니라면 이 메일을 무시하셔도 됩니다.
"""

        msg = MIMEText(body, _charset="utf-8")
        msg["Subject"] = subject
        msg["From"] = self.from_email
        msg["To"] = to_email
        return msg

    def send_email(self, to_email: str, code: str) -> None:
        """
        실제로 이메일을 전송하는 함수.
        """
        if not (self.smtp_user and self.smtp_password):
            raise RuntimeError("SMTP 계정 정보가 설정되어 있지 않습니다.")

        msg = self._build_email_message(to_email, code)

        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)

    def send_otp(self, to_email: str) -> str:
        code = self.get_code()
        self.send_email(to_email, code)
        return code
