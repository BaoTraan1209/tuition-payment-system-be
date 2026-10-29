import os
import smtplib
from email.message import EmailMessage
from pathlib import Path

from dotenv import load_dotenv
from Repositories.notification_repository import (
    get_notifications, mark_read, create_notification, get_owned_tuition_for_reminder
)

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def _send_email(receiver_email: str, subject: str, body: str):
    mail_username = os.getenv("MAIL_USERNAME")
    mail_password = os.getenv("MAIL_PASSWORD")
    mail_host = os.getenv("MAIL_HOST", "smtp.gmail.com")
    mail_port = int(os.getenv("MAIL_PORT", "587"))
    if not receiver_email:
        raise ValueError("Recipient email is missing.")
    if not mail_username or not mail_password:
        raise RuntimeError("Email configuration is incomplete.")

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = os.getenv("MAIL_FROM_ADDRESS") or mail_username
    message["To"] = receiver_email
    message.set_content(body)

    with smtplib.SMTP(mail_host, mail_port, timeout=15) as server:
        server.starttls()
        server.login(mail_username, mail_password)
        server.send_message(message)


def send_otp_email(receiver_email: str, otp: str, expires_in_minutes: int):
    _send_email(
        receiver_email,
        "iBanking - OTP Verification",
        f"Hello,\n\nYour OTP for tuition payment is: {otp}\n"
        f"This code expires in {expires_in_minutes} minutes. Do not share it with anyone.\n"
        "\nIf you did not request this code, please ignore this email."
    )


def send_payment_result_email(receiver_email: str, payment_id: int, amount: float, status: str):
    _send_email(
        receiver_email,
        "iBanking - Tuition Payment Result",
        f"Hello,\n\nYour tuition payment result is: {status}\n"
        f"Payment ID: {payment_id}\nAmount: {amount:,.0f} VND\n\nThank you."
    )


def send_tuition_status_email(receiver_email: str, tuition_id: int, amount: float, status: str, mssv: str):
    _send_email(
        receiver_email,
        "iBanking - Tuition Status Notification",
        f"Hello,\n\nHere is your tuition status update.\n"
        f"Student ID: {mssv}\nTuition ID: {tuition_id}\n"
        f"Amount: {amount:,.0f} VND\nStatus: {status}\n\n"
        "Please sign in to iBanking to review your tuition details."
    )


def list_notifications(db, payer_id: int):
    try:
        return get_notifications(db, payer_id)
    except Exception as exc:
        db.rollback()
        # Missing table should be fixed by applying SQL in README; do not hide it as empty data.
        raise RuntimeError("Could not load notifications. Ensure the notifications table exists.") from exc


def mark_notification_read(db, payer_id: int, notification_id: int):
    try:
        return mark_read(db, payer_id, notification_id)
    except Exception as exc:
        db.rollback()
        raise RuntimeError("Could not update notification. Ensure the notifications table exists.") from exc


def send_tuition_reminder(db, payer_id: int, tuition_id: int):
    tuition = get_owned_tuition_for_reminder(db, payer_id, tuition_id)
    if not tuition:
        raise ValueError("Tuition was not found for the current account.")
    if str(tuition["status"]).upper() == "PAID":
        raise ValueError("This tuition has already been paid.")
    email = tuition.get("email")
    if not email:
        raise ValueError("No email address is registered for this account.")

    amount = float(tuition["amount"] or 0)
    status = str(tuition["status"] or "UNPAID").upper()
    send_tuition_status_email(email, tuition_id, amount, status, tuition.get("mssv") or "")
    try:
        create_notification(
            db, payer_id, "Tuition status reminder",
            f"Tuition #{tuition_id}: {amount:,.0f} VND — status: {status}.",
            "TUITION"
        )
    except Exception as exc:
        db.rollback()
        # Email has already been sent. Tell the caller persistence failed, not that email failed.
        raise RuntimeError("Email was sent, but notification history could not be saved. Apply notifications table SQL.") from exc

    return {"tuition_id": tuition_id, "email": email, "status": status}
