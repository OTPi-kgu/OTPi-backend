import os

from dotenv import load_dotenv
from otpi import OTPi

load_dotenv()

otpi = OTPi(
    secret=os.getenv("OTP_SECRET"),
    smtp_host=os.getenv("SMTP_HOST"),
    smtp_user=os.getenv("SMTP_USER"),
    smtp_password=os.getenv("SMTP_PASSWORD"),
) 

email = os.getenv("TEST_EMAIL")
otpi.send_otp(email)

print("이메일로 OTP 코드가 발송되었습니다.")
otp = str(input("OTP 코드를 입력하세요: "))
if otpi.verify_code(otp):
    print("인증 성공!")