import streamlit as st

def uploads():
    # Display the header for the upload history section
    st.header("🕓 Recent Upload History")
    
    # Create an expandable section to show or hide the upload history
    with st.expander("📁 View Uploads"):
        # Check if there is any upload history stored in session state
        if st.session_state.upload_history:
            # Iterate over the upload history in reverse order (most recent first)
            for i, item in enumerate(reversed(st.session_state.upload_history), 1):
                # Display each uploaded file's name and timestamp
                st.write(f"{i}. 📄 {item['filename']} - ⏱️ {item['timestamp']}")
            
            # Provide a button to clear the upload history
            if st.button("🧹 Clear History"):
                st.session_state.upload_history.clear()  # Clear the list
                st.success("✅ Upload history cleared.")  # Show success message
        else:
            # Show a message when there are no uploads yet
            st.info("No uploads yet.")
