import smtplib
import sqlite3
import random
import os
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

DB_NAME = "users.db"

def create_users_table():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            username TEXT, password TEXT, email TEXT PRIMARY KEY, phone TEXT
        )''')
        conn.commit()

def email_exists(email):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        return c.fetchone() is not None

def add_user(username, password, email, phone):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (username, password, email, phone))
        conn.commit()

def validate_user(email, password):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT username, email, phone FROM users WHERE email=? AND password=?", (email, password))
        return c.fetchone()

def send_otp_email(receiver_email, otp):
    msg = EmailMessage()
    msg['Subject'] = 'Your OTP for ResumeBot'
    msg['From'] = EMAIL_SENDER
    msg['To'] = receiver_email
    msg.set_content(f"Your OTP is: {otp}\nIt expires in 5 minutes.")

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
        smtp.send_message(msg)
