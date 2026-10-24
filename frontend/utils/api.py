import os
from typing import Optional

import requests
import streamlit as st

BACKEND_URL = st.secrets.get("BACKEND_URL", os.getenv("BACKEND_URL", "http://localhost:8000"))


def get_headers() -> dict:
    """Return Authorization header from session state token."""
    token = st.session_state.get("token")
    if token:
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    return {"Content-Type": "application/json"}


def api_post(path: str, json: dict = None, authenticated: bool = False) -> requests.Response:
    headers = get_headers() if authenticated else {"Content-Type": "application/json"}
    return requests.post(f"{BACKEND_URL}{path}", json=json, headers=headers, timeout=30)


def api_get(path: str, params: dict = None) -> requests.Response:
    return requests.get(f"{BACKEND_URL}{path}", params=params, headers=get_headers(), timeout=30)


def api_put(path: str, json: dict = None) -> requests.Response:
    return requests.put(f"{BACKEND_URL}{path}", json=json, headers=get_headers(), timeout=30)


def api_delete(path: str) -> requests.Response:
    return requests.delete(f"{BACKEND_URL}{path}", headers=get_headers(), timeout=30)


def is_authenticated() -> bool:
    return bool(st.session_state.get("token"))


def logout():
    for key in ["token", "user", "current_event_id", "current_event_title"]:
        st.session_state.pop(key, None)
