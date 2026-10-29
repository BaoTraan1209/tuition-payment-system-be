import os
import hmac
import hashlib
import secrets

from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.orm import Session

from Repositories.otp_repository import (
    get_payment_email,
    invalidate_previous_otps,
    create_otp_record,
    get_latest_otp_for_update,
    increase_otp_attempts,
    mark_otp_used
)
from Services.notification_service import send_otp_email

load_dotenv()


def hash_otp(payment_id: int, otp: str) -> str:
    secret = os.getenv("OTP_SECRET")

    if not secret:
        raise RuntimeError("OTP_SECRET is not configured.")

    message = f"{payment_id}:{otp}".encode("utf-8")

    return hmac.new(
        secret.encode("utf-8"),
        message,
        hashlib.sha256
    ).hexdigest()



def request_otp(db: Session, payment_id: int, payer_id: int):
    if payment_id <= 0:
        raise ValueError("Payment ID must be greater than zero.")

    otp = f"{secrets.randbelow(1_000_000):06d}"
    expire_minutes = int(os.getenv("OTP_EXPIRE_MINUTES", "5"))

    # The authenticated request may already have opened a read transaction.
    db.rollback()
    with db.begin():
        payment = get_payment_email(db, payment_id, payer_id)

        if not payment:
            raise ValueError("Payment was not found.")

        if payment["status"] != "PENDING":
            raise ValueError(
                "OTP can only be requested for a pending payment."
            )

        email = payment["email"]

        if not email:
            raise ValueError(
                "The payer does not have an email address."
            )

        otp_hash = hash_otp(payment_id, otp)
        expires_at = datetime.now() + timedelta(
            minutes=expire_minutes
        )

        invalidate_previous_otps(db, payment_id)

        otp_id = create_otp_record(
            db,
            payment_id,
            otp_hash,
            expires_at
        )

    try:
        send_otp_email(email, otp, expire_minutes)
    except Exception as error:
        with db.begin():
            mark_otp_used(db, otp_id)

        raise RuntimeError(
            "Unable to send OTP email."
        ) from error

    return {
        "payment_id": payment_id,
        "expires_in_minutes": expire_minutes,
        "message": "OTP sent to the payer's registered email."
    }


def verify_otp(db: Session, payment_id: int, otp: str, payer_id: int | None = None) -> bool:
    if payment_id <= 0:
        raise ValueError("Payment ID must be greater than zero.")
    if not otp or not otp.isdigit() or len(otp) != 6:
        raise ValueError("OTP must contain exactly 6 digits.")

    if payer_id is not None:
        payment = get_payment_email(db, payment_id, payer_id)
        if not payment:
            raise ValueError("Payment was not found for the current payer.")
        db.rollback()  # close the read transaction before opening the locking transaction

    max_attempts = int(os.getenv("OTP_MAX_ATTEMPTS", "5"))
    error_message = None
    incorrect_otp = False

    with db.begin():
        record = get_latest_otp_for_update(db, payment_id)
        if not record:
            error_message = "OTP was not found."
        elif record["used"]:
            error_message = "OTP has already been used."
        elif record["expires_at"] <= datetime.now():
            mark_otp_used(db, record["otp_id"])
            error_message = "OTP has expired."
        elif record["attempt_count"] >= max_attempts:
            mark_otp_used(db, record["otp_id"])
            error_message = "Maximum OTP attempts exceeded."
        else:
            submitted_hash = hash_otp(payment_id, otp)
            if not hmac.compare_digest(submitted_hash, record["otp_hash"]):
                increase_otp_attempts(db, record["otp_id"])
                if record["attempt_count"] + 1 >= max_attempts:
                    mark_otp_used(db, record["otp_id"])
                    error_message = "Maximum OTP attempts exceeded."
                else:
                    error_message = "Incorrect OTP."
                incorrect_otp = True
            else:
                mark_otp_used(db, record["otp_id"])

    if error_message:
        raise ValueError(error_message)
    return True
