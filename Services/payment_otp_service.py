import os
import math
import secrets
import hashlib
import hmac

from Helpers.redis_helper import redis_client
from Helpers.email_helper import send_otp_email

class PaymentOTPService:
    def __init__(self):
        self.OTP_EXPIRE = int(os.getenv("PAYMENT_OTP_EXPIRE", 300))
        self.MAX_ATTEMPTS = int(os.getenv("PAYMENT_OTP_MAX_ATTEMPTS", 3))
        self.RESEND_COOLDOWN = int(os.getenv("PAYMENT_OTP_RESEND_COOLDOWN", 60))

    def get_otp_key(self, user_id: str, tuition_fee_id: int) -> str:
        return f"payment:otp:{user_id}:{tuition_fee_id}"

    def get_cooldown_key(self, user_id: str, tuition_fee_id: int) -> str:
        return f"payment:otp:cooldown:{user_id}:{tuition_fee_id}"

    def send_otp(
        self,
        user_id: str,
        tuition_fee_id: int,
        email: str
    ) -> dict:
        key = self.get_otp_key(user_id, tuition_fee_id)
        cooldown_key = self.get_cooldown_key(user_id, tuition_fee_id)

        cooldown = redis_client.set(
            cooldown_key,
            "1",
            ex=self.RESEND_COOLDOWN,
            nx=True
        )

        if not cooldown:
            raise ValueError("Please wait before requesting another OTP")

        try:
            # Tạo OTP 6 chữ số
            otp = f"{secrets.randbelow(900000) + 100000}"

            # Hash OTP trước khi lưu Redis
            otp_hash = hashlib.sha256(otp.encode()).hexdigest()

            redis_client.hset(key, mapping={
                "otp_hash": otp_hash,
                "verified": "false",
                "attempts": 0
            })

            redis_client.expire(key, self.OTP_EXPIRE)

            # Gửi OTP qua email
            expire_minutes = max(1, math.ceil(self.OTP_EXPIRE / 60))

            if not send_otp_email(
                email,
                otp,
                expire_minutes=expire_minutes
            ):
                raise RuntimeError("Failed to send OTP email")

            return {
                "expires_in": self.OTP_EXPIRE,
                "msg": "OTP sent successfully"
            }

        except Exception:
            redis_client.delete(key)
            redis_client.delete(cooldown_key)
            raise

    def verify_otp(
        self,
        user_id: str,
        tuition_fee_id: int,
        otp: str
    ) -> dict:
        key = self.get_otp_key(user_id, tuition_fee_id)

        otp_data = redis_client.hgetall(key)

        otp_data = {
            k.decode() if isinstance(k, bytes) else k:
            v.decode() if isinstance(v, bytes) else v
            for k, v in otp_data.items()
        }

        if not otp_data:
            raise ValueError("OTP not found or expired")

        if otp_data.get("verified") == "true":
            raise ValueError("OTP has already been verified")

        attempts = int(otp_data.get("attempts", 0))

        if attempts >= self.MAX_ATTEMPTS:
            redis_client.delete(key)
            raise ValueError("Maximum OTP attempts exceeded")

        otp_hash = hashlib.sha256(otp.encode()).hexdigest()

        if not hmac.compare_digest(
            otp_hash,
            otp_data.get("otp_hash", "")
        ):
            attempts += 1

            if attempts >= self.MAX_ATTEMPTS:
                redis_client.delete(key)
                raise ValueError("Maximum OTP attempts exceeded")

            redis_client.hset(key, "attempts", attempts)

            raise ValueError("Invalid OTP")

        redis_client.hset(key, "verified", "true")

        return {
            "verified": True,
            "msg": "OTP verified successfully"
        }

    def consume_otp(
        self,
        user_id: str,
        tuition_fee_id: int
    ) -> bool:
        key = self.get_otp_key(user_id, tuition_fee_id)

        script = """
            local verified = redis.call('HGET', KEYS[1], 'verified')

            if verified == 'true' then
                redis.call('DEL', KEYS[1])
                return 1
            end

            return 0
        """

        result = redis_client.eval(script, 1, key)

        return result == 1
