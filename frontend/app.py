import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

import streamlit as st
from frontend.utils.session import init_session_state
from frontend.utils.api_client import APIClient
from frontend.components.auth import render_auth_page
from frontend.components.sidebar import render_sidebar
from frontend.components.chat import render_chat_interface
from frontend.components.profile import render_profile

st.set_page_config(
    page_title="Interview Prep AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session_state()
api = APIClient()


def _load_theme_css():
    theme = st.session_state.get("theme", "light")
    st.markdown(f'<div data-theme="{theme}">', unsafe_allow_html=True)
    css_path = os.path.join(os.path.dirname(__file__), "styles", "custom.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def _render_header():
    st.markdown('<p class="app-title">Interview Prep AI</p>', unsafe_allow_html=True)


def main():
    _load_theme_css()

    if not st.session_state.authenticated:
        render_auth_page()
        return

    token = st.session_state.access_token

    if st.session_state.user and not st.session_state.get("settings_loaded"):
        profile = api.get_profile(token)
        if "error" not in profile:
            settings = profile.get("settings", {})
            st.session_state.theme = settings.get("preferred_theme", "light")
            st.session_state.settings_loaded = True

    _render_header()
    render_sidebar()

    if st.session_state.get("show_profile"):
        render_profile()
    else:
        render_chat_interface()


if __name__ == "__main__":
    main()
