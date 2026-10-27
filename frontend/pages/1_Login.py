import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.styles import inject_global_styles
from utils.api import api_post, BACKEND_URL

st.set_page_config(page_title="Sign In — CelebAI", page_icon="🎉", layout="centered")
inject_global_styles()

# Centered auth layout
st.markdown("""
<div style="max-width:460px;margin:2rem auto 0 auto">
    <div style="text-align:center;margin-bottom:2rem">
        <div style="font-size:3.5rem;margin-bottom:0.5rem">🎉</div>
        <h1 style="color:#e2e8f0;font-size:2rem;font-weight:800;margin:0 0 0.3rem 0">CelebAI</h1>
        <p style="color:#64748b;margin:0;font-size:0.95rem">AI-powered celebration & event planner</p>
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 5, 1])
with col2:
    tab_login, tab_register = st.tabs(["🔑  Sign In", "✨  Create Account"])

    # ------------------------------------------------------------------
    # LOGIN TAB
    # ------------------------------------------------------------------
    with tab_login:
        with st.form("login_form"):
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
            username = st.text_input("Username", placeholder="your_username")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)
            submit = st.form_submit_button("Sign In →", use_container_width=True, type="primary")

        if submit:
            if not username or not password:
                st.error("Please enter both username and password.")
            else:
                with st.spinner("Signing in... (first request may take ~30s to wake the server ☕)"):
                    try:
                        resp = api_post("/auth/login", json={"username": username, "password": password})
                        if resp.status_code == 200:
                            data = resp.json()
                            st.session_state["token"] = data["access_token"]
                            st.session_state["user"]  = {"username": username}
                            st.success("✅ Signed in! Redirecting...")
                            st.switch_page("Home.py")
                        elif resp.status_code == 401:
                            st.error("❌ Invalid username or password.")
                        else:
                            st.error(f"Login failed: {resp.text}")
                    except Exception as e:
                        st.error(f"Could not connect to server: {e}")

    # ------------------------------------------------------------------
    # REGISTER TAB
    # ------------------------------------------------------------------
    with tab_register:
        with st.form("register_form"):
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
            reg_username = st.text_input("Username", placeholder="choose_a_username",        key="reg_user")
            reg_email    = st.text_input("Email",    placeholder="you@example.com",           key="reg_email")
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                reg_password = st.text_input("Password",         type="password", placeholder="Min 8 chars", key="reg_pass")
            with col_p2:
                reg_confirm  = st.text_input("Confirm Password", type="password", placeholder="Repeat",      key="reg_confirm")
            st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)
            reg_submit = st.form_submit_button("Create Account →", use_container_width=True, type="primary")

        if reg_submit:
            if not all([reg_username, reg_email, reg_password, reg_confirm]):
                st.error("All fields are required.")
            elif reg_password != reg_confirm:
                st.error("Passwords do not match.")
            elif len(reg_password) < 8:
                st.error("Password must be at least 8 characters.")
            else:
                with st.spinner("Creating account... (first request may take ~30s to wake the server ☕)"):
                    try:
                        resp = api_post("/auth/register", json={
                            "username": reg_username,
                            "email":    reg_email,
                            "password": reg_password,
                        })
                        if resp.status_code == 201:
                            data = resp.json()
                            st.session_state["token"] = data["access_token"]
                            st.session_state["user"]  = {"username": reg_username}
                            st.success("🎉 Account created! Welcome aboard!")
                            st.switch_page("Home.py")
                        elif resp.status_code == 400:
                            st.error(resp.json().get("detail", "Registration failed."))
                        else:
                            st.error(f"Registration failed: {resp.text}")
                    except Exception as e:
                        st.error(f"Could not connect to server: {e}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
<div style="text-align:center">
    <small style="color:#334155">Backend: <code style="color:#7c3aed">{BACKEND_URL}</code></small>
</div>
""", unsafe_allow_html=True)
