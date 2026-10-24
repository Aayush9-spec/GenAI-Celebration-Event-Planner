import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from utils.api import api_get, api_post, api_put, api_delete
from utils.auth_guard import require_auth
from utils.styles import inject_global_styles, render_sidebar

st.set_page_config(page_title="My Events — Event Planner", page_icon="🎉", layout="wide")
require_auth()
inject_global_styles()
render_sidebar(st.session_state.get("current_event_title"))

st.markdown("""
<style>
    .event-card {
        background: #f7f8fa; border: 1px solid #e5e7eb;
        border-radius: 12px; padding: 1.2rem 1.5rem; margin-bottom: 0.8rem;
    }
    .event-badge {
        display: inline-block; padding: 0.2rem 0.7rem;
        border-radius: 20px; font-size: 0.78rem; font-weight: 600; margin-bottom: 0.5rem;
    }
    .badge-wedding { background: #fce7f3; color: #9d174d; }
    .badge-birthday { background: #ede9fe; color: #5b21b6; }
    .badge-community { background: #d1fae5; color: #065f46; }
</style>
""", unsafe_allow_html=True)

EVENT_ICONS = {"wedding": "💍", "birthday": "🎂", "community": "🏘️"}
BADGE_CLASSES = {"wedding": "badge-wedding", "birthday": "badge-birthday", "community": "badge-community"}

st.title("📅 My Events")

# ------------------------------------------------------------------
# New Event Form
# ------------------------------------------------------------------
with st.expander("➕ Create New Event", expanded=False):
    with st.form("new_event_form"):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Event Title *", placeholder="Sarah & John's Wedding")
            event_type = st.selectbox("Event Type *", ["wedding", "birthday", "community"])
            event_date = st.date_input("Event Date *")
        with col2:
            guest_count = st.number_input("Guest Count *", min_value=1, value=50)
            total_budget = st.number_input("Total Budget (₹) *", min_value=1000.0, value=100000.0, step=1000.0)
            city = st.text_input("City", placeholder="Mumbai")
        description = st.text_area("Description (optional)", placeholder="Brief description of the event...")
        submitted = st.form_submit_button("Create Event 🎉", use_container_width=True, type="primary")

    if submitted:
        from datetime import date, timedelta
        if event_date < date.today() + timedelta(days=6):
            st.error("Event date must be at least 1 week in the future.")
        elif not title:
            st.error("Event title is required.")
        else:
            payload = {
                "title": title,
                "event_type": event_type,
                "event_date": event_date.isoformat(),
                "guest_count": int(guest_count),
                "total_budget": float(total_budget),
                "city": city or None,
                "description": description or None,
            }
            resp = api_post("/events/", json=payload, authenticated=True)
            if resp.status_code == 201:
                st.success(f"Event '{title}' created! 🎉")
                st.rerun()
            else:
                st.error(f"Failed: {resp.json().get('detail', resp.text)}")

# ------------------------------------------------------------------
# List Events
# ------------------------------------------------------------------
resp = api_get("/events/")
if resp.status_code == 401:
    st.warning("Session expired. Please log in again.")
    st.switch_page("pages/1_Login.py")
elif resp.status_code != 200:
    st.error("Could not load events.")
else:
    events = resp.json()
    if not events:
        st.info("No events yet. Create your first event above! 👆")
    else:
        st.markdown(f"**{len(events)} event(s) found**")
        for ev in events:
            icon = EVENT_ICONS.get(ev["event_type"], "🎉")
            badge_cls = BADGE_CLASSES.get(ev["event_type"], "badge-wedding")
            col_main, col_actions = st.columns([4, 1])
            with col_main:
                st.markdown(f"""
<div class="event-card">
    <span class="event-badge {badge_cls}">{icon} {ev['event_type'].capitalize()}</span>
    <h4 style="margin:0.2rem 0">{ev['title']}</h4>
    <p style="color:#57606a; margin:0">
        📅 {ev['event_date']} &nbsp;|&nbsp; 👥 {ev['guest_count']} guests &nbsp;|&nbsp;
        💰 ₹{ev['total_budget']:,.0f} &nbsp;|&nbsp; 📋 {ev['plan_count']} plan(s)
        {f"&nbsp;|&nbsp; 📍 {ev['city']}" if ev.get('city') else ""}
    </p>
</div>
""", unsafe_allow_html=True)
            with col_actions:
                st.write("")
                if st.button("✨ Plan", key=f"plan_{ev['id']}", use_container_width=True):
                    st.session_state["current_event_id"] = ev["id"]
                    st.session_state["current_event_title"] = ev["title"]
                    st.switch_page("pages/3_Plan_Generator.py")
                if st.button("🗑️ Delete", key=f"del_{ev['id']}", use_container_width=True):
                    del_resp = api_delete(f"/events/{ev['id']}")
                    if del_resp.status_code == 204:
                        st.success("Event deleted.")
                        st.rerun()
                    else:
                        st.error("Delete failed.")
