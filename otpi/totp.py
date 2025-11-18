# otpi/totp.py
import hashlib
import hmac
import os
import struct
import time
from typing import Optional


class TOTP:
    """
    RFC 4226 / 6238 기반 TOTP 구현.
    secret: 난수 바이트 (서버/DB에만 저장되는 값)
    interval: OTP 유효 시간(초)
    digits: OTP 자리 수
    """

    def __init__(self, secret: bytes | str, interval: int, digits: int = 6):
        if isinstance(secret, str):
            secret = secret.encode()

        self.secret = secret
        self.interval = interval
        self.digits = digits

    @staticmethod
    def generate_secret(length: int = 20) -> bytes:
        """
        새 사용자용 랜덤 시크릿 생성 (DB에 그대로 bytes로 저장하는 용도)
        """
        return os.urandom(length)

    def counter(self, for_time: Optional[float] = None) -> int:
        if for_time is None:
            for_time = time.time()
        return int(for_time) // self.interval

    def generate_code(self, for_time: Optional[float] = None) -> str:
        """
        시간을 기반으로 OTP 코드 생성
        """
        counter = self.counter(for_time=for_time)
        counter_bytes = struct.pack(">Q", counter)
        hmac_hash = hmac.new(self.secret, counter_bytes, hashlib.sha1).digest()

        offset = hmac_hash[-1] & 0x0F
        code_int = struct.unpack(">I", hmac_hash[offset:offset + 4])[0]
        code_int = (code_int & 0x7FFFFFFF) % (10 ** self.digits)

        return str(code_int).zfill(self.digits)

    def verify_code(self, code: str, valid_window: int = 1) -> bool:
        """
        OTP 코드 검증.
        valid_window=1이면 현재 interval, 이전 interval, 다음 interval 까지 허용.
        """
        if not code.isdigit():
            return False

        now = time.time()
        code = code.zfill(self.digits)

        for offset in range(-valid_window, valid_window + 1):
            t = now + offset * self.interval
            expected = self.generate_code(for_time=t)
            if hmac.compare_digest(expected, code):
                return True

        return False
