import streamlit as st

def settings():
    st.header("⚙️ Settings")

    # Profile Image Section
    with st.container():
        st.subheader("🖼️ Change Profile Image")
    uploaded_file = st.file_uploader("Upload New Profile Image", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        st.session_state.profile_image = uploaded_file
        st.success("✅ Profile image updated!")

    try:
        st.image(st.session_state.profile_image, width=120)
    except:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=120)

    # Phone Number Update Section
    with st.container():
        st.subheader("📱 Update Phone Number")
        new_phone = st.text_input("Enter new phone number", value=st.session_state.phone, max_chars=15)
        update_phone_col1, update_phone_col2 = st.columns([3,1])
        with update_phone_col2:
            if st.button("Update Phone"):
                if new_phone.strip():
                    st.session_state.phone = new_phone.strip()
                    st.success("✅ Phone number updated!")
                else:
                    st.warning("⚠️ Please enter a valid phone number.")

    st.markdown("---")

    # Password Change Section
    with st.container():
        st.subheader("🔐 Change Password")
        with st.form("password_form", clear_on_submit=True):
            current_password = st.text_input("Current Password", type="password", placeholder="Enter current password")
            new_password = st.text_input("New Password", type="password", placeholder="Enter new password")
            confirm_password = st.text_input("Confirm New Password", type="password", placeholder="Confirm new password")
            submitted = st.form_submit_button("Apply Changes")

            if submitted:
                if current_password != st.session_state.password:
                    st.error("❌ Current password is incorrect.")
                elif new_password != confirm_password:
                    st.error("❌ New passwords do not match.")
                elif not new_password.strip():
                    st.warning("⚠️ New password cannot be empty.")
                else:
                    st.session_state.password = new_password
                    st.success("✅ Password updated successfully.")
