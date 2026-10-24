"""Shared CSS styles injected into every Streamlit page."""
import streamlit as st

GLOBAL_CSS = """
<style>
/* ---- Global ---- */
body { font-family: -apple-system, 'Segoe UI', system-ui, sans-serif; }

/* ---- Sidebar ---- */
section[data-testid="stSidebar"] {
    background: #1f2328 !important;
}
section[data-testid="stSidebar"] * { color: #e6edf3 !important; }
section[data-testid="stSidebar"] .stButton button {
    background: transparent !important;
    border: 1px solid #30363d !important;
    color: #e6edf3 !important;
    width: 100%;
    margin: 2px 0;
}
section[data-testid="stSidebar"] .stButton button:hover {
    background: #30363d !important;
}

/* ---- Cards ---- */
.feature-card {
    background: #f7f8fa;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    height: 100%;
    transition: box-shadow 0.2s;
}
.feature-card:hover { border-color: #7c5cd8; }
.feature-card h3 { color: #1f2328; margin: 0.5rem 0 0.3rem 0; }
.feature-card p { color: #57606a; font-size: 0.9rem; margin: 0; }

/* ---- Hero ---- */
.hero-section {
    background: linear-gradient(135deg, #7c5cd8 0%, #3b82d4 100%);
    color: white;
    padding: 3rem 2rem;
    border-radius: 16px;
    text-align: center;
    margin-bottom: 2rem;
}
.hero-section h1 { font-size: 2.8rem; margin: 0 0 0.5rem 0; }
.hero-section p { font-size: 1.1rem; opacity: 0.9; margin: 0; }

/* ---- Section headers ---- */
.section-header {
    background: linear-gradient(90deg, #7c5cd8 0%, #3b82d4 100%);
    color: white !important;
    padding: 0.6rem 1.2rem;
    border-radius: 8px;
    margin: 1.5rem 0 1rem 0;
    font-weight: 600;
}

/* ---- Badges ---- */
.badge {
    display: inline-block;
    padding: 0.2rem 0.7rem;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
}
.badge-wedding  { background: #fce7f3; color: #9d174d; }
.badge-birthday { background: #ede9fe; color: #5b21b6; }
.badge-community{ background: #d1fae5; color: #065f46; }

/* ---- User avatar ---- */
.user-avatar {
    width: 40px; height: 40px;
    background: #7c5cd8;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    color: white; font-weight: bold; font-size: 1.1rem;
    margin: 0 auto 0.5rem auto;
}

/* ---- Metric cards ---- */
div[data-testid="metric-container"] {
    background: #f7f8fa;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 0.5rem;
}
</style>
"""


def inject_global_styles():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def render_sidebar(current_event_title: str = None):
    """Render the standard sidebar with user info, nav, and logout."""
    with st.sidebar:
        user = st.session_state.get("user", {})
        username = user.get("username", "User") if user else "User"
        initials = username[:2].upper()

        st.markdown(f"""
<div style="text-align:center;padding:1rem 0 0.5rem 0">
    <div class="user-avatar">{initials}</div>
    <div style="font-weight:600;font-size:1rem">{username}</div>
    <div style="font-size:0.8rem;opacity:0.7">Event Planner</div>
</div>
""", unsafe_allow_html=True)

        if current_event_title:
            st.markdown(f"""
<div style="background:#30363d;border-radius:8px;padding:0.5rem 0.8rem;margin:0.5rem 0;font-size:0.85rem">
    🎯 <b>Active Event</b><br>{current_event_title}
</div>
""", unsafe_allow_html=True)

        st.divider()
        st.markdown("**Navigation**")
        st.page_link("Home.py", label="🏠 Dashboard")
        st.page_link("pages/2_My_Events.py", label="📅 My Events")
        st.page_link("pages/3_Plan_Generator.py", label="✨ Plan Generator")
        st.page_link("pages/4_AI_Assistant.py", label="🤖 AI Assistant")

        st.divider()
        if st.button("🚪 Sign Out", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.switch_page("pages/1_Login.py")
