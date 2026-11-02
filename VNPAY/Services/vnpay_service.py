
import os
import hmac
import hashlib

from datetime import datetime, timedelta
from urllib.parse import urlencode

from config.setting import APP_TIMEZONE
from dotenv import load_dotenv

load_dotenv()


class VnpayService:
    def __init__(self):
        self.tmn_code = os.getenv("VNPAY_TMN_CODE")
        self.hash_secret = os.getenv("VNPAY_HASH_SECRET")
        self.payment_url = os.getenv("VNPAY_PAYMENT_URL")
        self.return_url = os.getenv("VNPAY_RETURN_URL")

        self.version = os.getenv("VNPAY_VERSION", "2.1.0")
        self.command = os.getenv("VNPAY_COMMAND", "pay")
        self.currency = os.getenv("VNPAY_CURRENCY", "VND")
        self.locale = os.getenv("VNPAY_LOCALE", "vn")
        self.order_type = os.getenv("VNPAY_ORDER_TYPE", "other")
        self.expire_minutes = int(
            os.getenv("VNPAY_EXPIRE_MINUTES", "15")
        )

        if not all([
            self.tmn_code,
            self.hash_secret,
            self.payment_url,
            self.return_url
        ]):
            raise ValueError("VNPAY configuration is missing")

    def create_payment_url(
        self,
        order_id: str,
        amount: int,
        ip_address: str
    ) -> str:
        if amount <= 0:
            raise ValueError("Payment amount must be greater than zero")

        now = datetime.now(APP_TIMEZONE)

        params = {
            "vnp_Version": self.version,
            "vnp_Command": self.command,
            "vnp_TmnCode": self.tmn_code,
            "vnp_Amount": str(amount * 100),
            "vnp_CurrCode": self.currency,
            "vnp_TxnRef": order_id,
            "vnp_OrderInfo": f"Thanh toan hoc phi {order_id}",
            "vnp_OrderType": self.order_type,
            "vnp_Locale": self.locale,
            "vnp_ReturnUrl": self.return_url,
            "vnp_IpAddr": ip_address,
            "vnp_CreateDate": now.strftime("%Y%m%d%H%M%S"),
            "vnp_ExpireDate": (
                now + timedelta(minutes=self.expire_minutes)
            ).strftime("%Y%m%d%H%M%S")
        }

        sorted_params = sorted(params.items())
        sign_data = urlencode(sorted_params)

        secure_hash = hmac.new(
            self.hash_secret.encode("utf-8"),
            sign_data.encode("utf-8"),
            hashlib.sha512
        ).hexdigest()

        return (
            f"{self.payment_url}?{sign_data}"
            f"&vnp_SecureHash={secure_hash}"
        )

    def verify_payment_response(self, params: dict) -> bool:
        return self._verify_signature(params)

    def verify_ipn_response(self, params: dict) -> bool:
        return self._verify_signature(params)

    
    def _verify_signature(self, params: dict) -> bool:
        received_hash = params.get("vnp_SecureHash")

        if not received_hash:
            print("VNPAY: Missing secure hash")
            return False

        sign_params = {
            key: value
            for key, value in params.items()
            if key.startswith("vnp_")
            and key not in ["vnp_SecureHash", "vnp_SecureHashType"]
        }

        sorted_params = sorted(sign_params.items())
        sign_data = urlencode(sorted_params)

        calculated_hash = hmac.new(
            self.hash_secret.encode("utf-8"),
            sign_data.encode("utf-8"),
            hashlib.sha512
        ).hexdigest()

        is_valid = hmac.compare_digest(
            calculated_hash.lower(),
            str(received_hash).lower()
        )

        print("========== VNPAY SIGNATURE DEBUG ==========")
        print("PARAMS:", sign_params)
        print("RECEIVED HASH:", received_hash[:12], "...")
        print("CALCULATED HASH:", calculated_hash[:12], "...")
        print("SIGNATURE VALID:", is_valid)
        print("===========================================")

        return is_valid