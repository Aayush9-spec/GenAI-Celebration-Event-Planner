import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from utils.styles import inject_global_styles, render_sidebar
from utils.api import is_authenticated, api_get

st.set_page_config(
    page_title="🎉 CelebAI — Event Planner",
    page_icon="🎉",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_global_styles()

if is_authenticated():
    render_sidebar(st.session_state.get("current_event_title"))

# ------------------------------------------------------------------
# HERO
# ------------------------------------------------------------------
st.markdown("""
<div class="hero-section fade-in">
    <div class="hero-badge">🏆 Built for Hack2Skill &nbsp;·&nbsp; Powered by Google Gemini</div>
    <h1>🎉 CelebAI — Event Planner</h1>
    <p>Your AI co-planner for weddings, birthdays & community events<br>
    <span style="font-size:0.95rem;opacity:0.8">Budgets · Timelines · Vendor Checklists · Personalized Ideas</span></p>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# AUTH GATE
# ------------------------------------------------------------------
if not is_authenticated():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
<div style="text-align:center;padding:2.5rem 2rem;background:rgba(255,255,255,0.04);
border:1px solid rgba(255,255,255,0.1);border-radius:20px">
    <div style="font-size:3rem;margin-bottom:0.8rem">👋</div>
    <h3 style="color:#e2e8f0;margin:0 0 0.5rem 0">Welcome! Sign in to get started</h3>
    <p style="color:#94a3b8;margin:0 0 1.5rem 0">Create an account to start planning your perfect celebration with AI.</p>
</div>
""", unsafe_allow_html=True)
        if st.button("🔑  Sign In / Create Account", use_container_width=True, type="primary"):
            st.switch_page("pages/1_Login.py")

    st.markdown("<br>", unsafe_allow_html=True)

    # Features preview for non-logged in users
    st.markdown("""
<h3 style="color:#e2e8f0;text-align:center;margin-bottom:1.5rem">What you get with CelebAI</h3>
""", unsafe_allow_html=True)

    features = [
        ("💰", "Smart Budget Planner", "AI generates itemized cost breakdowns for your exact guest count, city, and event type."),
        ("📅", "Adaptive Timeline",    "Week-by-week milestones that adapt to your event date — from 1 week to 1+ year away."),
        ("✅", "Vendor Checklist",     "Never miss a supplier. Category-wise checklists with deadlines and expert booking tips."),
        ("🤖", "AI Chat Assistant",    "Conversational AI that knows your event — ask anything, get instant actionable answers."),
        ("🎨", "Theme & Ideas",        "Personalized theme suggestions, color palettes, and creative ideas for your celebration."),
        ("📄", "PDF Export",           "Download your complete event plan as a polished PDF to share with your team or family."),
    ]
    cols = st.columns(3)
    for i, (icon, title, desc) in enumerate(features):
        with cols[i % 3]:
            st.markdown(f"""
<div class="feature-card">
    <span class="icon">{icon}</span>
    <h3>{title}</h3>
    <p>{desc}</p>
</div>
""", unsafe_allow_html=True)
        if i == 2:
            st.markdown("<br>", unsafe_allow_html=True)

    st.divider()
    st.markdown("""
<div style="text-align:center;padding:1rem 0">
    <small style="color:#475569">GenAI Celebration & Event Planner · Hack2Skill Challenge · Powered by Google Gemini 1.5 Flash</small>
</div>
""", unsafe_allow_html=True)
    st.stop()

# ------------------------------------------------------------------
# DASHBOARD — STATS BAR
# ------------------------------------------------------------------
resp = api_get("/events/")
events = resp.json() if resp.status_code == 200 else []

total_budget = sum(e["total_budget"] for e in events)
total_guests = sum(e["guest_count"] for e in events)
total_plans  = sum(e["plan_count"]  for e in events)

m1, m2, m3, m4 = st.columns(4)
m1.metric("📋 Total Events",    len(events))
m2.metric("👥 Total Guests",    f"{total_guests:,}")
m3.metric("💰 Total Budget",    f"₹{total_budget:,.0f}" if total_budget < 10_000_000 else f"₹{total_budget/1_00_000:.1f}L")
m4.metric("✨ Plans Generated", total_plans)

st.markdown("<br>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# QUICK START
# ------------------------------------------------------------------
st.markdown("""
<div class="section-header">🚀 Quick Start — Create New Event</div>
""", unsafe_allow_html=True)

col_w, col_b, col_c, _ = st.columns([1, 1, 1, 1])
with col_w:
    if st.button("💍  Wedding", use_container_width=True, type="primary"):
        st.session_state["quick_event_type"] = "wedding"
        st.switch_page("pages/2_My_Events.py")
with col_b:
    if st.button("🎂  Birthday Party", use_container_width=True):
        st.session_state["quick_event_type"] = "birthday"
        st.switch_page("pages/2_My_Events.py")
with col_c:
    if st.button("🏘️  Community Event", use_container_width=True):
        st.session_state["quick_event_type"] = "community"
        st.switch_page("pages/2_My_Events.py")

st.markdown("<br>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# RECENT EVENTS
# ------------------------------------------------------------------
if events:
    st.markdown('<div class="section-header">📅 Your Recent Events</div>', unsafe_allow_html=True)

    BADGE = {"wedding": ("💍", "badge-wedding", "Wedding"),
             "birthday": ("🎂", "badge-birthday", "Birthday"),
             "community": ("🏘️", "badge-community", "Community")}

    for ev in events[:5]:
        icon, badge_cls, label = BADGE.get(ev["event_type"], ("🎉", "badge-birthday", ev["event_type"].title()))
        col_info, col_btn = st.columns([5, 1])
        with col_info:
            st.markdown(f"""
<div class="event-card">
    <div style="display:flex;align-items:center;gap:0.75rem;flex-wrap:wrap">
        <span class="badge {badge_cls}">{icon} {label}</span>
        <span style="color:#e2e8f0;font-weight:600;font-size:1rem">{ev['title']}</span>
        <span style="color:#64748b;font-size:0.82rem">·</span>
        <span style="color:#94a3b8;font-size:0.85rem">📅 {ev['event_date']}</span>
        <span style="color:#64748b;font-size:0.82rem">·</span>
        <span style="color:#94a3b8;font-size:0.85rem">👥 {ev['guest_count']} guests</span>
        <span style="color:#64748b;font-size:0.82rem">·</span>
        <span style="color:#a78bfa;font-size:0.85rem;font-weight:500">₹{ev['total_budget']:,.0f}</span>
        <span style="color:#64748b;font-size:0.82rem">·</span>
        <span style="color:#94a3b8;font-size:0.82rem">📋 {ev['plan_count']} plan(s)</span>
    </div>
</div>""", unsafe_allow_html=True)
        with col_btn:
            st.write("")
            if st.button("✨ Plan", key=f"hp_{ev['id']}", use_container_width=True, type="primary"):
                st.session_state["current_event_id"]    = ev["id"]
                st.session_state["current_event_title"] = ev["title"]
                st.switch_page("pages/3_Plan_Generator.py")
else:
    st.markdown("""
<div style="text-align:center;padding:3rem;background:rgba(255,255,255,0.03);
border:1px dashed rgba(255,255,255,0.1);border-radius:20px">
    <div style="font-size:3rem;margin-bottom:1rem">🎉</div>
    <h3 style="color:#e2e8f0;margin:0 0 0.5rem 0">No events yet</h3>
    <p style="color:#64748b;margin:0">Use Quick Start above to create your first event!</p>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# HOW IT WORKS
# ------------------------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-header">🔄 How It Works</div>', unsafe_allow_html=True)

steps = [
    ("1️⃣", "Create an Event",    "Add your event details — type, date, guests, budget, and city."),
    ("2️⃣", "Generate AI Plan",   "One click — Gemini AI creates your full plan in seconds."),
    ("3️⃣", "Refine with Chat",   "Ask follow-up questions to the AI assistant for deeper guidance."),
    ("4️⃣", "Export & Execute",   "Download your plan as PDF and start ticking off the checklist."),
]
step_cols = st.columns(4)
for col, (num, title, desc) in zip(step_cols, steps):
    with col:
        st.markdown(f"""
<div class="glass-card" style="text-align:center">
    <div style="font-size:2rem;margin-bottom:0.5rem">{num}</div>
    <div style="color:#e2e8f0;font-weight:600;margin-bottom:0.3rem;font-size:0.95rem">{title}</div>
    <div style="color:#94a3b8;font-size:0.82rem;line-height:1.5">{desc}</div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# FOOTER
# ------------------------------------------------------------------
st.divider()
st.markdown("""
<div style="text-align:center;padding:0.5rem 0 1rem 0">
    <small style="color:#334155">
        🎉 CelebAI — GenAI Celebration & Event Planner &nbsp;·&nbsp;
        Powered by <span style="color:#7c3aed">Google Gemini 1.5 Flash</span> &nbsp;·&nbsp;
        Built for <span style="color:#06b6d4">Hack2Skill 2024</span> 🏆
    </small>
</div>
""", unsafe_allow_html=True)
