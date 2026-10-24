import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from utils.styles import inject_global_styles, render_sidebar
from utils.api import is_authenticated

st.set_page_config(
    page_title="🎉 Event Planner — AI-Powered",
    page_icon="🎉",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_global_styles()

# Render sidebar
current_event = st.session_state.get("current_event_title")
if is_authenticated():
    render_sidebar(current_event)

# ------------------------------------------------------------------
# Hero Section
# ------------------------------------------------------------------
st.markdown("""
<div class="hero-section">
    <h1>🎉 Celebration & Event Planner</h1>
    <p>AI-powered planning for weddings, birthdays & community events<br>
    Powered by Google Gemini — budgets, timelines, vendors & more</p>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Auth Gate
# ------------------------------------------------------------------
if not is_authenticated():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
<div style="text-align:center;padding:2rem;background:#f7f8fa;border-radius:12px;border:1px solid #e5e7eb">
    <h3>Welcome! Please sign in to get started 👋</h3>
    <p style="color:#57606a">Create an account or log in to start planning your perfect event.</p>
</div>
""", unsafe_allow_html=True)
        if st.button("🔑 Sign In / Create Account", use_container_width=True, type="primary"):
            st.switch_page("pages/1_Login.py")
    st.stop()

# ------------------------------------------------------------------
# Feature Cards
# ------------------------------------------------------------------
st.markdown("### ✨ What can you do?")
col1, col2, col3, col4 = st.columns(4)

features = [
    ("💰", "Budget Planner", "AI generates a detailed cost breakdown tailored to your event type, guest count, and city."),
    ("📅", "Smart Timeline", "Auto-generated milestone timeline — from booking vendors to the event day."),
    ("✅", "Vendor Checklist", "Category-wise vendor tasks with booking deadlines and expert tips."),
    ("🤖", "AI Assistant", "Chat with your personal event planning AI — ask anything, anytime."),
]

for col, (icon, title, desc) in zip([col1, col2, col3, col4], features):
    with col:
        st.markdown(f"""
<div class="feature-card">
    <div style="font-size:2.5rem">{icon}</div>
    <h3>{title}</h3>
    <p>{desc}</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ------------------------------------------------------------------
# Quick Start
# ------------------------------------------------------------------
st.markdown("### 🚀 Quick Start")
st.markdown("Create a new event in seconds:")

col_w, col_b, col_c, col_space = st.columns([1, 1, 1, 1])

with col_w:
    if st.button("💍 Plan a Wedding", use_container_width=True, type="primary"):
        st.session_state["quick_event_type"] = "wedding"
        st.switch_page("pages/2_My_Events.py")
with col_b:
    if st.button("🎂 Plan a Birthday", use_container_width=True):
        st.session_state["quick_event_type"] = "birthday"
        st.switch_page("pages/2_My_Events.py")
with col_c:
    if st.button("🏘️ Community Event", use_container_width=True):
        st.session_state["quick_event_type"] = "community"
        st.switch_page("pages/2_My_Events.py")

st.divider()

# ------------------------------------------------------------------
# Stats / Existing Events Summary
# ------------------------------------------------------------------
from utils.api import api_get

resp = api_get("/events/")
if resp.status_code == 200:
    events = resp.json()
    if events:
        st.markdown("### 📊 Your Events")
        m1, m2, m3, m4 = st.columns(4)
        total_budget = sum(e["total_budget"] for e in events)
        total_guests = sum(e["guest_count"] for e in events)
        total_plans = sum(e["plan_count"] for e in events)
        m1.metric("Total Events", len(events))
        m2.metric("Total Guests", f"{total_guests:,}")
        m3.metric("Total Budget", f"₹{total_budget:,.0f}")
        m4.metric("Plans Generated", total_plans)

        st.markdown("**Recent Events**")
        for ev in events[:3]:
            icon = {"wedding": "💍", "birthday": "🎂", "community": "🏘️"}.get(ev["event_type"], "🎉")
            col_ev, col_btn = st.columns([5, 1])
            with col_ev:
                st.markdown(
                    f"{icon} **{ev['title']}** — {ev['event_date']} · "
                    f"{ev['guest_count']} guests · ₹{ev['total_budget']:,.0f}"
                )
            with col_btn:
                if st.button("Plan ✨", key=f"home_plan_{ev['id']}", use_container_width=True):
                    st.session_state["current_event_id"] = ev["id"]
                    st.session_state["current_event_title"] = ev["title"]
                    st.switch_page("pages/3_Plan_Generator.py")
    else:
        st.info("No events yet — create your first event using Quick Start above! 👆")

# ------------------------------------------------------------------
# Footer
# ------------------------------------------------------------------
st.divider()
st.markdown(
    "<center><small style='color:#57606a'>Made with ❤️ using Google Gemini AI · "
    "Celebration & Event Planner · Built for Hack2Skill</small></center>",
    unsafe_allow_html=True,
)
