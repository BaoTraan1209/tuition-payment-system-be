
import os
import html
import smtplib

from pathlib import Path
from email.message import EmailMessage

TEMPLATE_DIR = (
    Path(__file__).resolve().parent.parent
    / "resources"
    / "views"
    / "emails"
)

def send_email(
    to_email: str,
    subject: str,
    body: str,
    is_html: bool = False
) -> bool:
    msg = EmailMessage()

    msg["Subject"] = subject
    msg["From"] = os.getenv("MAIL_FROM_ADDRESS")
    msg["To"] = to_email

    if is_html:
        msg.set_content(
            "Please view this email using an HTML-compatible email client."
        )
        msg.add_alternative(body, subtype="html")
    else:
        msg.set_content(body)

    try:
        with smtplib.SMTP(
            os.getenv("MAIL_HOST"),
            int(os.getenv("MAIL_PORT", 587))
        ) as server:

            server.starttls()

            server.login(
                os.getenv("MAIL_USERNAME"),
                os.getenv("MAIL_PASSWORD")
            )

            server.send_message(msg)

        return True

    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def load_email_template(template_name: str, **kwargs) -> str:
    template_path = TEMPLATE_DIR / template_name

    if not template_path.is_file():
        raise FileNotFoundError(
            f"Email template not found: {template_name}"
        )

    template = template_path.read_text(encoding="utf-8")

    return template.format(**kwargs)

def send_otp_email(
    to_email: str,
    otp: str,
    expire_minutes: int = 5
) -> bool:
    template = load_email_template(
        "payment_otp.html",
        otp=html.escape(str(otp)),
        expire_minutes=expire_minutes
    )

    return send_email(
        to_email=to_email,
        subject="iBanking - OTP Verification",
        body=template,
        is_html=True
    )

def send_payment_success_email(
    to_email: str,
    fullname: str,
    payment_id: int,
    order_id: str,
    tuition_fee_id: int,
    amount: int,
    transaction_no: str,
    paid_at: str
) -> bool:
    template = load_email_template(
        "payment_success.html",
        fullname=html.escape(fullname or "Student"),
        payment_id=payment_id,
        order_id=html.escape(str(order_id)),
        tuition_fee_id=tuition_fee_id,
        amount=f"{amount:,.0f} VND",
        transaction_no=html.escape(str(transaction_no or "N/A")),
        paid_at=html.escape(str(paid_at))
    )

    return send_email(
        to_email=to_email,
        subject="iBanking - Tuition Fee Payment Successful",
        body=template,
        is_html=True
    )
