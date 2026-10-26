"""
Global styles + sidebar for GenAI Event Planner.
Premium dark theme with glassmorphism, animations, and rich visual hierarchy.
"""
import streamlit as st

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
    --primary:       #7c3aed;
    --primary-light: #a78bfa;
    --primary-dark:  #5b21b6;
    --secondary:     #06b6d4;
    --accent:        #f59e0b;
    --success:       #10b981;
    --danger:        #ef4444;
    --text:          #e2e8f0;
    --text-muted:    #94a3b8;
    --card:          rgba(255,255,255,0.05);
    --card-border:   rgba(255,255,255,0.1);
    --radius:        16px;
}

/* BASE */
.stApp {
    background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%) !important;
    font-family: 'Inter', -apple-system, sans-serif !important;
    color: var(--text) !important;
    min-height: 100vh;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; max-width: 1200px !important; }

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0d1a 0%, #1a1a2e 100%) !important;
    border-right: 1px solid rgba(124,58,237,0.25) !important;
}
section[data-testid="stSidebar"] * { color: var(--text) !important; }
section[data-testid="stSidebar"] .stButton button {
    background: rgba(124,58,237,0.1) !important;
    border: 1px solid rgba(124,58,237,0.25) !important;
    color: var(--text) !important;
    border-radius: 10px !important;
    font-size: 0.88rem !important;
    transition: all 0.2s !important;
}
section[data-testid="stSidebar"] .stButton button:hover {
    background: rgba(124,58,237,0.25) !important;
    border-color: var(--primary-light) !important;
    transform: translateX(3px) !important;
}

/* HERO */
.hero-section {
    background: linear-gradient(135deg, #7c3aed 0%, #06b6d4 100%);
    border-radius: 24px; padding: 4rem 3rem;
    text-align: center; margin-bottom: 2.5rem;
    position: relative; overflow: hidden;
    box-shadow: 0 20px 60px rgba(124,58,237,0.35);
}
.hero-section::before {
    content: '';
    position: absolute; top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(circle at 30% 20%, rgba(255,255,255,0.12) 0%, transparent 60%);
    pointer-events: none;
}
.hero-section h1 {
    font-size: 3rem; font-weight: 800; color: white !important;
    margin: 0 0 1rem 0; letter-spacing: -0.5px;
    text-shadow: 0 2px 20px rgba(0,0,0,0.2);
}
.hero-section p {
    font-size: 1.15rem; color: rgba(255,255,255,0.88) !important;
    margin: 0; line-height: 1.7;
}
.hero-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(255,255,255,0.18); backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 50px; padding: 6px 18px;
    font-size: 0.83rem; color: white !important; margin-bottom: 1.5rem;
    font-weight: 500;
}

/* FEATURE CARDS */
.feature-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px; padding: 1.8rem 1.4rem;
    text-align: center; height: 100%;
    transition: all 0.3s ease; position: relative; overflow: hidden;
}
.feature-card::after {
    content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #7c3aed, #06b6d4);
    transform: scaleX(0); transition: transform 0.3s ease; transform-origin: left;
}
.feature-card:hover::after { transform: scaleX(1); }
.feature-card:hover {
    border-color: rgba(124,58,237,0.4);
    box-shadow: 0 12px 40px rgba(124,58,237,0.15);
    transform: translateY(-4px);
}
.feature-card .icon { font-size: 2.6rem; margin-bottom: 0.9rem; display: block; }
.feature-card h3 { color: var(--text) !important; font-size: 1rem; font-weight: 600; margin: 0 0 0.5rem 0; }
.feature-card p  { color: var(--text-muted) !important; font-size: 0.84rem; line-height: 1.55; margin: 0; }

/* GLASS CARD */
.glass-card {
    background: rgba(255,255,255,0.05); backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: var(--radius); padding: 1.5rem;
    transition: all 0.3s ease; position: relative; overflow: hidden;
}
.glass-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
}
.glass-card:hover {
    border-color: rgba(124,58,237,0.45);
    box-shadow: 0 8px 32px rgba(124,58,237,0.18);
    transform: translateY(-2px);
}

/* SECTION HEADER */
.section-header {
    display: flex; align-items: center; gap: 10px;
    background: linear-gradient(90deg, rgba(124,58,237,0.18), rgba(6,182,212,0.08), transparent);
    border-left: 4px solid var(--primary);
    padding: 0.7rem 1.2rem; border-radius: 0 12px 12px 0;
    margin: 2rem 0 1.2rem 0; color: var(--text) !important;
    font-weight: 600; font-size: 1.05rem;
}

/* BADGES */
.badge { display: inline-flex; align-items: center; gap: 4px;
    padding: 0.2rem 0.75rem; border-radius: 50px;
    font-size: 0.73rem; font-weight: 600; }
