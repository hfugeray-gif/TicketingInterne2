import os
import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


def _build_headers() -> dict:
    headers = {}
    if st.session_state.get("current_user"):
        headers["x-demo-user"] = st.session_state["current_user"]
    if st.session_state.get("role"):
        headers["x-demo-role"] = st.session_state["role"]
    return headers


def api_get(path: str, params: dict | None = None):
    response = requests.get(
        f"{API_BASE_URL}{path}",
        params=params,
        headers=_build_headers(),
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


def api_post(path: str, payload: dict):
    response = requests.post(
        f"{API_BASE_URL}{path}",
        json=payload,
        headers=_build_headers(),
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


def api_patch(path: str, payload: dict):
    response = requests.patch(
        f"{API_BASE_URL}{path}",
        json=payload,
        headers=_build_headers(),
        timeout=15,
    )
    response.raise_for_status()
    return response.json()