# ----------- IMPORTS -----------
# Importing necessary libraries
import streamlit as st                    # Streamlit for building web apps
import sqlite3                            # SQLite for database operations
import hashlib                            # Hashlib for password hashing (security)
import os                                 # OS module for interacting with the file system
import random                             # Random module for generating random numbers (e.g., OTPs)
from PIL import Image                     # PIL (Pillow) for image handling and processing
import re                                 # Regular expressions for pattern matching (e.g., email/phone validation)
from streamlit_oauth import OAuth2Component
from utils import *
import random, time

# ----------- CONSTANTS -----------
PROFILE_PICTURE_PATH = './profile_pictures/'  # Directory to store profile images
# ----------- DATABASE SETUP -----------
def create_users_table():
    """Creates the users table if it doesn't already exist."""
    conn = sqlite3.connect("resume_bot.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT, 
                    email TEXT PRIMARY KEY,  
                    phone TEXT, 
                    password TEXT, 
                    profile_picture TEXT)''')
    conn.commit()
    conn.close()

def add_user(username, password, email, phone):
    """Registers a new user with hashed password."""
    conn = sqlite3.connect("resume_bot.db")
    c = conn.cursor()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    c.execute("INSERT INTO users (username, password, email, phone, profile_picture) VALUES (?, ?, ?, ?, ?)", 
              (username, hashed_password, email, phone, None))
    conn.commit()
    conn.close()

def validate_user(email, password):
    """Validates user credentials against stored hashed password."""
    conn = sqlite3.connect("resume_bot.db")
    c = conn.cursor()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    c.execute("SELECT username, email, phone, profile_picture FROM users WHERE email=? AND password=?", 
              (email, hashed_password))
    result = c.fetchone()
    conn.close()
    return result

def email_exists(email):
    """Checks if an email is already registered."""
    conn = sqlite3.connect("resume_bot.db")
    c = conn.cursor()
    c.execute("SELECT email FROM users WHERE email=?", (email,))
    result = c.fetchone()
    conn.close()
    return result is not None

def update_password(new_password):
    """Updates the password for the logged-in user."""
    conn = sqlite3.connect("resume_bot.db")
    c = conn.cursor()
    hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
    c.execute("UPDATE users SET password=? WHERE email=?", 
              (hashed_password, st.session_state.email))
    conn.commit()
    conn.close()

def update_phone(new_phone):
    """Updates the phone number for the logged-in user."""
    conn = sqlite3.connect("resume_bot.db")
    c = conn.cursor()
    c.execute("UPDATE users SET phone=? WHERE email=?", (new_phone, st.session_state.email))
    conn.commit()
    conn.close()
    st.session_state.phone = new_phone  # Update session state too

# ----------- PROFILE PICTURE -----------
if not os.path.exists(PROFILE_PICTURE_PATH):
    os.makedirs(PROFILE_PICTURE_PATH)  # Ensure directory exists

def upload_profile_picture(email):
    """Handles uploading and saving profile pictures."""
    uploaded_file = st.file_uploader("Upload Profile Picture", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        img_path = os.path.join(PROFILE_PICTURE_PATH, f"{email}.jpg")
        img.save(img_path)

        # Save the image path in the database
        conn = sqlite3.connect("resume_bot.db")
        c = conn.cursor()
        c.execute("UPDATE users SET profile_picture=? WHERE email=?", (img_path, email))
        conn.commit()
        conn.close()

        # Also update session state
        st.session_state.profile_picture = img_path

        st.success("✅ Profile picture uploaded and saved!")
        return img_path
    return None

    """Handles uploading and saving profile pictures."""
    uploaded_file = st.file_uploader("Upload Profile Picture", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        img_path = os.path.join(PROFILE_PICTURE_PATH, f"{email}.jpg")
        img.save(img_path)
        st.success("Profile picture uploaded!")
        return img_path
    return None

# ----------- UI PAGES -----------
def sidebar_navigation():
    """Displays the sidebar with page navigation."""
    st.sidebar.title("📂 Navigation")
    page = st.sidebar.radio("Select a page", ["Dashboard", "Profile", "Settings"])
    if page == "Dashboard":
        show_dashboard()
    elif page == "Profile":
        show_profile()
    elif page == "Settings":
        show_settings()

def show_dashboard():
    """Displays user dashboard with profile info and logout."""
    st.title("📊 Dashboard")
    st.success(f"Welcome, {st.session_state.username}!")

    # Display profile picture
    img_path = os.path.join(PROFILE_PICTURE_PATH, f"{st.session_state.email}.jpg")
    if os.path.exists(img_path):
        st.image(img_path, width=150, caption="Profile Picture")
    else:
        st.info("No profile picture uploaded yet.")

    # Show email and phone
    st.markdown(f"""**Email:** {st.session_state.email}  
**Phone:** {st.session_state.phone}""")

    # Logout button
    if st.button("🔒 Logout"):
        for key in ["logged_in", "username", "email", "phone"]:
            st.session_state.pop(key, None)
        st.success("Logged out.")
        st.rerun()

    upload_profile_picture(st.session_state.email)

def show_profile():
    """Displays user profile information."""
    st.title("👤 Profile")
    st.markdown(f"**Username:** {st.session_state.username}")
    st.markdown(f"**Email:** {st.session_state.email}")
    st.markdown(f"**Phone:** {st.session_state.phone}")
    upload_profile_picture(st.session_state.email)

def show_settings():
    """Allows user to update password and phone number."""
    st.title("⚙️ Settings")

    # Change password
    st.subheader("Change Password")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    if st.button("Change Password"):
        if new_password == confirm_password:
            update_password(new_password)
            st.success("Password changed.")
        else:
            st.error("Passwords do not match.")

    # Edit phone number
    st.subheader("Edit Phone Number")
    new_phone = st.text_input("New Phone Number")
    if st.button("Update Phone"):
        if new_phone.strip():
            update_phone(new_phone)
            st.success("Phone number updated.")
        else:
            st.warning("Phone number cannot be empty.")

# ----------- LOGIN & REGISTER UI -----------
def login():
    create_users_table()

    # Stylish Animated UI
    st.markdown("""
        <style>
        body { background: #f4f6f8; }
        .login-title {
            font-size: 40px;
            text-align: center;
            color: #2c3e50;
            color:#45c4e90
            animation: fadeIn 2s ease-in;
            font-weight: bold;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .stTabs [role="tablist"] {
            justify-content: center;
            font-size: 18px;
        }
        .stTextInput > div > div > input, .stSelectbox > div > div {
            border-radius: 8px;
            padding: 10px;
        }
        .stButton > button {
            background-color: #2980b9;
            color: white;
            padding: 10px;
            border-radius: 10px;
            font-size: 16px;
            transition: 0.3s ease;
        }
        .stButton > button:hover {
            background-color: #1f6696;
            color:Blue
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-title">🔐 ResumeBot - AI Login System</div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔓 Login", "📝 Register"])

    with tab1:
        with st.form("login_form"):
            email = st.text_input("📧 Email",placeholder="Enter Your Login Email")
            password = st.text_input("🔑 Password", type="password" , placeholder="Enter Your Login password")
            submitted = st.form_submit_button("Login")

            if submitted:
                result = validate_user(email, password)
                if result:
                    st.session_state.logged_in = True
                    st.session_state.username = result[0]
                    st.session_state.email = result[1]
                    st.session_state.phone = result[2]
                    st.session_state.profile_picture = result[3]
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials.")

    with tab2:
        with st.form("register_form"):
            username = st.text_input("👤 Username",placeholder="Enter the username")
            email = st.text_input("📧 Email",placeholder="Enter the email")

            country_codes = {
                "🇮🇳 India (+91)": "+91", "🇺🇸 USA (+1)": "+1", 
                "🇬🇧 UK (+44)": "+44", "🇦🇺 Australia (+61)": "+61",
                "🇯🇵 Japan (+81)": "+81", "🇩🇪 Germany (+49)": "+49"
            }
            country = st.selectbox("🌐 Country Code", list(country_codes.keys()))
            local_phone = st.text_input("📱 Phone Number",placeholder="Enter Your Phone number")
            phone = f"{country_codes[country]}{local_phone.strip()}"

            password1 = st.text_input("🔐 Password", type="password",placeholder="Enter the Password")
            password2 = st.text_input("🔁 Confirm Password", type="password",placeholder="Enter the confirm Password")

            otp_placeholder = st.empty()
            register_submit = st.form_submit_button("Send OTP")

            if register_submit:
                if password1 != password2:
                    st.warning("⚠️ Passwords do not match.")
                elif not all([username.strip(), password1.strip(), email.strip(), local_phone.strip()]):
                    st.warning("⚠️ All fields are required.")
                elif email_exists(email):
                    st.error("❌ Email already exists.")
                else:
                    otp = str(random.randint(100000, 999999))
                    st.session_state.generated_otp = otp
                    st.session_state.temp_user = (username, password1, email, phone)
                    otp_placeholder.success(f"✅ OTP Sent: {otp} (Simulated)")

        if "generated_otp" in st.session_state:
            user_otp = st.text_input("📨 Enter OTP sent to your email (Simulated)")
            if st.button("Verify & Register"):
                if user_otp == st.session_state.generated_otp:
                    u, p, e, ph = st.session_state.temp_user
                    add_user(u, p, e, ph)
                    st.success("✅ Registered! Please login.")
                    for k in ["generated_otp", "temp_user"]:
                        st.session_state.pop(k, None)

# ----------- MAIN -----------
if __name__ == "__main__":
    if "logged_in" in st.session_state and st.session_state.logged_in:
        sidebar_navigation()
    else:
        login()
