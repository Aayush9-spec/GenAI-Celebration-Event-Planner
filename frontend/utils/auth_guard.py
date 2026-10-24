import streamlit as st


def require_auth():
    """Redirect to login page if user is not authenticated."""
    if not st.session_state.get("token"):
        st.warning("Please sign in to continue.")
        st.switch_page("pages/1_Login.py")
        st.stop()
