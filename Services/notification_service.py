import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

def send_email(to_email, subject, body):
    # Create the email message
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = os.getenv('MAIL_FROM_ADDRESS')
    msg['To'] = to_email

    # Send the email
    try:
        with smtplib.SMTP(os.getenv('MAIL_HOST'), int(os.getenv('MAIL_PORT'))) as server:
            server.starttls()
            server.login(os.getenv('MAIL_USERNAME'), os.getenv('MAIL_PASSWORD'))
            server.send_message(msg)
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
    

def send_otp_email(to_email, otp, expire_minutes=5):
    subject = "iBanking - OTP Verification"
    body = f"""
                Dear User,

                You have requested to verify a tuition payment.

                Your One-Time Password (OTP) is:

                {otp}

                This OTP is valid for {expire_minutes} minutes.

                For your security:
                - Do not share this OTP with anyone.
                - This OTP can only be used once.
                - If you did not initiate this request, please ignore this email.

                Best regards,
                Tuition Payment System

                Automated Security Notification
                Please do not reply to this email.
            """
    return send_email(to_email, subject, body)


def send_payment_success_email(to_email, payment_id):
    subject = "iBanking - Tuition Fee Successfully Paid"
    body = f"""
                Hello,

                Your payment with ID {payment_id} has been successfully processed.

                Thank you for using iBanking.

                Best regards,
                iBanking.
                """
    return send_email(to_email, subject, body)