.badge-wedding   { background: rgba(244,63,94,0.12);  color: #fb7185 !important; border: 1px solid rgba(244,63,94,0.25); }
.badge-birthday  { background: rgba(124,58,237,0.12); color: #a78bfa !important; border: 1px solid rgba(124,58,237,0.25); }
.badge-community { background: rgba(16,185,129,0.12); color: #34d399 !important; border: 1px solid rgba(16,185,129,0.25); }

/* METRICS */
div[data-testid="metric-container"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 14px !important; padding: 1rem !important;
    transition: all 0.2s;
}
div[data-testid="metric-container"]:hover { border-color: rgba(124,58,237,0.35) !important; }
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 1.7rem !important; font-weight: 700 !important; color: var(--primary-light) !important;
}
div[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    color: var(--text-muted) !important; font-size: 0.82rem !important;
}

/* BUTTONS */
.stButton button { border-radius: 10px !important; font-weight: 500 !important; transition: all 0.2s ease !important; }
.stButton button[kind="primary"] {
    background: linear-gradient(135deg, #7c3aed, #06b6d4) !important;
    border: none !important; box-shadow: 0 4px 15px rgba(124,58,237,0.35) !important; color: white !important;
}
.stButton button[kind="primary"]:hover {
    box-shadow: 0 6px 22px rgba(124,58,237,0.55) !important; transform: translateY(-1px) !important;
}
.stButton button[kind="secondary"] {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important; color: var(--text) !important;
}
.stButton button[kind="secondary"]:hover {
    background: rgba(255,255,255,0.1) !important; border-color: var(--primary-light) !important;
}

/* INPUTS */
.stTextInput input, .stTextArea textarea, .stNumberInput input {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important; color: var(--text) !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.18) !important;
}
label, .stTextInput label, .stSelectbox label { color: var(--text-muted) !important; font-size: 0.86rem !important; }

/* SELECT */
div[data-baseweb="select"] > div {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important; color: var(--text) !important;
}

/* TABS */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.04) !important;
    border-radius: 12px !important; padding: 4px !important; gap: 4px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
}
.stTabs [data-baseweb="tab"] { border-radius: 8px !important; color: var(--text-muted) !important; font-weight: 500 !important; }
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #7c3aed, #06b6d4) !important; color: white !important;
}

/* FORMS */
div[data-testid="stForm"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 20px !important; padding: 2rem !important;
}

/* ALERTS */
div[data-testid="stInfo"]    { background: rgba(6,182,212,0.08) !important;  border: 1px solid rgba(6,182,212,0.25) !important;  border-radius: 12px !important; }
div[data-testid="stSuccess"] { background: rgba(16,185,129,0.08) !important; border: 1px solid rgba(16,185,129,0.25) !important; border-radius: 12px !important; }
div[data-testid="stError"]   { background: rgba(239,68,68,0.08) !important;  border: 1px solid rgba(239,68,68,0.25) !important;  border-radius: 12px !important; }
div[data-testid="stWarning"] { background: rgba(245,158,11,0.08) !important; border: 1px solid rgba(245,158,11,0.25) !important; border-radius: 12px !important; }

/* CHAT */
div[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 14px !important; margin-bottom: 0.6rem !important;
}
.stChatInput textarea {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 12px !important; color: var(--text) !important;
}

