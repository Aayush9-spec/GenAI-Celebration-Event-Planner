import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import plotly.graph_objects as go
from utils.api import api_get, api_post
from utils.auth_guard import require_auth
from utils.styles import inject_global_styles, render_sidebar

st.set_page_config(page_title="Plan Generator — Event Planner", page_icon="✨", layout="wide")
require_auth()
inject_global_styles()
render_sidebar(st.session_state.get("current_event_title"))

st.markdown("""
<style>
    .section-header {
        background: linear-gradient(90deg, #7c5cd8 0%, #3b82d4 100%);
        color: white; padding: 0.6rem 1.2rem; border-radius: 8px;
        margin: 1.5rem 0 1rem 0; font-weight: 600;
    }
    .theme-card {
        background: #f7f8fa; border: 1px solid #e5e7eb;
        border-radius: 10px; padding: 1rem; margin-bottom: 0.5rem;
    }
    .vendor-item { padding: 0.3rem 0; border-bottom: 1px solid #f0f0f0; }
    .timeline-item {
        border-left: 3px solid #7c5cd8; padding: 0.5rem 1rem;
        margin-bottom: 0.5rem; background: #fafafa; border-radius: 0 8px 8px 0;
    }
    .priority-high { border-left-color: #ef4444; }
    .priority-medium { border-left-color: #f59e0b; }
    .priority-low { border-left-color: #10b981; }
</style>
""", unsafe_allow_html=True)

st.title("✨ AI Plan Generator")

# ------------------------------------------------------------------
# Event Selector
# ------------------------------------------------------------------
resp = api_get("/events/")
if resp.status_code != 200:
    st.error("Could not load events. Please check your connection.")
    st.stop()

events = resp.json()
if not events:
    st.info("No events found. Create an event first in 📅 My Events.")
    st.stop()

event_options = {f"{e['title']} ({e['event_type']})": e for e in events}

# Pre-select from session state if available
default_idx = 0
if st.session_state.get("current_event_id"):
    for i, e in enumerate(events):
        if e["id"] == st.session_state["current_event_id"]:
            default_idx = i
            break

selected_label = st.selectbox("Select Event", list(event_options.keys()), index=default_idx)
selected_event = event_options[selected_label]
event_id = selected_event["id"]

st.session_state["current_event_id"] = event_id
st.session_state["current_event_title"] = selected_event["title"]

# Show event summary
col1, col2, col3, col4 = st.columns(4)
col1.metric("Event Type", selected_event["event_type"].capitalize())
col2.metric("Guests", selected_event["guest_count"])
col3.metric("Budget", f"₹{selected_event['total_budget']:,.0f}")
col4.metric("Date", selected_event["event_date"])

st.divider()

# ------------------------------------------------------------------
# Generate / Load Plan
# ------------------------------------------------------------------
col_gen, col_hist = st.columns([3, 1])

with col_gen:
    generate_btn = st.button(
        "✨ Generate AI Plan",
        type="primary",
        use_container_width=True,
        help="This will generate a new plan using Google Gemini AI (~10-20 seconds)",
    )

with col_hist:
    load_latest_btn = st.button("📂 Load Latest Plan", use_container_width=True)

plan_data = None

if generate_btn:
    with st.spinner("🤖 Generating your personalized event plan with Gemini AI... (this may take 15-20 seconds)"):
        resp = api_post(f"/events/{event_id}/plans/", authenticated=True)
        if resp.status_code == 201:
            plan_data = resp.json()
            st.session_state[f"plan_{event_id}"] = plan_data
            st.success("Plan generated successfully! 🎉")
        elif resp.status_code == 422:
            st.error(f"AI generation issue: {resp.json().get('detail', 'Unknown error')}")
        else:
            st.error(f"Failed to generate plan: {resp.text}")

elif load_latest_btn or st.session_state.get(f"plan_{event_id}"):
    if st.session_state.get(f"plan_{event_id}") and not load_latest_btn:
        plan_data = st.session_state[f"plan_{event_id}"]
    else:
        with st.spinner("Loading latest plan..."):
            resp = api_get(f"/events/{event_id}/plans/latest")
            if resp.status_code == 200:
                plan_data = resp.json()
                st.session_state[f"plan_{event_id}"] = plan_data
            elif resp.status_code == 404:
                st.info("No plan generated yet. Click '✨ Generate AI Plan' to create one.")
            else:
                st.error(f"Could not load plan: {resp.text}")

