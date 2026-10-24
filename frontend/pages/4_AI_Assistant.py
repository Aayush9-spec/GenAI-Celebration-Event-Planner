import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from utils.api import api_get, api_post, api_delete
from utils.auth_guard import require_auth
from utils.styles import inject_global_styles, render_sidebar

st.set_page_config(page_title="AI Assistant — Event Planner", page_icon="🤖", layout="wide")
require_auth()
inject_global_styles()
render_sidebar(st.session_state.get("current_event_title"))

st.markdown("""
<style>
    .chat-header {
        background: linear-gradient(90deg, #7c5cd8, #3b82d4);
        color: white; padding: 1rem 1.5rem; border-radius: 12px; margin-bottom: 1rem;
    }
    .assistant-info {
        background: #f7f8fa; border: 1px solid #e5e7eb;
        border-radius: 8px; padding: 0.8rem 1rem; margin-bottom: 1rem;
        font-size: 0.9rem; color: #57606a;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="chat-header">
    <h2 style="margin:0">🤖 AI Event Planning Assistant</h2>
    <p style="margin:0;opacity:0.9">Ask me anything about your event — vendors, budget, decorations, timeline...</p>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Event Selector
# ------------------------------------------------------------------
resp = api_get("/events/")
if resp.status_code != 200:
    st.error("Could not load events.")
    st.stop()

events = resp.json()
if not events:
    st.info("No events found. Create an event first in 📅 My Events.")
    st.stop()

event_options = {f"{e['title']} ({e['event_type']})": e for e in events}
default_idx = 0
if st.session_state.get("current_event_id"):
    for i, e in enumerate(events):
        if e["id"] == st.session_state["current_event_id"]:
            default_idx = i
            break

col_sel, col_clear = st.columns([4, 1])
with col_sel:
    selected_label = st.selectbox("Select Event", list(event_options.keys()), index=default_idx)
with col_clear:
    st.write("")
    clear_btn = st.button("🗑️ Clear Chat", use_container_width=True)

selected_event = event_options[selected_label]
event_id = selected_event["id"]
st.session_state["current_event_id"] = event_id

# Show event context
st.markdown(f"""
<div class="assistant-info">
    🎯 <b>Context:</b> {selected_event['event_type'].capitalize()} — <b>{selected_event['title']}</b>
    &nbsp;|&nbsp; 👥 {selected_event['guest_count']} guests
    &nbsp;|&nbsp; 💰 ₹{selected_event['total_budget']:,.0f}
    &nbsp;|&nbsp; 📅 {selected_event['event_date']}
    {f"&nbsp;|&nbsp; 📍 {selected_event['city']}" if selected_event.get('city') else ""}
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Clear chat
# ------------------------------------------------------------------
if clear_btn:
    del_resp = api_delete(f"/events/{event_id}/chat/")
    if del_resp.status_code == 204:
        st.session_state.pop(f"chat_history_{event_id}", None)
        st.success("Chat cleared.")
        st.rerun()
    else:
        st.error("Could not clear chat.")

# ------------------------------------------------------------------
# Load chat history
# ------------------------------------------------------------------
cache_key = f"chat_history_{event_id}"
if cache_key not in st.session_state:
    hist_resp = api_get(f"/events/{event_id}/chat/")
    if hist_resp.status_code == 200:
        st.session_state[cache_key] = hist_resp.json()
    else:
        st.session_state[cache_key] = []

history = st.session_state[cache_key]

# ------------------------------------------------------------------
# Render messages
# ------------------------------------------------------------------
chat_container = st.container()
with chat_container:
    if not history:
        st.markdown("""
<div style="text-align:center;padding:2rem;color:#57606a">
    <p>👋 No messages yet. Ask me anything about your event!</p>
    <p><small>Try: "What vendors should I book first?" or "Give me decoration ideas on a budget"</small></p>
</div>
""", unsafe_allow_html=True)
    else:
        for msg in history:
            role = msg["role"]
            content = msg["content"]
            with st.chat_message("user" if role == "user" else "assistant"):
                st.markdown(content)

# ------------------------------------------------------------------
# Chat input
# ------------------------------------------------------------------
user_input = st.chat_input("Ask your event assistant... (e.g. 'What's the best catering option?')")

if user_input:
    # Optimistically render user message
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            resp = api_post(
                f"/events/{event_id}/chat/",
                json={"content": user_input},
                authenticated=True,
            )
            if resp.status_code == 201:
                ai_reply = resp.json()["content"]
                st.markdown(ai_reply)
                # Update local cache
                st.session_state[cache_key].append({"role": "user", "content": user_input})
                st.session_state[cache_key].append({"role": "model", "content": ai_reply})
            else:
                error_detail = resp.json().get("detail", resp.text) if resp.content else resp.text
                st.error(f"Error: {error_detail}")