/* TIMELINE */
.timeline-item {
    border-left: 3px solid var(--primary); padding: 0.6rem 1rem;
    margin-bottom: 0.6rem; background: rgba(255,255,255,0.03);
    border-radius: 0 10px 10px 0; transition: all 0.2s;
}
.timeline-item:hover { background: rgba(124,58,237,0.07); border-left-color: var(--primary-light); }
.timeline-item.priority-high   { border-left-color: #ef4444; }
.timeline-item.priority-medium { border-left-color: #f59e0b; }
.timeline-item.priority-low    { border-left-color: #10b981; }

/* THEME & VENDOR CARDS */
.theme-card, .event-card {
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px; padding: 1.2rem; margin-bottom: 0.75rem; transition: all 0.2s;
}
.theme-card:hover, .event-card:hover {
    border-color: rgba(124,58,237,0.4); background: rgba(124,58,237,0.05);
    box-shadow: 0 4px 20px rgba(124,58,237,0.12);
}

/* USER AVATAR */
.user-avatar {
    width: 48px; height: 48px;
    background: linear-gradient(135deg, #7c3aed, #06b6d4);
    border-radius: 50%; display: flex; align-items: center; justify-content: center;
    color: white; font-weight: 700; font-size: 1.2rem;
    margin: 0 auto 0.5rem auto;
    box-shadow: 0 4px 15px rgba(124,58,237,0.35);
}

/* BUDGET BAR */
.budget-bar-container { background: rgba(255,255,255,0.08); border-radius: 6px; height: 8px; overflow: hidden; margin: 4px 0; }
.budget-bar-fill { height: 100%; border-radius: 6px; background: linear-gradient(90deg, #7c3aed, #06b6d4); }

/* SCROLLBAR */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); }
::-webkit-scrollbar-thumb { background: rgba(124,58,237,0.35); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--primary); }

/* DIVIDER */
hr { border-color: rgba(255,255,255,0.07) !important; margin: 1.5rem 0 !important; }

/* SPINNER */
.stSpinner > div { border-top-color: var(--primary) !important; }

/* CHECKBOX */
.stCheckbox label { color: var(--text) !important; font-size: 0.88rem !important; }

/* NUMBER INPUT */
.stNumberInput button { background: rgba(255,255,255,0.06) !important; border-color: rgba(255,255,255,0.12) !important; color: var(--text) !important; }

/* DATE INPUT */
.stDateInput input { background: rgba(255,255,255,0.06) !important; border: 1px solid rgba(255,255,255,0.12) !important; border-radius: 10px !important; color: var(--text) !important; }

/* EXPANDER */
.streamlit-expanderHeader { background: rgba(255,255,255,0.04) !important; border: 1px solid rgba(255,255,255,0.08) !important; border-radius: 10px !important; color: var(--text) !important; }
.streamlit-expanderContent { background: rgba(255,255,255,0.02) !important; border: 1px solid rgba(255,255,255,0.06) !important; border-top: none !important; border-radius: 0 0 10px 10px !important; }

/* PAGE LINK */
a[data-testid="stPageLink-NavLink"] {
    color: var(--text-muted) !important; font-size: 0.9rem !important;
    padding: 0.5rem 0.75rem !important; border-radius: 8px !important;
    display: flex !important; align-items: center !important;
    transition: all 0.2s !important; text-decoration: none !important;
    margin: 1px 0 !important;
}
a[data-testid="stPageLink-NavLink"]:hover {
    background: rgba(124,58,237,0.12) !important; color: var(--primary-light) !important;
}

@keyframes fadeInUp { from { opacity:0; transform:translateY(16px); } to { opacity:1; transform:translateY(0); } }
.fade-in { animation: fadeInUp 0.45s ease forwards; }
@keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:0.6; } }
.pulse { animation: pulse 2s infinite; }
</style>
"""


def inject_global_styles():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def render_sidebar(current_event_title: str = None):
    with st.sidebar:
        user = st.session_state.get("user", {})
        username = user.get("username", "User") if user else "User"
        initials = username[:2].upper()

        st.markdown(f"""
<div style="padding:1.5rem 1rem 1rem 1rem;border-bottom:1px solid rgba(255,255,255,0.07)">
    <div class="user-avatar">{initials}</div>
    <div style="text-align:center">
        <div style="font-weight:600;font-size:1rem;color:#e2e8f0">{username}</div>
        <div style="font-size:0.75rem;color:#7c3aed;font-weight:500;letter-spacing:0.3px">✨ AI Event Planner</div>
    </div>
</div>
""", unsafe_allow_html=True)

        if current_event_title:
            st.markdown(f"""
<div style="margin:0.8rem 0.75rem;background:rgba(124,58,237,0.12);border:1px solid rgba(124,58,237,0.28);
border-radius:10px;padding:0.6rem 0.8rem;font-size:0.82rem">
    <div style="color:#a78bfa;font-weight:600;font-size:0.72rem;letter-spacing:0.5px;margin-bottom:3px">🎯 ACTIVE EVENT</div>
    <div style="color:#e2e8f0">{current_event_title[:30]}{"…" if len(current_event_title)>30 else ""}</div>
</div>
""", unsafe_allow_html=True)

        st.markdown("""
<div style="padding:0.5rem 0.75rem 0.3rem;color:#475569;font-size:0.7rem;font-weight:700;
letter-spacing:0.8px;margin-top:0.5rem">NAVIGATION</div>
""", unsafe_allow_html=True)

        pages = [
            ("🏠", "Dashboard",       "Home.py"),
            ("📅", "My Events",       "pages/2_My_Events.py"),
            ("✨", "Plan Generator",  "pages/3_Plan_Generator.py"),
            ("🤖", "AI Assistant",    "pages/4_AI_Assistant.py"),
        ]
        for icon, label, path in pages:
            st.page_link(path, label=f"{icon}  {label}")

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        st.divider()

        if st.button("🚪  Sign Out", use_container_width=True, key="sidebar_logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.switch_page("pages/1_Login.py")

        st.markdown("""
<div style="padding:1rem 0.75rem;border-top:1px solid rgba(255,255,255,0.06);text-align:center;margin-top:0.5rem">
    <div style="font-size:0.68rem;color:#334155;margin-bottom:2px">Powered by</div>
    <div style="font-size:0.8rem;color:#7c3aed;font-weight:600">Google Gemini Flash</div>
    <div style="font-size:0.68rem;color:#334155;margin-top:4px">Built for Hack2Skill 🏆</div>
</div>
""", unsafe_allow_html=True)