# ------------------------------------------------------------------
# Render Plan
# ------------------------------------------------------------------
if plan_data:
    # ---- BUDGET BREAKDOWN ----
    st.markdown('<div class="section-header">💰 Budget Breakdown</div>', unsafe_allow_html=True)

    budget = plan_data.get("budget_breakdown", {})
    if budget and budget.get("items"):
        items = budget["items"]
        labels = [item["category"].replace("_", " ").title() for item in items]
        values = [item["amount"] for item in items]
        total = budget.get("total", sum(values))

        col_chart, col_table = st.columns([1, 1])

        with col_chart:
            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=0.4,
                textinfo="label+percent",
                hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<br>%{percent}<extra></extra>",
            )])
            fig.update_layout(
                title=f"Total Budget: ₹{total:,.0f}",
                showlegend=False,
                margin=dict(t=40, b=0, l=0, r=0),
                height=350,
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_table:
            st.markdown(f"**Total: ₹{total:,.0f} INR**")
            for item in items:
                cat = item["category"].replace("_", " ").title()
                amt = item["amount"]
                pct = item.get("percentage", 0)
                notes = item.get("notes", "")
                st.markdown(f"""
<div style="padding:0.4rem 0; border-bottom:1px solid #e5e7eb">
    <b>{cat}</b> — ₹{amt:,.0f} <span style="color:#57606a">({pct:.1f}%)</span>
    {"<br><small style='color:#57606a'>" + notes + "</small>" if notes else ""}
</div>""", unsafe_allow_html=True)
    else:
        st.warning("Budget breakdown not available in this plan.")

    # ---- TIMELINE ----
    st.markdown('<div class="section-header">📅 Event Timeline</div>', unsafe_allow_html=True)

    timeline = plan_data.get("timeline", {})
    milestones = timeline.get("milestones", [])
    if milestones:
        # Sort by offset (most negative first = earliest)
        sorted_ms = sorted(milestones, key=lambda x: x.get("offset", 0))
        col_tl1, col_tl2 = st.columns(2)
        half = len(sorted_ms) // 2

        for col, items_chunk in [(col_tl1, sorted_ms[:half]), (col_tl2, sorted_ms[half:])]:
            with col:
                for ms in items_chunk:
                    offset = ms.get("offset", 0)
                    unit = ms.get("unit", "week")
                    task = ms.get("task", "")
                    priority = ms.get("priority", "medium")
                    cat = ms.get("category", "")

                    if offset == 0:
                        label = "🎉 Event Day"
                    elif offset < 0:
                        label = f"{abs(offset)} {unit}(s) before"
                    else:
                        label = f"{offset} {unit}(s) after"

                    prio_class = f"priority-{priority}"
                    st.markdown(f"""
<div class="timeline-item {prio_class}">
    <small style="color:#57606a">{label} {f'· {cat}' if cat else ''}</small>
    <div>{task}</div>
</div>""", unsafe_allow_html=True)
    else:
        st.warning("Timeline not available in this plan.")

    # ---- VENDOR CHECKLIST ----
    st.markdown('<div class="section-header">✅ Vendor Checklist</div>', unsafe_allow_html=True)

    vendor_data = plan_data.get("vendor_checklist", {})
    categories = vendor_data.get("categories", [])
    if categories:
        checklist_key = f"checklist_{plan_data['id']}"
        if checklist_key not in st.session_state:
            # Build initial state from plan
            state = {}
            for cat in categories:
                for i, item in enumerate(cat.get("items", [])):
                    state[f"{cat['name']}_{i}"] = item.get("done", False)
            st.session_state[checklist_key] = state

        num_cols = min(3, len(categories))
        cols = st.columns(num_cols)
        for ci, cat in enumerate(categories):
            with cols[ci % num_cols]:
                st.markdown(f"**{cat['name']}**")
                for i, item in enumerate(cat.get("items", [])):
                    key = f"{cat['name']}_{i}"
                    checked = st.checkbox(
                        item["task"],
                        value=st.session_state[checklist_key].get(key, False),
                        key=f"chk_{plan_data['id']}_{cat['name']}_{i}",
                    )
                    st.session_state[checklist_key][key] = checked
                    if item.get("tips"):
                        st.caption(f"💡 {item['tips']}")
    else:
        st.warning("Vendor checklist not available.")

    # ---- THEME IDEAS ----
    st.markdown('<div class="section-header">🎨 Theme & Ideas</div>', unsafe_allow_html=True)

    theme = plan_data.get("theme_ideas", {})
    if theme:
        rec_theme = theme.get("recommended_theme", "")
        palette = theme.get("color_palette", [])
        ideas = theme.get("ideas", [])
        tips = theme.get("personalization_tips", [])

        if rec_theme:
            st.markdown(f"### 🌟 Recommended Theme: {rec_theme}")

        if palette:
            cols_p = st.columns(len(palette))
            for i, color in enumerate(palette):
                cols_p[i].markdown(
                    f'<div style="background:{color};height:40px;border-radius:8px;margin-bottom:0.3rem"></div>'
                    f'<center><small>{color}</small></center>',
                    unsafe_allow_html=True,
                )

        if ideas:
            st.markdown("#### 💡 Creative Ideas")
            idea_cols = st.columns(min(3, len(ideas)))
            for i, idea in enumerate(ideas):
                with idea_cols[i % min(3, len(ideas))]:
                    impact_color = {"low": "#10b981", "medium": "#f59e0b", "high": "#ef4444"}.get(
                        idea.get("estimated_cost_impact", "medium"), "#57606a"
                    )
                    st.markdown(f"""
<div class="theme-card">
    <b>{idea['title']}</b>
    <span style="float:right;color:{impact_color};font-size:0.8rem">
        {idea.get('estimated_cost_impact','').upper()} COST
    </span>
    <p style="margin:0.5rem 0 0 0;color:#57606a;font-size:0.9rem">{idea['description']}</p>
</div>""", unsafe_allow_html=True)

        if tips:
            st.markdown("#### 🎯 Personalization Tips")
            for tip in tips:
                st.markdown(f"- {tip}")
    else:
        st.warning("Theme ideas not available.")

    # ---- EXPORT BUTTON (placeholder — wired in Sub-Task 8) ----
    st.divider()
    col_export, _ = st.columns([1, 3])
    with col_export:
        if st.button("📄 Export as PDF", use_container_width=True):
            with st.spinner("Generating PDF..."):
                resp = api_get(f"/events/{event_id}/plans/export/pdf")
                if resp.status_code == 200:
                    st.download_button(
                        "⬇️ Download PDF",
                        data=resp.content,
                        file_name=f"event_plan_{event_id}.pdf",
                        mime="application/pdf",
                    )
                else:
                    st.error("PDF export not available yet.")
