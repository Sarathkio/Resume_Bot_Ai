# otp_utils.py
import smtplib
import random
import string
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_SENDER = 'sarathsarath53381@gmail.com'
EMAIL_PASSWORD = 'Sarath9843@#'  # Use an app password

otp_storage = {}

def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))

def send_email_otp(to_email, otp):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = to_email
    msg['Subject'] = 'Your OTP Verification Code'
    msg.attach(MIMEText(f"Your OTP is: {otp}\nThis OTP expires in 5 minutes.", 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send OTP: {e}")
        return False

def store_otp(email, otp):
    otp_storage[email] = {
        'otp': otp,
        'timestamp': datetime.now(),
        'attempts': 0
    }

def is_otp_valid(email, input_otp, expiry=5, max_attempts=3):
    if email not in otp_storage:
        return False, "No OTP found. Please resend."

    record = otp_storage[email]
    if datetime.now() - record["timestamp"] > timedelta(minutes=expiry):
        del otp_storage[email]
        return False, "OTP expired."

    if record["attempts"] >= max_attempts:
        del otp_storage[email]
        return False, "Max attempts reached."

    if input_otp == record["otp"]:
        del otp_storage[email]
        return True, "OTP verified."
    else:
        record["attempts"] += 1
        return False, f"Invalid OTP. Attempts left: {max_attempts - record['attempts']}"
