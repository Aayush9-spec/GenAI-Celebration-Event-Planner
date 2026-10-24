import streamlit as st

st.set_page_config(page_title="Login — Event Planner", page_icon="🎉", layout="centered")

# Inject custom CSS
st.markdown("""
<style>
    .auth-header { text-align: center; padding: 2rem 0 1rem 0; }
    .auth-header h1 { font-size: 2.2rem; color: #7c5cd8; }
    .auth-header p { color: #57606a; font-size: 1rem; }
    .stTabs [data-baseweb="tab-list"] { justify-content: center; }
    div[data-testid="stForm"] {
        background: #f7f8fa;
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="auth-header">
    <h1>🎉 Event Planner</h1>
    <p>Sign in to start planning your perfect celebration</p>
</div>
""", unsafe_allow_html=True)

# Import API helpers
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.api import api_post, BACKEND_URL

tab_login, tab_register = st.tabs(["🔑 Sign In", "📝 Create Account"])

# ------------------------------------------------------------------
# LOGIN TAB
# ------------------------------------------------------------------
with tab_login:
    with st.form("login_form"):
        st.subheader("Welcome back!")
        username = st.text_input("Username", placeholder="your_username")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        submit = st.form_submit_button("Sign In", use_container_width=True, type="primary")

    if submit:
        if not username or not password:
            st.error("Please enter both username and password.")
        else:
            with st.spinner("Signing in..."):
                try:
                    resp = api_post("/auth/login", json={"username": username, "password": password})
                    if resp.status_code == 200:
                        data = resp.json()
                        st.session_state["token"] = data["access_token"]
                        st.session_state["user"] = {"username": username}
                        st.success("Signed in successfully!")
                        st.switch_page("Home.py")
                    elif resp.status_code == 401:
                        st.error("Invalid username or password.")
                    else:
                        st.error(f"Login failed: {resp.text}")
                except Exception as e:
                    st.error(f"Could not connect to server: {e}")

# ------------------------------------------------------------------
# REGISTER TAB
# ------------------------------------------------------------------
with tab_register:
    with st.form("register_form"):
        st.subheader("Create your account")
        reg_username = st.text_input("Username", placeholder="choose_a_username", key="reg_user")
        reg_email = st.text_input("Email", placeholder="you@example.com", key="reg_email")
        reg_password = st.text_input("Password", type="password", placeholder="Min 8 characters", key="reg_pass")
        reg_confirm = st.text_input("Confirm Password", type="password", placeholder="Repeat password", key="reg_confirm")
        reg_submit = st.form_submit_button("Create Account", use_container_width=True, type="primary")

    if reg_submit:
        if not all([reg_username, reg_email, reg_password, reg_confirm]):
            st.error("All fields are required.")
        elif reg_password != reg_confirm:
            st.error("Passwords do not match.")
        elif len(reg_password) < 8:
            st.error("Password must be at least 8 characters.")
        else:
            with st.spinner("Creating account..."):
                try:
                    resp = api_post("/auth/register", json={
                        "username": reg_username,
                        "email": reg_email,
                        "password": reg_password,
                    })
                    if resp.status_code == 201:
                        data = resp.json()
                        st.session_state["token"] = data["access_token"]
                        st.session_state["user"] = {"username": reg_username}
                        st.success("Account created! Welcome aboard 🎉")
                        st.switch_page("Home.py")
                    elif resp.status_code == 400:
                        st.error(resp.json().get("detail", "Registration failed."))
                    else:
                        st.error(f"Registration failed: {resp.text}")
                except Exception as e:
                    st.error(f"Could not connect to server: {e}")

st.divider()
st.caption(f"Backend: `{BACKEND_URL}`")
