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
    

def send_otp_email(to_email, otp):
    subject = "iBanking - OTP Verification"
    body = f"""
                Hello,

                Your OTP verification code is: {otp}

                This code will expire in 5 minutes.

                Please do not share this code with anyone.

                Best regards,
                iBanking.
                """
    return send_email(to_email, subject, body)