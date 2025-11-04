import streamlit as st
import smtplib
import time
import random
import string
from email.mime.text import MIMEText

# ---------------------------- Email OTP Setup ----------------------------

def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))

def send_email_otp(receiver_email, otp):
    sender_email = "sarathsarath53381@gmail.com"
    sender_password = "Sarath9843@#"  # App password if 2FA is on
    subject = "Your OTP Verification Code"
    body = f"Your OTP is: {otp}\nIt will expire in 5 minutes."

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Failed to send email: {e}")
        return False

def is_otp_expired():
    return time.time() - st.session_state.get("otp_sent_time", 0) > 300  # 5 minutes

def can_resend():
    return time.time() - st.session_state.get("last_resend_time", 0) > 60  # 1 min cooldown

# ---------------------------- Main App ----------------------------

st.title("📧 Email OTP Verification")

# Email Input
if "email_verified" not in st.session_state:
    st.session_state.email_verified = False

if "otp" not in st.session_state:
    st.session_state.otp = ""
    st.session_state.otp_attempts = 0
    st.session_state.last_resend_time = 0

email = st.text_input("Enter your email to receive OTP", key="email_input")

# Send OTP
if st.button("Send OTP"):
    if email:
        st.session_state.otp = generate_otp()
        if send_email_otp(email, st.session_state.otp):
            st.session_state.otp_sent_time = time.time()
            st.session_state.otp_attempts = 0
            st.session_state.last_resend_time = time.time()
            st.success("OTP sent to your email.")
    else:
        st.warning("Please enter a valid email address.")

# OTP Verification
if st.session_state.otp:
    otp_input = st.text_input("Enter OTP", max_chars=6)

    if st.button("Verify OTP"):
        if is_otp_expired():
            st.error("❌ OTP expired. Please resend.")
        elif otp_input == st.session_state.otp:
            st.success("✅ OTP verified successfully.")
            st.session_state.email_verified = True
        else:
            st.session_state.otp_attempts += 1
            st.error("❌ Incorrect OTP.")
            if st.session_state.otp_attempts >= 3:
                st.warning("⚠️ Maximum attempts reached. Please resend OTP.")

    # Resend OTP
    if st.button("Resend OTP"):
        if can_resend():
            st.session_state.otp = generate_otp()
            if send_email_otp(email, st.session_state.otp):
                st.session_state.otp_sent_time = time.time()
                st.session_state.otp_attempts = 0
                st.session_state.last_resend_time = time.time()
                st.success("OTP resent successfully.")
        else:
            st.warning("Please wait 60 seconds before resending OTP.")

# Show verified status
if st.session_state.email_verified:
    st.success(f"🎉 Email {email} has been verified.")
