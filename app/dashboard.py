import hashlib
import streamlit as st
import sqlite3
import os
from PIL import Image

PROFILE_PICTURE_PATH = './profile_pictures/'

def update_password(new_password):
    conn = sqlite3.connect("resume_bot.db")
    c = conn.cursor()
    hashed = hashlib.sha256(new_password.encode()).hexdigest()
    c.execute("UPDATE users SET password=? WHERE email=?", (hashed, st.session_state.email))
    conn.commit()
    conn.close()

def update_phone(new_phone):
    conn = sqlite3.connect("resume_bot.db")
    c = conn.cursor()
    c.execute("UPDATE users SET phone=? WHERE email=?", (new_phone, st.session_state.email))
    conn.commit()
    conn.close()
    st.session_state.phone = new_phone

def upload_profile_picture(email):
    if not os.path.exists(PROFILE_PICTURE_PATH):
        os.makedirs(PROFILE_PICTURE_PATH)

    uploaded_file = st.file_uploader("Upload Profile Picture", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        img = Image.open(uploaded_file)
        img_path = os.path.join(PROFILE_PICTURE_PATH, f"{email}.jpg")
        img.save(img_path)

        conn = sqlite3.connect("resume_bot.db")
        c = conn.cursor()
        c.execute("UPDATE users SET profile_picture=? WHERE email=?", (img_path, email))
        conn.commit()
        conn.close()

        st.session_state.profile_picture = img_path
        st.success("✅ Profile picture updated!")
        return img_path
    return None

def show_dashboard():
    st.title("📊 Dashboard")
    st.success(f"Welcome, {st.session_state.username}!")

    img_path = os.path.join(PROFILE_PICTURE_PATH, f"{st.session_state.email}.jpg")
    if os.path.exists(img_path):
        st.image(img_path, width=150)
    else:
        st.info("No profile picture uploaded yet.")

    st.markdown(f"**Email:** {st.session_state.email}  \n**Phone:** {st.session_state.phone}")

    if st.button("🔒 Logout"):
        for k in ["logged_in", "username", "email", "phone", "profile_picture"]:
            st.session_state.pop(k, None)
        st.success("Logged out.")
        st.rerun()

    upload_profile_picture(st.session_state.email)

def show_profile():
    st.title("👤 Profile")
    st.markdown(f"**Username:** {st.session_state.username}")
    st.markdown(f"**Email:** {st.session_state.email}")
    st.markdown(f"**Phone:** {st.session_state.phone}")
    upload_profile_picture(st.session_state.email)

def show_settings():
    st.title("⚙️ Settings")
    new_password = st.text_input("New Password", type="password")
    confirm = st.text_input("Confirm Password", type="password")
    if st.button("Change Password"):
        if new_password == confirm:
            update_password(new_password)
            st.success("Password updated.")
        else:
            st.error("Passwords do not match.")

    new_phone = st.text_input("Update Phone")
    if st.button("Update Phone"):
        if new_phone.strip():
            update_phone(new_phone)
            st.success("Phone updated.")
        else:
            st.warning("Phone cannot be empty.")

def sidebar_navigation():
    st.sidebar.title("📂 Navigation")
    page = st.sidebar.radio("Choose Page", ["Dashboard", "Profile", "Settings"])
    if page == "Dashboard":
        show_dashboard()
    elif page == "Profile":
        show_profile()
    elif page == "Settings":
        show_settings()

if __name__ == "__main__":
    if "logged_in" in st.session_state and st.session_state.logged_in:
        sidebar_navigation()
    else:
        st.switch_page("login.py")
