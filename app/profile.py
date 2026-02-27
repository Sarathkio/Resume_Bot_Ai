import streamlit as st

def profile():
    st.markdown("## 👤 User Profile")
    st.write("---")  # Separator line for neatness

    col1, col2 = st.columns([1, 3])

    with col1:
        try:
            st.image(
                st.session_state.profile_image,
                width=140,
                caption=f"**{st.session_state.username}**",
                output_format="PNG"
            )
        except Exception:
            st.warning("⚠️ Unable to load profile image.")
            st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=140)

    with col2:
        st.markdown(
            f"""
            <div style="font-size:16px; line-height:1.6;">
            <p><strong>Username:</strong> {st.session_state.username or 'Not set'}</p>
            <p><strong>Email:</strong> {st.session_state.email or 'Not set'}</p>
            <p><strong>Phone:</strong> {st.session_state.phone or 'Not set'}</p>
            <p><strong>Account Type:</strong> {st.session_state.account_type}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("")  # Add some vertical spacing after profile info
