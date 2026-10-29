from sqlalchemy import text
from sqlalchemy.orm import Session

from Repositories.payment_repository import (
    create_payment, get_payment_for_payer, lock_account, debit_account,
    mark_tuition_paid, mark_payment_success, create_transaction
)
from Services.otp_service import verify_otp
from Services.notification_service import send_payment_result_email


def create_payment_request(db: Session, payer_id: int, tuition_id: int):
    if payer_id <= 0 or tuition_id <= 0:
        raise ValueError("Payer ID and tuition ID must be positive.")
    # The auth dependency has queried the current user using this same Session.
    # End that read transaction before starting the payment transaction.
    db.rollback()
    try:
        with db.begin():
            result = create_payment(db, payer_id, tuition_id)
        return result
    except ValueError:
        raise
    except Exception:
        raise


def complete_payment(db: Session, payer_id: int, payment_id: int, otp: str):
    if payer_id <= 0 or payment_id <= 0:
        raise ValueError("Invalid payer or payment ID.")

    # Confirm ownership before consuming OTP. OTP is single-use; if payment fails,
    # the payer can create/request a new OTP for the pending payment.
    payment = get_payment_for_payer(db, payment_id, payer_id)
    if not payment:
        raise ValueError("Payment was not found for the current payer.")
    if payment["status"] != "PENDING":
        raise ValueError("Only pending payments can be completed.")
    db.rollback()  # close read transaction before OTP verification starts

    verify_otp(db, payment_id, otp)

    email = None
    amount = payment["amount"]
    try:
        with db.begin():
            current_payment = get_payment_for_payer(db, payment_id, payer_id, lock=True)
            if not current_payment or current_payment["status"] != "PENDING":
                raise ValueError("Payment is no longer pending.")

            account = lock_account(db, payer_id)
            if not account:
                raise ValueError("Payment account was not found.")
            if account["status"] != "ACTIVE":
                raise ValueError("The account is not active.")
            if account["balance"] < amount:
                raise ValueError("Insufficient balance.")

            if not debit_account(db, payer_id, amount):
                raise ValueError("Unable to debit the account. Please retry.")
            if not mark_tuition_paid(db, current_payment["tuition_id"]):
                raise ValueError("Tuition was already paid or is no longer payable.")

            mark_payment_success(db, payment_id)
            create_transaction(db, payer_id, payment_id, amount)
            row = db.execute(text("SELECT email FROM payers WHERE payer_id = :payer_id"),
                             {"payer_id": payer_id}).mappings().first()
            email = row["email"] if row else None
    except ValueError:
        raise

    if email:
        try:
            send_payment_result_email(email, payment_id, float(amount), "SUCCESS")
        except Exception:
            # Payment is committed; email failure must not undo a successful payment.
            pass

    return {"payment_id": payment_id, "amount": float(amount), "status": "SUCCESS",
            "message": "Tuition payment completed successfully."}
